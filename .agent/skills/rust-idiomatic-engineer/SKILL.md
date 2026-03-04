---
name: rust-idiomatic-engineer
description: Generates high-performance, memory-safe Rust code using modern idioms (2024 Edition).
---

# Rust Expert Protocol

## Core Mandates
1.  **Async Runtime**: Default to `tokio` for all I/O. Use `axum` for web services.
2.  **Error Handling**: `unwrap()` and `expect()` are **FORBIDDEN** in production code.
    - *Pattern*: Use `Result<T, AppError>` and the `?` operator.
    - *Crate*: Use `thiserror` for library errors and `anyhow` for application errors.
3.  **Database**: Use `sqlx` (async) with compile-time query verification.
4.  **Serialization**: Use `serde` with `#[serde(rename_all = "camelCase")]` for JSON APIs.

## "Latest Version" Checklist (Verify via Web)
- Check latest syntax for: `tokio`, `axum`, `sqlx`, `serde`, `tracing`.
