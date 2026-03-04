# 🕵️ Sentinel — Ghost Invoice Traceability Report
**Generated:** 2026-03-04 22:19 UTC

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Invoice Lines Processed | 2 |
| Anomalies Detected | 1 |
| **Total Financial Exposure** | **$50.00** |

---

## Detailed Flag Evidence

### 1. 🔴 `PHANTOM_LINE` — SKU-CHILD-01
**Severity:** HIGH  |  **Invoice:** `INV-SCAF-01`  |  **Financial Impact:** `$50.00`

> SKU 'SKU-CHILD-01' (Child Component) appears on invoice INV-SCAF-01 but has NO matching Purchase Order and NO Proof of Delivery. Full billed amount $50.00 is unsubstantiated.
