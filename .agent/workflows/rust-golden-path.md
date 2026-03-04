---
description: The Rust "Golden Path" - A high-performance, secure procedural standard for code generation, validation, and testing.
---

# Rust Golden Path (v1.0.0)

## Objective
To enforce absolute architectural and deterministic precision in every line of Rust code generated for the VertexQuant platform.

## 1. Dependency & Toolchain Initialization
- **Action:** At the start of crate initialization, verify dependency versions to prevent memory drift and outdated library usage.
- **Standards:**
    - **Polars:** Explicitly target `polars = "0.53.0"` for all data pipelines and memory dataframes.
    - **Tokio:** Utilize `tokio = { version = "1.49.0", features = ["full"] }` for all asynchronous runtimes.
- **Validation:**
    - Perform `cargo fmt` after every distinct code generation sequence.
    - Execute `cargo clippy -- -D warnings` for all new logic.
    - // turbo
    - `cargo clippy -- -D warnings` must return zero warnings before moving to the next task.

## 2. State & Environment Management
- **Local Dev:** Use `.env` files for configuration. All connection secrets MUST be isolated here during the development sprint.
- **Secrets Protocol:** If transitioning to production (e.g., GCP Cloud Run), the agent MUST verify that all `.env` keys have been migrated to the **Secret Manager** perimeter.
- **Physical Isolation:** Generate database connection logic that enforces network and data patterns for isolated or confidential computing environments.

## 3. CI/CD & Testing Pipeline
- **Proptests:** For every algorithmic, mathematical, or state-mutating function, generate a corresponding `proptest` suite to validate behavior across vast input ranges.
- **Coverage:** Integrate `cargo-llvm-cov` to verify branch coverage.
    - Enforce a **Zero-Regression** policy on branch coverage. If coverage drops, the agent MUST refactor or add tests.
- **Performance:** For hot-path logic (e.g., `vq-math`), write and execute `criterion` benchmarks to prove latency and throughput stability.

## 4. Issue Remediation & Safety
- **Compiler Errors:** If a `rustc` error occurs:
    1. Parse the exact error code (e.g., `E0382`).
    2. Identify the ownership, borrowing, or lifetime rule violated.
    3. Document the structural fix BEFORE rewriting.
- **Vulnerability Scanning:** Execute `cargo audit` before finalizing any feature branch.
- **DBS Gate:** For any destructive operation (e.g., `DROP TABLE`), the agent must invoke the `covenant-protocol` validation for human approval.
