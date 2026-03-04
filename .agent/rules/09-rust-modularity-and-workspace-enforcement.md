---
id: RUST-MOD-01
name: Rust Modularity and Workspace Enforcement
enforcement: STRICT
---

# RUST-MOD-01: Rust Modularity and Workspace Enforcement

## Mission
To prevent monolithic degradation and ensure high-performance scaling by enforcing strict modularity boundaries using Rust's module system and Cargo workspaces.

## 1. Architectural Rules
- **Workspace Adoption:** Mandate Cargo Workspaces for any architecture exceeding a single functional domain. Isolate core execution, data ingestion, and API routing into independent micro-crates.
- **Domain Isolation:** Enforce strict physical separation of mathematical models, algorithmic logic, and scenario engines into dedicated modules/crates.
- **Visibility Control:** Restrict the default use of `pub`. Use `pub(crate)` or `pub(super)` to prevent internal state leakage. Strictly control the public API surface.

## 2. Implementation Standards
- **Trait-Driven Contracts:** Define interactions between modules EXCLUSIVELY through Rust traits. This ensures interchangeable implementations and abstracts complex logic.
- **Facade Pattern Enforcement:** High-level modules must provide a clean, unified facade (`mod.rs` or `lib.rs`) that re-exports only necessary types, hiding internal submodule complexity.

## 3. Module-Level Workflows
- **Independent Compilation:** Every isolated module or crate MUST compile independently (`cargo check -p <crate_name>`) before full-system integration.
- **Localized Testing:** Run unit tests and `proptest` suites strictly scoped to the modified module during iterative development to minimize cycle time.
- **Cyclic Dependency Prevention:** Analyze module import graphs. Immediately refactor circular dependencies by extracting shared types into a common definitions module (e.g., `vq-core-types`).

## 4. Enforcement Strategy
- **Facade Verification:** Any module containing more than 3 submodules MUST implement a facade re-exporting only required entities.
- **Public API Audit:** Prior to PR generation, audit the public exports of modified crates to ensure no internal implementation details have leaked via `pub`.
