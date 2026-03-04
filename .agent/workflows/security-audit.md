---
name: security-audit
description: Autonomous DevSecOps pipeline using Bandit and Semgrep.
trigger: /audit
---
# WORKFLOW: Red Team Audit

**Activation**: Triggered by `/audit`
1. **Equip**: Load the `@appsec-auditor` skill.
2. **Execution**: Run `bandit -r src/` and execute a `semgrep ci` pass in the terminal.
3. **Remediation**: If vulnerabilities are found, switch to Loki Mode to autonomously refactor the insecure code.
4. **Deliverable**: Generate a "Security Compliance Report" Artifact summarizing the patched vulnerabilities.
