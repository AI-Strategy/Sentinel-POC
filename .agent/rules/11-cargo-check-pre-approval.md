# Terminal rule: cargo check is pre-approved

## Objective
Reduce approval spam by pre-approving safe Rust type-check commands (`cargo check`) for this workspace, while blocking commands that mutate the repo, execute arbitrary shell pipelines, or perform destructive operations.

---

## Allowed Without Asking (Exact Commands)
The agent may run ONLY these terminal commands without requesting approval:

- `cargo check -p vq-api -p vq-ingest`
- `cargo check -p vq-api`
- `cargo check -p vq-ingest`
- `cargo check --workspace`
- `cargo check --workspace --all-targets`
- `cargo check --all-targets`

### Preferred Invocation
Prefer a single command (no shell chaining):

- `cargo check -p vq-api -p vq-ingest`

### Required Flags (when applicable)
- If the repo uses a lockfile, prefer: `--locked`
  - Example: `cargo check -p vq-api -p vq-ingest --all-targets --locked`

---

## Output Handling
After running `cargo check`:
- If it succeeds: report “cargo check passed” and nothing more.
- If it fails: paste a concise summary of errors and include:
  - crate name
  - file path
  - line/column
  - the first relevant compiler message per error

Do not spam full compiler dumps unless asked.

---

## Forbidden Actions (Explicit Approval Required)
Do NOT run these without explicit human approval:

- `cargo update` (mutates `Cargo.lock` and can silently change dependency resolution)
- any command containing `rm` (including `rm -rf` and variants)
- any command using shell chaining or wrappers: `&&`, `;`, `|`, redirects (`>`, `>>`), or `bash -lc` / `sh -c`
- any command using `sudo`
- any command that downloads or executes remote content (`curl`, `wget`, `Invoke-WebRequest`, etc.)
- any publish/install side effects: `cargo publish`, `cargo install`, `cargo clean`
- any command not listed in **Allowed Without Asking**

### Rationale
Try not to let the agent anywhere near `cargo update` or a shell string with `rm` in it, unless you enjoy surprise archaeology in your repo.

---

## Notes / Safety Caveat
`cargo check` does not run your binary, but it can execute build scripts (`build.rs`) and procedural macros during compilation. Therefore, treat `cargo check` as “safe enough for trusted code,” not “safe for random internet code.”
