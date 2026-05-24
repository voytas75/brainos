# Next slice brief — seeded benchmark isolation / read-safe health fix v1

## Recommended slice
Isolate the seeded retrieval benchmark from the caller database so `retrieval-health` can remain operationally read-safe and no longer fail because benchmark seeding tries to mutate the live DB.

## Why this now
Manual testing found the current remaining blocker: retrieval health invokes a seeded benchmark that writes fixtures into the active database. That is operationally unsafe and causes crashes or misleading behavior on live databases.

## Goal
Make seeded benchmark execution isolated from the caller DB and restore read-safe health behavior.

## Scope

### Do now
1. Inspect how benchmark seeding currently uses the live store/DB.
2. Run seeded benchmark in an isolated temp database.
3. Keep benchmark semantics intact while removing write-side effects on the caller DB.
4. Re-run the live health path.

### Do later
- explicit benchmark mode controls
- broader health/benchmark decoupling
- long-term benchmark storage strategy

## Acceptance checks
- `retrieval-health` no longer writes seeded benchmark fixtures to the live DB.
- seeded benchmark still works.
- live health no longer crashes for readonly/write-coupling reasons.
- tests stay green.

## Rollback
If the change risks benchmark semantics broadly, revert to the prior behavior and keep the defect note.

## Anti-goals
- do not redesign the benchmark suite
- do not retune retrieval behavior
- do not broaden into benchmark history or orchestration work
