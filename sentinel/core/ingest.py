"""
sentinel/core/ingest.py (v1.2)
-----------------------
Updated to support recursive item hierarchies and configuration-driven parsing.
"""

import json
import csv
import logging
import lxml.etree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class SourceRef:
    """Exact provenance for a single value so the evidence chain can cite it."""
    file: str
    record_index: int          # 0-based record/element position in file
    line_hint: int | None      # approximate line number (best-effort)
    field: str


@dataclass
class InvoiceLineItem:
    invoice_id: str
    vendor_name: str
    date: str
    sku: str
    description: str
    quantity: float
    billed_unit_price: float
    parent_sku: Optional[str] = None # Added for Phase 2 Hierarchies
    # provenance
    src_sku: SourceRef = field(default=None, repr=False)
    src_quantity: SourceRef = field(default=None, repr=False)
    src_billed_unit_price: SourceRef = field(default=None, repr=False)


@dataclass
class POLineItem:
    po_id: str
    item_reference: str
    agreed_unit_price: float
    status: str
    qty_authorized: float
    src_row: SourceRef = field(default=None, repr=False)
    src_agreed_unit_price: SourceRef = field(default=None, repr=False)
    src_qty_authorized: SourceRef = field(default=None, repr=False)


@dataclass
class PODLineItem:
    waybill_ref: str
    part_id: str
    qty_received_at_dock: float
    condition: str
    src_element: SourceRef = field(default=None, repr=False)
    src_qty_received: SourceRef = field(default=None, repr=False)


# ── helpers ──────────────────────────────────────────────────────────────────

def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or str(value).lower() == "null" or str(value).strip() == "":
        return default
    try:
        s = str(value).strip()
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        elif "," in s and "." in s:
            # Assume comma is thousands separator if dot exists
            s = s.replace(",", "")
        return float(s)
    except (ValueError, TypeError):
        return default


# ── loaders ──────────────────────────────────────────────────────────────────

def _find_json_line(path: Path, invoice_id: str, sku: str) -> int | None:
    """Best-effort approximation of a line number in a JSON file."""
    try:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        # Search for a line that likely marks this record
        for i, line in enumerate(lines, 1):
            if sku in line and invoice_id in text[max(0, text.find(line)-1000):text.find(line)+1000]:
                return i
    except Exception:
        pass
    return None


def load_invoices(path: str | Path) -> list[InvoiceLineItem]:
    path = Path(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to parse JSON in {path}: {e}")
        return []

    items: list[InvoiceLineItem] = []
    if not isinstance(raw, list):
        logger.warning(f"Expected list in {path}, got {type(raw)}")
        raw = [raw] if isinstance(raw, dict) else []

    for inv_idx, invoice in enumerate(raw):
        if not isinstance(invoice, dict): continue
        
        inv_id = str(invoice.get("invoice_id") or invoice.get("Id") or "UNKNOWN")
        vendor = str(invoice.get("vendor_name") or "UNKNOWN")
        
        line_items = invoice.get("line_items") or invoice.get("items")
        if not isinstance(line_items, list):
            if any(k in invoice for k in ["sku", "quantity", "billed_unit_price"]):
                line_items = [invoice]
            else:
                line_items = []

        for li_idx, li in enumerate(line_items):
            if not isinstance(li, dict): continue
            
            sku = str(li.get("sku") or li.get("item_reference") or "").strip()
            
            # Identify line hint for JSON
            line_no = _find_json_line(path, inv_id, sku)

            def ref(f, line_no=line_no): 
                return SourceRef(
                    file=str(path), record_index=inv_idx * 100 + li_idx,
                    line_hint=line_no, field=f
                )
            items.append(InvoiceLineItem(
                invoice_id=inv_id,
                vendor_name=vendor,
                date=str(invoice.get("date") or ""),
                sku=sku,
                description=str(li.get("description") or "").strip(),
                quantity=_safe_float(li.get("quantity", 0)),
                billed_unit_price=_safe_float(li.get("billed_unit_price", 0)),
                parent_sku=li.get("parent_sku"),
                src_sku=ref("sku"),
                src_quantity=ref("quantity"),
                src_billed_unit_price=ref("billed_unit_price"),
            ))
    return items


def load_purchase_orders(path: str | Path) -> list[POLineItem]:
    path = Path(path)
    items: list[POLineItem] = []

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row_idx, row in enumerate(reader):
            csv_line = row_idx + 2
            def ref(f, row_idx=row_idx, csv_line=csv_line):
                return SourceRef(
                    file=str(path), record_index=row_idx,
                    line_hint=csv_line, field=f
                )
            items.append(POLineItem(
                po_id=(row.get("po_id") or row.get("PO_id") or "").strip(),
                item_reference=row.get("item_reference", "").strip(),
                agreed_unit_price=_safe_float(row.get("agreed_unit_price", 0)),
                status=row.get("status", "").strip(),
                qty_authorized=_safe_float(row.get("qty_authorized", 0)),
                src_row=ref("row"),
                src_agreed_unit_price=ref("agreed_unit_price"),
                src_qty_authorized=ref("qty_authorized"),
            ))
    return items


def load_pod(path: str | Path) -> list[PODLineItem]:
    path = Path(path)
    try:
        parser = ET.XMLParser(recover=True)
        tree = ET.parse(str(path), parser=parser)
    except Exception as e:
        logger.error(f"Malformed XML in {path}: {e}")
        return []

    items: list[PODLineItem] = []
    elem_idx = 0
    
    # Using tree.xpath if preferred, or root.findall
    for delivery in tree.xpath("//delivery"):
        waybill = (delivery.get("waybill_ref") or delivery.get("waybill") or "UNKNOWN")
        for item_elem in delivery.xpath(".//item"):
            line_no = item_elem.sourceline
            
            ref = lambda f: SourceRef(
                file=str(path), record_index=elem_idx,
                line_hint=line_no, field=f
            )
            items.append(PODLineItem(
                waybill_ref=waybill,
                part_id=str(item_elem.get("part_id", "")).strip(),
                qty_received_at_dock=_safe_float(item_elem.get("qty_received_at_dock") or item_elem.get("qty_received") or 0),
                condition=str(item_elem.get("condition", "")).strip(),
                src_element=ref("item_element"),
                src_qty_received=ref("qty_received_at_dock"),
            ))
            elem_idx += 1
    return items
