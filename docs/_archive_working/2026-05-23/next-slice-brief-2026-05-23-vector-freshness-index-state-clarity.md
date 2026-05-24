# Next slice brief — vector freshness / index-state clarity

## Recommended slice
Tighten the semantics and operator interpretation of vector index states so `missing`, `stale`, `fresh`, `error`, and `disabled` are easier to reason about and less likely to blur runtime/setup issues with data/freshness issues.

## Why this now
BrainOS now has stronger retrieval contracts, health planes, readiness classification, backend boundary, and scoring policy visibility. The next maturity gap is derived-state discipline around vector freshness and index state interpretation.

## Goal
Make vector index state more governable without changing retrieval ranking behavior or widening product scope.

## Scope

### Do now
1. Inspect current vector-state semantics in code, tests, and operator surfaces.
2. Identify the smallest ambiguity that is still causing mixed interpretation.
3. Add one minimal clarity improvement in code/docs/tests.
4. Keep current retrieval/vector behavior unchanged unless a tiny semantic correction is clearly warranted.

### Do later
- broader reindex/freshness contract doc
- richer remediation hints per vector state
- automated repair workflows

## Acceptance checks
- vector-state semantics are more explicit for operators and tests.
- runtime/setup problems remain distinguishable from freshness/data problems.
- no retrieval ranking behavior change.
- targeted vector metadata/maintenance/health tests stay green.

## Rollback
If the change starts widening into vector workflow redesign, revert to the previous state and keep only the brief/inspection notes.

## Anti-goals
- do not retune ranking
- do not widen embeddable object families
- do not add automation loops
- do not redesign the whole vector subsystem
