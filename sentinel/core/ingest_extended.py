"""
sentinel/core/ingest_extended.py (v1.5)
---------------------------------
Multi-format ingestion layer for Sentinel.
Now supports direct Native PDF/PNG processing via Gemini Structured Outputs.

Supports:
  .json, .csv, .xml, .xls, .xlsx
  .pdf, .png, .jpg, .jpeg, .webp, .bmp (Native Gemini extraction)
"""

from __future__ import annotations

import base64
import io
import json
import logging
import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Extraction Pydantic Schemas ───────────────────────────────────────────────

class LineItem(BaseModel):
    sku: str = Field(..., description="Unique product identifier (SKU)")
    description: str = Field(..., description="Description of the item")
    quantity: float = Field(..., description="Quantity of items")
    billed_unit_price: Optional[float] = Field(None, description="Invoiced unit price (for invoices)")
    agreed_unit_price: Optional[float] = Field(None, description="Contracted unit price (for POs)")
    qty_received_at_dock: Optional[float] = Field(None, description="Received quantity (for PODs)")
    condition: Optional[str] = Field(None, description="Condition of items (for PODs)")

class DocumentExtraction(BaseModel):
    document_type: str = Field(..., description="One of: invoice | purchase_order | delivery_receipt | unknown")
    records: List[LineItem] = Field(..., description="List of extracted line items")
    summary: str = Field(..., description="One sentence summary of the document")
    invoice_id: Optional[str] = None
    po_id: Optional[str] = None
    waybill_ref: Optional[str] = None


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ParseResult:
    file_path: str
    file_type: str                     # extension
    document_type: str                 # invoice | purchase_order | delivery | unknown
    records: list[dict] = field(default_factory=list)
    raw_text: str = ""                 # for audit / debug
    errors: list[str] = field(default_factory=list)
    page_count: int = 0
    used_vision: bool = False


# ── Document-type heuristic for structured files ─────────────────────────────

_SIGNALS = {
    "invoice": {"invoice", "inv", "bill", "billed", "vendor", "billed_unit_price"},
    "purchase_order": {"purchase", "po", "order", "agreed_unit_price", "qty_authorized", "authorized"},
    "delivery": {"delivery", "pod", "waybill", "received", "dock", "condition", "waybill_ref"}
}

def _detect_doc_type(keys: list[str]) -> str:
    key_set = {k.lower() for k in keys}
    scores = {dt: sum(1 for s in signals if any(s in k for k in key_set)) for dt, signals in _SIGNALS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


# ── Gemini Native Processing (Multi-Modal) ────────────────────────────────────

def parse_with_gemini(path: Path) -> ParseResult:
    """Passes PDF/Image bytes directly to Gemini for structured extraction."""
    result = ParseResult(file_path=str(path), file_type=path.suffix.lstrip(".").lower(), document_type="unknown")
    result.used_vision = True
    
    try:
        from .llm import get_client
        client = get_client()
        if not client.available:
            result.errors.append("Gemini client unavailable — set GEMINI_API_KEY.")
            return result

        mime_types = {
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".bmp": "image/bmp"
        }
        
        mime_type = mime_types.get(path.suffix.lower(), "application/octet-stream")
        file_bytes = path.read_bytes()
        
        prompt = "Extract ALL structured line-item data from this procurement document. Maintain high fidelity for SKU/Item codes."
        
        # Use the new complete_json method with Pydantic schema
        extraction: DocumentExtraction = client.complete_json(
            prompt,
            images=[{"data": base64.b64encode(file_bytes).decode(), "mime_type": mime_type}],
            response_schema=DocumentExtraction
        )
        
        result.records = [r.model_dump() for r in extraction.records]
        
        # Add IDs to each record if applicable
        doc_id = extraction.invoice_id or extraction.po_id or extraction.waybill_ref
        if doc_id:
            for r in result.records:
                r["_document_id"] = doc_id
        
        result.document_type = extraction.document_type
        if result.document_type == "delivery_receipt": result.document_type = "delivery"
        result.raw_text = extraction.summary
        
    except Exception as exc:
        logger.error("Gemini Native extraction failed for %s: %s", path.name, exc)
        result.errors.append(str(exc))
        
    return result


# ── Structured Parsers ────────────────────────────────────────────────────────

def parse_json(path: Path) -> ParseResult:
    result = ParseResult(file_path=str(path), file_type="json", document_type="unknown")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        records = data if isinstance(data, list) else (list(data.values())[0] if isinstance(data, dict) and any(isinstance(v, list) for v in data.values()) else [data])
        result.records = records
        result.document_type = _detect_doc_type(list(records[0].keys()) if records else [])
    except Exception as exc: result.errors.append(str(exc))
    return result

def parse_csv(path: Path) -> ParseResult:
    result = ParseResult(file_path=str(path), file_type="csv", document_type="unknown")
    try:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            records = [dict(row) for row in csv.DictReader(fh)]
            result.records = records
            result.document_type = _detect_doc_type(list(records[0].keys()) if records else [])
    except Exception as exc: result.errors.append(str(exc))
    return result


# ── Ingest Mapper ────────────────────────────────────────────────────────────

PARSERS = {
    ".json": parse_json, 
    ".csv": parse_csv,
    # Native Gemini Vision/PDF Support
    ".pdf": parse_with_gemini,
    ".png": parse_with_gemini, ".jpg": parse_with_gemini, ".jpeg": parse_with_gemini,
    ".webp": parse_with_gemini, ".bmp": parse_with_gemini
}

def parse_file(path: str | Path, use_vision: bool = True) -> ParseResult:
    path = Path(path)
    ext = path.suffix.lower()
    if not path.exists(): return ParseResult(str(path), ext.lstrip("."), "unknown", errors=[f"Not found: {path}"])
    
    parser = PARSERS.get(ext)
    if not parser: return ParseResult(str(path), ext.lstrip("."), "unknown", errors=[f"Unsupported: {ext}"])
    
    logger.info("Ingesting %s …", path.name)
    return parser(path)

def parse_files(paths: list[str | Path]) -> list[ParseResult]:
    return [parse_file(p) for p in paths]
