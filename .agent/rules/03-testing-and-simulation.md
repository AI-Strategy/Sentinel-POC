name
  testing-and-simulation-protocols
description
  Encourages simulation, grants non-destructive testing autonomy, and enforces safe verification.
alwaysApply
  true

# Testing & Simulation Standards
1. **Non-Destructive Autonomy**: You are explicitly authorized to perform non-destructive testing (`pytest`, `cargo test`) without human approval.
2. **Simulation First**: Prioritize "Simulation" and "Scenario Testing" over direct execution against live dev environments.
   - *Protocol:* When modifying complex logic, create a discrete simulation script (`tests/sim_scenario_A.py`) first.
3. **Mocking External State**: Do not hit live GCP APIs or Google File Store during standard unit tests. Use mocks or test containers.
