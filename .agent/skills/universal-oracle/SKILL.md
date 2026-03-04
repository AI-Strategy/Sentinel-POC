---
name: universal-oracle
description: Enforces grounding roots for Rust, Postgres, Redis, and Polars documentation.
---

# Universal Oracle Protocol (v1.0)

## Mission
To eliminate "hallucinations" in the core stack by rooting all technical synthesis in official vendor documentation.

## Authority Roots (LEVEL 1)
When researching these technologies, you **MUST** use `search_web` with the following site restrictions to satisfy Level 1 of **LAW-05**:

| Technology | Authority Root (site:) |
| :--- | :--- |
| **Rust** | `doc.rust-lang.org/stable/` |
| **Postgres** | `postgresql.org/docs/` |
| **Redis** | `redis.io/docs/latest/` |
| **Polars** | `docs.rs/polars/latest/` |

## Retrieval Hierarchy (STRICT)
1.  **Level 1: Official Documentation**: 
    - Perform a `site:` restricted search on the relevant root above.
    - If found: Use as Absolute Truth. Ignore all tutorials/blogs.
2.  **Level 2: Web Corroboration**:
    - Only if Level 1 is missing specific edge cases.
    - Search GitHub issues or official release notes.
3.  **Level 3: Model Synthesis**:
    - **MUST** include: `⚠️ Warning: Synthetic Knowledge - Not Verified with Live Docs`.

## Protocol
- **Version Locking**: Always append the target version (e.g., `Postgres 18`, `Polars 0.40`).
- **Formatting**: Cite the specific URL from the authority root in the response.

## Usage
- **Trigger**: "What is the syntax for X in Polars?" or "How to configure RLS in Postgres?"
- **Response Prefix**: `[SOURCE]: Universal Oracle ([VENDOR] Docs)`
