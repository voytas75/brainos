# Next slice brief — health/benchmark evidence drilldown v1

## Recommended slice
Add a small evidence drilldown layer so retrieval health and benchmark output more clearly show which cases failed and whether the signal looks runtime-related, freshness-related, or quality-regression-like.

## Why this now
BrainOS now has quality interpretation contracts and action hints, but failure ergonomics are still too coarse. The next bounded improvement is to expose a little more evidence without redesigning reporting.

## Goal
Make benchmark/health failures easier to triage from current output alone.

## Scope

### Do now
1. Inspect current benchmark result shape.
2. Add compact failure drilldown to benchmark output.
3. Surface the same evidence in retrieval health quality output.
4. Add focused tests.

### Do later
- per-case remediation commands
- richer causal classification
- historical trend reporting

## Acceptance checks
- benchmark output shows failed cases explicitly.
- failures get a bounded classification hint.
- retrieval health exposes the same drilldown summary.
- tests stay green.

## Rollback
If this starts turning into a general observability framework, revert to the previous output shape and keep only the brief.

## Anti-goals
- do not redesign the whole benchmark format
- do not add history/trending
- do not retune retrieval behavior
