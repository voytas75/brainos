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

### Next
3. decision-check calibration from real cases
4. decision-history readability improvements
5. decision recall quality cleanup only if repeated misses appear

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
- decision-check calibration shows systematic caution/conflict error.

## Bottom line
After this sync, the correct next move is not another design loop.
It is real usage.
