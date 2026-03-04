---
description: How to evaluate Wasm sandbox latency and throughput.
---

# Wasm Performance Benchmarking

To ensure that the institutional sandbox remains within the performance envelope required for high-frequency simulation, you must periodically profile the execution latency.

## Prerequisites

1. The institutional sample module must be compiled:
   ```bash
   cargo build --package talos_client_sample --target wasm32-wasip1 --release
   ```

2. Gnuplot (optional) should be installed for high-fidelity trend visualization.

## Execution

To evaluate sandbox latency, execute the following command:

```bash
cargo bench -p execution_engine
```

## Telemetry Review

1. Locate the generated HTML report:
   `target/criterion/report/index.html`
2. **Acceptance Criteria:** The execution time of `execute_proprietary_model` must not exceed **5 milliseconds**.
3. If the performance envelope is breached, you must halt further commits and perform a memory layout audit of the `shared_schema` crate.
