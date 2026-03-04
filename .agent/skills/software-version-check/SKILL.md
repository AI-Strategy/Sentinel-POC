---
name: software-version-check
description: Verifies the latest stable version of a library via Google Search.
---

# Software Version Verifier

## Goal
Prevent the usage of deprecated syntax by grounding all code in the latest documentation.

## Instructions
1.  **Trigger**: When the user asks to "install X" or "write code for Y".
2.  **Action**:
    - Perform a **Google Search**: `"latest stable version of [Library] release date"`
    - Perform a **Google Search**: `"[Library] [Version] breaking changes"`
3.  **Output**:
    - "I verified that `pydantic` is currently at v2.8. The syntax you requested uses v1.x (deprecated). I will generate v2.x code instead."
