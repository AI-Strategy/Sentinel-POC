# .agent/rules/rust-hygiene.md
# Rule: Rust Hygiene Gate (anti-fatberg)
#
# Goal:
# - Prevent "small" Rust issues (warnings, fmt drift, clippy nits) from accumulating into a repo-wide mess.
# - Keep the loop fast, deterministic, and safe for an autonomous agent.

## Scope
Applies when any of the following change:
- `**/*.rs`
- `Cargo.toml`, `Cargo.lock`
- `rust-toolchain.toml` (if present)
- `.cargo/**`

## Required Gate (run in this exact order)
1) Format
- Command: `cargo fmt --all`
- Expected: exits 0; may modify files.

2) Fast compile check (cheap signal)
- Command: `cargo check --workspace --all-targets`
- Expected: exits 0 with **no errors**.

3) Lint (treat warnings as build failures for *our* workspace)
- Command:
  `cargo clippy --workspace --all-targets --all-features -- -D warnings`
- Expected: exits 0 with **no warnings**.

4) Tests (default to workspace tests)
- Command: `cargo test --workspace`
- Expected: exits 0.

## Auto-Remediation (allowed without approval)
If any step fails, the agent may attempt the following fixes, in order:

A) Formatting fixes
- Run: `cargo fmt --all`
- Then re-run steps 2–4.

B) Safe compiler/clippy autofix (workspace only)
- Allowed only if:
  - the failure is warnings/lints that clippy can fix, AND
  - changes are limited to Rust source files in this repo (no vendored code), AND
  - total diff is small (<= 200 changed lines).
- Command (choose one):
  - `cargo clippy --workspace --all-targets --all-features --fix --allow-dirty --allow-staged`
  - or `cargo fix --workspace --allow-dirty --allow-staged`
- Then re-run the full gate (steps 1–4).

C) Minimal code edits
- Agent may apply targeted edits to resolve:
  - unused imports/vars
  - clippy “obvious correctness” lints (e.g., needless clones, suspicious comparisons)
  - formatting-related parse issues
- Constraints:
  - No API redesigns.
  - No behavior changes unless required to fix a real bug.
  - No refactors “while we’re here”.

## Escalation (must ask for approval / stop and report)
Stop and report with:
- the exact failing command,
- the first ~80 lines of output,
- the files involved,
- the minimal proposed fix,
when any of the following occur:

1) Dependency changes or network-y actions are required
- Examples: adding/updating crates, regenerating lockfile due to version drift, feature flag redesign.

2) The fix is non-trivial
- Examples: lifetimes/ownership redesign, trait bounds rework, concurrency or unsafe changes.

3) The diff is large
- More than 200 changed lines OR touches more than 10 files.

4) Toolchain mismatch suspected
- Example signals: rustfmt/clippy output changes across runs, rust-analyzer disagrees with CLI results.

## Toolchain determinism
- Prefer a pinned toolchain via `rust-toolchain.toml`.
- If missing, the agent may propose adding a minimal file (requires approval unless explicitly allowed elsewhere):
  ```toml
  [toolchain]
  channel = "stable"
  components = ["rustfmt", "clippy"]
  profile = "minimal"
  ```

## Output handling

* Any gate failure must be treated as a blocker.
* The agent must not “ignore and continue” past warnings.
* After any auto-fix, always rerun the gate until clean or escalation triggers.

## Allowed Commands (auto-approved)

* `cargo fmt --all`
* `cargo check --workspace --all-targets`
* `cargo clippy --workspace --all-targets --all-features -- -D warnings`
* `cargo clippy --workspace --all-targets --all-features --fix --allow-dirty --allow-staged`
* `cargo fix --workspace --allow-dirty --allow-staged`
* `cargo test --workspace`
* `rustc -Vv`, `cargo -V`, `rustfmt -V`, `cargo clippy -V`

## Forbidden Commands (never auto-approved)

* `cargo update` (changes the world under your feet)
* `cargo install`
* `cargo publish`
* `cargo clean` (often hides the real problem)
* any shell pipelines or compound commands (e.g., `... && ...`, `... | ...`)
* any destructive filesystem commands (rm, del, etc.)

## Definition of Done

A change is “ready” only if:

* `cargo fmt --all` produces no further diffs
* `cargo check --workspace --all-targets` succeeds
* `cargo clippy ... -D warnings` succeeds
* `cargo test --workspace` succeeds
