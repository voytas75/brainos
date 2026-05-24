# Next slice brief — retrieval quality contract / benchmark interpretation

## Recommended slice
Add one short SSOT that defines what the current retrieval quality benchmark/eval corpus does prove, what it does not prove, and how to interpret failures in vector-ready vs degraded mode.

## Why this now
BrainOS now has more retrieval-quality fixtures, explicit health planes, scoring policy visibility, and benchmark mode semantics. The next risk is interpretation drift: green and red results can easily be over-read.

## Goal
Make retrieval quality signals more governable by explicitly bounding the meaning of the current eval/benchmark suite.

## Scope

### Do now
1. Inspect the current benchmark/eval surfaces and their semantics.
2. Write one short quality-contract doc.
3. Align API/README lightly where interpretation benefits from one extra line.

### Do later
- broader corpus tooling
- confidence scoring layers
- larger ambiguity suites

## Acceptance checks
- one explicit quality-contract doc exists.
- it distinguishes eval fixture purpose from benchmark purpose.
- it distinguishes vector-ready failures from degraded-mode failures.
- docs remain concise and bounded.

## Rollback
If the slice starts turning into a benchmark redesign or roadmap, revert to the previous docs state and keep only the brief.

## Anti-goals
- do not retune ranking
- do not widen runtime behavior
- do not expand into broad QA framework design
