# Next slice brief — retrieval health summary tightening v1

## Recommended slice
Add one compact retrieval-health summary/headline so operators can read the dominant interpretation faster without manually combining runtime, freshness, benchmark mode, and quality status.

## Why this now
BrainOS retrieval health now has better contracts, action hints, drilldown, and benchmark/explain handoff. The remaining small friction is that operators still have to synthesize the main takeaway themselves.

## Goal
Make retrieval-health easier to scan by adding a short dominant-summary field without redesigning the output.

## Scope

### Do now
1. Add one bounded summary/headline field to retrieval-health.
2. Keep precedence rules simple and explicit.
3. Add focused tests and light docs alignment.

### Do later
- richer narrative summaries
- multi-line operator recommendations
- historical summary comparisons

## Acceptance checks
- retrieval-health includes a compact summary/headline.
- summary reflects dominant interpretation precedence.
- tests stay green.
- no broad health UX redesign.

## Rollback
If this starts becoming a narrative reporting layer, revert to the previous health shape and keep only the brief.

## Anti-goals
- do not add verbose prose blobs
- do not retune health semantics
- do not redesign benchmark or explain output
