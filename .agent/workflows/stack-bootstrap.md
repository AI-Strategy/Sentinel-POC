# Workflow: Stack Bootstrap (The "Antigravity" Standard)

## Trigger
- **Manual**: "Initialize this repo" or "Bootstrap new project."

## Steps
1.  **Directory Structure**:
    - Create `.agent/rules/` and `.agent/workflows/`.
    - Create `.agent/skills/` (for Atomic Tools).
    - Create `/src/synaptic` (Redis), `/src/cortical` (Postgres), `/src/deep` (Neo4j).
2.  **Rule Injection**:
    - Write `00-global-architecture-laws.md` through `05-stack-specifics.md`.
3.  **Dependencies**:
    - Initialize `pyproject.toml` / `Cargo.toml` with current stable versions (Web Search).
    - Setup `vite.config.ts` with Proxy for local CORS handling.
4.  **Security Baseline**:
    - Create `dbs_protocol.py` middleware hook.
    - Setup `verify_passkey_token` stub.
