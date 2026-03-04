---
name: cicd-pipeline-generator
description: Generates secure, efficient GitHub Actions workflows.
---

# CI/CD Expert Protocol

## Security Standards
1.  **No Long-Lived Keys**: Use **Workload Identity Federation** (OIDC) for GCP/AWS auth.
    - *Forbidden*: Storing `GCP_SA_KEY` JSON in GitHub Secrets.
2.  **Pinning**: Pin Actions by SHA hash, not tag, for critical security.
    - *Example*: `uses: actions/checkout@a5ac7... # v4.0.0`
3.  **Least Privilege**: Workflows must declare strictly scoped `permissions:`.

## Optimization
- Implement **Dependency Caching** (`actions/cache`) for Rust (`~/.cargo`) and Python (`pip`).
- Use **Matrix Builds** for multi-platform verification only when necessary to save minutes.
