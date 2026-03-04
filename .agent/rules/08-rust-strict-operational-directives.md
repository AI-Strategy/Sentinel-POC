---
id: RUST-STRICT-01
name: Rust Strict Operational Directives
enforcement: STRICT
---

# RUST-STRICT-01: Rust Strict Operational Directives

## Mission
To establish enterprise-grade performance and security suitable for top-tier institutional clients by enforcing rigid Rust standards during code generation, review, and refactoring.

## 1. Rules & Syntax
- **Immutability First:** Default all variables to immutable. Require explicit justification within inline comments for any `mut` declaration.
- **Unsafe Code Prohibition:** Deny `unsafe` blocks. If an external library requires `unsafe` bindings, isolate the implementation in a dedicated wrapper crate and require mandatory cryptographic or manual safety proofs.
- **Error Handling:** Ban the use of `.unwrap()` and `.expect()` in production pathways. Enforce the use of `Result` types and the `?` operator. Use custom error enums with `thiserror`.
- **Clippy Enforcement:** Mandate `#![deny(clippy::pedantic)]` and `#![deny(clippy::unwrap_used)]` at the crate level.

## 2. Security & Data Integrity
- **Environment Variables:** Utilize `.env` files EXCLUSIVELY for local development. Enforce strict secrets management protocols for staging/production (GCP Secret Manager).
- **Execution Isolation:** Database interactions and execution layers (e.g., vq-math/wasm) MUST run within isolated or confidential computing environments.
- **Dependency Auditing:** Perform `cargo audit` checks. Block generation that introduces crates with known CVEs or unmaintained status.
- **Data Serialization:** Enforce strict type validation boundary layers when deserializing external data (e.g., via `serde`). Reject unvalidated or loosely typed inputs.

## 3. Skills & Implementation Standards
- **Concurrency:** Implement asynchronous operations using `tokio`. Mandate deterministic state management across all async boundaries to prevent race conditions.
- **Memory Optimization:** Utilize zero-cost abstractions. Avoid unnecessary cloning (`.clone()`). Enforce explicit ownership transfers or borrowing paradigms.
- **Algorithm Efficiency:** Implement exact mathematical and algorithmic logic tailored for high-throughput, low-latency financial/analytical modeling.

## 4. Testing & Verification
- **Property-Based Testing:** Enforce `proptest` for all algorithmic and mathematical functions.
- **Coverage Mandates:** 100% branch coverage required on core logic and state-mutating functions.
- **Fuzzing:** Implement `cargo fuzz` on all public-facing APIs and data ingestion pipelines.
- **Benchmarks:** Require `criterion` benchmarks for performance-critical pathways.

## 5. Issue Identification & Remediation
- **Critical Severity:** Classify any memory leak, panic, or data race as a critical severity issue requiring immediate rollback or halt.
- **Resolution Protocol:** When correcting a compilation error, identify the specific Rust compiler error code (e.g., `E0382`) and document the exact ownership or borrowing rule violated before generating the fix.
