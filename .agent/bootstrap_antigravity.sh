#!/bin/bash
set -e

echo "🚀 Initiating Antigravity 'Big Bang' Bootstrap..."
echo "📂 Creating directory structure..."

# --- 1. Directory Structure ---
mkdir -p .agent/{rules,skills,workflows,audit,daily_reports}
mkdir -p .agent/skills/{git-secure-commit,run-test-sim,software-version-check,zombie-port-manager,neo4j-deep-architect,rust-idiomatic-engineer,python-modern-architect,doc-architect,bifrost-mcp-gateway,repo-hygiene-officer,api-contract-guard,audit-logger,loop-sentinel,pii-redaction-guard,workspace-janitor}
mkdir -p src/{synaptic,cortical,deep}
mkdir -p tests/simulations
mkdir -p bin scripts

# --- 2. The Laws (Rules) ---
echo "📜 Writing Rules (00-05)..."

cat <<'EOF' > .agent/rules/00-global-architecture-laws.md
name
  global-architecture-laws
description
  Enforces strict modularity, zero-trust security, and web-first grounding.
alwaysApply
  true

# Global Architecture Laws (STRICT ENFORCEMENT)
1. **Web-First Grounding (Critical)**: Legacy training data is deprecated. You MUST perform a Google Search via the browser tool before citing syntax for:
   - **Python 3.13+** / **Rust 2024 Edition**
   - **Neo4j 5.x+** (Vector Indexes)
   - **React 19+** (Server Components)
2. **Zero-Trust Mandate**: EVERY memory retrieval or API endpoint MUST utilize the `verify_passkey_token` middleware. 
   - If a token is missing/expired: **Fail Closed** (HTTP 401). 
   - Never bypass authentication for "debugging."
3. **Strict Modularity**: NEVER mix database logic. 
   - `Synaptic` (Redis), `Cortical` (Postgres), and `Deep` (Neo4j) logic must remain exclusively in their respective `/src` directories.
4. **No REGEX (Last Resort)**: Use `Gemini 2.5 Flash` for complex text parsing. 
   - *Exception*: Regex is permitted ONLY if latency/cost is critical and documented.
5. **Deterministic Citations**: All narrative outputs must return a mathematically retrieved `source_uuid`. Hallucinations trigger the TalosCore Kill-Switch.
EOF

cat <<'EOF' > .agent/rules/01-hard-security-enforcement.md
name
  hard-security-enforcement
description
  Unbreakable security laws for code generation, database access, and GCP.
alwaysApply
  true

# Security Enforcement (NON-NEGOTIABLE)
1. **Identity & Access**: 
   - All internal/external APIs must use **OAuth Passkey** (Bearer Token). 
   - No "API Key" query parameters.
2. **Database Isolation**:
   - **Postgres**: No raw SQL in the `Cortical` layer without active **Row-Level Security (RLS)** bound to `user_id`. Connect via restricted role, never superuser.
   - **Redis**: Keys MUST have explicit `EXPIRE` (Ghost Mode, max 900s). Data-in-transit must use `rediss://`.
   - **Neo4j**: Use parameterized Cypher queries only. String concatenation is a P0 vulnerability.
3. **GCP & Infrastructure**:
   - **Google File Store**: Must be mounted via **Private VPC IP** only. Public exposure is a critical failure.
   - **IAM**: Service Accounts must be bound to Workload Identity (OIDC), not JSON keys.
EOF

cat <<'EOF' > .agent/rules/02-antigravity-scaling-standards.md
name
  antigravity-scaling-standards
description
  Engineering standards for scaling, modularity, and tool usage.
alwaysApply
  true

# Engineering Scaling Laws
1. **Skills over Scripts**: Favor atomic, reusable tools in `.agent/skills/` over monolithic script blocks.
2. **Version Control Hygiene**: For all major changes using "Deep Research" or "Canvas" modes, you must increment the internal version in the file header.
3. **Automated Documentation**: Every new function or module must be accompanied by updated markdown documentation in `/docs`. Undocumented code is considered broken code.
EOF

cat <<'EOF' > .agent/rules/03-testing-and-simulation.md
name
  testing-and-simulation-protocols
description
  Encourages simulation, grants non-destructive testing autonomy, and enforces safe verification.
alwaysApply
  true

# Testing & Simulation Standards
1. **Non-Destructive Autonomy**: You are explicitly authorized to perform non-destructive testing (`pytest`, `cargo test`) without human approval.
2. **Simulation First**: Prioritize "Simulation" and "Scenario Testing" over direct execution against live dev environments.
   - *Protocol:* When modifying complex logic, create a discrete simulation script (`tests/sim_scenario_A.py`) first.
