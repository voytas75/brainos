# BrainOS Evidence Map

This document is the short trustworthiness map for the current repo. It distinguishes what is directly proven in-repo, what is only bounded evidence, and what is still intentionally unproven.

## Proven in this repo

- Local storage core exists: SQLite schema, WAL mode, working memory, episodic memory, semantic memory, procedures, ledger, CLI, and Python API.
- Promotion flow exists: an episode can be previewed and promoted into semantic or procedural storage.
- Bounded retrieval surfaces exist: `recall`, `retrieval-explain`, `retrieval-health`, `retrieval-benchmark`, and `real-corpus-probe`.
- Vector maintenance surfaces exist: vector metadata state, sync commands, embedding adapter boundary, capability/readiness checks, and degraded-mode handling.
- Operator-facing decision support exists in bounded form: decision log/list/get, conflict checks, history, and inspect/provenance drill-down.

Primary repo-local evidence:
- [`scripts/e2e_smoke.sh`](../scripts/e2e_smoke.sh)
- [`scripts/retrieval_smoke.sh`](../scripts/retrieval_smoke.sh)
- [`scripts/canonical_e2e_demo.sh`](../scripts/canonical_e2e_demo.sh)
- `tests/test_brainos.py`
- `tests/test_retrieval_eval.py`
- `tests/test_explain_cli.py`
- `tests/test_health_cli.py`
- `tests/test_sqlite_vec_runtime.py`
- `tests/test_decision_cli.py`
- `tests/test_decision_conflicts.py`
- `tests/test_decision_history_cli.py`

## Bounded evidence only

- `retrieval-benchmark` is seeded-fixture evidence. It is useful regression signal, not proof of broad live-corpus relevance.
- `real-corpus-probe` is a small read-only sample aligned to available session data. It is stronger than a pure fixture, but still not broad corpus evidence.
- `retrieval_smoke.sh` proves a vector-ready green path only on the machine and environment where it is run.
- `canonical_e2e_demo.sh` proves the local end-to-end path honestly, but in default mode it does not force remote embedding calls or claim vector-ready success unless the environment is configured for it.
- The canonical demo defaults to a repo-local database path (`./brain_canonical_e2e.db`) and artifact directory so the walkthrough is easy to repeat and inspect.
- Historical notes under [`docs/_archive_working/`](./_archive_working/) are supporting context, not current SSOT.

## Still unproven or intentionally not claimed

- No claim of broad retrieval quality across open-ended or production-scale corpora.
- No claim of hosted/server behavior. The repo does not expose HTTP, MCP, or other network API servers.
- No claim of new retrieval algorithms beyond the current bounded lexical plus optional vector surfaces.
- No claim of autonomous decision making or full execution-loop behavior.
- No claim of large-scale performance, concurrency, or operational durability beyond the bounded local checks present here.

## Fast reading order

1. [`docs/canonical-e2e-demo.md`](./canonical-e2e-demo.md)
2. [`docs/STATUS.md`](./STATUS.md)
3. [`docs/retrieval-green-path-smoke-test.md`](./retrieval-green-path-smoke-test.md)
4. [`docs/retrieval-contract-v1.md`](./retrieval-contract-v1.md)
5. [`docs/retrieval-quality-contract-v1.md`](./retrieval-quality-contract-v1.md)
