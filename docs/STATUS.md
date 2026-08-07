# BrainOS Status

This file is the short current-status entrypoint. For the detailed trust map, use [`docs/evidence-map.md`](./evidence-map.md).

## Current bounded scope

BrainOS currently ships as a local SQLite storage and retrieval core with:
- Python API and local CLI
- working memory, episodes, semantic nodes/edges, procedures, decisions, and provenance
- bounded retrieval surfaces: `recall`, `retrieval-explain`, `retrieval-health`, `retrieval-benchmark`, `real-corpus-probe`
- vector maintenance and runtime diagnostics: `vector-index-*`, `capabilities`, `sqlite-vec-readiness`, `embedding-readiness`, `doctor`

BrainOS does not currently ship:
- HTTP, MCP, or other server APIs
- broad retrieval-quality guarantees outside the bounded fixtures and probes
- autonomous decision or execution-loop behavior

## Recommended reading order

1. [`docs/canonical-e2e-demo.md`](./canonical-e2e-demo.md)
2. [`docs/evidence-map.md`](./evidence-map.md)
3. [`docs/retrieval-green-path-smoke-test.md`](./retrieval-green-path-smoke-test.md)
4. [`docs/retrieval-contract-v1.md`](./retrieval-contract-v1.md)
5. [`docs/retrieval-quality-contract-v1.md`](./retrieval-quality-contract-v1.md)

## Honest interpretation rules

- Treat the canonical demo as the fastest local proof path.
- Treat `retrieval-benchmark` as seeded-fixture evidence, not live-corpus proof.
- Treat `real-corpus-probe` as small-sample evidence, not broad quality proof.
- Treat the canonical retrieval scenario set in [`docs/retrieval-evaluation-scenarios.md`](./retrieval-evaluation-scenarios.md) as the current bounded basis for retrieval claims.
- Treat vector-ready success as environment-dependent. If local embedding or `sqlite-vec` config is missing, the repo should be read as degraded rather than broken.
- Treat decision support as operator-facing support, not autonomous choice.

## Current risk framing

The main near-term risks are not that the local core is fundamentally broken.

The heavier risks are:
- bounded evidence that can be over-interpreted if the scenario set is not kept explicit
- heuristic retrieval behavior that can look stronger or weaker than it really is without explain/trace output
- accumulating operational and documentation debt that makes the repo look less healthy than the implementation actually is

## Current checkpoint

Remote stabilization checkpoint:
- locked `aiohttp` at `3.14.3`; Dependabot REST and GraphQL report zero open alerts after a successful dependency-graph run
- added a pinned, frozen CI workflow for lock consistency and tests; its current default-branch run succeeded
- made episode promotion rollback-safe when its durable promotion record fails
- deferred vector-table dimensions to the first successful embedding and kept mismatch detection for later rebuilds
- isolated the degraded-runtime operator acceptance pack from inherited `BRAINOS_SQLITE_VEC_PATH`
- current full local test posture: `138 passed`
- enabled secret scanning with push protection; CodeQL is active and has zero open alerts

`main` requires the strict `Lock and tests` check, including for repository administrators; review approval is not required.

## Supporting detail

- Current runtime and operator notes: [`docs/README-DEV.md`](./README-DEV.md)
- API and CLI reference: [`docs/api.md`](./api.md)
- Historical working notes: [`docs/_archive_working/`](./_archive_working/)
