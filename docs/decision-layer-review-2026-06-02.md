# BrainOS decision layer review — 2026-06-02

## Status
Short review after the current bounded implementation block covering:
- decision-support object v1
- decision recall/explain
- inspect/provenance
- decision-check v2 slice 1
- decision-history v1

This is a review note, not a new product contract.

## Verdict
The current decision layer is now **good enough to be useful and structurally honest**.

It is not complete, and it should not yet be presented as a full decision system.
But it is no longer a sketch.
It now has a coherent operator-facing spine.

## What is already quite good
### 1. The product boundary is clear
This is one of the strongest improvements.

The layer is now explicitly:
- decision support,
- recommendation-oriented,
- operator-final,
- provenance-aware.

That prevents a lot of future confusion and overclaim.

### 2. Decision is a real first-class object
This was the right move.

The `decisions` table plus:
- `decision-log`
- `decision-list`
- `decision-get`

turned the layer from idea-space into usable product surface.

### 3. Retrieval/explain integration is useful and improved, but not fully solved
Decision objects are not just storable; they are reachable through:
- `recall`
- `retrieval-explain`

That matters because it makes the layer operational instead of archival.

Recent diagnostic testing exposed uneven reachability for natural paraphrases and backlog-style wording.
The bounded retrieval-quality slice improved that gap through a canonical decision retrieval projection and regression coverage.
So this area is now materially better, but should still be treated as usage-sensitive rather than fully solved.

### 4. Inspect/provenance is a real strength
`inspect` and ledger linkage are already one of the most credible parts of the layer.

This is product value, not just engineering neatness.

### 5. Decision-check is in a healthier direction now
The important improvement is not perfection.
The important improvement is that the checker is now structured-signal-first instead of mostly lexical patching.

That gives it a better long-term foundation.

### 6. Decision history is now meaningfully useful
`decision-history` crossed an important threshold:
- we can see revisions,
- compare `current` vs `previous`,
- and see `changed_fields`.

That is already enough to support real operator review.

## What still needs work
### 1. Decision-check still needs validation pressure
The design direction is better, but it still needs more real usage.

Open questions:
- are the strong/medium/weak buckets calibrated well enough?
- is `caution` still too eager in some same-scope cases?
- is `review_after` actually useful as medium evidence or just technically available?

So this part is improved, but not yet fully trusted.

### 2. History is useful, but still shallow
Current `decision-history` is good as v1, but it is still basic.

Missing / future possibilities:
- better field-level diff formatting
- “last meaningful change” summaries
- cleaner display for large JSON field changes
- maybe later: explicit revision summaries

This is fine for now, but it is not finished.

### 3. Revision semantics are ledger-derived, not yet explicit
This is a good tradeoff for now.
But it means history is reconstructed rather than modeled directly.

That is acceptable at this stage, but should remain visible as a design constraint.

### 4. The wider operational layer is still intentionally incomplete
The decision layer is ahead of the rest of the operational model.
That is okay.
But it means:
- no mature `entity` layer yet,
- no mature `blocker` layer yet,
- no real `focus` surface yet.

So decision support is ahead of the surrounding orchestration model.

## Current quality judgment
Current quality is:
- **good enough to use**,
- **good enough to validate further through practice**,
- **not good enough to overclaim**.

That is a healthy place to be.

## Recommended posture
Treat this decision layer as:
- stable enough for bounded real usage,
- mature enough for reviews and retrieval continuity,
- still immature enough that future changes should be driven by observed operator friction, not roadmap excitement.

## Recommended next work principle
Do not open a broad new decision feature set immediately.

If work continues later, the best next moves should be chosen from:
1. targeted refinement from real usage,
2. improved history readability,
3. only then broader operational objects if truly needed.

## Bottom line
The decision layer is no longer the weak part of BrainOS.

Its biggest value now is that it is:
- bounded,
- inspectable,
- structurally honest,
- and already useful.

That is enough to pause, use it, and let real usage decide the next improvement.
