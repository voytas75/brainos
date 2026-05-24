# Retrieval contract v1

## Purpose
This document defines the current retrieval contract for BrainOS retrieval behavior. It is intentionally short and grounded in the current implementation.

## Inputs
Retrieval accepts:
- `query` text
- optional `session_id`
- result `limit`

## Result shape
Retrieval returns ranked hits drawn from BrainOS memory layers. Current result sets may include:
- episodic hits
- semantic hits

Operator/debug surfaces may also expose score components and retrieval-mode metadata.

## Current retrieval sources
Current retrieval combines:
1. episodic FTS recall
2. semantic-name matching
3. optional sqlite-vec similarity for episodes
4. optional sqlite-vec similarity for semantic nodes

## Fallback posture
- Retrieval must remain valid when sqlite-vec is unavailable.
- Non-vector retrieval is a legitimate degraded mode.
- Vector participation is optional and should improve ranking when available, not define correctness on its own.

## Session filtering
- When `session_id` is provided, retrieval must preserve session isolation for episodic results.
- Vector participation must not bypass session filtering.

## Vector participation rules
- Vector similarity is used only when runtime capability and embedding state permit it.
- Vector-only weak/noise hits should not outrank stronger lexical or semantically grounded matches.
- Vector behavior is additive to retrieval quality, not a replacement for lexical grounding.

## Explainability fields
The operator/debug explain surface should make it possible to inspect:
- why a hit ranked
- which retrieval components participated
- score-component visibility sufficient for debugging bounded ranking changes
- which scoring policy version was active for the result

## Protected quality expectations
The current protected baseline covers:
- lexical semantic graph query cases
- procedural/bootstrap query cases
- embedding/semantic quality query cases
- competing similar-hit cases
- session-filter protection for vector results
- weak vector-only noise suppression

## Top-hit success
A protected retrieval case is considered successful when the expected canonical top hit for that case remains the top-ranked result under the current bounded eval/benchmark suite.

## Out of scope for v1
This contract does not yet define:
- broad semantic graph traversal guarantees
- procedural retrieval sophistication
- broad relevance guarantees outside the protected eval/benchmark corpus
- external API contracts

## Scoring policy surface
Current retrieval scoring behavior is grouped under an explicit policy surface.

Current active version:
- `retrieval-scoring-v1`

This version label improves explainability and tuning governance without changing retrieval behavior on its own.

## Stability note
This contract should stay stable across small tuning/refactor changes unless there is an intentional contract revision.
