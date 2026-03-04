name
  incident-post-mortem
description
  Triggered when a task fails. Analyzes logs, identifies root cause, and logs to the Incident Graph.

steps
  1. **Log Collection**
     - Run `tail -n 50` on the application logs.
     - Capture the exact error trace.

  2. **Root Cause Analysis (RCA)**
     - Query: "Based on this stack trace and the recent changes to [File], what is the likely cause?"
     - Constraint: Do not guess. If unknown, state "Unknown."

  3. **Graph Update**
     - Add a `FAILURE` node to the GraphRAG connected to the `Code Module`.
     - *Reasoning*: "This module is fragile regarding [Condition]." (Helps future agents be careful).

  4. **Report**
     - Generate `.audit/incident_[id].md` with:
       - Error
       - Root Cause
       - Proposed Fix
