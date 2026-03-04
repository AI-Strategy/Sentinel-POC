---
description: [Skill for enforcing structured, event-based telemetry across institutional domain boundaries]
---

# Cryptographic Telemetry and Audit Logging Skill

To maintain a perfect, reviewable audit trail without exposing data to external points, follow these commands:

1. **Instrumentation**: You must implement structured, event-based logging using the `tracing` (v0.1) and `tracing-subscriber` (v0.3.22) crates for all module boundary crossings.
2. **Boundary Recording**: Every invocation of the `ProprietaryAlgorithm` trait must record the specific `ScenarioParameter` payload passed and the cryptographic hash of the `ExecutionResult` returned.
3. **Macro Usage**: You must use the `tracing::instrument` macro on all trait methods to automatically capture contextual metadata and state transitions.
4. **Zero-Trust Persistence**: You must define a unified audit trail that writes deterministically to the isolated host environment, strictly ensuring that sensitive telemetry remains within the fiduciary boundary of the H4D node.
