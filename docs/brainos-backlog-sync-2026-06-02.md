# BrainOS backlog sync — 2026-06-02

## Status
Short backlog sync note after the latest bounded BrainOS decision-layer work.

This note exists to prevent queue drift after a concentrated implementation block.

## Current decision-layer state
The decision layer now has:
- decision-support object v1
- decision recall / explain integration
- inspect / provenance
- decision-check v2 slice 1
- decision-history v1
- decision recall quality slice v1
- review + stability review + docs closeout

This is enough to pause broad feature expansion and switch the next pressure source to real usage.

## Queue after sync
### Now
1. bounded real usage of the current decision layer
2. collect friction notes from actual operator use
3. keep watching for missed true conflicts after the comparability-gate fix

### Next
4. decision-history readability improvements
5. decision recall quality cleanup only if repeated misses appear

### Closed since this note
- the bounded `decision-check` calibration block is now closed through structural conflict correction and generic `option_id_overlap` gating; see `docs/decision-check-v2-closeout-2026-06-03.md`.
- the first bounded real-data rerun after the comparability-gate fix passed; see `docs/brainos-realdata-bounded-rerun-2026-06-03-140404.md`.

### Later
6. retrieval credibility maintenance as ongoing discipline
7. broader operational objects only if repeated need appears (`entity`, `blocker`, `focus`)

## Explicitly not next
Do not pull these forward unless usage clearly forces them:
- autonomous decision behavior
- LLM-generated decision briefs
- large semantic conflict engines
- broad workflow/orchestration expansion
- large metadata ontology growth

## Return trigger
Reopen implementation only when one of these happens:
- repeated real usage friction appears,
- repeated decision recall misses appear,
- history readability becomes a real operator problem,
- real-data validation shows systematic `decision-check` caution/conflict error despite the current closeout.

## Bottom line
After this sync and rerun, the correct next move is still not another design loop.
It is bounded real usage with observation.
