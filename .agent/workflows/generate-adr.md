---
name: generate-adr
description: Autonomously drafts Architecture Decision Records (ADR) to prevent context drift.
trigger: /adr
---
# WORKFLOW: Architecture Decision Record Generator

**Activation**: Triggered by `/adr <topic>`

## Execution Sequence:
1. **Analyze**: Review the recent git diffs and codebase changes related to the `<topic>`. Load the `@architecture-board` skill.
2. **Drafting**: Create a new markdown file in `docs/adrs/` named `YYYY-MM-DD-topic-name.md`.
3. **Format Enforcement**: The ADR MUST contain:
   * **Title & Date**: Clear identification.
   * **Status**: (Proposed / Accepted / Deprecated).
   * **Context**: What was the engineering problem? Empathize with the technical debt.
   * **Decision**: The mathematical or architectural choice made (e.g., "Why did we choose EdDSA over RS256?").
   * **Consequences**: The operational impact (Trade-offs in Cost, Performance, and Reliability).
4. **Commit**: Save the file natively and update the root `README.md` to link to it.
