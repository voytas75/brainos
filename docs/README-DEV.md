# BrainOS development and operator notes

This document holds the more detailed technical and operational material that would otherwise make the top-level README too heavy.

## Who this document is for

Use this file if you need:
- runtime diagnostics
- smoke-test details and artifact paths
- embedding and `sqlite-vec` configuration notes
- operator-oriented CLI behavior expectations

If you want the project overview, quick start, or repo map, go back to `../README.md`.

## Document map

- [Canonical demo](#canonical-demo)
- [Evidence map](#evidence-map)
- [Retrieval evaluation scenarios](#retrieval-evaluation-scenarios)
- [Diagnostic CLI contract](#diagnostic-cli-contract-verified)
- [Smoke tests](#smoke-tests)
- [CLI error behavior](#cli-error-behavior)
- [Promotion audit](#promotion-audit)
- [Vector metadata status](#vector-metadata-status)
- [Embedding execution adapter status](#embedding-execution-adapter-status)
- [LiteLLM embedding provider configuration](#litellm-embedding-provider-configuration)
- [`sqlite-vec` runtime configuration](#sqlite-vec-runtime-configuration)

## Canonical demo

If you need one honest walkthrough first, run:

```bash
./scripts/canonical_e2e_demo.sh
```

This produces one artifact directory under `artifacts/canonical-e2e/` and reports `PASS`, `DEGRADED`, or `FAIL` without pretending vector-ready evidence exists when the local environment is not configured for it.

Optional stronger vector-ready pass:

```bash
BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC=1 ./scripts/canonical_e2e_demo.sh
```

## Evidence map

Use [`docs/evidence-map.md`](./evidence-map.md) when you need the shortest answer to:
- what is directly proven here
- what is only bounded evidence
- what remains intentionally unproven

## Retrieval evaluation scenarios

Use [`docs/retrieval-evaluation-scenarios.md`](./retrieval-evaluation-scenarios.md) when you need the canonical bounded scenario set behind current retrieval claims.

This is the small review surface that keeps BrainOS from over-claiming retrieval quality based on a few good demos or a few bad impressions.

## Diagnostic CLI contract (verified)

BrainOS exposes operator-oriented diagnostic commands that prefer structured JSON over tracebacks.

### Commands

- `doctor`
- `retrieval-health`
- `embedding-readiness`
- `sqlite-vec-readiness`
- `capabilities`
- `decision-log`
- `decision-list`
- `decision-get`
- `decision-check`
- `decision-history`
- `inspect`
- `retrieval-explain`

`retrieval-explain` is the main operator surface for understanding why a result appeared. It should be used before declaring a quality regression, because many apparent failures are really runtime drift, low evidence, or heuristic edge cases.

### Expected response shape

#### Success path

- `status: "ok"` or `ok: true`
- `action_hint: "noop"`

#### Degraded runtime path

- usually `status: "warn"`
- sometimes `ok: false` on readiness-style commands
- machine-readable fields such as `error_kind`, `detail`, `action_hint`
- normal operator handling should not depend on traceback parsing

### `sqlite-vec` runtime terminology

Two related surfaces are exposed intentionally.

#### 1. Capability probe (`capabilities`)

Field:
- `sqlite_vec_runtime_origin`

Current values:
- `explicit_path`
- `disabled_without_explicit_path`

Meaning:
- BrainOS capability probing only treats `sqlite-vec` as active when there is an explicit configured path
- without explicit configuration, ambient probing is disabled on purpose

#### 2. Env health (`embedding-readiness`, `doctor`, `retrieval-health`)

Fields:
- `sqlite_vec_env.runtime_origin`
- `sqlite_vec_env.configured`

Current `runtime_origin` values:
- `explicit_configured`
- `ambient_detected`
- `not_configured`

Meaning:
- `configured = true` only for explicit intended configuration
- `ambient_detected` means a foreign or runtime-inherited `sqlite-vec` path was seen, but BrainOS does not treat it as the intended active configuration

### How to read `recommended_fix` and `next_debug`

#### `recommended_fix`

The most direct operator next move for the current degraded path.

For `sqlite-vec` runtime issues this currently points to:
- `action_hint: "configure_sqlite_vec_path"`
- `target: "BRAINOS_SQLITE_VEC_PATH"`

#### `next_debug`

The next diagnostic handoff when the system has enough runtime to inspect retrieval quality.

Current retrieval benchmark failures point to:
- `retrieval-explain`

### Example commands

```bash
uv run brainos --db ./brain.db capabilities
uv run brainos --db ./brain.db sqlite-vec-readiness
uv run brainos --db ./brain.db embedding-readiness
uv run brainos --db ./brain.db retrieval-health --benchmark-limit 5
uv run brainos --db ./brain.db doctor --benchmark-limit 5
```

## Smoke tests

### Canonical bounded demo

Run the main evaluation path:

```bash
./scripts/canonical_e2e_demo.sh
```

Output artifacts:
- `artifacts/canonical-e2e/`
- `artifacts/canonical-e2e/summary.json`

### Storage-core smoke test

Run the original storage-core smoke test:

```bash
./scripts/e2e_smoke.sh
```

Output artifact:
- `artifacts/e2e-summary.json`

### Retrieval green-path smoke test

Run the bounded retrieval and runtime smoke test:

```bash
source .env
./scripts/retrieval_smoke.sh
```

Output artifacts:
- `artifacts/retrieval-smoke/`
- `artifacts/retrieval-smoke/summary.json`

Purpose:
- verify retrieval runtime green path on a fresh DB
- verify vector sync plus `recall`, `retrieval-explain`, and `retrieval-health`
- catch env/runtime regressions that can otherwise look like ordinary retrieval failure

Interpretation:
- `PASS` = runtime ready and at least one ranked retrieval hit returned
- `FAIL` = runtime or env broken, or no ranked hit on the bounded corpus
- this is **not** a broad retrieval-quality benchmark

### Operator acceptance pack

Run the bounded operator-interpretation pack:

```bash
./scripts/operator_acceptance.sh
```

Output artifacts:
- `artifacts/operator-acceptance/`
- `artifacts/operator-acceptance/summary.json`

Purpose:
- verify runtime issues are classified before quality interpretation
- verify empty DB low-evidence behavior remains explicit
- verify degraded runtime messaging still preserves lexical fallback interpretation
- verify direct fix hints survive degraded runtime paths

Interpretation:
- `PASS` = the current operator-facing degraded/runtime semantics match the bounded acceptance scenarios
- `FAIL` = at least one expected runtime/degraded interpretation contract drifted
- this is an operator interpretation pack, **not** a retrieval-quality benchmark

## CLI error behavior

For expected user-facing errors such as not found, invalid promotion metadata, or duplicate promotion, the CLI exits with code `2` and returns a compact JSON error object on stderr.

## Promotion audit

To inspect whether a specific episode was already promoted:

```bash
uv run brainos --db ./brain.db episode-promotion-get <episode-id>
```

## Vector metadata status

Current codebase includes:
- vector metadata lifecycle table
- embedding profile contract surface
- stale and missing tracking for embeddable objects
- episode and semantic-node embedding generation paths
- vector sync commands for `missing`, `stale`, `error`, and `disabled` states
- bounded vector participation in retrieval when runtime readiness permits it

It does **not** claim:
- always-on vector readiness on every machine
- broad retrieval quality proof beyond the bounded fixtures/probes
- background vector maintenance outside the explicit operator commands

## Embedding execution adapter status

Current code includes a real LiteLLM-based embedding adapter boundary.

### What exists now

- logical embedding profile contract
- environment-based Azure and LiteLLM resolution
- execution path for episode embedding generation
- execution path for semantic-node embedding generation
- vector metadata updates to `fresh` or `error`
- bounded `sqlite-vec` storage when capability is available

### What is still not implemented

- batch refresh workflows
- hosted embedding services owned by BrainOS
- background workers for continuous vector maintenance

## LiteLLM embedding provider configuration

BrainOS uses LiteLLM as the execution adapter for embeddings.
Current default and tested operational target: Azure embeddings.

### Primary BrainOS config entry

- `BRAINOS_EMBEDDING_MODEL` — provider-prefixed model or deployment name passed to LiteLLM

Provider is resolved from the model prefix, for example:
- `azure/<your-embedding-deployment>`
- `openai/text-embedding-3-small`
- `ollama/nomic-embed-text`
- `bedrock/<provider-specific-model>`
- `vertex_ai/<provider-specific-model>`

### Embedding provider matrix

| Provider path | Model example | Required env | Optional env | Current posture | Notes |
| --- | --- | --- | --- | --- | --- |
| Azure OpenAI | `azure/<deployment>` | `BRAINOS_EMBEDDING_MODEL`, `AZURE_API_BASE`, `AZURE_API_KEY`, `AZURE_API_VERSION` | `BRAINOS_EMBEDDING_PROVIDER` | tested + backward-compatible | Current default and tested path. Uses Azure compatibility env aliases. |
| OpenAI | `openai/text-embedding-3-small` | `BRAINOS_EMBEDDING_MODEL`, `OPENAI_API_KEY` | `BRAINOS_EMBEDDING_PROVIDER`, `BRAINOS_EMBEDDING_API_BASE`, `BRAINOS_EMBEDDING_API_VERSION` | tested | Best simple non-Azure path today. |
| Ollama | `ollama/nomic-embed-text` | `BRAINOS_EMBEDDING_MODEL` | `BRAINOS_EMBEDDING_PROVIDER`, `BRAINOS_EMBEDDING_API_BASE` | documented, not yet verified here | Usually pair with a local Ollama endpoint such as `http://localhost:11434`. |
| OpenAI-compatible endpoint | `openai/<model-name>` | `BRAINOS_EMBEDDING_MODEL` | `BRAINOS_EMBEDDING_API_BASE`, `BRAINOS_EMBEDDING_API_KEY`, `BRAINOS_EMBEDDING_API_VERSION` | best-effort/custom | Use when the backend speaks OpenAI-style embeddings but is not OpenAI itself. |
| Other LiteLLM provider prefix | `bedrock/...`, `vertex_ai/...`, `gemini/...`, etc. | `BRAINOS_EMBEDDING_MODEL` | provider-specific env and/or generic `BRAINOS_EMBEDDING_*` env | experimental posture | BrainOS passes through the provider-prefixed model and validates only currently implemented provider families explicitly. |

### Public BrainOS config contract

Preferred BrainOS-facing config surface:
- `BRAINOS_EMBEDDING_MODEL`
- `BRAINOS_EMBEDDING_PROVIDER` (optional override)
- `BRAINOS_EMBEDDING_API_BASE` (optional generic endpoint)
- `BRAINOS_EMBEDDING_API_KEY` (optional generic key)
- `BRAINOS_EMBEDDING_API_VERSION` (optional, only where relevant)
- `BRAINOS_EMBEDDING_HEADERS_JSON` (reserved advanced surface)

Compatibility aliases currently preserved:
- `AZURE_API_BASE`
- `AZURE_API_KEY`
- `AZURE_API_VERSION`
- `OPENAI_API_KEY`

### Azure compatibility path

Required environment variables:
- `BRAINOS_EMBEDDING_MODEL`
- `AZURE_API_BASE`
- `AZURE_API_KEY`
- `AZURE_API_VERSION`

Example `.env`:

```dotenv
BRAINOS_EMBEDDING_MODEL="azure/<your-embedding-deployment>"
AZURE_API_BASE="https://<your-resource>.openai.azure.com"
AZURE_API_KEY="***"
AZURE_API_VERSION="2024-10-21"
```

### OpenAI path

Required environment variables:
- `BRAINOS_EMBEDDING_MODEL`
- `OPENAI_API_KEY`

Example `.env`:

```dotenv
BRAINOS_EMBEDDING_MODEL="openai/text-embedding-3-small"
OPENAI_API_KEY="***"
```

### Ollama path

Minimal local example:

```dotenv
BRAINOS_EMBEDDING_MODEL="ollama/nomic-embed-text"
BRAINOS_EMBEDDING_API_BASE="http://localhost:11434"
```

### OpenAI-compatible endpoint path

Example for a custom endpoint exposing OpenAI-style embeddings:

```dotenv
BRAINOS_EMBEDDING_MODEL="openai/<your-model-name>"
BRAINOS_EMBEDDING_API_BASE="https://<your-endpoint>/v1"
BRAINOS_EMBEDDING_API_KEY="***"
```

Shell environment variables still override `.env` when you need a temporary test override.

### Notes

- BrainOS keeps provider specifics out of store and domain logic.
- `brainos-embedding-default` is the logical profile resolved through LiteLLM.
- Azure env names remain supported as the current backward-compatible path.
- Current explicit health and readiness validation is strongest for Azure and OpenAI.
- Other provider prefixes are intended to pass through LiteLLM, but should be treated as best-effort until explicitly verified in this repo.
- If `sqlite-vec` is unavailable, embedding execution may still succeed but vector storage is marked `disabled`.
- If no provider-prefixed model or explicit provider is configured yet, the embedding contract should report `operational_provider: unknown` rather than pretending a configured backend exists.

## Runtime interpretation truth table

| Surface | What it tells you | What it does **not** tell you | Normal next move when degraded/red |
| --- | --- | --- | --- |
| `capabilities` | Whether ambient/explicit sqlite-vec capability is available to the current process | Whether embeddings are configured correctly; whether retrieval quality is good | If `sqlite_vec=false`, inspect `BRAINOS_SQLITE_VEC_PATH` and compare with readiness |
| `sqlite-vec-readiness` | Whether BrainOS can explicitly load the configured sqlite-vec path and run a probe | Whether the retrieval layer is relevant or high quality | Fix configured path / runtime loading first |
| `embedding-readiness` | Whether embedding config, dependencies, and sqlite-vec prerequisites look operationally ready | Whether a provider call already succeeded on this corpus | Set missing env, fix invalid env, or resolve dependency/runtime issues |
| `retrieval-health.runtime` | The current runtime posture: dependencies, sqlite-vec env, embedding config, DB runtime | Whether benchmark results imply broad retrieval maturity | Classify runtime issues before reading quality failures |
| `retrieval-health.freshness` | Whether vector index state is fresh, stale, missing, disabled, or error-marked | Whether ranking policy itself regressed | Reindex/repair if stale or error-heavy; do not confuse with scoring drift |
| `retrieval-benchmark` | Small bounded quality signal on protected benchmark cases | Proof of broad live-corpus retrieval quality | Read together with runtime posture, freshness posture, and mode |
| `real-corpus-probe` | Small sample evidence from available live-ish corpus data | Broad quality proof or stable regression baseline | Use as supporting evidence, not as the only ranking truth |

### Practical reading order

1. `sqlite-vec-readiness` for explicit-path truth
2. `capabilities` / `retrieval-health.runtime` for current process/runtime posture
3. `retrieval-health.freshness` for maintenance/data-state interpretation
4. `retrieval-benchmark` mode and pass/fail
5. `retrieval-explain` for hit-level diagnosis

### Important semantic rules

- `degraded` does **not** automatically mean `broken`.
- `low_evidence` does **not** mean `quality regression`.
- `operational_provider: unknown` means the provider is not yet inferable/configured, not that Azure/OpenAI is failing silently.
- Runtime/setup failures should be fixed before treating bounded benchmark output as a ranking problem.

## `sqlite-vec` runtime configuration

BrainOS can load `sqlite-vec` explicitly when the runtime does not expose `vec0` by default.

### Required environment variable

- `BRAINOS_SQLITE_VEC_PATH`

Example `.env` value:

```dotenv
BRAINOS_SQLITE_VEC_PATH="/absolute/path/to/sqlite-vec/vec0.so"
```

Environment loading contract:
- BrainOS starts lookup from the database directory.
- If no `.env` exists there, it walks upward through parent directories.
- The first `.env` found wins.
- Existing process env still overrides `.env` values unless explicit override is requested.

### Verification commands

```bash
uv run brainos --db ./brain.db capabilities
uv run brainos --db ./brain.db sqlite-vec-readiness
```

### Expected healthy result

- `sqlite_vec: true`
- `sqlite_vec_loaded: true`
- readiness `ok: true`

If `sqlite-vec-readiness` fails because `BRAINOS_SQLITE_VEC_PATH` is unset, treat that as a setup failure, not a generic retrieval failure.
