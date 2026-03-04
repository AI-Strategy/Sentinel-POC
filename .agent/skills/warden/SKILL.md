# 🛡️ Antigravity-Warden (SEC-001)

## Trigger: 
* On every `#privileged` code generation.
* Scheduled: 08:00 and 20:00 PST.

Logic (Passive vs. Blocking):
This skill operates in **Passive Mode** by default to prioritize development performance. Semantic analysis via **Gemini 3 Flash** is performed **On-Demand** to identify vulnerabilities.

1. **Semantic Secret Hunting**: Manual scan via `/warden-scan` for passwords or keys using LLM reasoning.
2. **On-Demand Port Audit**: Inspect `docker-compose.yml` when triggered, flagging `0.0.0.0` bindings.
3. **Artifact Analysis**: Optional GCP container scanning for Python 3.13 CVEs.
4. **Passive Shadow Audit**: Bi-daily logging to `/security/warden-audit.log` without build interruption.

## Actions:
* **AUDIT**: Record findings to `/security/` report; do not block commits unless in `#production` mode.
* **NOTIFY**: Provide a "Big Red Button" summary for manual review after `#security-review` triggers.

## Compliance Citation:
- **Protocol Zero**: v2026.02
- **DBS Protocol**: v1.5
