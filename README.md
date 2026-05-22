# BrainOS

BrainOS is a SQLite-first cognitive memory system for LLM agents.

This repository contains the first local, production-oriented slice based on the BrainOS technical PDF: a deterministic single-file storage core with working, episodic, semantic, procedural, and provenance layers.

## What this project is

BrainOS stores multiple memory layers for an LLM agent inside a single SQLite database file.

Current implementation provides:
- working memory as JSON key/value state
- episodic memory as session-scoped events
- full-text search over episodes with FTS5
- semantic memory as nodes and edges
- procedural memory as JSON-defined procedures
- consolidation preview and explicit promotion from episodes into semantic/procedural layers
- promotion state tracking and duplicate-promotion protection
- an immutable ledger with chained hashes for provenance/audit

The current repo is a **local storage core**, not a full runtime platform yet.

## What problem it solves

Instead of splitting agent memory across multiple services, BrainOS keeps the core memory model in one transactional SQLite file.

That gives:
- low infrastructure cost
- deterministic local behavior
- ACID transactions
- simple portability
- easy local development and testing

## Current status

Implemented now:
- single-file SQLite database (`brain.db`)
- WAL mode and foreign keys
- JSON validation on JSON-bearing columns
- `wm`
- `episodes`
- `episodes_fts`
- `semantic_nodes`
- `semantic_edges`
- `procedures`
- `ledger`
- Python API
- CLI
- tests and smoke checks

Not implemented yet:
- vector storage/runtime integration beyond capability detection
- hybrid retrieval orchestration (`FTS + vector + graph`)
- full cognitive execution loop from the PDF
- schema migrations beyond current hardening baseline
- HTTP API

## How it works

BrainOS maps five memory areas into one SQLite database.

### 1. Working memory
Short-lived, current agent state.

Table:
- `wm`

Use cases:
- current mode
- temporary state
- active flags
- local runtime context

### 2. Episodic memory
Append-style event memory for sessions.

Tables:
- `episodes`
- `episodes_fts`

Use cases:
- interaction history
- observations
- logs worth recalling
- searchable memory fragments

### 3. Semantic memory
Graph-like knowledge storage.

Tables:
- `semantic_nodes`
- `semantic_edges`

Use cases:
- concepts
- entities
- facts
- relations between concepts

### 4. Procedural memory
Structured procedures stored as JSON.

Table:
- `procedures`

Use cases:
- workflows
- reusable agent routines
- DAG-like step definitions

### 5. Provenance / ledger
Every meaningful write creates an auditable event.

Table:
- `ledger`

Properties:
- causal reference support
- chained hashes
- immutable event history for inspection

## Architecture notes

The attached PDF describes a strong target architecture, but the provided excerpt is incomplete in two important places:
- the execution-flow section is cut off
- `sqlite-vec` is mentioned, but operational details are incomplete in the excerpt

So this repo intentionally implements the durable storage core first.

One explicit implementation decision:
- the PDF narrative implies cryptographic chaining, but the shown ledger DDL did not include an explicit link field
- this implementation adds `previous_hash` to make the chain explicit and verifiable

## Environment and tooling

### Virtual environment
Yes — this repo should use a local virtual environment managed by `uv`.

Preferred workflow:
- `uv sync --extra dev`
- `uv run ...`

### `.env`
No — this repo does **not** require a `.env` file right now.

Reason:
- no external APIs
- no secrets
- no server runtime config
- only local SQLite storage

Add `.env` only when the project gains real external integrations.

## How to run

### 1. Install dependencies

```bash
uv sync --extra dev
```

### 2. Initialize the database

```bash
uv run brainos --db ./brain.db init
```

### 3. Write working memory

```bash
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
```

### 4. Read working memory

```bash
uv run brainos --db ./brain.db wm-get agent_state
```

### 5. Add episodic memory

```bash
uv run brainos --db ./brain.db episode-add session-1 'Agent initialized successfully' --metadata-json '{"source":"manual"}'
```

### 6. Search episodic memory

```bash
uv run brainos --db ./brain.db episode-search Agent --limit 5
```

### 7. Preview consolidation candidate from an episode

```bash
uv run brainos --db ./brain.db consolidation-preview <episode-id>
```

### 8. Promote episode into semantic/procedural layer

