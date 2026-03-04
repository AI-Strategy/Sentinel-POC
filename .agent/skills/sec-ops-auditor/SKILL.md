---
name: sec-ops-auditor
description: Scans code and configuration for OWASP Top 10 and cloud misconfigurations.
---

# Security Auditor Protocol

## Audit Targets
1.  **Injection**: Check all SQL/Cypher queries for string concatenation. (Must use parameters).
2.  **Secrets**: Scan for entropy in code files (API keys, passwords).
3.  **Dependencies**: Check `Cargo.lock` / `requirements.txt` against known CVE databases (via Web Search).
4.  **Auth**: Verify every API endpoint has a `verify_passkey_token` dependency.

## Reporting
- Generate a report in `.audit/security_scan_[date].md`.
- Flag any "High" severity findings as blocking for deployment.
