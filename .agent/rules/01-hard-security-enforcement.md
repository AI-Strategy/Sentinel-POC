name: hard-security-enforcement
description: Unbreakable security laws for code, DB access, and GCP.
alwaysApply: true

# Security Enforcement (NON-NEGOTIABLE)
1. **Identity & Access**: 
   - All internal/external APIs must use **OAuth Passkey** (Bearer Token). 
   - No "API Key" query parameters.

2. **Secrets Management Lifecycle**:
   - **Local/Dev**: `.env` files are **PERMITTED** for local development.
   - **Git Hygiene**: `.env` files must be strictly added to `.gitignore`. Committing an `.env` file is a critical security failure.
   - **Production**: `.env` files are **FORBIDDEN** in production. You must transition to GCP Secret Manager or Environment Variable injection before deployment.

3. **Database Isolation**:
   - **Postgres**: No raw SQL without active RLS. Connect via restricted role.
   - **Redis**: Keys must have explicit `EXPIRE` (Ghost Mode).
   - **Neo4j**: Use parameterized Cypher queries only.

4. **GCP & Infrastructure**:
   - **Google File Store**: Must be mounted via **Private VPC IP** only.
   - **IAM**: Service Accounts must be bound to Workload Identity (OIDC).
