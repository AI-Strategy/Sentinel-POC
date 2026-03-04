---
name: delegate-to-jules
description: Handoff heavy, asynchronous tasks to Google Jules in the cloud via GitHub Issues.
trigger: /jules
---
# WORKFLOW: Jules Cloud Handoff

**Activation**: Triggered by `/jules <task description>`

## Execution Sequence:
1. **Scope the Work**: Assess the task. If it involves massive refactoring across dozens of files, do not execute it locally.
2. **Execute Handoff**: Use the GitHub MCP server or the `gh` CLI to create a new GitHub Issue containing the exact `<task description>`.
3. **Trigger Jules**: Add the label `jules-execute` to the GitHub Issue. This acts as the webhook to wake up the Jules cloud agent on the repository.
4. **Monitor**: Output the GitHub Issue URL to the Commander and advise them to wait for Jules to submit a Pull Request.
