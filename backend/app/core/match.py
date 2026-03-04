"""
sentinel/core/match.py  (v0.3 — Gemini)
-----------------------------------------
Links Invoice → PO → POD via exact match, fuzzy match, then Gemini LLM.
All Claude/Anthropic references replaced with GeminiClient from llm.py.
"""

import json
import logging
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Optional

from .llm import get_client
from .ingest import InvoiceLineItem, POLineItem, PODLineItem

logger = logging.getLogger(__name__)

FUZZY_THRESHOLD = 0.72


@dataclass
class TransactionObject:
    invoice_line:         InvoiceLineItem
    po_line:              Optional[POLineItem]  = None
    pod_line:             Optional[POLineItem] = None
    match_method_inv_po:  str   = "unmatched"
    match_score_inv_po:   float = 0.0
    match_method_inv_pod: str   = "unmatched"
    match_score_inv_pod:  float = 0.0
    notes: list[str] = field(default_factory=list)


def _fuzzy_score(a: str, b: str) -> float:
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()


def _best_fuzzy(sku: str, candidates: list[str]) -> tuple[str | None, float]:
    best_key, best_score = None, 0.0
    for cand in candidates:
        s = _fuzzy_score(sku, cand)
        if s > best_score:
            best_score, best_key = s, cand
    return best_key, best_score


def _llm_match(invoice_sku: str, invoice_desc: str, candidates: list[dict]) -> tuple[str | None, float]:
    """Use Gemini to choose the best matching candidate SKU."""
    if not candidates:
        return None, 0.0
    try:
        client = get_client()
        if not client.available:
            return None, 0.0
        prompt = f"""You are a procurement data-matching assistant.

Invoice item:
  SKU: {invoice_sku}
  Description: {invoice_desc}

Candidate items from Purchase Order / Proof of Delivery:
{json.dumps(candidates, indent=2)}

Identify which candidate (by "key") is the same physical item as the invoice SKU.
If none match, use null.

Respond ONLY with valid JSON (no markdown):
{{"matched_key": "<key or null>", "confidence": <0.0-1.0>, "reason": "<one sentence>"}}"""

        result = client.complete_json(prompt, max_tokens=256)
        return result.get("matched_key"), float(result.get("confidence", 0.0))
    except Exception as exc:
        logger.warning("Gemini LLM match failed for %s: %s", invoice_sku, exc)
        return None, 0.0


def link_transactions(
    invoices: list[InvoiceLineItem],
    pos:      list[POLineItem],
    pods:     list[PODLineItem],
    use_llm:  bool = True,
) -> list[TransactionObject]:
    po_by_sku  = {p.item_reference.upper(): p for p in pos}
    pod_by_sku = {p.part_id.upper(): p for p in pods}
    transactions = []

    for inv in invoices:
        txn = TransactionObject(invoice_line=inv)
        sku = inv.sku.upper()

        # ── PO match ──────────────────────────────────────────────────────
        if sku in po_by_sku:
            txn.po_line = po_by_sku[sku]
            txn.match_method_inv_po, txn.match_score_inv_po = "exact", 1.0
        else:
            best_key, score = _best_fuzzy(inv.sku, list(po_by_sku.keys()))
            if score >= FUZZY_THRESHOLD:
                txn.po_line = po_by_sku[best_key]
                txn.match_method_inv_po = "fuzzy"
                txn.match_score_inv_po  = round(score, 3)
                txn.notes.append(f"PO fuzzy ({score:.0%}): '{inv.sku}'→'{txn.po_line.item_reference}'")
            elif use_llm:
                candidates = [{"key": k, "description": k} for k in po_by_sku]
                matched_key, conf = _llm_match(inv.sku, inv.description, candidates)
                if matched_key and matched_key.upper() in po_by_sku:
                    txn.po_line = po_by_sku[matched_key.upper()]
                    txn.match_method_inv_po = "gemini"
                    txn.match_score_inv_po  = round(conf, 3)
                    txn.notes.append(f"PO Gemini (conf={conf:.0%}): '{inv.sku}'→'{matched_key}'")
                else:
                    txn.notes.append(f"No PO match for '{inv.sku}'")
            else:
                txn.notes.append(f"No PO match for '{inv.sku}'")

        # ── POD match ─────────────────────────────────────────────────────
        if sku in pod_by_sku:
            txn.pod_line = pod_by_sku[sku]
            txn.match_method_inv_pod, txn.match_score_inv_pod = "exact", 1.0
        else:
            best_key, score = _best_fuzzy(inv.sku, list(pod_by_sku.keys()))
            if score >= FUZZY_THRESHOLD:
                txn.pod_line = pod_by_sku[best_key]
                txn.match_method_inv_pod = "fuzzy"
                txn.match_score_inv_pod  = round(score, 3)
                txn.notes.append(f"POD fuzzy ({score:.0%}): '{inv.sku}'→'{txn.pod_line.part_id}'")
            elif use_llm:
                candidates = [{"key": k, "description": k} for k in pod_by_sku]
                matched_key, conf = _llm_match(inv.sku, inv.description, candidates)
                if matched_key and matched_key.upper() in pod_by_sku:
                    txn.pod_line = pod_by_sku[matched_key.upper()]
                    txn.match_method_inv_pod = "gemini"
                    txn.match_score_inv_pod  = round(conf, 3)
                    txn.notes.append(f"POD Gemini (conf={conf:.0%}): '{inv.sku}'→'{matched_key}'")
                else:
                    txn.notes.append(f"No POD match for '{inv.sku}'")
            else:
                txn.notes.append(f"No POD match for '{inv.sku}'")

        transactions.append(txn)

    return transactions
