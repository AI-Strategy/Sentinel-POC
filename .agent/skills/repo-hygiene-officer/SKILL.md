---
name: repo-hygiene-officer
description: Identifies and safely archives unused files, strictly avoiding critical config/script deletion.
---

# Repo Hygiene Protocol

## Safety First (The "Do Not Touch" List)
1.  **Critical Whitelist**: NEVER flag or touch:
    - `*.env*` (Configs)
    - `Dockerfile`, `docker-compose*`
    - `.github/*` (Workflows)
    - `bin/*` or `scripts/*` (Maintenance scripts often look unused).
    - `*schema*` (Database definitions).

## Detection Logic
1.  **Asset Scan**:
    - Scan `/public` or `/assets` for images/fonts.
    - Search codebase for string references (e.g., `"logo.png"`).
    - If count == 0 -> Mark as **ZOMBIE**.
2.  **Code Scan (Knip/Deadfile)**:
    - Use `knip` (TS) or `vulture` (Python) to find exported but unused functions.
    - *Constraint*: Low confidence? Do not report.

## The "Soft Delete" Action
- **NEVER** run `rm` directly on detected junk.
- **Action**: Move to `_archive/junk_[date]/`.
    - *Reasoning*: If we break production, we can `mv` it back instantly.
- **Report**: "Moved 14 unused images to `_archive/`. Please review and delete after 1 week."

## Usage
- **Trigger**: Weekly `cron` or Manual "Sweep the repo."
