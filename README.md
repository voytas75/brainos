# BrainOS

BrainOS is a SQLite-first cognitive memory core for LLM agents.

It gives an agent a local, auditable, multi-layer memory system in a single SQLite file: working memory, episodic memory, semantic memory, procedural memory, decision support, provenance, and bounded retrieval diagnostics.

In practice, BrainOS helps you keep agent memory local, inspectable, and portable without standing up a multi-service memory stack.

**Project stage:** early-stage, experimental, and local-first.

**Current scope:** BrainOS is a local storage and retrieval core, not a full agent runtime or hosted platform.

## Why BrainOS is different

- **One file, not a memory stack zoo** — core agent memory lives in one transactional SQLite database, with fewer moving parts to provision and debug.
- **Auditability by default** — meaningful writes are tracked through a provenance ledger with chained hashes, so state changes stay inspectable.
- **Built for local-first agent work** — simple to run, test, inspect, and carry between environments without extra service glue.

## Why this exists

Many agent-memory architectures split state across multiple services and runtime layers. BrainOS takes the opposite approach: keep the core memory model in one transactional SQLite database.

That gives:
- deterministic local behavior
- low infrastructure cost
- ACID transactions
- simple portability
- easy local testing and inspection

## Who this is for

BrainOS is for people building local or operator-facing LLM systems who want:
- one-file memory storage
- explicit audit and provenance trails
- a pragmatic storage core before a larger runtime platform

Good fit:
- local-first experimentation
- bounded production-style memory slices
- operator-facing systems that need inspectable state

## What BrainOS is not

BrainOS is not:
- a full agent runtime
- a hosted memory platform
- a broad retrieval-science platform
- a workflow engine for autonomous execution

## Current status

### Implemented now

- single-file SQLite database (`brain.db`)
- WAL mode and foreign keys
- JSON validation on JSON-bearing columns
- working memory (`wm`)
- episodic memory (`episodes`, `episodes_fts`)
- semantic memory (`semantic_nodes`, `semantic_edges`)
- procedural memory (`procedures`)
- decision support objects (`decisions`)
- immutable provenance ledger (`ledger`)
- bounded retrieval/runtime surfaces (`recall`, `retrieval-explain`, `retrieval-health`, `retrieval-benchmark`, `real-corpus-probe`)
- vector maintenance and readiness surfaces (`vector-index-*`, `capabilities`, `sqlite-vec-readiness`, `embedding-readiness`, `doctor`)
- Python API
- CLI
- tests and smoke checks

### Not implemented yet

- broad retrieval guarantees beyond the current bounded recall/explain/ranking slices
- full cognitive execution loop from the source PDF
- broad migration framework beyond the current hardening baseline
- HTTP/MCP/server APIs

## Quick start

### 1. Install dependencies

```bash
uv sync --extra dev
```

### 2. Optional local environment

Core storage flows work without a `.env` file.
If you want retrieval/vector diagnostics that depend on embeddings or `sqlite-vec`, provide local env configuration first.

### 3. Initialize a database

```bash
uv run brainos --db ./brain.db init
```

### 4. Write and read working memory

```bash
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db wm-get agent_state
```

### 5. Add and search an episode

```bash
uv run brainos --db ./brain.db episode-add session-1 'Agent initialized successfully' --metadata-json '{"source":"manual"}'
uv run brainos --db ./brain.db episode-search Agent --limit 5
```

### 6. Run a minimal test

```bash
uv run pytest tests/test_brainos.py -q
```

## Example workflow

```bash
uv run brainos --db ./brain.db init
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized' --metadata-json '{"source":"smoke"}'
uv run brainos --db ./brain.db recall BrainOS --session-id session-1 --limit 5
uv run brainos --db ./brain.db ledger
```

## Memory model

BrainOS maps multiple memory layers into one SQLite database:

- **Working memory** — short-lived runtime state
- **Episodic memory** — session events and searchable history
- **Semantic memory** — nodes, edges, and durable knowledge structure
- **Procedural memory** — JSON-defined reusable procedures
- **Decision support** — operator-facing decision briefs and history
- **Provenance ledger** — auditable write history with chained hashes

### Working memory in practice

Working memory is for small, current operational state that higher-level agent logic may need to read or update between steps.

Typical uses:
- current mode such as `ready`, `busy`, `paused`, or `error`
- active task or step checkpoint
- short-lived control flags
- small local runtime context worth persisting across process boundaries or restarts

`wm-set` and `wm-get` are storage primitives, not an autonomous control loop.
BrainOS stores the value and records the write in the ledger, but it does not automatically interpret keys such as `agent_state` unless a higher-level application, wrapper, or orchestrator is explicitly written to do so.

Use working memory when you need a compact shared state like “what is happening now”.
Do not use it as a substitute for episodic history, durable semantic knowledge, or large document storage.

## Project structure

