# Neo4j Environment Manager Skill

## Goal
Maintain the "Deep Memory" layer and verify Authority Scoring within the Neo4j 2026.1 Enterprise environment.

## Context
The Deep Memory layer uses native vector indexing (HNSW) and Seniority Weighting math to ground the system's reasoning. This skill empowers an agent to autonomously manage this infrastructure.

## Operational Instructions

### 1. Health & Integrity Checks
- **Scan for Incompleteness**: Identify `[:ESTABLISHED]` edges that are missing the mandatory `rank_weight` property.
- **Authority Review**: Verify that `Source` nodes correspond to valid `user_id` entries with seniority scores (2-10).
- **Orphan Detection**: Identify Knowledge nodes with no incoming `[:ESTABLISHED]` or `[:SUPERSEDED_BY]` relationships.

### 2. Vector Index Optimization
- **Cypher 25 Integration**: Utilize `CREATE VECTOR INDEX ... WITH [...]` to co-locate metadata (`tenant_id`, `clearance_level`) for **In-Index Filtering**.
- **Benchmark Retrieval**: Periodically execute `SEARCH` (Native 2026 keyword) instead of legacy `db.index.vector.queryNodes` to verify hardware-accelerated traversal.
- **Attribute Matching**: Ensure all index configurations match the baseline (Metric: `cosine`, Dimensions: 1024, Type: `FLOAT32`).

### 3. Reporting & Handoff
- **Handoff Report**: Generate a summary artifact detailing the current node count, edge distribution, and index performance status.
- **Automation**: Trigger a Red Team audit of ReBAC traversal rules if any `clearance_level` mismatches are detected.

---
*Authorized for Deep Memory Sub-Agents*
