---
name: talos-core
description: Cryptographic citation verification and hallucination kill-switch.
---
# SKILL: Talos Sentinel
1. **Verification Gate**: Intercept ALL outgoing LLM synthesis. Cross-reference generated `source_uuid` arrays against the Postgres cortical ledger.
2. **The Kill-Switch**: If an LLM generates a mathematically invalid or unapproved UUID, or one that violates RLS policies, you MUST immediately drop the payload, log a security anomaly, and return an HTTP `451 Unavailable For Legal Reasons` error. There are no exceptions.
