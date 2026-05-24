# Next slice brief — retrieval explain evidence alignment v1

## Recommended slice
Add a small evidence-alignment layer so `retrieval-explain` better mirrors the benchmark/health drilldown posture and makes top-hit outcomes easier to diagnose from the explain output alone.

## Why this now
BrainOS now exposes `failed_cases` and bounded `failure_hint` classification in benchmark/health output. The next small step is to make explain output more directly useful when inspecting why a specific top hit won.

## Goal
Improve explain-side diagnostic usefulness without redesigning retrieval or explain output structure.

## Scope

### Do now
1. Inspect current `retrieval-explain` output shape.
2. Add one or two compact diagnostic fields that help align explain with benchmark drilldown.
3. Add focused tests and light docs alignment.

### Do later
- richer pairwise comparison output
- expected-vs-actual benchmark explain integration
- deeper counterfactual ranking analysis

## Acceptance checks
- explain output exposes a small extra diagnostic hint.
- change stays bounded and readable.
- tests stay green.
- no retrieval behavior retune.

## Rollback
If the change starts turning into a ranking-debug framework, revert to the previous explain shape and keep only the brief.

## Anti-goals
- do not redesign explain output wholesale
- do not add benchmark coupling into normal explain calls
- do not retune ranking
