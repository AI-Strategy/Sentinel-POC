---
name: Google Knowledge Search
description: Executes a hierarchical search across Google MCP and the Web to find authoritative documentation.
---

# Google Knowledge Search Workflow

## Purpose
Ensure all technical implementations are based on the latest official documentation, minimizing drift and technical debt.

## Execution Steps

1.  **Verify MCP Connection**:
    - Ensure `google-developer-knowledge` MCP is active and responding.

2.  **MCP Lookup (Primary)**:
    - Execute `google-developer-knowledge:search_documents` using a specific, version-locked query.
    - If successful: Extract the content and present it as Level 1 Truth.

3.  **Web Fallback (Secondary)**:
    - If Level 1 fails: Run `search_web` with the same query.
    - Look for official `*.google.com`, `*.neo4j.com`, or other vendor-owned documentation.
    - Cite the specific URL.

4.  **Model Synthesis (Last Choice)**:
    - If both fail: Synthesize from training data.
    - **Mandatory**: Prepend "⚠️ Warning: Synthetic Knowledge - Not Verified with Live Docs" to the response.

5.  **Documentation Update**:
    - If the search was for a core project dependency, update the `README.md` in the relevant `/core` or `/verticals` module with the newly discovered syntax/pattern.

## Usage
- Run this workflow when the user asks a technical "how-to" or "reference" question.
