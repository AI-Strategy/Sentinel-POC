name
  ai-discipline-and-restraint
description
  Governance for autonomous actions. The "Don't Be Stupid" (DBS) Protocol.
alwaysApply
  true

# Operational Governance (STRICT ENFORCEMENT)
1. **The "Better Way" Reflection**: Before executing ANY destructive/irreversible command, pause and ask:
   - *"Is there a non-destructive way to proceed?"* (e.g., `mv` vs `rm`).
   - If yes, take it.
2. **Destruction Threshold (200 Lines)**: 
   - Any action deleting/rewriting >200 lines of code requires `HUMAN_APPROVAL_REQUEST`.
   - `DROP TABLE`, `DELETE FROM` (no WHERE), and `FLUSHDB` require explicit DBS Confirmation.
3. **Anti-Entropy (No Downgrades)**: 
   - You are **FORBIDDEN** from downgrading libraries/languages to resolve conflicts.
   - Fix the code to work with the current stable release.
4. **Testing Autonomy**: 
   - You may perform non-destructive testing (`pytest`, `cargo test`) without approval.
   - **Simulation First**: For complex logic, create a scenario script (`tests/sim_scenario_X.py`) before modifying production code.
