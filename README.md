# BrainOS

BrainOS is a SQLite-first cognitive memory core for LLM agents.

It gives an agent a local, auditable, multi-layer memory system in a single SQLite file: working memory, episodic memory, semantic memory, procedural memory, decision support, and provenance.

**Current scope:** BrainOS is a local storage and retrieval core, not a full agent runtime or hosted platform.

## Why BrainOS is different

- **One file, not a memory stack zoo** — core agent memory lives in one transactional SQLite database.
- **Auditability by default** — meaningful writes are tracked through a provenance ledger with chained hashes.
- **Built for local-first agent work** — simple to run, inspect, test, and carry between environments.

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
- a finished hybrid retrieval stack
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
- Python API
- CLI
- tests and smoke checks

### Not implemented yet

- full hybrid retrieval platform beyond the current bounded recall/explain/ranking slices
- full cognitive execution loop from the source PDF
- broad migration framework beyond the current hardening baseline
- HTTP API

## Quick start

### 1. Install dependencies

```bash
uv sync --extra dev
```

### 2. Initialize a database

```bash
uv run brainos --db ./brain.db init
```

### 3. Write and read working memory

```bash
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db wm-get agent_state
```

### 4. Add and search an episode

```bash
uv run brainos --db ./brain.db episode-add session-1 'Agent initialized successfully' --metadata-json '{"source":"manual"}'
uv run brainos --db ./brain.db episode-search Agent --limit 5
```

### 5. Run a minimal test

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

### Core lifecycle
- `init`
- `schema-status`
- `capabilities`

### Working and episodic memory
- `wm-set`, `wm-get`
- `episode-add`, `episodes-list`, `episode-search`
- `consolidation-preview`, `promote-episode`, `episode-promotion-get`
- `recall`

### Semantic and procedural memory
- `semantic-node-upsert`, `semantic-node-get`
- `semantic-edge-upsert`, `semantic-edges-list`
- `procedure-create`, `procedure-list`, `procedure-get`

### Decision support and inspection
- `decision-log`, `decision-list`, `decision-get`
- `decision-check`, `decision-history`
- `inspect`
- `ledger`, `ledger-verify`

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

## Design notes

The source BrainOS PDF describes a larger target architecture, but the available excerpt is incomplete in important places, especially around execution flow and `sqlite-vec` operational details.

This repository therefore implements the durable local storage core first.

One explicit implementation decision:
- the PDF narrative implies cryptographic chaining, but the shown ledger DDL did not include an explicit link field
- this implementation adds `previous_hash` to make the chain explicit and verifiable

## Documentation map

Use the docs this way:
- start with `README.md` for project overview and quick start
- read `docs/api.md` for exact Python API and CLI reference
- read `docs/implementation-notes.md` for design tradeoffs and spec-gap notes
- read `docs/README-DEV.md` for runtime, operator, and development details

## Roadmap

Recommended next slice:
1. add optional `sqlite-vec` capability detection and vector-table bootstrap
2. define retrieval that combines FTS, vector similarity, and graph neighborhood
3. add real schema migrations beyond current hardening baseline
4. formalize the cognitive execution loop
5. optionally add a local HTTP API
