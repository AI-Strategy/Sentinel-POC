---
name: workspace-janitor
description: Cleans up temporary artifacts, zombie processes, and Docker debris.
---

# Workspace Janitor Protocol

## Triggers
- **Post-Workflow**: Run after `feature-dev-loop` completes.
- **Manual**: "Clean up the workspace."

## Capabilities
1.  **Process Hygiene**:
    - Identifies and kills "Zombie" processes (Extension of `zombie-port-manager`).
    - Kills orphaned `node` or `python` processes consuming >1GB RAM for >1 hour.
2.  **Docker Prune**:
    - Runs `docker system prune -f` if disk usage > 80%.
    - Removes stopped containers labeled `antigravity-test-worker`.
3.  **Temp File Sweep**:
    - Deletes `tmp/` artifacts older than 24 hours.
    - **Safety**: Never deletes files in `/src` or `/docs`.
