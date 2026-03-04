---
description: Advanced Polars optimization strategies for isolated Wasm sandbox execution.
---

# Polars Performance & Memory Optimization

To guarantee that high-density simulations (10,000+ iterations) do not breach the 10MB memory ceiling of the WebAssembly sandbox, you must strictly adhere to the following Polars optimization rules.

## 1. Lazy Execution Mandatory
Whenever calculating permutations exceeding **1,000 iterations** within `vq_math`, you must strictly construct a `LazyFrame` pipeline.

* **Directive:** Do not perform eager `DataFrame` transformations on large datasets. Always transition to `.lazy()` immediately following ingress.
* **Benefit:** Deferring execution allows the Polars optimizer to prune unused columns and minimize intermediate memory-allocation spikes.

## 2. Boundary Collect Rule
You must defer the `.collect()` execution to the absolute end of the FFI boundary.

* **Directive:** Process all filters, aggregations, and mathematical transformations within the `LazyFrame`.
* **Constraint:** A single `.collect()` should occur only when the final simulation result is required for serialization.

## 3. Memory Hygiene
* Avoid deep copies of `DataFrames`.
* Use `Arc` or reference-counting where appropriate to share static data (e.g., Cap Table constants) across simulation paths.
* If memory usage spikes, perform a layout audit of the `shared_schema` to ensure dtypes are optimal (e.g., using `f32` if `f64` precision is not mathematically required for the specific tranche).