- `src/brainos/` — core package
- `src/brainos/schema.py` — schema and initialization
- `src/brainos/store.py` — storage API
- `src/brainos/cli.py` — CLI entrypoint
- `src/brainos/ledger.py` — canonical JSON and hash helpers
- `tests/` — test suite
- `scripts/` — smoke scripts
- `docs/api.md` — Python API and CLI reference
- `docs/implementation-notes.md` — design decisions and spec-gap notes
- `docs/README-DEV.md` — deeper development and operator notes

## Main commands

Representative CLI commands:

- lifecycle: `init`, `schema-status`, `capabilities`
- working memory: `wm-set`, `wm-get`
- episodic memory: `episode-add`, `episodes-list`, `episode-search`, `recall`
- promotion flow: `consolidation-preview`, `promote-episode`, `episode-promotion-get`
- semantic memory: `semantic-node-upsert`, `semantic-node-get`, `semantic-edge-upsert`, `semantic-edges-list`
- procedures: `procedure-create`, `procedure-list`, `procedure-get`
- decision support: `decision-log`, `decision-list`, `decision-get`, `decision-check`, `decision-history`
- inspection and audit: `inspect`, `ledger`, `ledger-verify`

For the full command surface and arguments, see `docs/api.md`.

## Python usage

```python
from brainos import BrainOSStore

store = BrainOSStore("brain.db")
store.initialize()

store.set_working_memory("agent_state", {"mode": "ready"})
store.add_episode(
    session_id="session-1",
    content="Agent initialized successfully",
    metadata={"source": "bootstrap"},
)
store.upsert_semantic_node(
    node_id="n1",
    name="SQLite",
    node_type="Concept",
    properties={"role": "storage"},
)

results = store.search_episodes_text("initialized")
print(results)

store.close()
```

## Development verification

Run a minimal verification path:

```bash
uv run pytest tests/test_brainos.py -q
uv run brainos --db ./brain.db init
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized with WAL and ledger' --metadata-json '{"source":"smoke"}'
uv run brainos --db ./brain.db episode-search BrainOS --limit 5
uv run brainos --db ./brain.db ledger
```

## 10-minute evaluation path

If you want one honest repo-local walkthrough, run:

```bash
./scripts/canonical_e2e_demo.sh
```

If your shell cannot run the script directly, use:

```bash
bash ./scripts/canonical_e2e_demo.sh
```

This produces `./artifacts/canonical-e2e/summary.json` and classifies the result as `PASS`, `DEGRADED`, or `FAIL`.

- `PASS` means the local core path is working and the bounded retrieval/runtime surfaces are green on this machine.
- `DEGRADED` means the core path worked, but vector-ready evidence was skipped or unavailable in the current environment.
- `FAIL` means a core storage, retrieval, promotion, or ledger check broke.

If you already have embedding and `sqlite-vec` env configured and want stronger vector-ready evidence, run:

```bash
BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC=1 ./scripts/canonical_e2e_demo.sh
```

## Design notes

The source BrainOS PDF describes a larger target architecture, but the available excerpt is incomplete in important places, especially around execution flow and `sqlite-vec` operational details.

This repository therefore implements the durable local storage core first.

One explicit implementation decision:
- the PDF narrative implies cryptographic chaining, but the shown ledger DDL did not include an explicit link field
- this implementation adds `previous_hash` to make the chain explicit and verifiable

## Documentation map

Use the docs this way:
- start with `README.md` for project overview and quick start
- read [`docs/canonical-e2e-demo.md`](docs/canonical-e2e-demo.md) for the fastest honest repo walkthrough
- read [`docs/evidence-map.md`](docs/evidence-map.md) for what is proven vs only bounded evidence
- read [`docs/api.md`](docs/api.md) for exact Python API and CLI reference
- read [`docs/implementation-notes.md`](docs/implementation-notes.md) for design tradeoffs and spec-gap notes
- read [`docs/README-DEV.md`](docs/README-DEV.md) for runtime, operator, and development details
- read [`docs/STATUS.md`](docs/STATUS.md) for the concise current project status
- read [`docs/retrieval-contract-v1.md`](docs/retrieval-contract-v1.md) and [`docs/retrieval-quality-contract-v1.md`](docs/retrieval-quality-contract-v1.md) for retrieval semantics and evaluation posture
- read [`docs/decision-support-contract-v1.md`](docs/decision-support-contract-v1.md) for the current decision-support contract
- read [`CONTRIBUTING.md`](CONTRIBUTING.md) if you want to contribute changes
- read [`SECURITY.md`](SECURITY.md) for vulnerability reporting expectations

## Current posture

Current priority is trustworthiness of the existing local core:
- keep README/docs aligned with the code that actually exists
- keep one canonical demo path easy to run and easy to read honestly
- treat vector-ready retrieval as environment-dependent evidence, not a blanket project claim
