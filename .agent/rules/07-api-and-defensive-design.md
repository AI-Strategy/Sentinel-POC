---
name: api-and-defensive-design
description: Enforces Directives 7, 14, 18, and 19.
alwaysApply: true
---
# API Design & Defensive Posture (v1.5.0)

1. **Error Handling (Dir 18)**: Fail Fast, Fail Loud. Never swallow exceptions silently (no bare `except:`). Implement max 3 retries with exponential backoff (1s, 2s, 4s) and jitter for transient failures. 
2. **API Design Standards (Dir 19)**: Enforce strict REST principles. Use correct HTTP status codes (201, 204, 409, 422). Enforce cursor-based pagination and include `X-RateLimit-*` headers on all responses.
3. **Defensive Input Handling (Dir 14)**: Assume the perimeter is breached. Never pass raw user input to SQL, shells, or `eval()`. Use allowlists.
4. **Get Home Mode (Dir 7)**: Systems must degrade gracefully. If Deep Memory (Neo4j) fails, standard CRUD operations must continue uninterrupted.
