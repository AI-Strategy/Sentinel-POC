name
  sudo-override
description
  Emergency protocol to bypass DBS guardrails. USAGE IS AUDITED.

steps
  1.  **Declaration of Intent**
      - User MUST state: "I invoke Sudo Override for [Reason]."
      - *Constraint*: Reason cannot be empty.

  2.  **Risk Assessment (Agent)**
      - Agent explicitly lists the guardrails being disabled.
      - *Example*: "Disabling `dbs-operational-governance` Rule 2 (Destruction Threshold)."

  3.  **The "Break Glass" Log**
      - Log a `CRITICAL` event to `.audit/emergency_log.jsonl`.
      - Alert: "⚠️ SUDO OVERRIDE ACTIVE. SAFETY OFF."

  4.  **Execution**
      - Execute the destructive command (e.g., `DROP SCHEMA public CASCADE`).
      - *Post-Action*: Immediately re-enable guardrails.
