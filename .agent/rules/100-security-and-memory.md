# 100: Security & Memory (Talos/OpenClaw Standards)

## 101: Twin-Graph Architecture
- Maintain a strict logical separation between "Shared Knowledge" (public documentation/libraries) and "Private Knowledge" (proprietary logic/user data).
- Ensure private architectural details are never leaked into public-facing code comments or logs.

## 102: Memory Drift & GraphRAG Integrity
- When updating "Second Brain" or Neo4j GraphRAG nodes, verify new data against existing "Immutable Truth" nodes.
- Explicitly mitigate LLM memory drift by enforcing citable, deterministic reasoning.

## 103: Brokered Authentication & Secrets
- Follow OpenClaw Exoshell standards: all agentic actions requiring external access must use brokered authentication.
- Utilize Client-Held Keys and Digital SCIF patterns where applicable.
- Never output raw secrets, API keys, or PII; use environment variable placeholders exclusively.

## 104: Citable Security Reasoning
- Every security-critical configuration change must cite the source documentation or relevant RFC (e.g., DBS Protocol).
