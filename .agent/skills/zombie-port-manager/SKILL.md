---
name: zombie-port-manager
description: Frees up a blocked port by killing the process holding it.
---

# Zombie Port Manager

## Goal
Ensure port discipline by killing "zombie" processes instead of opening new ports.

## Instructions
1.  **Identify**: Find the PID occupying the port.
    - *Command*: `lsof -t -i:3000` (or target port).
2.  **Verify**: Is this a critical system process? (Unlikely for >1024).
3.  **Kill**:
    - *Command*: `kill -9 [PID]`
4.  **Report**: "Port 3000 was blocked by PID 12345 (python). I have killed it. Port 3000 is now free."

## Python Tool (`scripts/kill_port.py`)
```python
import subprocess
import sys

def kill_port(port):
    try:
        pid = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode().strip()
        if pid:
            subprocess.run(f"kill -9 {pid}", shell=True)
            print(f"Killed PID {pid} on port {port}")
    except:
        print(f"Port {port} is free.")

if __name__ == "__main__":
    kill_port(sys.argv[1])
