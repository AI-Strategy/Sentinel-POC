# 200: Operational Scaling (Antigravity Engine)

## 201: Modular Skills (Production Ready)
- Favor atomic, reusable tools in `.agent/skills/` over monolithic scripts.
- Every skill must include robust error handling, logging, and be ready for high-concurrency environments.

## 202: Context Consolidation
- At the conclusion of a significant task, perform a "Context Consolidation" turn.
- Summarize the session state and update the project’s local knowledge base to ensure high-fidelity context for future sessions.

## 203: DBS (Don't Be Stupid) Protocol
- High-risk actions (deployments, mass deletions, financial API calls) require a multi-step verification of intent and potential impact.
- The agent must pause and request explicit approval for any action identified as high-risk under the DBS Protocol.

## 204: Autonomy for Efficiency
- Design all systems to be self-healing and highly automated.
- Prioritize architectural decisions that minimize human maintenance time, supporting a goal of high-efficiency operational freedom.
