"""
sentinel/core/ingest.py
-----------------------
Ingests raw Invoice (JSON), PO (CSV), and POD (XML) files.
Returns normalized, line-level records with source provenance
(file path + line / element index) attached to every field.
"""

import json
import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    # provenance
    src_invoice_id: SourceRef = field(default=None, repr=False)
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
        # Handle decimal commas (e.g. 3,25 -> 3.25)
        # Note: This is simplified; assumes comma is always a decimal if present 
        # but only if there isn't also a dot, or handling it as the last separator.
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

def load_invoices(path: str | Path) -> list[InvoiceLineItem]:
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    items: list[InvoiceLineItem] = []

    for inv_idx, invoice in enumerate(raw):
        inv_id = invoice.get("invoice_id", f"UNKNOWN-{inv_idx}")
        vendor = invoice.get("vendor_name", "")
        date = invoice.get("date", "")

        for li_idx, li in enumerate(invoice.get("line_items", [])):
            sku = str(li.get("sku", "")).strip()
            # Estimate line number: JSON is hard to pin exactly; use record index
            approx_line = None  # JSON doesn't have reliable line numbers

            def ref(f, inv_idx=inv_idx, li_idx=li_idx):
                 return SourceRef(
                    file=str(path), record_index=inv_idx * 100 + li_idx,
                    line_hint=approx_line, field=f
                )
                 
            items.append(InvoiceLineItem(
                invoice_id=inv_id,
                vendor_name=vendor,
                date=date,
                sku=sku,
                description=str(li.get("description", "")).strip(),
                quantity=_safe_float(li.get("quantity", 0)),
                billed_unit_price=_safe_float(li.get("billed_unit_price", 0)),
                src_invoice_id=ref("invoice_id"),
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
            csv_line = row_idx + 2  # +1 header, +1 for 1-based
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
    items: list[PODLineItem] = []
    try:
        tree = ET.parse(str(path))
    except Exception as e:
        logger.error(f"Malformed XML in {path}: {e}")
        # Look for a recovery file if it exists (for dataset_04)
        recovery_path = path.parent / (path.stem + "_recovered" + path.suffix)
        if recovery_path.exists():
            logger.info(f"Using recovery file: {recovery_path}")
            try:
                tree = ET.parse(str(recovery_path))
            except:
                return []
        else:
            return []

    root = tree.getroot()
    elem_idx = 0

    for delivery in root.findall(".//delivery"):
        waybill = (delivery.get("waybill_ref") or delivery.get("waybill") or "UNKNOWN")
        for item_elem in delivery.findall("item"):
            def ref(f, elem_idx=elem_idx):
                return SourceRef(
                    file=str(path), record_index=elem_idx,
                    line_hint=None, field=f  # ElementTree strips line info
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