3. **Mocking External State**: Do not hit live GCP APIs or Google File Store during standard unit tests. Use mocks or test containers.
EOF

cat <<'EOF' > .agent/rules/04-dbs-operational-governance.md
name
  dbs-operational-governance
description
  The "Don't Be Stupid" Protocol. Safe-guards against irreversible actions and enforces self-correction.
alwaysApply
  true

# Operational Governance (STRICT ENFORCEMENT)
1. **The "Better Way" Reflection**: Before executing ANY destructive or irreversible command, you must explicitly pause and ask yourself: *"Is there a better, non-destructive way to proceed?"*
2. **Destruction Threshold (200 Lines)**:
   - Deleting or rewriting >200 lines of code in a single turn requires explicit `HUMAN_APPROVAL_REQUEST`.
   - `DROP TABLE`, `DELETE FROM` (without specific IDs), and `FLUSHDB` are strictly prohibited without a multi-turn confirmation sequence.
3. **No New Ports (Zombie Rule)**: You are forbidden from opening new ports (e.g., 3001, 8081) simply because the primary port is blocked. Kill the zombie process instead.
4. **Anti-Downgrade Protection**: You may not downgrade libraries (Python, Rust, Node) to resolve conflicts.
EOF

cat <<'EOF' > .agent/rules/05-stack-specifics.md
name
  stack-specific-standards
description
  Strict technical standards for Python/Rust, React, Neo4j, and GCP infrastructure.
alwaysApply
  true

# Stack & Implementation Standards
1. **Frontend (React/Vite/Tailwind)**:
   - **Type Safety**: All components must be typed with strict TypeScript interfaces. No `any`.
   - **CORS (Dev)**: Do not hack headers. Use the **Vite Proxy** (`server.proxy`).
   - **Styling**: Use Tailwind utility classes. No custom CSS files unless strictly necessary.
2. **Backend (Python/Rust)**:
   - **Async Mandate**: All I/O operations (Postgres, Redis, Neo4j) must be `async/await`.
   - **Rust Safety**: Use `tokio`. `unwrap()` is forbidden in production; use `Result<T, E>`.
   - **CORS (Prod)**: Handle at Ingress/Load Balancer or strictly typed Middleware (no wildcard `*`).
3. **Data Layer**:
   - **Neo4j Vector**: Create Vector Indexes with explicit dimensions (e.g., 1536). Use `db.index.vector.queryNodes`.
   - **Postgres**: Always use connection pooling (`pgbouncer` or `asyncpg`).
   - **Redis**: Verify `protected-mode yes` and explicit TTLs (Ghost Mode).
EOF

# --- 3. The Workflows (Habits) ---
echo "🔄 Writing Workflows..."

cat <<'EOF' > .agent/workflows/feature-dev-loop.md
name
  feature-dev-loop
description
  Strict development loop for Python/Rust & React. Enforces Async I/O, Simulation First, and Type Safety.

steps
  1. **Context & Simulation (Rule 03-2)**
     - **Constraint**: If logic involves GraphRAG or complex math, create `tests/sim_scenario_X.py` FIRST.
     - **Check**: Search web for latest library versions (Rule 00-1). Do not use deprecated syntax.

  2. **Backend Implementation (Rust/Python)**
     - Implement core logic using `async/await`.
     - **Security**: Decorate endpoints with `@verify_passkey_token`.
     - **Data**: Use parameterized Cypher/SQL queries.

  3. **Frontend Implementation (React/Vite)**
     - Create components with **Strict TypeScript** interfaces.
     - Use **Tailwind** for styling.
     - Ensure `vite.config.ts` proxy is used for local dev.

  4. **Verification & Linting**
     - Run `npm run type-check`.
     - Run `cargo test` or `pytest`.
     - **Self-Correction**: If a test fails, FIX the code. DO NOT downgrade the test or library.

  5. **Final Review (DBS)**
     - Check: Did we delete >200 lines? If yes, trigger DBS Protocol.
     - Check: Are we using Regex? If yes, refactor to use Gemini Flash.
EOF

cat <<'EOF' > .agent/workflows/deploy-gcp-secure.md
name
  deploy-gcp-secure
description
  Secure deployment pipeline for GCP. Enforces OIDC, Passkeys, and 0-Trust networking.

