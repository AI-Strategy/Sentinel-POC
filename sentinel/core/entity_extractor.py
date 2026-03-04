"""
sentinel/core/entity_extractor.py
----------------------------------
Gemini-powered entity extraction layer.

Given raw text or parsed records from any source document, extracts a
canonical set of ENTITIES and RELATIONS in a structured JSON envelope
ready for:
  - Postgres  (raw entity rows via postgres.py)
  - Neo4j     (nodes + relationships via graph.py)

Entity schema produced
----------------------
{
  "extraction_id": "<uuid>",
  "source_file": "<path or connector label>",
  "document_type": "invoice | purchase_order | delivery_receipt | unknown",
  "extracted_at": "<iso8601>",
  "entities": {
    "vendors":   [{ "vendor_id", "name", "name_variants": [], "confidence" }],
    "items":     [{ "item_id", "sku", "description", "unit", "category" }],
    "invoices":  [{ "invoice_id", "vendor_id", "date", "currency",
                    "line_items": [{ "item_id","sku","qty","unit_price","total" }] }],
    "purchase_orders": [{ "po_id", "item_id", "agreed_price", "qty_authorized",
                          "status", "currency" }],
    "deliveries": [{ "waybill_ref", "item_id", "qty_received", "condition",
                     "delivery_date" }]
  },
  "relations": [
    { "from_type","from_id","relation","to_type","to_id","properties" }
  ],
  "anomalies": [
    { "type","description","severity","entity_refs": [] }
  ]
}
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from .llm import GeminiClient, get_client

logger = logging.getLogger(__name__)

# ── Prompts ───────────────────────────────────────────────────────────────────

_ENTITY_EXTRACTION_PROMPT = """You are a procurement data intelligence engine.

Your task: extract ALL entities and relationships from the following procurement document data.

Return ONLY a valid JSON object — no markdown fences, no commentary — matching this exact schema:

{{
  "document_type": "<invoice|purchase_order|delivery_receipt|unknown>",
  "entities": {{
    "vendors": [
      {{ "vendor_id": "<slug>", "name": "<canonical name>", "name_variants": ["<alt name>"], "confidence": 0.0-1.0 }}
    ],
    "items": [
      {{ "item_id": "<sku-slug>", "sku": "<sku>", "description": "<text>", "unit": "<each|meter|kg|etc>", "category": "<fasteners|cable|pump|service|etc>" }}
    ],
    "invoices": [
      {{
        "invoice_id": "<id>", "vendor_id": "<slug>", "date": "<YYYY-MM-DD>", "currency": "USD",
        "line_items": [
          {{ "item_id": "<sku-slug>", "sku": "<sku>", "qty": 0, "unit_price": 0.0, "total": 0.0 }}
        ]
      }}
    ],
    "purchase_orders": [
      {{ "po_id": "<id>", "item_id": "<sku-slug>", "agreed_price": 0.0, "qty_authorized": 0, "status": "<APPROVED|PENDING>", "currency": "USD" }}
    ],
    "deliveries": [
      {{ "waybill_ref": "<ref>", "item_id": "<sku-slug>", "qty_received": 0, "condition": "<GOOD|DAMAGED>", "delivery_date": "<YYYY-MM-DD|null>" }}
    ]
  }},
  "relations": [
    {{ "from_type": "<Vendor|Invoice|PurchaseOrder|Delivery|Item>", "from_id": "<id>", "relation": "<ISSUED_BY|COVERS_ITEM|FULFILS_PO|DELIVERED_AS|etc>", "to_type": "<type>", "to_id": "<id>", "properties": {{}} }}
  ],
  "anomalies": [
    {{ "type": "<PRICE_MISMATCH|QTY_MISMATCH|PHANTOM_LINE|MISSING_PO|DAMAGED_GOODS>", "description": "<text>", "severity": "<HIGH|MEDIUM|LOW>", "entity_refs": ["<id>"] }}
  ]
}}

Rules:
- Normalise vendor names: "Apex Industrial Supplies Inc.", "APEX INDUSTRIAL", and "Apex Industrial Supplies" → same vendor_id "apex-industrial"
- item_id = lowercased SKU slug (e.g. "APX-BOLT-M12" → "apx-bolt-m12")
- If a billed item has NO corresponding PO entry, flag it as PHANTOM_LINE anomaly
- If invoiced quantity ≠ received quantity, flag as QTY_MISMATCH
- If invoiced price ≠ PO agreed price (> 1% tolerance), flag as PRICE_MISMATCH
- Emit a relation for every logical link you detect in the data

INPUT DATA:
{input_data}
"""

_VISION_EXTRACTION_PROMPT = """You are a procurement document OCR and entity extraction engine.

Examine this document image and extract ALL procurement entities and relationships.

