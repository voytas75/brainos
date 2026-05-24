# Next slice brief — scoring policy surface v1

## Recommended slice
Extract the current retrieval scoring constants into an explicit scoring-policy surface and give the current policy a stable version label, without changing retrieval behavior.

## Why this now
BrainOS now has a cleaner retrieval backend boundary, stronger health semantics, and clearer runtime/readiness posture. The next maturity gap is that retrieval scoring behavior still lives mainly as local constants and implicit semantics.

## Goal
Turn scoring from implicit local tuning into a visible, named policy surface while preserving current ranking behavior.

## Scope

### Do now
1. Inspect current scoring constants and where explain/ranking depends on them.
2. Introduce one explicit policy object/module for current scoring behavior.
3. Give the policy a stable version name.
4. Make retrieval/explain surfaces able to report which policy version is active.
5. Keep ranking behavior unchanged.

### Do later
- policy-specific tuning docs
- alternative policy versions
- policy-driven runtime selection
- broader explain semantics cleanup

## Acceptance checks
- scoring constants are centralized behind one explicit policy surface.
- policy version is visible in retrieval/explain output.
- no ranking behavior regression.
- eval / benchmark / explain tests stay green.

## Rollback
If the change starts to alter ranking behavior or spreads into a broad tuning refactor, revert to the previous constant-based implementation and keep only the brief.

## Anti-goals
- do not retune scoring
- do not change retrieval result ordering
- do not widen public API beyond minimal policy visibility
- do not add runtime policy switching
