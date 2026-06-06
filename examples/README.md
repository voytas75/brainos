# BrainOS examples

These examples are intentionally small.
They are meant to teach the usage contract of BrainOS layers, not to simulate a full agent runtime.

## Goals

Use these examples to understand:
- what each layer is for
- what BrainOS stores for you
- what higher-level application logic still needs to decide

## Included examples

### [`working_memory_flow.py`](working_memory_flow.py)
Shows working memory as passive operational state.
It demonstrates a simple `ready -> busy -> ready` flow and makes explicit that BrainOS stores the state, but does not interpret it automatically.
See also: [`scripts/e2e_smoke.sh`](../scripts/e2e_smoke.sh).

Run:

```bash
uv run python examples/working_memory_flow.py
```

### [`episode_recall_flow.py`](episode_recall_flow.py)
Shows episodic memory as searchable history.
It writes a few episodes and recalls them with a simple query so the difference between working memory and episodic memory stays clear.
See also: [`scripts/retrieval_smoke.sh`](../scripts/retrieval_smoke.sh) and [`scripts/canonical_e2e_demo.sh`](../scripts/canonical_e2e_demo.sh).

Run:

```bash
uv run python examples/episode_recall_flow.py
```

### [`ledger_inspection.py`](ledger_inspection.py)
Shows the audit trail.
It writes a bit of working memory and an episode, then prints the ledger so you can see how BrainOS records meaningful writes.
See also: [`scripts/e2e_smoke.sh`](../scripts/e2e_smoke.sh) and [`scripts/canonical_e2e_demo.sh`](../scripts/canonical_e2e_demo.sh).

Run:

```bash
uv run python examples/ledger_inspection.py
```

### [`python_api_quickstart.py`](python_api_quickstart.py)
Shows one compact Python API walkthrough.
It initializes a database, writes working memory and an episode, upserts one semantic node, and prints the stored objects.
See also: [`scripts/canonical_e2e_demo.sh`](../scripts/canonical_e2e_demo.sh).

Run:

```bash
uv run python examples/python_api_quickstart.py
```

## Notes

- Each example creates its own temporary SQLite database under `examples/tmp/`.
- You can delete that directory at any time.
- These examples are teaching artifacts, not production orchestration patterns.
