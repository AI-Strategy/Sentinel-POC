"""
sentinel/core/detect.py
-----------------------
Ghost Invoice leakage detection engine.

Flags three categories of financial leakage:
  PRICE_VARIANCE   – invoiced unit price ≠ PO contracted price
  QTY_MISMATCH     – invoiced quantity ≠ physically received quantity
  PHANTOM_LINE     – billed item has no PO and/or no POD entry
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .match import TransactionObject
from .ingest import SourceRef


class GhostType(str, Enum):
    PRICE_VARIANCE = "PRICE_VARIANCE"
    QTY_MISMATCH   = "QTY_MISMATCH"
    PHANTOM_LINE   = "PHANTOM_LINE"


@dataclass
class GhostFlag:
    ghost_type:       GhostType
    severity:         str                 # HIGH | MEDIUM | LOW
    invoice_id:       str
    sku:              str
    description:      str
    invoiced_value:   float | str
    expected_value:   float | str
    delta:            float | str
    financial_impact: float               # $ exposure (0 if not calculable)
    evidence_refs:    list[SourceRef]     # exact file+line pointers
    narrative:        str                 # human-readable summary
    transaction:      Optional[TransactionObject] = None # Added for system compatibility


PRICE_TOLERANCE_PCT = 0.01   # flag if price differs by more than 1%
QTY_TOLERANCE       = 0      # flag any quantity discrepancy


def _pct_diff(a: float, b: float) -> float:
    if b == 0:
        return float("inf")
    return abs(a - b) / b


def _severity_price(pct: float) -> str:
    if pct > 0.10:  return "HIGH"
    if pct > 0.02:  return "MEDIUM"
    return "LOW"


def _severity_qty(delta: float, unit_price: float) -> str:
    impact = abs(delta) * unit_price
    if impact > 500:  return "HIGH"
    if impact > 100:  return "MEDIUM"
    return "LOW"


def detect_ghosts(transactions: list[TransactionObject]) -> list[GhostFlag]:
    flags: list[GhostFlag] = []

    for txn in transactions:
        inv  = txn.invoice_line
        po   = txn.po_line
        pod  = txn.pod_line

        # ── PHANTOM LINE ──────────────────────────────────────────────────
        # Completely unmatched on both PO and POD → hardest ghost
        if po is None and pod is None:
            flags.append(GhostFlag(
                ghost_type=GhostType.PHANTOM_LINE,
                severity="HIGH",
                invoice_id=inv.invoice_id,
                sku=inv.sku,
                description=inv.description,
                invoiced_value=inv.billed_unit_price,
                expected_value="N/A – no PO or POD exists",
                delta="100% phantom",
                financial_impact=round(inv.quantity * inv.billed_unit_price, 2),
                evidence_refs=[inv.src_sku, inv.src_billed_unit_price, inv.src_quantity],
                narrative=(
                    f"SKU '{inv.sku}' ({inv.description}) appears on invoice "
                    f"{inv.invoice_id} but has NO matching Purchase Order and "
                    f"NO Proof of Delivery. Full billed amount "
                    f"${inv.quantity * inv.billed_unit_price:,.2f} is unsubstantiated."
                ),
                transaction=txn
            ))
            continue   # no further checks possible

        # Partially phantom: no PO
        if po is None:
            flags.append(GhostFlag(
                ghost_type=GhostType.PHANTOM_LINE,
                severity="HIGH",
                invoice_id=inv.invoice_id,
                sku=inv.sku,
                description=inv.description,
                invoiced_value=inv.billed_unit_price,
                expected_value="N/A – no PO exists",
                delta="no authorisation",
                financial_impact=round(inv.quantity * inv.billed_unit_price, 2),
                evidence_refs=[inv.src_sku, inv.src_billed_unit_price],
                narrative=(
                    f"SKU '{inv.sku}' billed on invoice {inv.invoice_id} "
                    f"has NO corresponding Purchase Order. Goods may have been "
                    f"delivered but were never formally authorised."
                ),
                transaction=txn
            ))

        # Partially phantom: no POD
        if pod is None:
            flags.append(GhostFlag(
                ghost_type=GhostType.PHANTOM_LINE,
                severity="MEDIUM",
                invoice_id=inv.invoice_id,
                sku=inv.sku,
                description=inv.description,
                invoiced_value=inv.billed_unit_price,
                expected_value="N/A – no POD exists",
                delta="no physical receipt",
                financial_impact=round(inv.quantity * inv.billed_unit_price, 2),
                evidence_refs=[inv.src_sku, inv.src_quantity],
                narrative=(
                    f"SKU '{inv.sku}' billed on invoice {inv.invoice_id} "
                    f"has NO Proof of Delivery. Vendor charged for goods "
                    f"that cannot be confirmed as received."
                ),
                transaction=txn
            ))

        # ── PRICE VARIANCE ────────────────────────────────────────────────
        if po is not None:
            pct = _pct_diff(inv.billed_unit_price, po.agreed_unit_price)
            if pct > PRICE_TOLERANCE_PCT:
                delta_per_unit = inv.billed_unit_price - po.agreed_unit_price
                impact = round(delta_per_unit * inv.quantity, 2)
                flags.append(GhostFlag(
                    ghost_type=GhostType.PRICE_VARIANCE,
                    severity=_severity_price(pct),
                    invoice_id=inv.invoice_id,
                    sku=inv.sku,
                    description=inv.description,
                    invoiced_value=inv.billed_unit_price,
                    expected_value=po.agreed_unit_price,
                    delta=round(delta_per_unit, 4),
                    financial_impact=impact,
                    evidence_refs=[
                        inv.src_billed_unit_price,
                        po.src_agreed_unit_price,
                    ],
                    narrative=(
                        f"SKU '{inv.sku}': invoiced at ${inv.billed_unit_price:.4f}/unit "
                        f"vs PO contracted price ${po.agreed_unit_price:.4f}/unit "
                        f"({pct:.1%} variance). Over {inv.quantity} units, "
                        f"over-billing = ${impact:+,.2f}."
                    ),
                    transaction=txn
                ))

        # ── QTY MISMATCH ──────────────────────────────────────────────────
        if pod is not None:
            qty_delta = inv.quantity - pod.qty_received_at_dock
            if abs(qty_delta) > QTY_TOLERANCE:
                impact = round(qty_delta * inv.billed_unit_price, 2)
                flags.append(GhostFlag(
                    ghost_type=GhostType.QTY_MISMATCH,
                    severity=_severity_qty(qty_delta, inv.billed_unit_price),
                    invoice_id=inv.invoice_id,
                    sku=inv.sku,
                    description=inv.description,
                    invoiced_value=inv.quantity,
                    expected_value=pod.qty_received_at_dock,
                    delta=qty_delta,
                    financial_impact=impact,
                    evidence_refs=[
                        inv.src_quantity,
                        pod.src_qty_received,
                    ],
                    narrative=(
                        f"SKU '{inv.sku}': invoiced for {inv.quantity} units "
                        f"but only {pod.qty_received_at_dock} units logged at dock "
                        f"(waybill {pod.waybill_ref}). "
                        f"Delta of {qty_delta:+} units @ ${inv.billed_unit_price} = "
                        f"${impact:+,.2f} exposure."
                        + (f" Condition flag: {pod.condition}." if "DAMAGED" in pod.condition else "")
                    ),
                    transaction=txn
                ))

    return flags
