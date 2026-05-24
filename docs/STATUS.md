# BrainOS Retrieval Eval Status

## Latest operator/runtime slice
- project-local `.env` is now supported as the preferred project-scoped runtime config surface; shell env still overrides it.
- operator-first check is now `doctor`.
- LiteLLM noise is suppressed so operator CLI stays JSON-first.
- Azure embedding config validation now accepts real Azure API version shapes.
- vector sync now persists `vector_index_state` correctly under transaction.
- benchmark seeded DB now syncs vector state before scoring, so benchmark green/red reflects the seeded retrieval path instead of an unseeded fixture artifact.
- current verified operator state on local `brain.db`: vector freshness `fresh:30`, retrieval benchmark `5/5`, retrieval-health `status: ok`.

## Scope
Deterministic regression fixtures for unified retrieval quality.

## Current protected case classes
- lexical semantic graph query
- procedural/bootstrap query
- embedding/semantic quality query
- competing similar hits (`reset runtime`)
- session filter protection for vector results
- weak vector-only noise suppression

## Current gate
- `tests/test_retrieval_eval.py`

## Notes
- This is a bounded regression baseline, not a full ranking benchmark suite.
- Current fixtures are deterministic and monkeypatched by design.
- Future tuning should preserve or intentionally revise these expectations.
- Benchmark interpretation now distinguishes `vector-ready` from `degraded-non-vector` runs so degraded-path output is not read as the same class of signal as a vector-ready pass/fail.
- Retrieval quality interpretation SSOT: `docs/retrieval-quality-contract-v1.md`.

## gate_reason
Expanded eval fixture baseline must stay green before scoring changes are trusted.

- lexical-overlap preference when similar vector hits compete


## Real-sample benchmark pass v0
- queries now include more natural BrainOS-like phrasing
- protects session filtering on vector hits
- checks maintenance/reindex retrieval wording
- keeps nonsense/noise suppression as a hard gate
- score components are now surfaced on ranked hits for operator/debug visibility
- benchmark mode should be read together with runtime capability: `vector-ready` and `degraded-non-vector` are intentionally different operator states