```bash
uv run brainos --db ./brain.db promote-episode <episode-id>
```

### 9. Recall from episodic memory

```bash
uv run brainos --db ./brain.db recall Agent --session-id session-1 --limit 5
```

### 10. Create a semantic node

```bash
uv run brainos --db ./brain.db semantic-node-upsert n1 SQLite Concept --properties-json '{"kind":"database"}'
```

### 11. Create a semantic edge

```bash
uv run brainos --db ./brain.db semantic-edge-upsert n1 n2 RELATES_TO --weight 1.0
```

### 12. Create a procedure

```bash
uv run brainos --db ./brain.db procedure-create bootstrap '[{"step":"init-db"},{"step":"load-state"}]' --description 'Initialize BrainOS'
```

### 13. Check schema status

```bash
uv run brainos --db ./brain.db schema-status
```

### 14. Check runtime capabilities

```bash
uv run brainos --db ./brain.db capabilities
```

### 15. Verify ledger integrity

```bash
uv run brainos --db ./brain.db ledger-verify
```

### 16. Inspect ledger

```bash
uv run brainos --db ./brain.db ledger
```

## Typical local workflow

```bash
uv sync --extra dev
uv run pytest tests/test_brainos.py -q
uv run brainos --db ./brain.db init
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized' --metadata-json '{"source":"smoke"}'
uv run brainos --db ./brain.db ledger
```

## Python usage

Minimal example:

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

## Main commands

Available CLI commands:
- `init`
- `wm-set`
- `wm-get`
- `episode-add`
- `episodes-list`
- `consolidation-preview`
- `episode-promotion-get`
- `promote-episode`
- `episode-search`
- `recall`
- `semantic-node-upsert`
- `semantic-node-get`
- `semantic-edge-upsert`
- `semantic-edges-list`
- `procedure-create`
- `procedure-list`
- `procedure-get`
- `schema-status`
- `capabilities`
- `ledger-verify`
- `ledger`

Example:

```bash
uv run brainos --db ./brain.db init
```

## Project structure

- `README.md` — main project description, how it works, how to run
- `docs/api.md` — Python API and CLI reference
- `docs/implementation-notes.md` — implementation decisions, spec gaps, next slice notes
- `src/brainos/schema.py` — schema and initialization
- `src/brainos/store.py` — storage API
- `src/brainos/ledger.py` — canonical JSON + hash helpers
- `src/brainos/cli.py` — CLI entrypoint
- `tests/` — tests

## Docs map

Use docs this way:
- start with `README.md` if you want to understand the project and run it
- read `docs/api.md` if you want the exact API surface
- read `docs/implementation-notes.md` if you want design tradeoffs and spec-gap notes

## Design constraints

What is solid already:
- deterministic local persistence
- transactional writes
- audit-friendly ledger trail
- simple Python integration
- local testability

What is intentionally deferred:
- vector runtime bootstrapping
- embedding integration
- ranking fusion
- graph traversal/retrieval API
- procedure execution engine
- network exposure

## Development verification

Run tests:

```bash
uv run pytest tests/test_brainos.py -q
```

Run a simple smoke path:

```bash
uv run brainos --db ./brain.db init
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized with WAL and ledger' --metadata-json '{"source":"smoke"}'
uv run brainos --db ./brain.db episode-search BrainOS --limit 5
uv run brainos --db ./brain.db ledger
```

## Roadmap

Recommended next slice:
1. add optional `sqlite-vec` capability detection and vector-table bootstrap
2. define retrieval that combines FTS, vector similarity, and graph neighborhood
3. add real schema migrations beyond current hardening baseline beyond v1 bootstrap
4. formalize the cognitive execution loop
5. optionally add a local HTTP API


## Official smoke test

Run the bounded end-to-end smoke test:

```bash
./scripts/e2e_smoke.sh
```

It writes a summary artifact to:
- `artifacts/e2e-summary.json`


## CLI error behavior

For expected user-facing errors (for example not found, invalid promotion metadata, duplicate promotion), CLI exits with code `2` and returns a compact JSON error object on stderr.


## Promotion audit

To inspect whether a specific episode was already promoted:

```bash
uv run brainos --db ./brain.db episode-promotion-get <episode-id>
```
