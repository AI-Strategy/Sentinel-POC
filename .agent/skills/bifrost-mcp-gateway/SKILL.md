---
name: bifrost-mcp-gateway
description: Manages the Bifrost Gateway configuration, virtual keys, and MCP tool registration.
---

# Bifrost Gateway Expert

## Configuration Standards (v1.x)
1.  **Zero-Config Deployment**:
    - Prefer **Docker** deployment: `docker run -p 8080:8080 maximhq/bifrost`.
    - Persistence: Always mount volume `-v $(pwd)/bifrost_data:/app/data` to persist virtual keys and logs.
2.  **Virtual Keys (Governance)**:
    - **Never** expose raw provider keys to the client.
    - Create **Virtual Keys** for each agent identity (e.g., `vk-search-agent`).
    - Enforce tool scoping: `curl -X PUT /api/governance/virtual-keys/{id}` to whitelist only necessary tools (e.g., `filesystem:read_only`).
3.  **Semantic Caching**:
    - Enable semantic caching for high-traffic read operations (e.g., documentation lookups) to reduce LLM costs.

## MCP Tool Registration
- **Filesystem**: Use `@modelcontextprotocol/server-filesystem` via `npx` (STDIO mode).
- **Postgres**: Register `mcp-server-postgres` with read-only credentials for the gateway.

## Protocol
- **Action**: When adding a new tool, register it in Bifrost *first*, then assign it to the specific Agent's Virtual Key.
