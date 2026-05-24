# Next slice brief — real-corpus retrieval quality probe v1

## Recommended slice
Add one bounded, read-only real-corpus retrieval quality probe so BrainOS can inspect retrieval behavior on a small sample of naturally accumulated local data without pretending to solve broad evaluation.

## Why this now
The recent hardening run made retrieval/health/vector semantics more explicit and trustworthy. The biggest remaining uncertainty is whether those improved surfaces still hold up on more realistic local-corpus conditions rather than only seeded fixtures.

## Goal
Create a tiny real-corpus probe that gives more honest evidence about retrieval behavior on naturally accumulated data.

## Scope

### Do now
1. Inspect current real-sample retrieval test/probe surfaces.
2. Add one small real-corpus probe path or fixture using realistic local-style examples.
3. Keep it read-only and bounded.
4. Add focused tests/docs.

### Do later
- larger real-corpus suites
- automated corpus sampling
- scoring retune based on probe results

## Acceptance checks
- one bounded real-corpus probe artifact/path exists.
- probe is explicit about being small and non-exhaustive.
- tests stay green.
- no benchmark redesign or ranking retune.

## Rollback
If this starts turning into broad corpus analytics, revert to the previous surfaces and keep only the brief.

## Anti-goals
- do not scrape or ingest large live corpora
- do not broaden into evaluation framework work
- do not change ranking behavior in this slice
