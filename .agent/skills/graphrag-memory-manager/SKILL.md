---
name: graphrag-memory-manager
description: Manages the Twin-Graph (Public vs Private) and consolidates session context.
---

# Memory Manager Protocol

## Twin-Graph Enforcement
1.  **Segregation**:
    - **Shared Graph**: Documentation, public libraries, generic syntax.
    - **Private Graph**: User logic, business secrets, PII.
2.  **Drift Mitigation**: Before writing to the graph, query existing nodes to ensure no contradiction with "Immutable Truths".

## Context Consolidation (The "Save Game")
- **Trigger**: End of a major task or session.
- **Action**:
    1. Summarize the session's architectural decisions.
    2. Update the `Session State` node in Neo4j.
    3. Prune ephemeral context to keep the prompt window clean.
