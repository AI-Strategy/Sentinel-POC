"""
sentinel/core/match.py (v1.1 - Gemini)
-------------------------------------
Links Invoice line items → PO line items → POD line items into
a unified "Transaction Object".

Strategy (layered):
  1. Exact SKU / item_reference / part_id match (cheapest).
  2. Fuzzy string match via difflib (medium cost).
  3. Gemini-assisted semantic match for ambiguous pairs (expensive,
     only triggered when fuzzy confidence < FUZZY_THRESHOLD).
"""

import json
import logging
from dataclasses import dataclass, field
from rapidfuzz import process, fuzz
from typing import Optional

from .llm import get_client, GeminiClient
from .ingest import InvoiceLineItem, POLineItem, PODLineItem

logger = logging.getLogger(__name__)

FUZZY_THRESHOLD = 0.85          # Higher precision to avoid false matches in large sets
LLM_BATCH_SIZE  = 20            # max pairs sent to Gemini in one call


@dataclass
class TransactionObject:
    """A fully-linked (or partially-linked) transaction across all three sources."""
    invoice_line:  InvoiceLineItem
    po_line:       Optional[POLineItem]  = None
    pod_line:      Optional[PODLineItem] = None
    match_method_inv_po:  str = "unmatched"   # exact | fuzzy | gemini | unmatched
    match_score_inv_po:   float = 0.0
    match_method_inv_pod: str = "unmatched"
    match_score_inv_pod:  float = 0.0
    notes: list[str] = field(default_factory=list)


def _fuzzy_score(a: str, b: str) -> float:
    return fuzz.ratio(a.upper(), b.upper()) / 100.0


def _best_fuzzy(
    invoice_sku: str,
    candidates: list[str],
) -> tuple[str | None, float]:
    """Return the best-matching candidate and its score using RapidFuzz process."""
    if not candidates:
        return None, 0.0
    
    # rapidfuzz.process.extractOne is extremely optimized
    result = process.extractOne(invoice_sku.upper(), candidates, scorer=fuzz.ratio)
    if result:
        match_str, score, index = result
        return match_str, score / 100.0
    return None, 0.0


def _llm_match(
    invoice_sku: str,
    invoice_desc: str,
    candidates: list[dict],
    client: Optional[GeminiClient] = None,
) -> tuple[str | None, float]:
    """
    Ask Gemini to choose the best matching candidate SKU.
    Returns (matched_key_or_None, confidence_0_to_1).
    """
    if not candidates:
        return None, 0.0
    try:
        if client is None:
            client = get_client()
        if not client.available:
            return None, 0.0

        prompt = f"""You are a procurement data-matching assistant.

Invoice item:
  SKU: {invoice_sku}
  Description: {invoice_desc}

Candidate items from Purchase Order / Proof of Delivery:
{json.dumps(candidates, indent=2)}

Task: identify which candidate (by "key") is the same physical item as the invoice SKU.
If none match, state null.

Respond ONLY with valid JSON matching this structure:
{{"matched_key": "<key or null>", "confidence": <0.0-1.0>, "reason": "<one sentence>"}}
"""
        # Using GeminiClient's complete_json which handles the modern SDK + JSON formatting
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
    """
    For every invoice line, attempt to find a matching PO line and POD line.
    Returns a list of TransactionObjects (some partially matched).
    """
    # Build lookup indices
    po_by_sku:  dict[str, POLineItem]  = {p.item_reference.upper(): p for p in pos}
    pod_by_sku: dict[str, PODLineItem] = {p.part_id.upper(): p for p in pods}

    transactions: list[TransactionObject] = []

    for inv in invoices:
        txn = TransactionObject(invoice_line=inv)
        inv_sku_upper = inv.sku.upper()

        # ── PO match ──────────────────────────────────────────────────────
        if inv_sku_upper in po_by_sku:
            txn.po_line = po_by_sku[inv_sku_upper]
            txn.match_method_inv_po = "exact"
            txn.match_score_inv_po = 1.0
        else:
            # Multi-factor fuzzy: combine SKU and Description
            candidates = list(po_by_sku.keys())
            best_key, score = _best_fuzzy(inv.sku, candidates)
            
            # Additional check: does description also match?
            if best_key and score >= FUZZY_THRESHOLD:
                cand_po = po_by_sku[best_key]
                desc_score = _fuzzy_score(inv.description, cand_po.item_reference) # If no description in PO, use key
                
                # If the score is very high on SKU, or decent on both
                if score > 0.95 or (score > 0.85 and desc_score > 0.5):
                    txn.po_line = cand_po
                    txn.match_method_inv_po = "fuzzy"
                    txn.match_score_inv_po = round(score, 3)
                    txn.notes.append(f"PO matched via fuzzy: '{inv.sku}' → '{best_key}'")
                elif use_llm:
                    # Fallback to LLM if it's "close but not sure"
                    llm_candidates = [{"key": k, "description": k} for k in candidates[:50]] # Limit context
                    matched_key, conf = _llm_match(inv.sku, inv.description, llm_candidates)
                    if matched_key and matched_key.upper() in po_by_sku:
                        txn.po_line = po_by_sku[matched_key.upper()]
                        txn.match_method_inv_po = "gemini"
                        txn.match_score_inv_po = round(conf, 3)
                        txn.notes.append(f"PO matched via Gemini: '{inv.sku}' → '{matched_key}'")
            elif use_llm:
                # Potential match not even in fuzzy top? Unlikely but check LLM if requested
                pass
            
            if not txn.po_line:
                txn.notes.append(f"No PO match found for SKU '{inv.sku}'")

        # ── POD match ─────────────────────────────────────────────────────
        if inv_sku_upper in pod_by_sku:
            txn.pod_line = pod_by_sku[inv_sku_upper]
            txn.match_method_inv_pod = "exact"
            txn.match_score_inv_pod = 1.0
        else:
            candidates = list(pod_by_sku.keys())
            best_key, score = _best_fuzzy(inv.sku, candidates)
            if best_key and score >= FUZZY_THRESHOLD:
                cand_pod = pod_by_sku[best_key]
                if score > 0.95: # Very strict for POD
                    txn.pod_line = cand_pod
                    txn.match_method_inv_pod = "fuzzy"
                    txn.match_score_inv_pod = round(score, 3)
                    txn.notes.append(f"POD matched via fuzzy: '{inv.sku}' → '{best_key}'")
                elif use_llm:
                    llm_candidates = [{"key": k, "description": k} for k in candidates[:50]]
                    matched_key, conf = _llm_match(inv.sku, inv.description, llm_candidates)
                    if matched_key and matched_key.upper() in pod_by_sku:
                        txn.pod_line = pod_by_sku[matched_key.upper()]
                        txn.match_method_inv_pod = "gemini"
                        txn.match_score_inv_pod = round(conf, 3)
                        txn.notes.append(f"POD matched via Gemini: '{inv.sku}' → '{matched_key}'")
            
            if not txn.pod_line:
                txn.notes.append(f"No POD match found for SKU '{inv.sku}'")


        transactions.append(txn)

    return transactions
