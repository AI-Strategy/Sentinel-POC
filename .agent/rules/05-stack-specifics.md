name
  stack-specific-standards
description
  Strict technical standards for Python/Rust, React, Neo4j, and GCP infrastructure.
alwaysApply
  true

# Stack & Implementation Standards
1. **Frontend (React/Vite/Tailwind)**:
   - **Type Safety**: All components must be typed with strict TypeScript interfaces. No `any`.
   - **CORS (Dev)**: Do not hack headers. Use the **Vite Proxy** (`server.proxy`) to tunnel API requests.
   - **Styling**: Use Tailwind utility classes. No custom CSS files unless strictly necessary.
2. **Backend (Python/Rust)**:
   - **Async Mandate**: All I/O operations (Postgres, Redis, Neo4j) must be `async/await`. Blocking code is prohibited.
   - **Rust Safety**: Use `tokio`. `unwrap()` is forbidden in production; use `Result<T, E>`.
   - **CORS (Prod)**: Handle at Ingress/Load Balancer or strictly typed Middleware (no wildcard `*`).
3. **Data Layer**:
   - **Neo4j Vector**: Create Vector Indexes with explicit dimensions (e.g., 1536). Use `db.index.vector.queryNodes`.
   - **Postgres**: Always use connection pooling (`pgbouncer` or `asyncpg`).
   - **Redis**: Verify `protected-mode yes` and explicit TTLs (Ghost Mode).
