---
description: Verify VM attestation state before processing privileged data
---
# Security Compliance Workflow: VM Attestation Check
// [cite: 4209] - v2026.02 Standard

## 1. Verify GCE Attestation
Run the following gcloud command to inspect the instance security configuration.
// turbo
```powershell
gcloud compute instances describe vault-nerve-center-secure --format="json(confidentialInstanceConfig, shieldedInstanceConfig)"
```

## 2. Check Confidential Output
1. Parse the JSON result.
2. Verify `confidentialInstanceConfig.enableConfidentialCompute` is set to `true`.
3. Verify `shieldedInstanceConfig.enableSecureBoot` is set to `true`.

## 3. TalosCore Initialization
- If the checks pass: Proceed to initialize the **TalosCore Anti-Drift Engine**.
- If the checks fail: Terminate session and log a **CRITICAL SECURITY ALERT** to the `cortical_memory` interaction ledger.

## 4. Documentation
Record the attestation report as a `handover` artifact if this is a first-time deployment.
