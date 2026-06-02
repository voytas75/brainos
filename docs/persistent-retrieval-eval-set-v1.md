# Persistent retrieval eval set v1

## Status
This document defines the small persistent retrieval eval set that should be treated as the current ranking SSOT.

It is intentionally small.
Its purpose is not broad corpus coverage.
Its purpose is to keep retrieval credibility anchored on a stable, inspectable set of canonical cases.

## Why this exists
BrainOS already has:
- deterministic retrieval eval fixtures,
- a seeded retrieval benchmark,
- retrieval quality / runtime / vector-state contracts.

The next risk is drift in what the benchmark is *for*.
This document freezes the current small set of canonical ranking cases so future scoring work is judged against the same protected retrieval targets.

## Operator rule
When retrieval ranking changes are proposed, interpret quality in this order:
1. runtime posture,
2. freshness posture,
3. persistent eval set results,
4. seeded benchmark results,
5. explain-side diagnosis.

If the persistent eval set regresses, treat that as a stronger warning than a hand-picked one-off example.

## Current canonical case families
The current persistent eval set should protect these families:
1. lexical semantic graph retrieval
2. bootstrap / procedural retrieval
3. embedding / semantic retrieval wording
4. similar-hit disambiguation for runtime-reset phrasing
5. session-filter protection for vector results
6. policy-version wording / explain-surface retrieval
7. nonsense / weak-noise suppression

## Canonical cases
### Case 1 — semantic graph retrieval
- query: `semantic graph`
- expected top episode family: semantic-memory edges content
- expected top semantic family: `Semantic Memory`
- why it matters: protects lexical + semantic graph retrieval from drifting into weaker generic memory hits

### Case 2 — bootstrap / initialization retrieval
- query: `initialize database`
- expected top episode family: bootstrap/init-db/load-state content
- expected top semantic family: `Bootstrap Procedure`
- why it matters: protects procedural retrieval wording and setup-path discoverability

### Case 3 — embedding quality retrieval
- query: `embedding quality`
- expected top episode family: Azure embeddings / semantic recall quality content
- expected top semantic family: semantic-memory concept family
- why it matters: protects retrieval around embedding/quality wording, which is easy to blur with generic recall language

### Case 4 — runtime reset disambiguation
- query: `reset runtime`
- expected top episode family: reset runtime data safely before reindexing
- expected negative nearby distractor: reset browser window size
- expected top semantic family: `Runtime Reset`
- why it matters: protects against similar-hit drift and weak vector-only confusion

### Case 5 — session-filter protection
- query: `reset runtime`
- constrained session: `eval`
- expected behavior: the top result should remain the same-session runtime-reset episode, not the similar other-session hit
- why it matters: protects session isolation and prevents a dangerous class of semantically plausible but wrong cross-session matches

### Case 6 — policy version retrieval
- query: `policy version`
- expected top episode family: retrieval scoring policy visibility in explain output
- expected top semantic family: `Retrieval Scoring Policy`
- why it matters: protects retrieval around self-diagnostic policy wording and explain-surface operator questions

### Case 7 — nonsense / weak-noise suppression
- query: `nonsense request`
- expected behavior: weak far-distance vector-only noise should not become a protected success story
- why it matters: protects against over-reading vector participation as relevance

## Source of truth in code
Current source anchors live in:
- `tests/test_retrieval_eval.py`
- `src/brainos/benchmark.py`

This document is the SSOT for *why* these cases exist and which families are canonical.
Code/tests remain the execution surface.

## What counts as success
A canonical case is considered protected when:
- the expected canonical top episode stays top-ranked,
- and the expected canonical top semantic hit stays top-ranked,
- or, in explicitly negative/noise cases, weak irrelevant vector-only noise stays suppressed.

This is intentionally top-hit-biased.
That is a feature, not a bug, at the current stage.
The current priority is credibility and stability, not broad exploratory shortlist richness.

## How to evolve this set
Do not expand the set casually.

Add or change a case only when at least one of these is true:
- a real operator question recurs,
- a real regression escaped the current protected set,
- a new retrieval surface becomes product-critical,
- an older case is no longer canonical and should be explicitly replaced.

Every change should state:
- what new failure class it protects,
- why the old set was insufficient,
- whether the new case is additive or replaces an older one.

## Non-goals
This eval set is not trying to be:
- a broad benchmark suite,
- a full live-corpus quality proxy,
- a semantic search leaderboard,
- a substitute for explain-side inspection.

## Recommended next implementation alignment
Keep this set small and persistent.
If code alignment is needed next, the most sensible follow-up is:
- make the persistent eval set more explicit in test/benchmark fixtures,

not:
- broaden the set aggressively,
- optimize for arbitrary phrasing coverage,
- weaken the top-hit contract too early.
