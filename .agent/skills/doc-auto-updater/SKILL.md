---
name: doc-auto-updater
description: Automatically updates CHANGELOG.md and README.md based on git history.
---

# Doc Auto-Updater

## Goal
Ensure documentation never drifts from code reality.

## Trigger
Run this skill before `git-secure-commit` on a `feat` or `fix`.

## Protocol
1.  **Read Diff**: Analyze the staged changes.
2.  **Generate Entry**: Create a changelog entry in "Keep a Changelog" format.
3.  **Update README**:
    - If a new environment variable was added → Add to `README.md` Configuration section.
    - If a new script was added → Add to "Usage" section.
