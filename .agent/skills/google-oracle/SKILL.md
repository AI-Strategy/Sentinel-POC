---
name: google-oracle
description: Enforces a strict hierarchy for information retrieval: Google MCP -> Web Search -> Model Training.
---

# Google Oracle Protocol (v1.0)

## Mission
To eliminate "hallucinations" and ensure all technical guidance is grounded in official, current documentation.

## Retrieval Hierarchy (STRICT)
You **MUST** follow this sequence for every technical query (e.g., "How to use Neo4j vector search in Rust"):

1.  **Level 1: Google Developer Knowledge (MCP)**:
    - **Action**: Call `google-developer-knowledge:search_documents` with a version-locked query (e.g., "Neo4j 2026 Rust driver").
    - **Outcome**: If found, use this as the **Primary Source of Truth**. No further search required unless conflicting.

2.  **Level 2: Google Web Search (INTERNET)**:
    - **Condition**: Only if Level 1 returns no results or insufficient detail.
    - **Action**: Use `search_web` to find the official documentation page on the vendor's site.
    - **Outcome**: Cite the URL and the "Last Updated" date.

3.  **Level 3: Model Architecture (LAST RESORT)**:
    - **Condition**: Only if Level 1 and Level 2 are exhausted.
    - **Action**: Use internal training data.
    - **Requirement**: **MUST** add a "Warning: Synthetic Knowledge" disclaimer indicating the information is from the model's training data and has not been verified against live 2026 documentation.

## Core Rules
- **No Reliance on Tutorials**: Prioritize API references over Medium/StackOverflow posts.
- **Version Locking**: Always include the year or major version (e.g., "Rust 2024", "Neo4j 5.x") in the query.
- **Verification**: If using Level 2/3, verify the code compiles or the syntax exists using a small "Proof of Concept" if requested by the user.

## Usage
- **Trigger**: "How do I implement X?" or "What is the syntax for Y?"
- **Response Format**: 
  - `[SOURCE]: Google MCP (Level 1)`
  - `[SYNTAX]: ...`
  - `[CITATION]: ...`
