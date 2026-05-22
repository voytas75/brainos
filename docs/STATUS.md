# BrainOS Retrieval Eval Status

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

## gate_reason
Expanded eval fixture baseline must stay green before scoring changes are trusted.

- lexical-overlap preference when similar vector hits compete


## Real-sample benchmark pass v0
- queries now include more natural BrainOS-like phrasing
- protects session filtering on vector hits
- checks maintenance/reindex retrieval wording
- keeps nonsense/noise suppression as a hard gate
