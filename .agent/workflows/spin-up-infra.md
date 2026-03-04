---
name: spin-up-infra
description: Autonomously writes and launches a docker-compose.yml for local databases.
trigger: /infra
---
# WORKFLOW: Local Infrastructure Mechanic
**Activation**: Triggered by `/infra`
1. **Scaffold**: If missing, write a `docker-compose.yml` in the root directory that provisions PostgreSQL 18.x, Redis 7.4, and Neo4j 2026.1 Enterprise/Community.
2. **Constraints**: Ensure all passwords, users, and ports match the `.env` file perfectly. Mount local volumes (e.g., `./.docker-data/postgres:/var/lib/postgresql/data`) for data persistence.
3. **Launch**: Execute `docker compose up -d` in the terminal to spin up the databases in the background.
4. **Verify**: Run `docker ps` to verify containers are healthy and ports are mapped.
