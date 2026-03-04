---
name: api-contract-guard
description: Detects "Widows" (unused endpoints) and "Orphans" (broken frontend calls) between React and Rust/Python.
---

# API Contract Guard Protocol

## Goal
Ensure 1:1 parity between Backend Routes and Frontend Clients.

## Protocol
1.  **Route Discovery (The Truth)**:
    - **Rust**: Scan `axum` routers for `route("/path", get(handler))`.
    - **Python**: Scan `FastAPI` decorators `@app.get("/path")`.
    - *Output*: List of `[METHOD] /path`.

2.  **Client Usage Scan**:
    - **React**: Scan for `fetch`, `axios`, or `useQuery` strings.
    - *Regex Fallback (Permitted)*: Use strict patterns to find url strings.

3.  **Discrepancy Analysis**:
    - **Orphan Detection (Critical)**: Frontend calls `/api/v1/user` -> Backend has no such route.
        - *Action*: FAIL build. Report "Frontend is calling a ghost."
    - **Widow Detection (Cleanup)**: Backend has `/api/v1/legacy` -> Frontend never calls it.
        - *Action*: WARN. "Endpoint appears unused. Verify before deprecation."
    - **Type Mismatch**:
        - Check if Frontend `interface User` matches Backend `struct User`.
        - Suggest running `bun run gen-api-types` (if configured).

## Usage
- **Trigger**: Run automatically on `pull_request` merging to `main`.
- **Manual**: "Check for broken API links."
