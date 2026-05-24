# Next slice brief — empty-db / low-evidence health semantics v1

## Recommended slice
Tighten retrieval-health semantics so fresh or low-evidence databases are not reported as if they were ordinary retrieval-quality regressions.

## Why this now
BrainOS health/quality operator surfaces are now much clearer, but the current semantics can still over-warn on a fresh database where there is simply not enough retrieval evidence yet.

## Goal
Distinguish low-evidence/empty-db posture from real retrieval-quality regression posture.

## Scope

### Do now
1. Inspect current retrieval-health behavior on fresh DB semantics.
2. Add a bounded low-evidence classification.
3. Prevent ordinary quality-regression interpretation when evidence is insufficient.
4. Add focused tests and light docs alignment.

### Do later
- richer corpus sufficiency thresholds
- benchmark seeding-mode distinctions
- historical evidence tracking

## Acceptance checks
- retrieval-health can report low-evidence posture explicitly.
- fresh DB does not look like an ordinary quality regression.
- tests stay green.
- no redesign of benchmark corpus.

## Rollback
If this turns into corpus analytics or benchmark redesign, revert to the prior semantics and keep only the brief.

## Anti-goals
- do not redesign the benchmark suite
- do not add dynamic thresholds beyond a small bounded rule
- do not retune retrieval behavior
