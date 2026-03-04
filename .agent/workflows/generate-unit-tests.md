---
name: Generate and Verify Unit Tests
description: Scans all new or modified files in /src and generates corresponding pytest unit tests with 100% branch coverage.
---

# Mission Statement
Ensure the integrity of the Tribrid Memory Vault by enforcing a "Tests-First" verification loop for all modular services.

# Execution Steps
1. **Identify Targets**: Use the `ls` and `git status` tools to identify all files in `/src` created or modified since the last commit.
2. **Web-First Research**: For each identified file, perform a Google Search for the latest 2026 best practices for testing its specific dependencies (e.g., "pytest asyncpg 2026 mock strategies").
3. **Generate Tests**:
    - Create a corresponding test file in `tests/unit/` with the `test_` prefix.
    - **Mocking Strategy**: Implement a "Pure Mock" strategy—no real hits to Neo4j, Postgres, or Redis.
    - **Edge Cases**: Explicitly include tests for null inputs, network timeouts, and unauthorized clearance levels.
4. **Verify Coverage**:
    - Execute `pytest --cov=src` in the terminal.
    - Goal: Achieve 100% line and function coverage.
5. **Auto-Document**: Whenever a test reveals a new error condition (e.g., 403 Forbidden), update the category-specific `README.md` to reflect the new HTTP error codes and handling logic.

# Constraints
- Do not use non-deterministic data (random numbers or system dates) in tests.
- Ensure every `catch` block in the source has a corresponding failing test case to verify its behavior.
