---
name: pii-redaction-guard
description: Scans and redacts PII/PHI from text before logging or external transmission.
---

# PII Redaction Protocol

## Goal
Prevent accidental leakage of Client PII in logs, error messages, or public graph nodes.

## Capabilities
1.  **Pattern Scrubbing**:
    - **Strict**: SSNs, Credit Card Numbers, API Keys (sk-...).
    - **Contextual**: Email addresses and Phone numbers (unless explicitly whitelisted).
2.  **Replacement Strategy**:
    - Replace with hash or token: `john@doe.com` -> `[EMAIL_REDACTED_A1B2]`.
    - Maintain referential integrity (same PII = same token) within a session for debugging.
3.  **Legal Hold**:
    - If a file is tagged `privileged_work_product`, this guard is **bypassed** only for internal storage in the "Private Graph."

## Usage
- **Automatic**: Hook into `audit-logger`.
- **Manual**: "Scrub this error trace before I paste it into the issue tracker."
