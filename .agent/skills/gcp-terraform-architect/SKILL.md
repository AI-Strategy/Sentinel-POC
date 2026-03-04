---
name: gcp-terraform-architect
description: Generates Infrastructure as Code (IaC) for GCP following Well-Architected frameworks.
---

# Infrastructure Expert Protocol

## Network Security (Zero Trust)
1.  **Private by Default**: Cloud Functions, Cloud Run, and File Store must attach to a **Private VPC**.
2.  **No Public IPs**: Databases (Cloud SQL, Redis) must NOT have public IP addresses.

## State Management
- Use GCS Bucket for Terraform State with **Object Versioning** enabled.
- Implement **State Locking** to prevent race conditions.

## "Latest Version" Checklist
- Check `google` provider version constraints.
- Verify latest machine types (e.g., use `t2d` or `c3` over legacy types).
