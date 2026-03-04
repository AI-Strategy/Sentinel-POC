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
4. **Injection Prevention**: Agents are forbidden from using string concatenation for SQL/Cypher.
