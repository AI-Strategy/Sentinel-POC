---
id: LAW-05
name: Information Grounding Hierarchy
enforcement: STRICT
---

# LAW-05: Information Grounding Hierarchy

## Directive
Antigravity agents **MUST** prioritize official, live, and version-locked documentation over all other sources of knowledge to prevent technical drift (2025-2026 standards).

## Hierarchy of Truth (MANDATORY)

1.  **PRIMARY: Official Vendor Authority Root**:
    - **Google/Product Stack**: You MUST first use the `google-developer-knowledge` MCP server.
    - **Neo4j/Graph**: You MUST use the `neo4j-oracle` (site:neo4j.com/docs/).
    - **Core Stack (Rust, Postgres, Redis, Polars)**: You MUST use the `universal-oracle` (Official Roots: doc.rust-lang.org, postgresql.org, redis.io, docs.rs/polars).
    - Treat content from these roots as **Absolute Truth**.

2.  **SECONDARY: Live Web Search (General)**:
    - If (and only if) the Primary Root has no record, you MUST use `search_web` for corroborating sources.
    - You MUST verify the "Last Updated" date to ensure it is within the 18-month window.

3.  **TERTIARY: Internal Model Training**:
    - You may ONLY rely on your internal training data if BOTH Level 1 and Level 2 are exhausted.
    - If Level 3 is used, you **MUST** prepend the warning: `⚠️ Warning: Synthetic Knowledge - Not Verified with Live Docs`.

## Protocol
Before citing code or standard patterns, the agent must internally check: 
"Have I checked the MCP? Have I checked the Live Web?"

Failure to follow this hierarchy for project-critical decisions (e.g., API migrations, Security patterns) is a violation of **Protocol Zero**.
