# 🛠️ Sentinel v1.3 — Operational Guide & CLI Reference

**Status:** ✅ CURRENT  
**Version:** 1.3  
**Substrate:** Liquid Enterprise OS (Phase 1 & Phase 2)

---

## 1. Lifecycle Management (`Makefile`)
The Sentinel project uses a `Makefile` to orchestrate the complex interaction between the Python forensic engine and the Neo4j graph substrate.

| Command | Action |
| :--- | :--- |
| `make install` | Initializes the virtual environment and syncs dependencies (`pip install`). |
| `make up` | Launches the orchestrated Docker stack (FastAPI + Neo4j 2026.01.4). |
| `make down` | Gracefully stops the stack. |
| `make run-batch` | Executes the full reconciliation pipeline across all dirty datasets. |
| `make propagate-demo` | **[Phase 2]** Demonstrates a live round-trip price update in the graph. |
| `make e2e` | Runs the automated Ingest -> Grade -> Teardown verification loop. |
| `make clean` | Purges all temporary files, reports, caches, and Docker volumes. |

---

## 2. Manual Execution (PowerShell)
If `make` is not installed on the host system, use the following direct commands from the project root:

### **Pipeline Execution**
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python sentinel\main.py --batch-dir data/sentenil_dirty_datasets --reports output/reports
```

### **Automated Grading**
```powershell
.\venv\Scripts\python tests/grader.py --datasets data/sentenil_dirty_datasets --reports output/reports --out output/
```

### **Round-Trip Update Demo**
```powershell
curl -X POST http://localhost:8000/graph/update-po `
  -H "Content-Type: application/json" `
  -d '{"po_id": "PO-2024-001", "item_reference": "APX-BOLT-M12", "new_price": 0.75}'
```

---

## 3. Directory Structure (Forensic Context)
- `data/sentenil_dirty_datasets/`: Root for all forensic source files.
- `output/reports/`: Target for exact-match reconciliation reports (`*.reconciliation_report.json`).
- `sentinel/core/`: The "Liquid Substrate" – Ingestion, Matching, and Detection logic.
- `docs/`: Central repository for architectural and operational compliance reports.

---
_Sentinel Phase 2 — Liquid Enterprise OS Operational Plane v1.3_
