# Global Rule: Always Use agents.md

**Severity**: CRITICAL
**Scope**: Global

## Directive
All AI Agents operating within this workspace **MUST** read and adhere to the `agents.md` protocol located at `.agent/agents.md`, `--agents/agents.md`, or the repository root.

## Requirements
1.  **Context Loading**: Before beginning any task, verify the project structure and tech stack defined in `agents.md`.
2.  **Persona Alignment**: Adopt the appropriate persona (e.g., "Python Modern Architect", "Neo4j Deep Architect") as defined in the protocol.
3.  **Constraint Adherence**: Strictly follow the "Boundaries & Safeguards" listed in `agents.md`.

## Enforcement
Any plan or code generation that contradicts `agents.md` without explicit user override is considered a violation of the workspace contract.
