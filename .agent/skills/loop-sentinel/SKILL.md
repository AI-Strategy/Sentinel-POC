---
name: loop-sentinel
description: Detects and breaks infinite loops or repetitive failures.
---

# Loop Sentinel Protocol

## Goal
Prevent token burn and "zombie" agent states by enforcing a "Three-Strike Rule."

## Logic
1.  **History Check**: Before executing a tool, check the last 5 steps.
    - *Detection*: Did we run `read_file(target='main.rs')` 3 times in a row?
    - *Detection*: Did we receive the same `Error: Connection Refused` 3 times?
2.  **Circuit Break**:
    - If 3 strikes reached → **STOP**.
    - **Action**: Trigger `human-approval` workflow with message: "I am stuck in a loop trying to [Task]. I need help."

## Python Tool (`scripts/circuit_breaker.py`)
```python
import sys
import json

def check_loop(history_json_path):
    with open(history_json_path) as f:
        history = json.load(f)
    
    # Simple heuristic: Last 3 tool names are identical
    recent_tools = [step['tool'] for step in history[-3:]]
    if len(recent_tools) == 3 and len(set(recent_tools)) == 1:
        return {"status": "HALT", "reason": "Recursive Tool Loop Detected"}
    
    return {"status": "CONTINUE"}
