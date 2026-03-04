name
  dbs-operational-governance
description
  The "Don't Be Stupid" Protocol. Safe-guards against irreversible actions and enforces self-correction.
alwaysApply
  true

# Operational Governance (STRICT ENFORCEMENT)
1. **The "Better Way" Reflection**: Before executing ANY destructive or irreversible command, you must explicitly pause and ask yourself: *"Is there a better, non-destructive way to proceed?"*
2. **Destruction Threshold (200 Lines)**:
   - Deleting or rewriting >200 lines of code in a single turn requires explicit `HUMAN_APPROVAL_REQUEST`.
   - `DROP TABLE`, `DELETE FROM` (without specific IDs), and `FLUSHDB` are strictly prohibited without a multi-turn confirmation sequence.
3. **No New Ports (Zombie Rule)**: You are forbidden from opening new ports (e.g., 3001, 8081) simply because the primary port is blocked. Kill the zombie process instead.
