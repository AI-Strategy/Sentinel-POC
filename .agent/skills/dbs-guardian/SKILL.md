#### **6. DBS Guardian (`dbs-guardian`)**
*Enforces: Rule 05-1 (Don't Be Stupid).*
*File:* `.agent/skills/dbs-guardian/SKILL.md`

```markdown
---
name: dbs-guardian
description: Analyzes high-risk actions and enforcing the "Better Way" reflection.
---

# DBS Guardian

## Goal
Prevent irreversible damage to the codebase or database.

## Trigger
Auto-runs when the agent plans to:
- Delete >200 lines of code.
- Run `DROP`, `DELETE`, `FLUSHDB`.
- Modify `infrastructure/` files.

## Protocol
1.  **Pause**: Stop execution.
2.  **Reflect**: "Is there a non-destructive way?"
    - *Example*: Use `mv` instead of `rm`. Use `soft_delete` column instead of `DELETE`.
3.  **Ask**: If no safe way exists, prompt the user:
    - "I need to perform a destructive action (Reason: X). Reply 'APPROVED' to proceed."
