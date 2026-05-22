# BrainOS

BrainOS is a SQLite-first cognitive memory system for LLM agents.

This repository implements the first local, production-oriented slice based on the attached BrainOS technical PDF: a deterministic single-file storage core with working, episodic, semantic, procedural, and provenance layers.

## Status

**Current state:** usable local storage core / first commit candidate.

Included now:
- single-file SQLite database (`brain.db`)
- WAL mode and foreign keys
- JSON validation on JSON-bearing columns
- working memory (`wm`)
- episodic memory (`episodes` + FTS5 search mirror)
- semantic memory (`semantic_nodes`, `semantic_edges`)
- procedural memory (`procedures`)
- immutable ledger (`ledger`) with chained SHA-256 hashes
- Python API for local integration
- CLI for initialization and basic operations
- tests and smoke checks

Not included yet:
- mandatory vector search runtime with `sqlite-vec`
- full hybrid retrieval orchestration (`vector + FTS + graph`)
- full cognitive execution loop from the PDF
- schema migrations / versioning
- HTTP API

## Environment policy

### Virtual environment
Yes — this repo should use a local virtual environment.

Preferred workflow:
- use `uv sync --extra dev`
- use `uv run ...`
- do not rely on manual activation as the default workflow

### `.env`
No — this repo does **not** currently require a `.env` file.

Reason:
- current implementation is local-only
- no API keys are needed
- no external services are required
- no runtime configuration is required beyond the SQLite file path

Add `.env` only when the project gains real external integrations, for example:
- embedding providers
- remote APIs
- telemetry backends
- server runtime configuration

## Why this shape

The attached PDF describes a strong target architecture, but the provided excerpt is incomplete in two important places:
- the execution-flow section is cut off
- `sqlite-vec` usage is referenced but not fully operationalized

So this repository takes the sensible first step:
- implement the durable storage core now
- keep vector support optional
- leave retrieval/orchestration as the next slice instead of faking completeness

## Architecture overview

BrainOS maps five memory areas into one SQLite database:

1. **Working memory**
   - fast key/value state
   - JSON-validated values
   - intended for current agent state, flags, and short-lived context

2. **Episodic memory**
   - append-style event storage
   - each episode belongs to a session
   - FTS5 mirror enables keyword search

3. **Semantic memory**
   - graph-like knowledge representation
   - nodes + typed edges
   - suitable for concepts, entities, facts, and relations

4. **Procedural memory**
   - executable or semi-executable procedure definitions
   - JSON steps structure for workflows / DAG-like action descriptions

5. **Provenance / ledger**
   - every meaningful write emits a ledger event
   - ledger entries are hash-chained for auditability
   - causal links can reference prior events

## Data model

Implemented tables / virtual tables:
- `wm`
- `episodes`
- `episodes_fts`
- `semantic_nodes`
- `semantic_edges`
- `procedures`
- `ledger`

Implemented indexes:
- `idx_episodes_session`
- `idx_edges_target`
- `idx_ledger_timestamp`

### Ledger note

The PDF excerpt describes a cryptographically linked ledger, but the shown DDL did not include an explicit previous-link column.

This implementation adds:
- `previous_hash`

That makes the chain explicit and testable.

## Install

Install dependencies with `uv`:

```bash
uv sync --extra dev
```

## Quick start

Initialize a database:

```bash
uv run python -m brainos.cli --db ./brain.db init
```

Store working memory:

```bash
uv run python -m brainos.cli --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run python -m brainos.cli --db ./brain.db wm-get agent_state
```

Add and search episodic memory:

```bash
uv run python -m brainos.cli --db ./brain.db episode-add session-1 'Agent initialized successfully' --metadata-json '{"source":"manual"}'
uv run python -m brainos.cli --db ./brain.db episode-search Agent --limit 5
```

Inspect the ledger:

```bash
uv run python -m brainos.cli --db ./brain.db ledger
```

Run tests:

```bash
uv run pytest tests/test_brainos.py -q
```

## Python API

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

See full API notes in [`docs/api.md`](docs/api.md).

## CLI surface

Available commands:
- `init`
- `wm-set`
- `wm-get`
- `episode-add`
- `episode-search`
- `ledger`

Example:

```bash
uv run brainos --db ./brain.db init
```

## Package layout

- `src/brainos/schema.py` — schema and initialization
- `src/brainos/store.py` — main storage API
- `src/brainos/ledger.py` — canonical JSON + hash helpers
- `src/brainos/cli.py` — command-line interface
- `docs/api.md` — first API reference
- `docs/implementation-notes.md` — spec gaps and implementation choices
- `tests/` — unit and smoke tests

## Design constraints and tradeoffs

### What is production-ready now
- deterministic local persistence
- audit-friendly write path
- transactional SQLite storage
- local testability
- simple integration surface for Python-based agents

### What is intentionally deferred
- vector runtime bootstrapping
- embedding provider abstraction
- retrieval ranking policies
- background consolidation flows
- network service exposure

That is deliberate. The current repo is a reliable storage core, not yet a complete cognitive OS runtime.

## Roadmap

Recommended next slice:
1. add optional `sqlite-vec` capability detection and vector-table bootstrap
2. define a retrieval API combining FTS, vector similarity, and graph neighborhood
3. add schema versioning / migrations
4. formalize the cognitive execution loop
5. optionally add a local HTTP API
