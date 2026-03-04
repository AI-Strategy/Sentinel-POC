name: antigravity-lifecycle
description: Rules for repo hygiene, API contracts, and secret lifecycles.
alwaysApply: true

# Lifecycle & Hygiene Laws
1. **The API Contract**: 
   - **Widow/Orphan Check**: Backend and Frontend must sync. 
   - **Breaking Changes**: Update `gen-api-types` immediately upon Backend changes.

2. **Repo Hygiene**:
   - **Dead Code**: Move unused files to `_archive/`.
   - **Safety Zone**: The `repo-hygiene-officer` is FORBIDDEN from touching `*.env*`, `bin/`, or `.github/`.
   - **Secret Audit**: Periodically scan to ensure no `.env` files have been accidentally tracked in git.

3. **Documentation Debt**:
   - Update READMEs every 3 files changed.
   - Maintain `CHANGELOG.md` for all features.
