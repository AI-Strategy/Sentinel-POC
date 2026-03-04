name
  stack-standards
description
  Strict technical standards for Rust, React, and Neo4j.
alwaysApply
  true

# Tech Stack Standards
1. **Frontend (React/Vite/Tailwind)**:
   - **Strict Typing**: No `any`. All components must have TypeScript interfaces.
   - **State**: Use TanStack Query or Server Actions. Avoid `useEffect` chains.
   - **Style**: Tailwind utility classes only. No custom CSS files unless necessary.
2. **Backend (Python/Rust)**:
   - **Async Mandate**: All I/O (DB, Network) must be `async/await`.
   - **Rust**: Use `tokio`. No `unwrap()` in production; use `Result` matching.
   - **Python**: Use Pydantic for all data validation.
3. **Data Layer**:
   - **Neo4j Vector**: Create indexes with explicit dimensions (e.g., 1536). Use `db.index.vector.queryNodes`.
   - **Postgres**: Always use connection pooling (`pgbouncer`).
