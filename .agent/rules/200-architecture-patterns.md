# System Architecture & Memory Management

## 1. Knowledge Base Integration
- Every significant architectural decision must be recorded in a `.md` file within the `/docs/decisions/` folder.
- Follow the "Protocol Zero" Twin-Graph pattern: Distinguish between "Shared Knowledge" (libraries/docs) and "Private Knowledge" (project-specific logic).
- When a task is 80% complete, perform a "Context Consolidation" turn to summarize the session state and update the local knowledge base.

## 2. Production-Ready Scaling
- Modularize code: Favor atomic skills in `.agent/skills/` over monolithic scripts.
- Version Control: For all major changes using "Deep Research" or "Canvas" modes, increment the internal version in the file header and provide a change summary.
- Verification: Every Implementation Plan must include a "Verification Plan" section specifying how the agent will use the Browser tool or Terminal to prove the task is complete.
