---
description: [Workflow for implementing and managing Wasm sandboxing for proprietary client math]
---

# Wasm Sandbox Implementation Workflow

When generating or modifying the `client_integrations` crate, you must adhere to the following strict procedural steps:

1. **Target Specification**: You must compile all external mathematical models to the `wasm32-wasip1` target.
2. **Runtime Locking**: You must instantiate the WebAssembly runtime using `wasmtime` (targeted at v42.0.0).
3. **Resource Gating**:
    - You must configure `wasmtime::Config` to strictly limit memory allocation to a maximum of 10MB using the `StoreLimits` mechanism.
    - You must restrict execution epochs via the `.consume_fuel(true)` directive.
4. **Error Handling**: Any panic, out-of-bounds memory access, or timeout within the Wasm module must return a strictly typed `ExecutionError` (e.g., `Timeout`, `MemoryExhaustion`) and immediately terminate the sandbox instance.
5. **Security Perimeter**: You must ensure that no system-level interfaces (WASI) are granted to the guest beyond basic deterministic data ingestion via linear memory.
