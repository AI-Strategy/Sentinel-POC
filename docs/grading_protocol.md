# 🏆 Sentinel Grading & Verification Protocol

To ensure the integrity of the "Ghost Invoice" reconciliation and achieve a 100% pass rate in Phase 1, the system includes an automated grading harness. This tool scores candidate reports against the ground-truth datasets for precision, recall, and evidence accuracy.

## 📋 Execution Command

Run the following command from the project root to perform a full audit of all generated reports:

```powershell
python tests/grader.py --datasets data/sentenil_dirty_datasets --reports output/reports --out output/
```

## 🔍 Parameters

| Argument | Purpose |
| :--- | :--- |
| `--datasets` | Path to the directory containing dirty datasets (JSON/CSV/XML) and their `ground_truth.json` keys. |
| `--reports` | Path to the candidate report directory containing `{dataset_name}.reconciliation_report.json` files. |
| `--out` | Target directory for the final `grade_summary.json` and `grade_summary.md` artifacts. |

## 📈 Scoring Metrics

The grading harness evaluates three primary dimensions:

1.  **F1 Score**: Harmonic mean of Precision and Recall. A target of **>0.9** is required for a `✅ PASS` status.
2.  **Financial Impact Variance**: Measures the delta between detected leakage values and ground truth. Must be within **$0.01 tolerance**.
3.  **Evidence Accuracy**: Validates that every flag is pinned to the correct source file and physical line number.

## 🛠️ Typical Workflow

1.  **Ingest & Process**: Run the batch orchestrator (`make run-batch`).
2.  **Verify**: Execute the grader command above.
3.  **Analyze**: Review `output/grade_summary.md` for a high-level pass/fail summary.

---
_Sentinel Phase 1 — Liquid Enterprise OS Submission v1.1_
