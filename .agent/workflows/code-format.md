---
name: code-format
description: Autonomously lints and formats all Python code using Ruff.
trigger: /format
---
# WORKFLOW: Lightning Linter
**Activation**: Triggered by `/format`
1. **Install Tooling**: Ensure `ruff` is installed (`pip install ruff` in the active virtual environment).
2. **Execution**: Run `ruff check --fix src/ tests/` in the terminal to autonomously fix import sorting and unused variables.
3. **Formatting**: Run `ruff format src/ tests/` in the terminal to enforce strict code styling.
