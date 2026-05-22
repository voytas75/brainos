# BrainOS API v0.1

This document describes the first local API surface for BrainOS.

## Scope

Current API surface is intentionally small:
- Python package API via `BrainOSStore`
- local CLI for bootstrap and smoke usage

This is a storage-core API, not yet a retrieval orchestration or network API.

## Environment

Preferred local workflow uses `uv`:

```bash
uv sync --extra dev
uv run pytest
uv run brainos --db ./brain.db init
```

Current version does not require a `.env` file.

---

## Python API

Import:

```python
from brainos import BrainOSStore
```

### `BrainOSStore(db_path, enable_vector=False)`

Create a store bound to a SQLite database path.

Parameters:
- `db_path: str | Path` — location of the SQLite database file
- `enable_vector: bool = False` — attempts to create `episodes_vec` when vector support is enabled

Notes:
- enables SQLite foreign keys
- enables WAL mode
- does not automatically initialize schema; call `initialize()` first

### `initialize()`

Creates schema objects if they do not exist.

Creates:
- `wm`
- `episodes`
- `episodes_fts`
- `semantic_nodes`
- `semantic_edges`
- `procedures`
- `ledger`
- optionally `episodes_vec`

### `close()`

Closes the SQLite connection.

### `transaction()`

Context manager for atomic operations.

Example:

```python
with store.transaction():
    ...
```

---

## Working memory

### `set_working_memory(key, value, causal_event_id=None) -> str`

Upserts a JSON value in `wm` and appends a ledger event.

Parameters:
- `key: str`
- `value: dict[str, Any]`
- `causal_event_id: str | None = None`

Returns:
- `event_id: str` — ledger event id

Behavior:
- inserts or updates the key
- refreshes `updated_at`
- creates a ledger `working / UPDATE` event

### `get_working_memory(key) -> dict | None`

Returns parsed JSON value for a working-memory key, or `None` if not found.

---

## Episodic memory

### `add_episode(session_id, content, metadata=None, episode_id=None, causal_event_id=None) -> str`

Creates an episode row, mirrors it into FTS, and appends a ledger event.

Parameters:
- `session_id: str`
- `content: str`
- `metadata: dict[str, Any] | None = None`
- `episode_id: str | None = None`
- `causal_event_id: str | None = None`

Returns:
- `episode_id: str`

Behavior:
- inserts a row into `episodes`
- inserts a mirrored row into `episodes_fts`
- appends a ledger `episodic / CREATE` event

### `search_episodes_text(query, limit=10) -> list[dict]`

Runs FTS5 search against episodic memory.

Parameters:
- `query: str`
- `limit: int = 10`

Returns row dictionaries with:
- `id`
- `session_id`
- `timestamp`
- `content`
- `metadata`

Note:
- `metadata` is currently returned as stored JSON string from SQLite rows

---

## Semantic memory

### `upsert_semantic_node(node_id, name, node_type, properties=None, causal_event_id=None) -> str`

Creates or updates a semantic node and appends a ledger event.

Parameters:
- `node_id: str`
- `name: str`
- `node_type: str`
- `properties: dict[str, Any] | None = None`
- `causal_event_id: str | None = None`

Returns:
- ledger `event_id: str`

### `upsert_semantic_edge(source_id, target_id, predicate, weight=1.0, causal_event_id=None) -> str`

Creates or updates a semantic edge and appends a ledger event.

Parameters:
- `source_id: str`
- `target_id: str`
- `predicate: str`
- `weight: float = 1.0`
- `causal_event_id: str | None = None`

Returns:
- ledger `event_id: str`

Constraints:
- referenced nodes must exist
- foreign keys are enforced

---

## Procedural memory

### `create_procedure(name, steps, description=None, procedure_id=None, causal_event_id=None) -> str`

Creates a procedure definition and appends a ledger event.

Parameters:
- `name: str`
- `steps: list[dict[str, Any]]`
- `description: str | None = None`
- `procedure_id: str | None = None`
- `causal_event_id: str | None = None`

Returns:
- `procedure_id: str`

Notes:
- `steps` are stored as JSON in `steps_json`
- current implementation does not validate a strict DAG schema yet

---

## Ledger / provenance

### `list_ledger() -> list[dict]`

Returns ledger rows in chronological order.

Fields:
- `event_id`
- `timestamp`
- `layer`
- `action`
- `payload`
- `causal_event_id`
- `previous_hash`
- `crypto_hash`

### Hash chaining

Each ledger event includes:
- its own `crypto_hash`
- `previous_hash` pointing to the prior event hash

Hash basis currently includes:
- `event_id`
- `layer`
- `action`
- canonicalized payload JSON
- `causal_event_id`
- `previous_hash`

This is implemented in `brainos.ledger.compute_event_hash()`.

---

## CLI API

Entry point:

```bash
brainos --db ./brain.db <command>
```

Equivalent:

```bash
python -m brainos.cli --db ./brain.db <command>
```

### `init`

Initialize schema.

```bash
brainos --db ./brain.db init
```

Optional:

```bash
brainos --db ./brain.db init --enable-vector
```

### `wm-set`

```bash
brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
```

Output:
- ledger event id

### `wm-get`

```bash
brainos --db ./brain.db wm-get agent_state
```

Output:
- JSON value or `null`

### `episode-add`

```bash
brainos --db ./brain.db episode-add session-1 'Agent initialized' --metadata-json '{"source":"manual"}'
```

Output:
- episode id

### `episode-search`

```bash
brainos --db ./brain.db episode-search Agent --limit 5
```

Output:
- JSON array of episode rows

### `ledger`

```bash
brainos --db ./brain.db ledger
```

Output:
- JSON array of ledger rows

---

## Error behavior

Current version follows simple fail-fast behavior:
- invalid JSON in checked columns raises SQLite error
- missing foreign-key targets raise SQLite error
- unsupported vector table creation will fail if `--enable-vector` is used without proper runtime support

This is acceptable for the first local commit.

Future versions should add:
- clearer domain exceptions
- capability probing for vector support
- migration/version diagnostics

---

## Compatibility notes

Target baseline:
- Python 3.10+
- SQLite 3.38+

Assumptions:
- SQLite build includes JSON functions
- FTS5 support is available
- `sqlite-vec` may be absent

---

## Non-goals for v0.1

Not part of this API yet:
- remote server mode
- authentication / authorization
- embedding generation
- ranking fusion
- graph traversal API
- procedure execution engine
- background compaction / consolidation workers