steps
  1. **Pre-Flight Security Check**
     - Scan for hardcoded secrets or PII.
     - Verify `requirements.txt`/`Cargo.toml` for deprecated packages.

  2. **Infrastructure Validation**
     - **File Store**: Ensure mount is Private VPC IP only.
     - **IAM**: Verify Service Accounts are OIDC-bound.
     - **Ports**: Confirm no new ports are exposed.

  3. **Container Build**
     - Build using `distroless` or `alpine` base.
     - **CORS**: Verify Ingress/LB handles CORS.

  4. **Database Safety**
     - **Neo4j**: Verify vector index dimensions match model.
     - **Postgres**: Check for blocking locks (`DROP TABLE`).
     - **DBS Protocol**: If destructive, pause for approval.

  5. **Zero-Trust Handover**
     - Verify `verify_passkey_token` middleware is active.
     - Log deployment to `.audit/deploy_log.json`.
EOF

cat <<'EOF' > .agent/workflows/daily-health-check.md
name
  daily-health-check
description
  Runs a comprehensive system health check (Dependencies, Graph Integrity, Security).

steps
  1. **Dependency Scan**
     - Run `cargo audit` and `pip-audit`.
     - Check for critical CVEs.

  2. **Graph Integrity Check**
     - Query Neo4j: "Are there any disconnected nodes?"
     - Query Redis: "Are there any keys missing TTLs?"

  3. **Documentation Sync**
     - Run `doc-architect` to ensure READMEs match code.

  4. **Status Report**
     - Generate summary in `.agent/daily_reports/YYYY-MM-DD.md`.
EOF

# --- 4. The Skills (Muscles) ---
echo "🛠️ Writing Skills & Protocols..."

# Rust Expert
cat <<'EOF' > .agent/skills/rust-idiomatic-engineer/SKILL.md
---
name: rust-idiomatic-engineer
description: Generates high-performance, memory-safe Rust code using modern idioms (2024 Edition).
---
# Rust Expert Protocol
1. **Async Runtime**: Default to `tokio` for all I/O. Use `axum` for web services.
2. **Error Handling**: `unwrap()` and `expect()` are **FORBIDDEN** in production. Use `Result<T, AppError>`.
3. **Database**: Use `sqlx` (async) with compile-time verification.
4. **Serialization**: Use `serde` with `#[serde(rename_all = "camelCase")]`.
EOF

# Python Expert
cat <<'EOF' > .agent/skills/python-modern-architect/SKILL.md
---
name: python-modern-architect
description: Generates strictly typed, async Python 3.13+ code.
---
# Python Expert Protocol
1. **Strict Typing**: All function signatures must have type hints.
2. **Validation**: Use **Pydantic v2** (`model_validate`, NOT `parse_obj`).
3. **Concurrency**: Code must be `async/await` native (`FastAPI`, `asyncpg`).
4. **Linting**: Code must pass `ruff` check.
EOF

# Neo4j Deep Architect
cat <<'EOF' > .agent/skills/neo4j-deep-architect/SKILL.md
---
name: neo4j-deep-architect
description: Master skill for Neo4j 5.x+, GDS, Vector Indexing, and Bulk Ingestion.
---
# Neo4j Expert Protocol
1. **Native Vectors**: Use `VECTOR<FLOAT32>`. Index with `db.index.vector.queryNodes`.
2. **GDS**: Use Native Projections (`gds.graph.project`).
3. **Ingestion**: Use `CALL { ... } IN TRANSACTIONS` for bulk loads.
4. **Cypher Standards**: Strict usage of `$params`. No string concatenation.
EOF

# Doc Architect
cat <<'EOF' > .agent/skills/doc-architect/SKILL.md
---
name: doc-architect
description: Maintains READMEs, CHANGELOGs, and inline documentation.
---
# Doc Architect Protocol
1. **Module READMEs**: Scan folders and generate READMEs with Purpose, Exports, and Dependencies.
2. **Root Sync**: Update project tree in root `README.md`.
3. **Docstrings**: Scan Python/Rust files for missing docstrings and auto-draft them.
EOF

# Repo Hygiene Officer
cat <<'EOF' > .agent/skills/repo-hygiene-officer/SKILL.md
---
name: repo-hygiene-officer
description: Identifies and safely archives unused files.
---
# Repo Hygiene Protocol
1. **Safety First**: NEVER touch `*.env*`, `Dockerfile`, `.github/*`, or `bin/*`.
2. **Detection**: Use `knip` (TS) or `vulture` (Python) to find dead code.
3. **Soft Delete**: Move junk to `_archive/junk_[date]/`. NEVER `rm` directly.
EOF

# Zombie Port Manager (Script Wrapper)
cat <<'EOF' > .agent/skills/zombie-port-manager/SKILL.md
---
name: zombie-port-manager
description: Frees up a blocked port by killing the process holding it.
---
# Zombie Port Manager
1. **Identify**: `lsof -t -i:[PORT]`
2. **Kill**: `kill -9 [PID]`
3. **Report**: "Port [PORT] was blocked by PID [PID]. Killed it."
EOF

