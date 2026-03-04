# 🧶 Sentinel v1.2 — Hierarchical Data Ingestion

**Status:** ✅ IMPLEMENTED  
**Version:** 1.2  
**Capability:** Recursive Item Hierarchies (Bill of Materials)

---

## 1. Objective
Enable the Sentinel "Liquid OS" to handle complex item relationships beyond flat lists. This v1.2 update introduces support for **Parent-Child SKU mappings**, allowing the forensic engine to identify leakage within bundled products, assemblies, and service packages.

## 2. Ingestor Enhancements ([`ingest.py`](file:///d:/Projects/Sentinel/repo/Sentinel-POC/sentinel/core/ingest.py))
- **Dataclass Extension:** `InvoiceLineItem` now includes an optional `parent_sku: str`.
- **Recursive Extraction:** The JSON loader now proactively captures hierarchical metadata from nested `line_items`.
- **Robustness:** Integrated `lxml` XPath for the Proof of Delivery (POD) engine to ensure exact line-number provenance for sub-components.

## 3. Graph Substrate ([`graph.py`](file:///d:/Projects/Sentinel/repo/Sentinel-POC/sentinel/core/graph.py))
- **Topological Mapping:** The Graph Engine now creates an **`IS_CHILD_OF`** relationship between `InvoiceLine` nodes.
- **Forensic Evidence:** Child items retain their own physical line-number pointers while being logically linked to their parent assemblies.

## 4. NLQ Intelligence ([`nlq.py`](file:///d:/Projects/Sentinel/repo/Sentinel-POC/sentinel/core/nlq.py))
The Natural Language Query engine has been grounded in the new v1.2 schema. Auditors can now ask complex topological questions:
> *"Show all children of parent SKU 'BUNDLE-01' that have a price variance > 5%."*

---
_Sentinel Phase 2 — Topological Intelligence & Forensic Graphs_
