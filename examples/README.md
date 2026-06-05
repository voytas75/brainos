# BrainOS examples

These examples are intentionally small.
They are meant to teach the usage contract of BrainOS layers, not to simulate a full agent runtime.

## Goals

Use these examples to understand:
- what each layer is for
- what BrainOS stores for you
- what higher-level application logic still needs to decide

## Included examples

### `working_memory_flow.py`
Shows working memory as passive operational state.
It demonstrates a simple `ready -> busy -> ready` flow and makes explicit that BrainOS stores the state, but does not interpret it automatically.

Run:

```bash
uv run python examples/working_memory_flow.py
```

### `episode_recall_flow.py`
Shows episodic memory as searchable history.
It writes a few episodes and recalls them with a simple query so the difference between working memory and episodic memory stays clear.

Run:

```bash
uv run python examples/episode_recall_flow.py
```

### `ledger_inspection.py`
Shows the audit trail.
It writes a bit of working memory and an episode, then prints the ledger so you can see how BrainOS records meaningful writes.

Run:

```bash
uv run python examples/ledger_inspection.py
```

## Notes

- Each example creates its own temporary SQLite database under `examples/tmp/`.
- You can delete that directory at any time.
- These examples are teaching artifacts, not production orchestration patterns.