Return ONLY valid JSON — no markdown fences — matching this exact schema:
{{
  "document_type": "<invoice|purchase_order|delivery_receipt|unknown>",
  "entities": {{
    "vendors": [ {{ "vendor_id": "<slug>", "name": "<name>", "name_variants": [], "confidence": 0.95 }} ],
    "items": [ {{ "item_id": "<sku-slug>", "sku": "<sku>", "description": "<desc>", "unit": "<unit>", "category": "<cat>" }} ],
    "invoices": [ {{ "invoice_id": "<id>", "vendor_id": "<slug>", "date": "<YYYY-MM-DD>", "currency": "USD", "line_items": [ {{ "item_id": "<slug>", "sku": "<sku>", "qty": 0, "unit_price": 0.0, "total": 0.0 }} ] }} ],
    "purchase_orders": [ {{ "po_id": "<id>", "item_id": "<slug>", "agreed_price": 0.0, "qty_authorized": 0, "status": "APPROVED", "currency": "USD" }} ],
    "deliveries": [ {{ "waybill_ref": "<ref>", "item_id": "<slug>", "qty_received": 0, "condition": "GOOD", "delivery_date": null }} ]
  }},
  "relations": [ {{ "from_type": "<type>", "from_id": "<id>", "relation": "<REL>", "to_type": "<type>", "to_id": "<id>", "properties": {{}} }} ],
  "anomalies": []
}}
"""


# ── Main extractor ────────────────────────────────────────────────────────────

class EntityExtractor:
    """
    Drives Gemini to extract entities and relations from parsed document data.
    Works on three input forms:
      1. list[dict]  — pre-parsed records from ingest_extended
      2. str         — raw text (from PDF extraction)
      3. list[dict images] — [{"data": b64, "mime_type": "image/png"}]
    """

    def __init__(self, client: GeminiClient | None = None):
        self.llm = client or get_client()

    def extract_from_records(
        self,
        records: list[dict],
        source_label: str = "unknown_source",
        document_type_hint: str = "unknown",
    ) -> dict:
        """Extract entities from pre-parsed structured records."""
        input_data = json.dumps(records, indent=2, default=str)
        prompt = _ENTITY_EXTRACTION_PROMPT.format(input_data=input_data[:8000])
        return self._run_extraction(prompt, source_label, document_type_hint)

    def extract_from_text(
        self,
        text: str,
        source_label: str = "unknown_source",
        document_type_hint: str = "unknown",
    ) -> dict:
        """Extract entities from raw text (PDF, OCR output, etc.)."""
        prompt = _ENTITY_EXTRACTION_PROMPT.format(input_data=text[:8000])
        return self._run_extraction(prompt, source_label, document_type_hint)

    def extract_from_image(
        self,
        images: list[dict],
        source_label: str = "unknown_source",
    ) -> dict:
        """Extract entities from image(s) using Gemini Vision."""
        try:
            result = self.llm.complete_json(
                _VISION_EXTRACTION_PROMPT,
                images=images,
                max_tokens=4096,
            )
            return self._wrap_result(result, source_label, used_vision=True)
        except Exception as exc:
            logger.error("Vision entity extraction failed for %s: %s", source_label, exc)
            return self._empty_result(source_label, error=str(exc))

    def extract_combined(
        self,
        all_records: dict[str, list[dict]],
        source_label: str = "combined_sources",
    ) -> dict:
        """
        Extract entities from all three document types simultaneously.
        all_records = {"invoices": [...], "purchase_orders": [...], "deliveries": [...]}
        This is the primary call for full reconciliation — Gemini sees everything at once
        and can detect cross-document anomalies directly.
        """
        combined = {
            "invoices":         all_records.get("invoices", []),
            "purchase_orders":  all_records.get("purchase_orders", []),
            "delivery_receipts": all_records.get("deliveries", []),
        }
        input_data = json.dumps(combined, indent=2, default=str)
        prompt = _ENTITY_EXTRACTION_PROMPT.format(input_data=input_data[:12000])
        return self._run_extraction(prompt, source_label, "combined")

    # ── internals ─────────────────────────────────────────────────────────────

    def _run_extraction(
        self,
        prompt: str,
        source_label: str,
        document_type_hint: str,
    ) -> dict:
        try:
            result = self.llm.complete_json(prompt, max_tokens=4096)
            return self._wrap_result(result, source_label)
        except Exception as exc:
            logger.error("Entity extraction failed for %s: %s", source_label, exc)
            return self._empty_result(source_label, error=str(exc))

    def _wrap_result(
        self,
        gemini_output: dict,
        source_label: str,
        used_vision: bool = False,
    ) -> dict:
        return {
            "extraction_id":   str(uuid.uuid4()),
            "source_file":     source_label,
            "document_type":   gemini_output.get("document_type", "unknown"),
            "extracted_at":    datetime.now(timezone.utc).isoformat(),
            "used_vision":     used_vision,
            "entities":        gemini_output.get("entities", _empty_entities()),
            "relations":       gemini_output.get("relations", []),
            "anomalies":       gemini_output.get("anomalies", []),
        }

    def _empty_result(self, source_label: str, error: str = "") -> dict:
        return {
            "extraction_id":  str(uuid.uuid4()),
            "source_file":    source_label,
            "document_type":  "unknown",
            "extracted_at":   datetime.now(timezone.utc).isoformat(),
            "used_vision":    False,
            "entities":       _empty_entities(),
            "relations":      [],
            "anomalies":      [],
            "error":          error,
        }


def _empty_entities() -> dict:
    return {
        "vendors": [], "items": [], "invoices": [],
        "purchase_orders": [], "deliveries": [],
    }


# ── Convenience function ──────────────────────────────────────────────────────

def extract_entities(
    records_or_text: list[dict] | str,
    source_label: str = "unknown",
    document_type_hint: str = "unknown",
    gemini_api_key: str | None = None,
) -> dict:
    """One-shot entity extraction. Returns the full extraction envelope."""
    client = get_client(api_key=gemini_api_key)
    extractor = EntityExtractor(client)
    if isinstance(records_or_text, str):
        return extractor.extract_from_text(records_or_text, source_label, document_type_hint)
    return extractor.extract_from_records(records_or_text, source_label, document_type_hint)
