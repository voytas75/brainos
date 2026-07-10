# BrainOS

BrainOS is a SQLite-first cognitive memory core for LLM agents.

It gives an agent a local, auditable memory system in a single SQLite file, with working memory, episodes, semantic structures, procedures, decisions, provenance, and bounded retrieval diagnostics.

BrainOS is early-stage, experimental, and local-first. It is a storage and retrieval core, not a full agent runtime or hosted platform.

## Why BrainOS

- **One file, not a memory stack zoo** — core agent memory lives in one transactional SQLite database.
- **Auditability by default** — meaningful writes are tracked through a provenance ledger with chained hashes.
- **Local-first by design** — simple to run, inspect, test, and move between environments.

## What it is

BrainOS currently provides:

- a local SQLite memory core
- a Python API and local CLI
- working memory, episodes, semantic nodes/edges, procedures, decisions, and provenance
- bounded retrieval and runtime diagnostics

## What it is not

BrainOS is not:

- a full agent runtime
- a hosted memory platform
- an autonomous workflow engine
- a broad retrieval-quality guarantee across open-ended corpora

## Quick start

Install dependencies:

```bash
uv sync --extra dev
```

Initialize a database:

```bash
uv run brainos --db ./brain.db init
```

Write and read working memory:

```bash
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db wm-get agent_state
```

Add and search an episode:

```bash
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized successfully' --metadata-json '{"source":"manual"}'
uv run brainos --db ./brain.db episode-search BrainOS --limit 5
```

If you want small Python walkthroughs instead of raw CLI snippets, see [`examples/README.md`](examples/README.md).

## 10-minute honest evaluation path

If you want one recommended repo-local walkthrough, run:

```bash
./scripts/canonical_e2e_demo.sh
```

Fallback if your shell cannot run the script directly:

```bash
bash ./scripts/canonical_e2e_demo.sh
```

This produces artifacts under `./artifacts/canonical-e2e/` and classifies the run as:

- `PASS` — the local core path worked and the bounded retrieval/runtime surfaces were green
- `DEGRADED` — the local core path worked, but vector-ready evidence was skipped or unavailable in the current environment
- `FAIL` — a core storage, retrieval, promotion, or ledger check failed

If your local environment is already configured for embeddings and `sqlite-vec`, you can request a stronger vector-ready pass:

```bash
BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC=1 ./scripts/canonical_e2e_demo.sh
```

## Core concepts

BrainOS maps several memory layers into one SQLite database:

- **Working memory** — current operational state
- **Episodes** — searchable session history
- **Semantic memory** — durable knowledge as nodes and edges
- **Procedures** — reusable JSON-defined procedures
- **Decisions** — operator-facing decision records
- **Ledger** — auditable write history with chained hashes

## Documentation map

Use the docs this way:

- read [`docs/canonical-e2e-demo.md`](docs/canonical-e2e-demo.md) for the fastest honest repo walkthrough
- read [`docs/STATUS.md`](docs/STATUS.md) for the current bounded scope
- read [`docs/evidence-map.md`](docs/evidence-map.md) for what is proven vs only bounded evidence
- read [`docs/retrieval-evaluation-scenarios.md`](docs/retrieval-evaluation-scenarios.md) for the canonical bounded scenario set behind current retrieval claims
- read [`docs/api.md`](docs/api.md) for exact Python API and CLI reference
- read [`docs/implementation-notes.md`](docs/implementation-notes.md) for design tradeoffs and spec-gap notes
- read [`docs/README-DEV.md`](docs/README-DEV.md) for runtime, operator, and development details
- read [`docs/retrieval-contract-v1.md`](docs/retrieval-contract-v1.md) and [`docs/retrieval-quality-contract-v1.md`](docs/retrieval-quality-contract-v1.md) for retrieval semantics and evaluation posture
- read [`docs/decision-support-contract-v1.md`](docs/decision-support-contract-v1.md) for the current decision-support contract

## Current status

BrainOS currently provides a coherent local SQLite memory core with Python and CLI surfaces, bounded retrieval diagnostics, promotion flow, and provenance.

The implementation is healthier than the most cautious reading of the docs might imply, but the project should still be read through bounded evidence rather than confidence by vibe.

The main current risks are not broken-code risk. They are bounded evidence, heuristic retrieval behavior, and growing operational/documentation debt.

It does not currently provide server APIs, autonomous runtime behavior, or broad retrieval guarantees across open-ended corpora.
