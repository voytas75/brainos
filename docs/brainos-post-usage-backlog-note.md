# BrainOS post-usage backlog note

## Status
Short backlog note for what should return to the queue after the current decision-layer usage and review cycle.

This is a prioritization note, not a new roadmap.

## Verdict
Do not reopen broad BrainOS feature expansion from momentum alone.

After the current usage/review block, only a small set of follow-up items should come back into the queue.
Those items should be driven by observed friction and credibility needs, not by product breadth.

## Return-to-queue order
### 1. decision-check calibration from real usage
Reason:
- `decision-check` is in a healthier direction after v2 slice 1,
- but it still needs validation pressure from real cases,
- especially around `caution` calibration and the usefulness of medium signals.

What to look for:
- whether `different_recommendations` is only treated as structured divergence when the decisions share a comparable option space,
- whether bare shared scope is opening `caution` before there is enough structured evidence,
- false `caution` cases
- missing `caution`/`conflict` cases
- whether `review_after` meaningfully helps
- whether medium signals like `option_id_overlap` are actually helping after the caution gate is tightened
- whether signal buckets remain interpretable

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
- persistent eval set and runtime/health alignment now exist and should stay protected.

What to guard:
- persistent eval set as ranking SSOT
- health-plane separation
- sqlite-vec green path integrity

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
After usage, the queue should reopen in this order:
1. improve the precision and trust of what already exists,
2. improve readability of decision history,
3. protect retrieval credibility,
4. only then widen the operational model.
