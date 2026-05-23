# Next slice brief — fresh-db vec-table bootstrap / fallback fix v1

## Recommended slice
Fix the fresh-database vector recall path so retrieval health/benchmark no longer crash when sqlite-vec runtime is available but vector tables have not yet been created.

## Why this now
Manual startup testing found the current blocker: fresh DB init + readiness succeed, but retrieval benchmark/health crash because recall assumes `episodes_vec` / `semantic_nodes_vec` already exist.

## Goal
Make fresh-db retrieval behavior safe by either bootstrapping vec tables when appropriate or falling back cleanly when they are absent.

## Scope

### Do now
1. Inspect vec-table lifecycle assumptions in recall path.
2. Add bounded absent-table fallback for vector search paths.
3. Keep retrieval behavior otherwise unchanged.
4. Re-run fresh-db startup path.

### Do later
- eager vector-table bootstrap policy decisions
- broader fresh-db onboarding flows
- vector-table migration redesign

## Acceptance checks
- fresh-db retrieval health/benchmark no longer crash on missing vec tables.
- tests stay green.
- no ranking retune.

## Rollback
If the fallback changes retrieval semantics too broadly, revert to the previous path and keep the defect note.

## Anti-goals
- do not redesign vector architecture
- do not broaden into onboarding workflows
- do not change scoring behavior
