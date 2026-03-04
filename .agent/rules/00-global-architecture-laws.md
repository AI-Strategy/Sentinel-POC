name
  global-architecture-laws
description
  Enforces strict modularity, zero-trust security, and web-first grounding.
alwaysApply
  true

# Global Architecture Laws (STRICT ENFORCEMENT)
1. **Web-First Grounding (Critical)**: Legacy training data is deprecated. You MUST perform a Google Search via the browser tool before citing syntax for:
   - **Python 3.13+** / **Rust 2024 Edition**
   - **Neo4j 5.x+** (Vector Indexes & GDS)
   - **React 19+** (Server Components & Actions)
2. **Zero-Trust Mandate**: EVERY memory retrieval or API endpoint MUST utilize the `verify_passkey_token` middleware. 
   - If a token is missing/expired: **Fail Closed** (HTTP 401). 
   - Never bypass authentication for "debugging."
3. **Strict Modularity**: NEVER mix database logic. 
   - `Synaptic` (Redis), `Cortical` (Postgres), and `Deep` (Neo4j) logic must remain exclusively in their respective `/src` directories.
4. **No REGEX (Last Resort)**: Use `Gemini 2.5 Flash` (or equivalent small LLM) for complex text parsing. 
   - *Exception*: Regex is permitted ONLY if latency/cost is critical and the pattern is explicitly documented.
5. **Deterministic Citations**: All narrative outputs must return a mathematically retrieved `source_uuid`. Hallucinations trigger the TalosCore Kill-Switch.
