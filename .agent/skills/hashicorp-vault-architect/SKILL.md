---
name: hashicorp-vault-architect
description: Implements Zero Trust secret management and brokered authentication using HashiCorp Vault 1.21+.
---

# HashiCorp Vault Expert Protocol

## Core Mandates
1. **Brokered Authentication**: Default to Vault 1.21.3 for all dynamic credential generation and access control.
2. **Workload Identity**: Enforce SPIFFE authentication standards for workload identity and inter-service communication. 
3. **Kubernetes Integration**: Use the Vault Secrets Operator (VSO) to deliver secrets directly to pods at startup. You are **FORBIDDEN** from persisting Vault secrets into native Kubernetes `Secret` objects.
4. **Compliance & Recovery**: Configure core cryptographic operations to maintain FIPS 140-3 Level 1 compliance. Enable fine-grained secret recovery to allow targeted restoration of individual configuration items without rolling back the entire cluster.

## "Latest Version" Checklist (Verify via Web)
- Check latest syntax for: `vault` (1.21+), `vault-helm` (0.32+), `vault-csi-provider` (1.7+).
