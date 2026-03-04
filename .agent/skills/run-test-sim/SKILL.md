---
name: run-test-sim
description: Runs tests with a preference for simulation scenarios over live execution.
---

# Run Test & Simulation

## Goal
Execute verification suites while prioritizing non-destructive simulations.

## Protocol
1.  **Downgrade Check**: If a test fails, you are **FORBIDDEN** from suggesting a dependency downgrade. You must suggest a code fix.
2.  **Simulation Priority**:
    - If the user asks to "test the graph logic," look for `tests/sim_scenario_*.py` first.
    - Run the simulation before running the full integration suite.
3.  **Command Mapping**:
    - Python: `pytest --asyncio-mode=strict`
    - Rust: `cargo test -- --nocapture`
    - React: `npm run type-check && npm test`
