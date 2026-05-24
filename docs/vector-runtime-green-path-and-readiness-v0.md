# Vector runtime green path and readiness v0

## Purpose
This note gives the current operator-facing green path for BrainOS native vector runtime and explains how to classify the most common runtime states.

This is a runtime/runbook note, not an architecture essay.

## Goal
Reach one of two legitimate states:
- `vector-ready`
- `degraded-non-vector`

Anything else should be treated as a setup or runtime problem and classified explicitly.

## Canonical checks
Use these commands in order:

```bash
uv run brainos --db ./brain.db doctor
uv run brainos --db ./brain.db embedding-readiness
uv run brainos --db ./brain.db sqlite-vec-readiness
```

Operator default:
- start with `doctor`
- use `embedding-readiness` when the likely problem is env/config/runtime for embeddings
- use `sqlite-vec-readiness` when you specifically need explicit-path sqlite-vec proof rather than the higher-level operator summary

## Green path

### 1. Run the operator summary first

```bash
uv run brainos --db ./brain.db doctor
```

Read this first because it aggregates the critical operator checks into one place:
- retrieval health
- embedding runtime prerequisites
- sqlite-vec capability
- SQLite WAL posture
- critical dependencies

Desired healthy signals:
- `status: ok`
- `failed_checks: []`
- `checks.embedding_runtime: true`
- `checks.sqlite_vec_capability: true`

If `doctor` warns, use the nested sections to classify the failure before going deeper.

### 2. Check embedding runtime prerequisites when doctor points there

```bash
uv run brainos --db ./brain.db embedding-readiness
```

Use this when the likely problem is missing env/config rather than retrieval quality.

Desired healthy signals:
- `status: ok`
- no missing Azure embedding env
- `BRAINOS_SQLITE_VEC_PATH` configured correctly when vector runtime is expected
- critical dependency path available

### 3. Configure explicit sqlite-vec path when needed

Required env:
- `BRAINOS_SQLITE_VEC_PATH`

Example:

```bash
export BRAINOS_SQLITE_VEC_PATH="/path/to/vec0.so"
```

BrainOS currently expects an explicit loadable sqlite-vec extension path when `vec0` is not already available in the runtime.

### 4. Run readiness check

```bash
uv run brainos --db ./brain.db sqlite-vec-readiness
```

Expected success shape:
- `ok: true`
- `path: <resolved extension path>`
- `rows: [...]`

Expected failure shape:
- `ok: false`
- `error: <human-readable summary>`
- `error_kind: <stable classification>`
- `detail: <short operator hint>`

This check does more than capability detection:
- loads the extension
- creates a temporary vec table
- inserts sample rows
- runs a vector match query

So this is the real runtime-readiness check, not just a config echo.

### 5. Check retrieval health interpretation when you need the full retrieval/freshness/quality view

```bash
uv run brainos --db ./brain.db retrieval-health
```

Interpretation:
- `runtime.status=ok` → vector capability path is healthy
- `runtime.status=warn` → runtime capability/setup issue is present
- `runtime.embedding_config` / `runtime.sqlite_vec_env` now expose the most important prereq failures directly
- `quality.status=degraded` → retrieval quality output is being reported from a legitimate degraded non-vector path
- `quality.status=warn` → benchmark is not green in a non-degraded path

## Runtime state classification

### State A — vector-ready
Criteria:
- `capabilities.sqlite_vec=true`
- `capabilities.sqlite_vec_loaded=true`
- `sqlite-vec-readiness.ok=true`

Meaning:
- sqlite-vec is available and loadable
- BrainOS can use native vector storage/retrieval paths
- retrieval benchmark/health should be interpreted as vector-capable signals

### State B — degraded-non-vector
Criteria:
- BrainOS initializes and runs
- recall still works
- sqlite-vec capability is unavailable or not configured
- retrieval health/benchmark reports degraded mode explicitly

Meaning:
- this is a legitimate fallback operating mode
- retrieval quality may be reduced
- product behavior should still remain usable

