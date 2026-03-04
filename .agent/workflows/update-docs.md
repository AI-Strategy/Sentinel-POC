---
name: Update Vault Documentation
description: Transpiles Neo4j and Postgres schemas into scannable Category READMEs.
---

# Mission
Keep the human and AI team synchronized by ensuring documentation matches the actual database state.

# Execution Steps
1. **Schema Extraction**:
   - Execute `neo4j-schema` to extract the current Graph model (labels, properties, and vector indexes).
   - Execute `pg_dump --schema-only` to capture the latest Postgres RLS policies.
2. **Web-First Syntax Check**: Perform a Google Search for "Neo4j 2026.1 best practices for GraphRAG documentation" to ensure we use the correct terminology.
3. **Markdown Transpilation**:
   - Update `src/deep_memory/README.md` with the new Graph schema and Cypher query templates.
   - Update `src/cortical_layer/README.md` with the latest RLS policy definitions.
4. **Consistency Audit**: Verify that the `agents.md` manifest still aligns with the updated database architecture. If not, propose an update to the Coordinator.

# Constraints
- Never truncate existing documentation; append changes to the "Version Control" section of the README.
- Include mermaid.js diagrams for all new graph relationship updates.
