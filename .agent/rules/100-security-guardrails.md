# Security & Compliance Guardrails

## 1. Terminal & Command Safety
- Never execute destructive commands (e.g., `rm -rf /`, `DROP TABLE`) without explicit, multi-turn user confirmation.
- Use a "Deny List" for high-risk binaries and shell built-ins.
- Ensure all automated scripts are treated as "black boxes"—execute with `--help` or `--version` first to verify interface before usage.

## 2. LLM Security (Talos/Protocol Zero Standards)
- Mitigate "Memory Drift": When updating long-term memory or GraphRAG nodes, verify the new data does not contradict existing "Immutable Truth" nodes.
- Citability: Every reasoning step that leads to a security configuration change must cite the source documentation verified via search.
- PII/Sensitive Data: Never output raw secrets, API keys, or PII into logs or artifacts. Use environment variable placeholders exclusively.
