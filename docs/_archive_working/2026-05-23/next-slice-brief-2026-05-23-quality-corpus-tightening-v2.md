# Next slice brief — quality corpus tightening v2

## Recommended slice
Add a few higher-value retrieval quality cases that increase ambiguity coverage without turning the benchmark/eval suite into a broad research corpus.

## Why this now
BrainOS now has clearer retrieval contracts, health semantics, backend boundaries, scoring-policy visibility, and vector-state semantics. The next maturity gap is still quality anchoring: the current protected corpus is useful but still too narrow.

## Goal
Strengthen retrieval quality protection with a few realistic ambiguity cases while preserving bounded test posture.

## Scope

### Do now
1. Inspect the current eval and real-sample corpus for the highest-value missing ambiguities.
2. Add only a few cases that exercise realistic retrieval competition.
3. Keep fixtures deterministic and narrow.
4. Keep ranking behavior unchanged.

### Do later
- larger ambiguity suites
- corpus tooling/refactoring
- more realistic mixed-session datasets

## Acceptance checks
- at least a few realistic ambiguity cases are added.
- existing bounded eval posture remains understandable.
- tests stay green.
- no scoring retune in this slice.

## Rollback
If the corpus starts turning into a broad benchmark redesign, revert to the previous fixture set and keep only the brief/inspection notes.

## Anti-goals
- do not widen into research benchmarking
- do not retune ranking
- do not add runtime complexity
- do not expand product surface
