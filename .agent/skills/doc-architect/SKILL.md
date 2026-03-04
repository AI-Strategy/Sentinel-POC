---
name: doc-architect
description: Maintains READMEs, CHANGELOGs, and inline documentation to prevent technical debt.
---

# Doc Architect Protocol

## Trigger
Run this skill automatically after any `git-secure-commit` that touches >3 files, or manually via "Update docs".

## Capabilities
1.  **Module README Generation**:
    - **Input**: Scans a folder (e.g., `/src/deep`).
    - **Action**: Generates a `README.md` listing:
        - **Purpose**: One sentence summary.
        - **Exports**: Public functions/classes with signatures.
        - **Dependencies**: Internal and external imports.
2.  **Root README Synchronization**:
    - Updates the "Project Structure" tree in the root `README.md`.
    - Checks that all Environment Variables used in code are documented in `.env.example` (but values are blank).
3.  **Docstring Enforcer**:
    - Scans Python/Rust files for missing docstrings on public methods.
    - *Auto-Fix*: Generates a draft docstring based on the function signature and complexity.

## Usage
- User: "I just refactored the vector search. Update the docs."
- Agent: "Scanning `/src/deep/vector`... Updated `README.md` with new `search_hybrid()` signature and added `NEO4J_INDEX_DIMENSIONS` to `.env.example`."
