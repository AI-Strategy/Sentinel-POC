---
name: api-bridge-builder
description: Generates strict TypeScript clients from Backend OpenAPI/Swagger definitions.
---

# API Bridge Builder Protocol

## Goal
Eliminate "Widows & Orphans" by generating the Frontend Client SDK directly from the Backend source of truth.

## Triggers
- **Manual**: "Regenerate the API client."
- **Automatic**: Runs after `feature-dev-loop` when Backend files are modified.

## Capabilities
1.  **Schema Extraction**:
    - **Rust (Axum)**: Runs `cargo run --bin gen-spec` to output `openapi.json`.
    - **Python (FastAPI)**: Runs `python scripts/extract_openapi.py` to output `openapi.json`.
2.  **Client Generation**:
    - Uses `openapi-typescript-codegen` or `orval` to generate typed hooks.
    - *Command*: `npx openapi-typescript-codegen -i ./openapi.json -o ./src/client -c fetch`
3.  **Strict Typing Enforcement**:
    - **No `any`**: The generated client includes full TypeScript interfaces for all Request/Response bodies.
    - **Widow Check**: If the Backend removes an endpoint, the Frontend build will fail (Type Error) immediately.

## Verification
- **Orphan Check**: Scans `src/pages` for usages of methods that no longer exist in the generated client.
- **Report**: "Regenerated API Client. 3 endpoints updated. 0 breaking changes detected."
