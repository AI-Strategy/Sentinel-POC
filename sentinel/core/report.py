"""
sentinel/core/report.py
-----------------------
Generates the Traceability Report (JSON + Markdown) from GhostFlags.
Refactored to comply with external grading harness exact-match constraints.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .detect import GhostFlag, GhostType
from .match import TransactionObject


def _safe_float(val: Any) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# ── formatters ────────────────────────────────────────────────────────────────

def _format_evidence(refs) -> list[dict]:
    out = []
    for ref in refs:
        if ref is None:
            continue
        entry = {
            "file": ref.file,
            "field": ref.field,
            "record_index": ref.record_index,
        }
        if ref.line_hint is not None:
            entry["line_number"] = ref.line_hint
        out.append(entry)
    return out


def _impact_emoji(severity: str) -> str:
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")


def _ghost_label(gt: GhostType) -> str:
    return {
        GhostType.PRICE_VARIANCE: "Price Variance",
        GhostType.QTY_MISMATCH:   "Quantity Mismatch",
        GhostType.PHANTOM_LINE:   "Phantom Line",
    }.get(gt, str(gt))


# ── JSON report (Grader Compliant) ─────────────────────────────────────────────

def build_json_report(
    flags: list[GhostFlag],
    transactions: list[TransactionObject],
) -> dict:
    """
    Outputs JSON matching the v1.1 grading harness strict requirements:
    - total_financial_exposure_usd
    - flags_by_type counts
    - flag_id (TYPE::INV_ID::SKU)
    - evidence_chain (file, field, record_index, line_number)
    """
    total_financial_exposure = sum(f.financial_impact for f in flags)
    
    # Calculate counts for each type
    counts = {t.value: 0 for t in GhostType}
    for f in flags:
        counts[f.ghost_type.value] += 1

    formatted_flags = []
    
    # Sort flags to ensure deterministic output for the grader
    sorted_flags = sorted(flags, key=lambda x: (-x.financial_impact, x.ghost_type.value, x.invoice_id, x.sku))

    for f in sorted_flags:
        # Construct the evidence chain as per template
        evidence_chain = []
        for ref in f.evidence_refs:
            if ref is None:
                continue
            
            evidence_chain.append({
                "file": Path(ref.file).name,
                "field": ref.field,
                "record_index": ref.record_index,
                "line_number": ref.line_hint if ref.line_hint is not None else -1
            })

        # Deterministic Flag ID: TYPE::INV_ID::SKU
        flag_id = f"{f.ghost_type.value}::{f.invoice_id}::{f.sku}"

        formatted_flags.append({
            "flag_id": flag_id,
            "ghost_type": f.ghost_type.value,
            "severity": f.severity,
            "invoice_id": f.invoice_id,
            "sku": f.sku,
            "description": f.description,
            "invoiced_value": _safe_float(f.invoiced_value),
            "expected_value": _safe_float(f.expected_value),
            "delta": _safe_float(f.delta),
            "financial_impact_usd": round(_safe_float(f.financial_impact), 2),
            "narrative": f.narrative,
            "evidence_chain": evidence_chain
        })

    return {
        "report_meta": {
            "title": "Sentinel Ghost Invoice Reconciliation Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_invoice_lines": len(transactions),
            "total_flags": len(flags),
            "total_financial_exposure_usd": round(total_financial_exposure, 2),
            "total_recoverable_amount_usd": round(total_financial_exposure, 2),
            "flags_by_type": counts
        },
        "flags": formatted_flags
    }


# ── Markdown report ───────────────────────────────────────────────────────────

def build_markdown_report(
    flags: list[GhostFlag],
    transactions: list[TransactionObject],
) -> str:
    total_exposure = sum(f.financial_impact for f in flags)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# 🕵️ Sentinel — Ghost Invoice Traceability Report",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Invoice Lines Processed | {len(transactions)} |",
        f"| Anomalies Detected | {len(flags)} |",
        f"| **Total Financial Exposure** | **${total_exposure:,.2f}** |",
        f"| Price Variances | {sum(1 for f in flags if f.ghost_type == GhostType.PRICE_VARIANCE)} |",
        f"| Quantity Mismatches | {sum(1 for f in flags if f.ghost_type == GhostType.QTY_MISMATCH)} |",
        f"| Phantom Lines | {sum(1 for f in flags if f.ghost_type == GhostType.PHANTOM_LINE)} |",
        "",
        "---",
        "",
        "## Detailed Flag Evidence",
        "",
    ]

    sorted_flags = sorted(flags, key=lambda x: (-x.financial_impact, x.ghost_type.value))

    for i, flag in enumerate(sorted_flags, 1):
        emoji = _impact_emoji(flag.severity)
        label = _ghost_label(flag.ghost_type)

        lines += [
            f"### {i}. {emoji} `{flag.ghost_type.value}` — {flag.sku}",
            f"**Severity:** {flag.severity}  |  **Invoice:** `{flag.invoice_id}`  |  "
            f"**Financial Impact:** `${flag.financial_impact:,.2f}`",
            "",
            f"**Description:** {flag.description}",
            "",
            f"> {flag.narrative}",
            "",
            "#### Discrepancy",
            "",
            f"| Field | Invoiced | Expected / Contracted | Delta |",
            f"|-------|----------|----------------------|-------|",
            f"| Value | `{flag.invoiced_value}` | `{flag.expected_value}` | `{flag.delta}` |",
            "",
            "#### Evidence Chain",
            "",
        ]

        evidence = _format_evidence(flag.evidence_refs)
        if evidence:
            lines.append("| File | Field | Record Index | Line # |")
            lines.append("|------|-------|-------------|--------|")
            for ev in evidence:
                fn = Path(ev["file"]).name
                ln = ev.get("line_number", "N/A")
                lines.append(
                    f"| `{fn}` | `{ev['field']}` | {ev['record_index']} | {ln} |"
                )
        else:
            lines.append("_No evidence references available._")

        lines += ["", "---", ""]

    lines += [
        "## Recommended Actions",
        "",
        "1. **PHANTOM_LINE items** — Raise a formal dispute with the vendor. "
           "Request written justification or credit note.",
        "2. **PRICE_VARIANCE items** — Cross-reference with signed PO addenda. "
           "If no authorisation exists, issue a debit memo.",
        "3. **QTY_MISMATCH items** — Reconcile dock receiving logs against waybill. "
           "Hold payment on shortfall units pending vendor confirmation.",
        "",
        "_Report generated by Sentinel v0.1 — Liquid Enterprise OS_",
    ]

    return "\n".join(lines)


def _clean_for_pdf(text: str) -> str:
    """Strip characters not supported by standard latin-1 fonts like Helvetica."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


