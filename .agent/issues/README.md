# Antigravity Issue & Documentation Tracker

This directory serves as the centralized location for documenting systemic network, architectural, and compilation issues encountered by developers and AI agents across this repository.

## Structure
- `/open` - For actively tracked issues and blockers.
- `/resolved` - For documented resolutions to past blockers.

## Protocol
When an AI agent encounters a persistent system error (e.g. 500 Route Error, fetch failure, database connection drop), the agent MUST:
1. Check `/issues/resolved` to see if a known fix exists for the current paradigm (e.g., node fetch overrides, database driver downgrades).
2. If the issue is unresolved/new, document it in `/issues/open` if execution is blocked.
3. Upon resolution, move or create the issue documentation in `/issues/resolved`.

### Issue Template
Use the following format when documenting an issue:
```markdown
# Issue: [Title]

## Date: [YYYY-MM-DD]
**Status:** [Open | Resolved]
**Component:** [Frontend | Backend | DB | Agent | etc.]
**Impact:** [Description of how this breaks the workspace]

### Context
[Detailed explanation of the error trace and environment]

### Root Cause
[Explanation of why this happens]

### Resolution (if resolved)
[Exact code or configuration changes required to fix it permanently]
```
