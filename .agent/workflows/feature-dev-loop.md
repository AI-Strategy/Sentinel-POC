# Workflow: Feature Development Loop (Python/Rust + React)

## Trigger
- **Manual**: User invokes "Build feature X" or "Refactor module Y".
- **Context**: `.agent/rules/05-stack-specifics.md` is active.

## Phase 1: Context & Simulation (Non-Destructive)
1.  **Stack Verification**:
    - Confirm the request aligns with the "No Downgrade" rule.
    - If logic is complex (e.g., GraphRAG weights, Financial Math), **STOP** and generate a simulation script (`tests/sim_scenario_X.py`) first.
    - *Goal:* Verify logic *before* touching production code.
2.  **Dependency Check**:
    - Are we adding a library? -> **Search Web** for the latest version (e.g., `cargo search`, `pip index`).
    - *Constraint:* Do not use regex for parsing; use `Gemini Flash` if needed.

## Phase 2: Implementation (Atomic & Async)
3.  **Backend (Python/Rust)**:
    - Implement core logic using `async/await` for all I/O (Neo4j, Postgres, Redis).
    - **Security**: Decorate new endpoints with `@verify_passkey_token`.
    - **Data**: Use parameterized Cypher queries for Neo4j (No string concat).
4.  **Frontend (React/Vite)**:
    - Create components with **Strict TypeScript** interfaces.
    - Use **Tailwind** for styling (No custom CSS files unless defined in design system).
    - Ensure `vite.config.ts` proxy is used for local dev (CORS handling).

## Phase 3: Verification & Linting
5.  **Automated Checks**:
    - Run `npm run type-check`.
    - Run `cargo test` or `pytest`.
    - *Self-Correction:* If a test fails, fix the code. **DO NOT** downgrade the test or the library.

## Phase 4: DBS Compliance Check
6.  **Final Review**:
    - Did we delete >200 lines of code? -> If yes, trigger **DBS Protocol** (User Approval).
    - Did we open a new port? -> If yes, **FAIL**. Find and kill the zombie process instead.
