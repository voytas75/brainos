# sqlite-vec runtime posture contract v1

## Purpose

This document defines the current `sqlite-vec` runtime interpretation for BrainOS. It is an operator contract, not proof that vector retrieval is broadly healthy.

## Authority

The implementation anchors are `src/brainos/sqlite_vec.py` and `src/brainos/schema.py`. If this document conflicts with those sources or their tests, code and tests win until this contract is corrected.

## Explicit-path only

BrainOS does **not** probe ambient `sqlite-vec` availability. A usable vector runtime requires an explicit `BRAINOS_SQLITE_VEC_PATH`.

- No configured path → `sqlite_vec=false` with runtime origin `disabled_without_explicit_path`.
- Configured path → BrainOS attempts to load that exact extension path and run a temporary vec0 probe.
- Load or probe failure → `sqlite_vec=false` with the reported runtime error.

This avoids treating inherited extensions or host-specific ambient state as BrainOS configuration.

## Surfaces

### `capabilities`

`brainos capabilities` reports the capability posture for the current process. Its `sqlite_vec_runtime_origin` is either:

- `explicit_path`
- `disabled_without_explicit_path`

It never claims an ambient probe result.

### `sqlite-vec-readiness`

`brainos sqlite-vec-readiness` loads the configured extension path and exercises a temporary vec0 table with a small query.

- `ok=true` means the configured path loaded and the readiness probe completed.
- `path_not_configured`, `extension_load_failed`, and `readiness_probe_failed` identify the relevant failure class.

### Diagnostics

`embedding-readiness`, `retrieval-health`, and `doctor` expose runtime context and remediation hints. They are local diagnostics: they do not run `retrieval-benchmark` or an embedding provider.

## Operator rule

1. Run `sqlite-vec-readiness` to validate an explicitly configured extension.
2. Read `capabilities` and diagnostic runtime fields for the process posture.
3. Interpret retrieval quality only through an explicit `retrieval-benchmark` run and its bounded evidence contract.

## Stability note

Keep this contract aligned with explicit-path-only behavior. Any future ambient-probe design requires an intentional code, test, and contract change.