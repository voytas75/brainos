# Next slice brief — retrieval backend contract narrowing

## Recommended slice
Introduce a minimal retrieval backend contract so `RetrievalService` depends on a narrow retrieval-facing surface instead of broad `BrainOSStore` internals.

## Why this now
BrainOS now has stronger retrieval docs, health semantics, and runtime/readiness clarity. The main remaining architectural weakness is that retrieval orchestration still leans too directly on the full store object.

## Goal
Improve retrieval architecture integrity without changing retrieval behavior, scoring policy, or product surface.

## Scope

### Do now
1. Inspect the actual `RetrievalService` backend calls.
2. Define one minimal backend protocol/interface for retrieval needs only.
3. Type/narrow `RetrievalService` to that contract.
4. Keep `BrainOSStore` as the implementation of that contract.
5. Preserve current CLI/test behavior.

### Do later
- deeper backend/store decoupling
- scoring policy surface versioning
- broader retrieval contract enforcement
- alternate backend implementations

## Acceptance checks
- `RetrievalService` no longer depends semantically on a broad store type.
- retrieval-facing backend methods are explicit and small.
- no retrieval behavior change.
- eval / benchmark / explain / health tests stay green.

## Rollback
If the narrowing starts spreading into broad store redesign, revert to the previous retrieval boundary and keep only the dependency inspection notes.

## Anti-goals
- do not retune scoring
- do not widen retrieval features
- do not change health semantics
- do not add new backends
- do not refactor unrelated store responsibilities
