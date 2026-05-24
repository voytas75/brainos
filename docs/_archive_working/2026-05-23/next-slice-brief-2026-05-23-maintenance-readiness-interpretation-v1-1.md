# Next slice brief — maintenance/readiness interpretation v1.1

## Recommended slice
Add small operator-facing interpretation hints to maintenance/readiness surfaces so BrainOS more clearly signals whether the next action is likely `retry`, `runtime fix`, `reindex`, or `noop`.

## Why this now
BrainOS now has readiness classification, vector-state contract docs, health planes, and retrieval quality interpretation. The next small maturity gain is to make the current maintenance/readiness outputs easier to act on without redesigning workflows.

## Goal
Improve operator actionability of current maintenance/readiness surfaces without changing retrieval behavior or introducing automation.

## Scope

### Do now
1. Inspect current readiness/health/sync outputs for missing operator hints.
2. Add small explicit interpretation fields where current output is still too implicit.
3. Add focused tests for the new hints.

### Do later
- remediation command suggestions
- grouped operator actions
- automated repair workflows

## Acceptance checks
- readiness/health/sync outputs expose clearer next-action interpretation.
- tests stay green.
- no ranking change.
- no workflow expansion.

## Rollback
If the slice starts becoming a broad health UX redesign, revert to previous output and keep only the brief/inspection notes.

## Anti-goals
- do not add background automation
- do not retune ranking
- do not redesign all CLI output
