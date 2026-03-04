---
name: solve-issue
description: Autonomous workflow to fetch, plan, and execute a fix for a GitHub issue.
trigger: /solve
---
# WORKFLOW: Autonomous Issue Resolution

**Activation**: Triggered by `/solve <issue-number>` (or `/solve backlog` for the highest priority).

## Execution Sequence (Loki Mode):
1. **Fetch**: Load the `@github-manager` skill. Use the `gh` CLI to read the issue.
2. **Plan**: Generate an **Implementation Plan Artifact**. Determine which domain experts (`@postgres-expert`, `@redis-expert`, `@oauth-expert`) are required. **Wait for Commander's Sign-off.**
3. **Equip & Execute**: Load the required skills into active memory. Write the code asynchronously across the `/src/` directories.
4. **Verify**: Trigger the `/test` workflow internally. DO NOT proceed until `pytest` coverage is green.
5. **Deploy**: Push the branch and submit the Pull Request for human review.
