name
  daily-health-check
description
  Runs a comprehensive system health check (Dependencies, Graph Integrity, Security).

steps
  1. **Dependency Scan**
     - Run `cargo audit` (Rust) and `pip-audit` (Python).
     - Check for critical CVEs.
     - **Action**: If critical CVE found, generate a `security-fix` branch immediately.

  2. **Graph Integrity Check**
     - Query Neo4j: "Are there any disconnected nodes or nodes missing required properties?"
     - Query Redis: "Are there any keys missing TTLs?" (Ghost Mode check).

  3. **Documentation Sync**
     - Run `doc-architect` to ensure READMEs match the current code state.

  4. **Status Report**
     - Generate a summary in `.agent/daily_reports/YYYY-MM-DD.md`.
     - *Output*: "System Healthy. 2 minor dependency updates available. Graph integrity 100%."
