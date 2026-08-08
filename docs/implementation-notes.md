# Historical implementation notes

> **Status:** archival design context, not a current runtime or product contract.

This file preserves a short record of early implementation tradeoffs and source-PDF gaps. It may describe work that has since been completed, superseded, or deliberately deferred. Do not use it to infer current configuration, provider behavior, schema status, or supported CLI behavior.

## Current authority

Use these documents instead:

- [`../PLAN.md`](../PLAN.md) and [`../BOUNDS.md`](../BOUNDS.md) — accepted scope and anti-scope.
- [`api.md`](./api.md) — current Python and CLI reference.
- [`README-DEV.md`](./README-DEV.md) — operator and development guidance.
- [`runtime-posture-contract-v1.md`](./runtime-posture-contract-v1.md) — `sqlite-vec` runtime interpretation.
- [`retrieval-quality-contract-v1.md`](./retrieval-quality-contract-v1.md) — bounded retrieval evaluation interpretation.
- [`evidence-map.md`](./evidence-map.md) — what the repository currently proves.

## Historical design context

The early local-first design chose a single SQLite file with WAL, foreign keys, JSON-bearing columns, FTS5 episode search, and a chained ledger. The supplied source material was incomplete about cognitive execution flow, FTS synchronization, and some validation rules; those decisions were made explicitly in code and tests rather than inferred as product guarantees.

Vector storage and embedding support were introduced later as capability- and configuration-gated surfaces. Their current behavior is defined by the runtime, API, and contract documents above, not by this historical note.

For detailed provenance, use Git history and the tests nearest to the relevant behavior.