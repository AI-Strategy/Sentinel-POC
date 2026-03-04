# 📚 Sentinel Documentation Repository

Welcome to the Sentinel "Liquid Enterprise OS" documentation vault. This directory contains the technical specifications, compliance reports, and architectural blueprints for the Phase 1 POC.

## 📑 Core Documentation Index

| Document | Description | Version | Status |
| :--- | :--- | :--- | :--- |
| [**System Architecture v2.0**](./sentinel_architecture_v2_0.md) | Definitive technical blueprint for the Liquid OS & Dashboard. | 2.0 | 💎 Current |
| [**Compliance Verification**](./phase1_compliance_verification_v1_3.md) | Official Phase 1 readiness and grading compliance. | 1.3 | ✅ Ready |
| [**Architecture & Execution**](./architecture_execution_protocol.md) | Technical blueprint for the "Walking Skeleton" pipeline. | 1.0 | 📄 Active |
| [**NLQ Evaluation Suite**](./nlq_evaluation_suite_v1_0.md) | Test cases and evaluation results for Natural Language Queries. | 1.0 | 🧪 Verified |
| [**Security Audit**](./security_audit_v0.3.md) | DevSecOps and vulnerability assessment report. | 0.3 | 🔒 Secure |

## 🏗️ v2.0 High-Fidelity Highlights
The latest **v1.1 Forensic Substrate** introduces:
- **Exact Line Extraction**: Every anomaly is linked to a physical `.sourceline` via `lxml`.
- **Gemini 1.5 Flash Layer**: Multi-layer entity resolution (Exact → Fuzzy → LLM).
- **High-Velocity Graph**: Bulk ingestion using Neo4j `UNWIND` patterns for sub-5s performance.

---
_Documentation maintained by the Sentinel Core Intelligence Team._
