---
name: git-secure-commit
description: Commits changes to git with strict security checks and semantic formatting.
---

# Git Secure Commit

## Protocol (Strict Enforcement)
1.  **Secret Scan**: 
    - **Check**: Is `.env` or `.env.local` staged for commit?
    - **Action**: If yes, **HARD BLOCK**. "You are attempting to commit a `.env` file. Remove it from staging (`git reset .env`) and add it to `.gitignore`."
    - **Content Scan**: Scan other files for hardcoded keys (`sk-...`, `ey...`).

2.  **Semantic Message**: Format as `type(scope): description`.
3.  **Push Guard**: Do not push to `main` directly.
