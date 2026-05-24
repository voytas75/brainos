# Next slice brief — vec0 knn query compatibility fix v1

## Recommended slice
Fix the live sqlite-vec KNN query compatibility bug so BrainOS recall paths no longer fail with `A LIMIT or 'k = ?' constraint is required on vec0 knn queries.`

## Why this now
Manual testing found a real runtime defect: readiness succeeds, but live retrieval health/benchmark can still crash inside vector recall because the actual vec0 query path does not satisfy the runtime KNN contract.

## Goal
Make live vec0-backed recall queries compatible with the current sqlite-vec runtime contract.

## Scope

### Do now
1. Inspect the current `vector_search_episodes` and `vector_search_semantic_nodes` SQL.
2. Fix the vec0 KNN query shape.
3. Add focused tests.
4. Re-run the previously failing live CLI path.

### Do later
- broader sqlite-vec compatibility matrix work
- ranking retune
- vector query optimization work

## Acceptance checks
- vector recall queries no longer raise the vec0 KNN contract error.
- tests stay green.
- `retrieval-health` no longer crashes for this reason.

## Rollback
If the fix risks broader query semantics, revert to the previous query shape and keep the defect note.

## Anti-goals
- do not retune ranking
- do not redesign retrieval behavior
- do not broaden into vector architecture work
