---
name: secret-injector
description: Securely injects secrets from GCP/Vault into the runtime environment without writing .env files.
---

# Secret Injector Protocol

## Goal
Enable `localhost` development without ever committing or creating a plaintext `.env` file.

## Protocol
1.  **Source**: Connect to GCP Secret Manager (using `gcloud` auth) or a local 1Password CLI (`op`).
2.  **Injection**:
    - **Python**: Use `os.environ.update(secrets)` *before* app startup.
    - **Rust**: Use `dotenvy::from_read` with a memory stream, not a file.
    - **Node**: Use `--env-file` (Node 20+) pointing to a named pipe, not a disk file.
3.  **Audit**: Log "Secrets Injected for [Project]" to the audit trail. NEVER log the values.

## Python Tool (`scripts/inject_secrets.py`)
```python
import subprocess
import json
import os

def get_gcp_secrets(project_id):
    # Fetch all secrets for the project
    cmd = f"gcloud secrets list --project={project_id} --format=json"
    secrets_list = json.loads(subprocess.check_output(cmd, shell=True))
    
    env_vars = {}
    for secret in secrets_list:
        name = secret['name'].split('/')[-1].upper()
        # Fetch latest version payload
        val_cmd = f"gcloud secrets versions access latest --secret={name} --project={project_id}"
        val = subprocess.check_output(val_cmd, shell=True).decode().strip()
        env_vars[name] = val
        
    return env_vars
