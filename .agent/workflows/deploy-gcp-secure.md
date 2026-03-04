# Workflow: Secure Deployment (GCP & 0-Trust)

## Trigger
- **Event**: Push to `main` or Manual "Deploy to Production".

## Phase 1: Pre-Flight Security (Hard Fail)
1.  **Secret Scan**:
    - Scan for hardcoded `.env` values or raw keys.
    - Verify all secrets are injected via GitHub Actions Secrets / Workload Identity.
2.  **Infrastructure Validation**:
    - **Google File Store**: Verify mount is via **Private VPC IP** only (No Public IP).
    - **IAM**: Confirm Service Account is OIDC-bound (No JSON Keys).

## Phase 2: Build & Artifacts
3.  **Container Build**:
    - Build using `distroless` or `alpine` base.
    - **CORS Check**: Verify Ingress/Load Balancer handles CORS (not app code).
    - **Code Freeze**: Ensure no "Last Resort" Regex was used without a documented waiver.

## Phase 3: Database & State
4.  **Migration Guard**:
    - **Neo4j**: Check Vector Index dimensions (e.g., 1536).
    - **Postgres**: Check for locking operations (`DROP TABLE`).
    - **Redis**: Ensure `protected-mode yes` and valid TTLs (Ghost Mode).
    - *Action:* If destructive, pause for **DBS Human Approval**.

## Phase 4: Zero-Trust Handover
5.  **Traffic Shift**:
    - Deploy to staging slot.
    - Verify `verify_passkey_token` middleware rejects invalid requests (401/403).
    - Shift traffic and log to `.audit/deploy_log.json`.
