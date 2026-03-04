name
  git-hygiene
description
  Rules for version control and secrets management.
alwaysApply
  true

# Git & Secrets Laws
1. **No Secrets**: Never commit `.env` files. Use GitHub Actions Secrets.
2. **Commit Discipline**: 
   - Commits must be atomic and semantic (e.g., `feat: add user auth`, not `update`).
   - **Docs**: Update `/docs/changelog.md` with every major feature.
3. **Branching**: Use `feature/` or `fix/` branches. Never push directly to `main` without a passed test suite.