# Bifrost Gateway
cat <<'EOF' > .agent/skills/bifrost-mcp-gateway/SKILL.md
---
name: bifrost-mcp-gateway
description: Manages Bifrost Gateway, virtual keys, and MCP tools.
---
# Bifrost Gateway Protocol
1. **Zero-Config**: Deploy via Docker with volume persistence.
2. **Virtual Keys**: Create scoped keys for each agent identity. Never expose raw provider keys.
3. **Registration**: Register tools in Bifrost first, then whitelist in Virtual Key.
EOF

# Audit Logger
cat <<'EOF' > .agent/skills/audit-logger/SKILL.md
---
name: audit-logger
description: Appends structured, immutable logs to the audit trail.
---
# Audit Logger Protocol
1. **Structure**: JSON-L with timestamp, actor, action_type, context_hash, reasoning.
2. **Storage**: `.audit/events_<date>.jsonl`.
3. **Privilege**: Tag `PRIVILEGED` if client_id is present.
EOF

# Loop Sentinel
cat <<'EOF' > .agent/skills/loop-sentinel/SKILL.md
---
name: loop-sentinel
description: Detects and breaks infinite loops or repetitive failures.
---
# Loop Sentinel Protocol
1. **History Check**: Check last 5 steps.
2. **Circuit Break**: If 3 strikes (same tool/error) -> STOP and request human help.
EOF

# PII Redaction Guard
cat <<'EOF' > .agent/skills/pii-redaction-guard/SKILL.md
---
name: pii-redaction-guard
description: Scans and redacts PII/PHI from text before logging.
---
# PII Redaction Protocol
1. **Scrub**: SSNs, Credit Cards, API Keys.
2. **Replace**: Use `[EMAIL_REDACTED_HASH]` to maintain referential integrity.
3. **Legal Hold**: Bypass only for "Private Graph" storage.
EOF

# --- 5. Hygiene Configurations ---
echo "🧹 Writing Hygiene Configs..."

cat <<'EOF' > knip.json
{
  "$schema": "https://unpkg.com/knip@5/schema.json",
  "entry": ["src/main.tsx", "src/index.tsx", "vite.config.ts", "tailwind.config.js"],
  "project": ["src/**/*.{ts,tsx,js,jsx}"],
  "ignore": ["**/*.d.ts", "**/*.test.{ts,tsx}", "bin/**", "scripts/**", "public/**"],
  "ignoreDependencies": ["lucide-react", "clsx", "tailwind-merge"],
  "rules": {"files": "warn", "dependencies": "warn", "unlisted": "error", "exports": "warn"}
}
EOF

cat <<'EOF' > pyproject.toml
[tool.vulture]
min_confidence = 80
paths = ["src", "bin", "scripts"]
exclude = ["tests/", "docs/", ".venv/", "migrations/", "conftest.py"]
sort_by_size = true
verbose = false
ignore_names = ["model_config", "Config", "__main__", "lifespan"]

[tool.ruff]
line-length = 100
EOF

# --- 6. Python Utility Scripts (bin/) ---
echo "🐍 Writing Utility Scripts..."

cat <<'EOF' > scripts/log_event.py
import json
import datetime
import hashlib
import sys
from typing import Literal

def log_event(action: str, reasoning: str, status: str, client_id: str = None):
    entry = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "action": action,
        "reasoning": reasoning,
        "status": status,
        "client_id": client_id,
        "integrity_hash": hashlib.sha256(reasoning.encode()).hexdigest()
    }
    filename = f".audit/events_{datetime.date.today()}.jsonl"
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Event logged to {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        log_event(sys.argv[1], sys.argv[2], sys.argv[3])
EOF

cat <<'EOF' > scripts/kill_port.py
import subprocess
import sys

def kill_port(port):
    try:
        pid = subprocess.check_output(f"lsof -t -i:{port}", shell=True).decode().strip()
        if pid:
            subprocess.run(f"kill -9 {pid}", shell=True)
            print(f"Killed PID {pid} on port {port}")
        else:
            print(f"Port {port} is free.")
    except Exception as e:
        print(f"Port {port} is free or error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        kill_port(sys.argv[1])
EOF

chmod +x scripts/*.py

echo "✅ ANTIGRAVITY BOOTSTRAP COMPLETE."
echo "   - Rules Enhanced (00-05)"
echo "   - Workflows Created (Loop, Deploy, Health)"
echo "   - Skills & Experts Installed"
echo "   - Hygiene Configured"
echo "   - Ready for Operation."
