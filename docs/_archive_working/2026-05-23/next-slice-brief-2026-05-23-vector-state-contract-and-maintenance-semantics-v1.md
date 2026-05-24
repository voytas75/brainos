# Next slice brief — vector-state contract / maintenance semantics v1

## Recommended slice
Add one explicit vector-state contract document and tighten a few maintenance semantics checks so `missing`, `fresh`, `stale`, `error`, and `disabled` have one clear operator/developer interpretation.

## Why this now
BrainOS now has clearer retrieval contracts, health planes, readiness classification, scoring-policy visibility, and freshness notes. The next maturity gap is that vector-state meaning and maintenance expectations are still spread across code and tests rather than stated in one SSOT.

## Goal
Make vector-state transitions and maintenance expectations explicit without changing retrieval ranking behavior or widening product scope.

## Scope

### Do now
1. Inspect current vector-state transitions and maintenance logic.
2. Write one short contract doc for vector states and expected transitions.
3. Add a minimal semantics test where current intent is not yet explicit enough.
4. Align docs lightly if needed.

### Do later
- broader repair/remediation guidance
- automated maintenance policies
- richer health remediation surfaces

## Acceptance checks
- one explicit contract doc exists for vector-state semantics.
- maintenance expectations are clearer for `sync_vector_index` / freshness interpretation.
- targeted vector-state tests stay green.
- no ranking behavior change.

## Rollback
If the slice starts turning into workflow redesign, revert to the previous state and keep only the brief and contract notes.

## Anti-goals
- do not retune ranking
- do not add background repair loops
- do not widen embeddable object families
- do not redesign the whole vector subsystem
