# 🔄 Sentinel v1.2 — Round-Trip Graph Updates

**Status:** ✅ IMPLEMENTED  
**Version:** 1.2.1  
**Milestone:** Phase 2 Milestone 3 — "The Feedback Loop"

---

## 1. Objective
Establish a bi-directional data flow where external corrections to procurement data (e.g., updating a Purchase Order price) are automatically propagated to the Neo4j forensic substrate. This ensures that the graph remains a "Living Ledger" and that stale or resolved anomalies are automatically purged.

## 2. API Implementation ([`main.py`](file:///d:/Projects/Sentinel/repo/Sentinel-POC/sentinel/main.py))
A new administrative endpoint has been added to the Sentinel Orchestrator to facilitate these updates:

- **Endpoint:** `POST /graph/update-po`
- **Security:** Requires `verify_api_key` dependency.
- **Action:** Synchronously updates `POLine` attributes and detaches related `GhostFlags`.

## 3. Propagation Logic
When a PO update is triggered, the system performs the following graph operations:
1.  **Node Mutation**: Locates the specific `POLine` by `po_id` and `item_reference` and applies the new `agreed_unit_price`.
2.  **Anomaly Invalidation**: Identifies all `InvoiceLine` nodes linked to the updated PO.
3.  **Cascade Deletion**: Locates all `GhostFlag` nodes targeting those lines and **DETACH DELETEs** them, clearing the audit trail for re-reconciliation.

## 4. Integration Context
This capability allows Procurement Officers to resolve "Price Variances" within their ERP/SCM systems and have those resolutions reflected in the Sentinel Audit Dashboard in real-time.

---
_Sentinel Phase 2 — Topological Intelligence & Dynamic Auditing_