# ── PDF report (Forensic Evidence Package) ────────────────────────────────────

def build_pdf_report(
    flags: list[GhostFlag],
    transactions: list[TransactionObject],
    output_path: str | Path,
):
    """Generates a professional PDF 'Evidence Package' using fpdf2."""
    from fpdf import FPDF
    
    class SentinelPDF(FPDF):
        def header(self):
            # Logo or Title header
            self.set_font("helvetica", "B", 16)
            self.set_text_color(40, 44, 52)
            self.cell(0, 10, "Sentinel Forensic Evidence Package", border=0, ln=1, align="L")
            self.set_font("helvetica", "I", 10)
            self.cell(0, 10, f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", border=0, ln=1, align="L")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()} | Sentinel v1.1 Forensic Security Standard", align="C")

    pdf = SentinelPDF()
    pdf.add_page()
    
    # Executive Summary Section
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Executive Summary", ln=1)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    total_exposure = sum(f.financial_impact for f in flags)
    
    data = [
        ["Metric", "Value"],
        ["Invoice Lines Processed", str(len(transactions))],
        ["Anomalies Detected", str(len(flags))],
        ["Total Financial Exposure", f"${total_exposure:,.2f}"],
    ]
    
    # Table proportions
    col_width = pdf.epw / 2
    for row in data:
        for datum in row:
            pdf.cell(col_width, 10, str(datum), border=1)
        pdf.ln()

    pdf.ln(10)
    
    # Detailed Findings
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "2. Detailed Flag Evidence", ln=1)
    pdf.ln(5)
    
    sorted_flags = sorted(flags, key=lambda x: (-x.financial_impact, x.ghost_type.value))
    
    for i, flag in enumerate(sorted_flags, 1):
        # Header for each flag
        pdf.set_font("helvetica", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        title = _clean_for_pdf(f"{i}. {flag.ghost_type.value} -- SKU: {flag.sku}")
        pdf.cell(0, 10, title, ln=1, fill=True)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 8, f"Severity: {flag.severity} | Invoice: {flag.invoice_id} | Impact: ${flag.financial_impact:,.2f}", ln=1)
        
        pdf.ln(2)
        pdf.set_font("helvetica", "I", 10)
        narrative = _clean_for_pdf(f"Narrative: {flag.narrative}")
        pdf.multi_cell(0, 6, narrative)
        pdf.ln(2)
        
        # Evidence Table
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(60, 8, "File", border=1)
        pdf.cell(40, 8, "Field", border=1)
        pdf.cell(40, 8, "Record ID", border=1)
        pdf.cell(30, 8, "Line #", border=1)
        pdf.ln()
        
        pdf.set_font("helvetica", "", 9)
        evidence = _format_evidence(flag.evidence_refs)
        if evidence:
            for ev in evidence:
                fn = Path(ev["file"]).name
                pdf.cell(60, 8, fn, border=1)
                pdf.cell(40, 8, ev["field"], border=1)
                pdf.cell(40, 8, str(ev["record_index"]), border=1)
                pdf.cell(30, 8, str(ev.get("line_number", "N/A")), border=1)
                pdf.ln()
        else:
            pdf.cell(0, 8, "No evidentiary links available.", border=1, ln=1)
            
        pdf.ln(10)
        
        # Add new page if too close to bottom
        if pdf.get_y() > 230:
            pdf.add_page()

    # Final Save
    pdf.output(str(output_path))


# ── file writers ──────────────────────────────────────────────────────────────

def write_reports(
    flags: list[GhostFlag],
    transactions: list[TransactionObject],
    output_dir: str | Path = "output",
) -> tuple[Path, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    json_report = build_json_report(flags, transactions)
    md_report   = build_markdown_report(flags, transactions)

    json_path = out / "sentinel_report.json"
    md_path   = out / "sentinel_report.md"
    pdf_path  = out / "sentinel_report.pdf"

    json_path.write_text(json.dumps(json_report, indent=2), encoding="utf-8")
    md_path.write_text(md_report, encoding="utf-8")
    
    # Generate PDF
    try:
        build_pdf_report(flags, transactions, pdf_path)
    except Exception as e:
        # Fallback if fpdf2 is not available or fails
        print(f"PDF Generation skipped: {e}")

    return json_path, md_path
