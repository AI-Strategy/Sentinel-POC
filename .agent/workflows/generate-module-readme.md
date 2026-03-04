---
name: generate-module-readme
description: Agent_Lambda loop to enforce Directive 21 embedded documentation.
trigger: /readme
---
# WORKFLOW: Embedded Documentation Standards
**Activation**: Triggered by `/readme <directory_path>`
1. **Scan**: Analyze new functions, modules, or agents in the target directory.
2. **Embedded README Requirement**: EVERY major function or agent MUST have a dedicated `README.md` in its directory.
3. **Strict Template Enforcement**: The README MUST contain these exact headers:
   * `## Core Function` (What does this do?)
   * `## Purpose` (Why does this exist?)
   * `## Human-Understandable Examples` (Code blocks showing usage)
   * `## Dependencies` (What libraries are required)
   * `## Known Limitations` (What doesn't this do?)
4. **Verification**: Reject the task if a new module is missing this file.
