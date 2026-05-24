# Next slice brief — benchmark seeding / fixture truthfulness v1

## Recommended slice
Make benchmark and health output more explicit about seeded-fixture truthfulness so operators do not over-read seeded benchmark results as evidence about the current user database corpus.

## Why this now
BrainOS now distinguishes low-evidence database posture from ordinary quality regression, but the benchmark still seeds its own bounded corpus. Without an explicit truthfulness note, operators could conflate implementation-level seeded benchmark success with real-corpus evidence.

## Goal
Separate seeded benchmark evidence from live database evidence more explicitly in current operator surfaces.

## Scope

### Do now
1. Add explicit seeded-fixture metadata to benchmark output.
2. Surface the same truthfulness note through retrieval health quality output.
3. Keep semantics bounded and docs-first.
4. Add focused tests.

### Do later
- alternate real-corpus benchmark modes
- corpus sufficiency scoring
- benchmark history/trending

## Acceptance checks
- benchmark output clearly says it uses seeded fixtures.
- retrieval health quality output preserves that distinction.
- tests stay green.
- no benchmark redesign.

## Rollback
If this turns into multi-mode benchmarking or corpus analytics, revert to the simpler benchmark surface and keep only the brief.

## Anti-goals
- do not change retrieval behavior
- do not redesign the benchmark workflow
- do not pretend seeded benchmark proves live corpus quality
