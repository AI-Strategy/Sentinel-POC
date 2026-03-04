# Workflow: Database Migration (DBS Protocol)

## Trigger
- **Manual**: "Update schema," "Add column," or "Re-index graph."

## Phase 1: The "Better Way" Reflection
1.  **Pause & Reflect**:
    - Ask: *"Is there a non-destructive way to achieve this?"*
    - *Example:* Instead of `RENAME COLUMN` (downtime), can we `ADD COLUMN` + `Backfill`?
    - If a safer path exists, propose it.

## Phase 2: Backup & Snapshot
2.  **Safety Net**:
    - Verify recent snapshot for Cloud SQL / Neo4j Aura.
    - **Redis**: Confirm no permanent data is stored in volatile keys (Ghost Mode check).

## Phase 3: Execution (Transaction Wrapped)
3.  **Apply Changes**:
    - **Postgres**: Run migration in `BEGIN...COMMIT` block.
    - **Neo4j**: Apply schema changes using parameterized Cypher.
    - **Vector**: Re-index only if strictly necessary (High Compute Cost).

## Phase 4: Verification
4.  **Audit**:
    - Run `EXPLAIN ANALYZE` / `PROFILE` to verify performance.
    - Update "Shared Knowledge" graph with new schema structure.
    - Log event to `.audit/migration_log.json`.
