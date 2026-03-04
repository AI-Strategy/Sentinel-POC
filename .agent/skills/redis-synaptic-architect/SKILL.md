---
name: redis-synaptic-architect
description: Expert in Redis async patterns, Pub/Sub, and caching strategies (2025 Standards).
---

# Redis Expert Protocol

## Best Practices (2025)
1.  **Asyncio Native**: Use `redis.asyncio` (from `redis-py` 5.0+). NEVER use blocking clients in the main thread.
2.  **Ghost Mode Enforcement**:
    - **Rule**: Every `SET` command must have an `ex` (expiry) or be flagged as `#PERMANENT`.
    - *Anti-Pattern*: Keys without TTL cause memory leaks.
3.  **Connection Pooling**:
    - Use `BlockingConnectionPool` with a `max_connections` limit to prevent socket exhaustion.
4.  **No "KEYS" Command**:
    - Strictly forbid `KEYS *`. Use `SCAN` for iteration.

## Stack-Specifics
- **Pub/Sub**: Use for real-time agent signalling (e.g., "Stop Generation").
- **Serialization**: Use `ORJSON` for storing complex dicts in Redis strings.
