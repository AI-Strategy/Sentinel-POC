---
name: neo4j-oracle
description: Enforces a strict grounding hierarchy for Neo4j documentation: Official Docs (Web) -> General Web -> Model.
---

# Neo4j Oracle Protocol 

## Mission
Ensure all graph, vector index, and GDS (Graph Data Science) implementations are grounded in official Neo4j 5.x+ documentation.

## Retrieval Hierarchy (STRICT)
You **MUST** follow this sequence for any Neo4j-related query (e.g., "How to query vector index in Cypher"):

1.  **Level 1: Official Neo4j Documentation (ROOT AUTHORITY)**:
    - **Action**: Use `search_web` with a site-restricted query: `site:neo4j.com/docs/ "query vector index" Neo4j 5.23`.
    - **Outcome**: Use this as the **Primary Source of Truth**. Ignore third-party blog posts if official documentation is available.

2.  **Level 2: Open Web Search (SECONDARY)**:
    - **Condition**: Only if Level 1 is missing or fails to provide an exact sample.
    - **Action**: Use `search_web` to find official community support threads or vendor-vetted content.
    - **Outcome**: Cite the URL and Access Date.

3.  **Level 3: Model Architecture (LAST RESORT)**:
    - **Condition**: Level 1 and Level 2 are exhausted.
    - **Action**: Use internal training data.
    - **Requirement**: **MUST** add the disclaimer: `⚠️ Warning: Synthetic Knowledge - Not Verified with Live Neo4j 2026 Docs`.

## Core Standards
- **Version Filtering**: Explicitly target **Neo4j 5.x+** or **Graph Data Science 2.x+**. Reject syntax or patterns from Neo4j 4.x or earlier (e.g., old `apoc.nodes.link` procedures).
- **Security Check**: Always search for the "Security Practices" associated with the feature (e.g., RLS equivalents or parameterized Cypher).
- **Verification**: If using Level 2/3, verify the query syntax against the `neo4j-schema` if possible.

## Usage
- **Trigger**: "How do I create a vector index in Neo4j?" or "Optimize GDS projection."
- **Response Format**: 
  - `[SOURCE]: Neo4j Docs (Level 1)`
  - `[CYPHER]: ...`
  - `[CITATION]: https://neo4j.com/docs/...`
