# BrainOS post-usage backlog note

## Status
Short backlog note for what should return to the queue after the current decision-layer usage and review cycle.

This is a prioritization note, not a new roadmap.

## Verdict
Do not reopen broad BrainOS feature expansion from momentum alone.

After the current usage/review block, only a small set of follow-up items should come back into the queue.
Those items should be driven by observed friction and credibility needs, not by product breadth.

## Return-to-queue order
### 1. continue bounded real usage and collect friction notes
Reason:
- the key real-data false-`conflict` blocker was removed in the rerun,
- the continuity/current-direction recall slice has now also held up across repeated bounded real-usage runs,
- the next uncertainty is now broader real-case coverage rather than immediate checker redesign,
- the right next pressure is more usage, not another speculative tuning pass.

What to look for:
- missed true `caution`/`conflict` cases,
- repeated false `caution` cases,
- whether `review_after` meaningfully helps,
- whether medium signals still add value after the comparability-gate fix,
- whether signal buckets remain interpretable under more than one workstream.

References:
- `docs/decision-check-v2-closeout-2026-06-03.md`
- `docs/brainos-realdata-bounded-rerun-2026-06-03-140404.md`
- `docs/brainos-real-usage-20260603-194037.md`
- `docs/brainos-real-usage-20260603-194509.md`
- `docs/brainos-real-usage-20260603-195948.md`

### 2. decision-history readability improvements
Reason:
- `decision-history` is already useful,
- but current output is still relatively raw,
- especially for larger field changes.

Candidate improvements:
- cleaner field-diff presentation
- better “last meaningful change” summary
- easier reading of JSON-heavy field changes

### 3. retrieval credibility maintenance
Reason:
- retrieval credibility is still more important than new breadth,
- the bounded continuity/current-direction ranking weakness is now fixed and validated,
- persistent eval set and runtime/health alignment now exist and should stay protected.

What to guard:
- persistent eval set as ranking SSOT
- health-plane separation
- sqlite-vec green path integrity
- continuity/current-direction decision recall behavior after future scoring changes

### 4. only then consider broader operational objects
Reason:
- decision support is ahead of the wider operational layer,
- but there is still no strong evidence yet that `entity`, `blocker`, or `focus` should be the next immediate move.

Condition for return:
- repeated operator need across multiple real cases,
- not architecture enthusiasm alone.

## Explicit deprioritized items
Do not pull these forward unless real usage clearly forces them:
- autonomous decision behavior
- LLM-generated decision briefs
- broad workflow/orchestration layer
- large metadata ontology expansion
- aggressive semantic conflict engines

## Bottom line
After the rerun plus repeated bounded real-usage validation, the queue should reopen in this order:
1. continue bounded real usage and collect friction notes,
2. improve readability of decision history,
3. protect retrieval credibility,
4. only then widen the operational model.
