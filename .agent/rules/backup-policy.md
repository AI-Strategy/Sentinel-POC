# Backup Policy: Tribrid Memory Vault (v2026.02)

## 1. Schedule & Rotation (RPO: 8 Hours)
All agents must adhere to the following **Grandfather-Father-Son** orchestration schedule.

| Backup Type | Frequency | Window | Retention |
| :--- | :--- | :--- | :--- |
| **Full (L0)** | 2x / Week | Sun/Wed 02:00 UTC | 4 Weeks (8 Fulls) |
| **Incremental (L1)** | 3x / Day | 00:00, 08:00, 16:00 UTC | 14 Days |

## 2. Infrastructure: Administrative Isolation (The Air-Gap)
To prevent internal compromise or ransomware from deleting recovery data, backups are restricted to **Project B (Backup Vault)**.
- **Cross-Project Transport**: Backups must be streamed from the live project (Project A) to the secure project (Project B).
- **Immutable Vault**: Target buckets in Project B MUST have **Object Versioning** and a **30-day Bucket Lock (Retention Policy)**.
- **IAM Hardening**: The production VM is restricted to the **`roles/storage.objectCreator`** (Write-Only) role.

## 3. Tooling & Transport
- **Postgres (Cortical)**: Use `pgbackrest` with `--type=full` or `--type=incr`.
- **Neo4j (Deep)**: Use `neo4j-admin database backup` with `--type=AUTO`.
- **Storage**: Backups must be streamed directly to the `gs://vault-backups-${GCP_PROJECT_ID}/` bucket.

## 3. Security Mandates
- **At-Rest Encryption**: All backup artifacts MUST be encrypted using **AES-256-CBC** before upload.
- **WORM Integrity**: The target GCS bucket MUST have **Object Versioning** and **Bucket Lock** enabled.
- **Verification Loop**: The QA Agent must perform a successful dry-run restore every Sunday to verify data consistency.

## 4. Verification & Recovery Loop (The Clean Room)
The integrity of the "Digital SCIF" depends on the verifiability of its recovery state.
- **Project C (Recovery Project)**: Every Sunday, the QA Agent MUST provision a temporary, isolated project (Project C) to verify restoration.
- **In-Place Validation**: Restore latest artifacts -> Verify checksums -> Confirm service health (Heartbeat).
- **Failure Protocol**: If recovery verification fails, trigger a `#critical` alert on the `SecurityShield` and escalate to security admins.
