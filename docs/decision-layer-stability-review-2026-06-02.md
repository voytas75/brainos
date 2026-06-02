# BrainOS decision layer stability review — 2026-06-02

## Status
Short stability review after the latest bounded decision-layer slices, including:
- decision-support object v1
- structured-signal `decision-check` v2 slice 1
- `decision-history` v1
- decision recall quality slice v1

This is a review note, not a new contract.

## Verdict
The decision layer is now **stable enough for bounded real usage**.

Not “finished”.
Not “broad”.
But stable enough that the next meaningful improvements should come from observed usage friction rather than speculative redesign.

## What is now stable enough
### 1. Decision storage contract
The core decision object shape is stable enough to use.

Why:
- it captures question / options / recommendation / risk / uncertainty,
- it is already tested,
- recent slices strengthened retrieval and history without forcing schema churn.

### 2. Provenance and inspectability
This part is solid.

Why:
- writes are ledger-backed,
- `inspect` works,
- `decision-history` reconstructs a usable change view,
- the layer is auditable instead of opaque.

### 3. Retrieval reachability is materially better
The decision recall quality slice improved the weakest earlier gap.

Why:
- there is now a canonical retrieval projection,
- naturalish paraphrase queries are better covered,
- explain-side surfacing is more credible than before.

This area is improved enough to count as usable, even if still not perfect.

### 4. Decision-check has a healthier foundation
It is more stable directionally because it is no longer centered on ad-hoc lexical patching.

Why:
- structured signals now drive the verdict,
- lexical overlap is weak/contextual,
- the checker is still inspectable and bounded.

That is a much better stability posture than the earlier token-tuning path.

## What is still not fully stable
### 1. decision-check calibration
The checker direction is good, but calibration still needs more pressure from real cases.

Open risk:
- some `caution` cases may still be too eager or not eager enough depending on how decisions cluster in practice.

### 2. decision-history readability
History is functionally useful, but presentation is still basic.

Open risk:
- larger JSON field changes may become hard to read as real usage grows.

### 3. decision retrieval coverage
Reachability is improved, but not yet something to overclaim as “solved”.

Open risk:
- natural phrasing that is further from the canonical projection may still miss.

## What should not happen now
Do not respond to this improved stability by immediately widening scope into:
- autonomous decision behavior,
- LLM-generated decision briefs,
- broad workflow/orchestration surfaces,
- large new operational object families without pressure.

That would turn stability into drift.

## Recommended posture after this review
Use the current decision layer in bounded real scenarios.

If more work is needed later, prioritize:
1. calibration of existing quality surfaces,
2. readability improvements,
3. only then broader expansion.

## Bottom line
The decision layer is now in a good state:
- stable enough to use,
- stable enough to review,
- not stable enough to oversell.

That is the right place to be.
