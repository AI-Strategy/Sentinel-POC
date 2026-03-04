---
name: python-modern-architect
description: Generates strictly typed, async Python 3.13+ code.
---

# Python Expert Protocol

## Core Mandates
1.  **Strict Typing**: All function signatures must have type hints. Use `typing.Annotated` where beneficial.
2.  **Validation**: Use **Pydantic v2** for all data models.
    - *Syntax*: `model_validate()`, NOT `parse_obj()` (deprecated).
3.  **Concurrency**: Code must be `async/await` native.
    - *Web*: `FastAPI` or `Litestar`.
    - *DB*: `asyncpg` or `SQLAlchemy` (AsyncSession).
4.  **Linting**: Code must pass `ruff` check (replacing flake8/isort).

## "Latest Version" Checklist (Verify via Web)
- Check latest syntax for: `pydantic` (v2+), `fastapi`, `sqlalchemy` (v2+), `langchain` (if applicable).
