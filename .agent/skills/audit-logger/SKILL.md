---
name: audit-logger
description: Appends structured, immutable logs to the audit trail.
---

# Audit Logger Protocol

## Goal
Create a defensible chain of custody for all autonomous decisions.

## Protocol
1.  **Structure**: Logs must be JSON-L objects with:
    - `timestamp` (ISO 8601)
    - `actor` (Agent ID or User ID)
    - `action_type` (e.g., `EXECUTE_TOOL`, `DECISION_POINT`, `ERROR`)
    - `context_hash` (Hash of the input prompt for integrity)
    - `reasoning` (The "Why")
2.  **Storage**: Append to `.audit/events_<date>.jsonl`.
3.  **Privilege**: If `client_id` is present, tag as `PRIVILEGED`.

## Python Tool (`scripts/log_event.py`)
```python
import json
import datetime
import hashlib
from typing import Literal

def log_event(action: str, reasoning: str, status: Literal["SUCCESS", "FAILURE", "BLOCKED"], client_id: str = None):
    entry = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "action": action,
        "reasoning": reasoning,
        "status": status,
        "client_id": client_id,
        "integrity_hash": hashlib.sha256(reasoning.encode()).hexdigest()
    }
    
    filename = f".audit/events_{datetime.date.today()}.jsonl"
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return f"Event logged to {filename}"