### State C — setup failure
Examples:
- `sqlite-vec-readiness` fails because `BRAINOS_SQLITE_VEC_PATH` is unset
- configured path is wrong or unloadable
- extension load fails before readiness succeeds

Meaning:
- runtime is not vector-ready
- degraded mode may still be valid for BrainOS overall
- operator should fix path/config before expecting vector behavior

### State D — freshness/data issue
Examples:
- `retrieval-health.freshness.status=warn`
- stale vectors present
- vector errors present in index state

Meaning:
- runtime may be fine
- problem is with vector freshness/state, not capability loading itself

### State E — freshness incomplete but not broken
Examples:
- `retrieval-health.freshness.status=ok`
- `retrieval-health.freshness.notes` includes `missing_vectors_present`
- `retrieval-health.freshness.notes` includes `disabled_vectors_present`

Meaning:
- the vector index is not fully populated or is capability-gated for some objects
- this should stay visible to operators, but it is not the same class of signal as stale/error freshness failure

## Common failure classes

### 1. Missing sqlite-vec path
Observed signal:
- `sqlite-vec-readiness` returns:
  - `error_kind="path_not_configured"`
  - `error="sqlite-vec path not configured; set BRAINOS_SQLITE_VEC_PATH"`

Interpretation:
- setup failure
- fix env/path first

### 2. Extension load failure
Observed signal:
- `sqlite-vec-readiness` returns:
  - `error_kind="extension_load_failed"`

Interpretation:
- configured path exists but sqlite cannot load it correctly
- treat as runtime/setup failure

### 3. vec0 unavailable in capability check
Observed signal:
- `capabilities.sqlite_vec=false`
- `capabilities.sqlite_vec_error="no such module: vec0"`

Interpretation:
- runtime cannot use sqlite-vec natively in the current environment
- either configure explicit extension loading or accept degraded mode

### 4. Readiness probe failure after load
Observed signal:
- `sqlite-vec-readiness` returns:
  - `error_kind="readiness_probe_failed"`

Interpretation:
- sqlite-vec may have loaded, but the actual temp-table/probe flow did not succeed
- treat as a runtime-readiness failure, not a quality failure

### 5. Benchmark not green in degraded mode
Observed signal:
- `retrieval-benchmark.mode=degraded-non-vector`
- `retrieval-health.quality.status=degraded`

Interpretation:
- do not read this as the same class of failure as a vector-ready benchmark regression
- first resolve runtime posture if vector-capable evaluation is required

### 6. Benchmark not green in vector-ready mode
Observed signal:
- `retrieval-benchmark.mode=vector-ready`
- `retrieval-health.quality.status=warn`

Interpretation:
- treat as a retrieval quality/regression signal, not a runtime fallback artifact


## Practical operator rule
Always classify problems in this order:
1. `doctor`
2. embedding/runtime prereqs when flagged
3. explicit sqlite-vec readiness success/failure
4. freshness state
5. benchmark/quality signal

Do not start with benchmark interpretation before runtime posture is known.

## Current evidence on this host/session
Observed during this review:
- `capabilities` returned `sqlite_vec=false`
- `sqlite_vec_error="no such module: vec0"`
- `sqlite-vec-readiness` failed when `BRAINOS_SQLITE_VEC_PATH` was not configured

This confirms that the current docs must treat explicit path configuration and degraded-mode interpretation as first-class operational concerns.


## Readiness interpretation hints

Current readiness output now includes a small `action_hint` field.

Current meanings:
- `noop` → runtime/readiness looks good; no immediate repair action implied
- `runtime_fix` → fix sqlite-vec path/load/runtime posture first
- `retry_or_runtime_fix` → probe failure may be transient or still indicate runtime/setup trouble

This field is intentionally advisory and bounded. It is not an automation contract.


## Ambient vs explicit runtime posture

Current contract reference:
- `docs/runtime-posture-contract-v1.md`

In short:
- `capabilities` reports ambient process posture
- `sqlite-vec-readiness` reports explicit configured-path readiness
- these may differ legitimately until ambient availability is established
