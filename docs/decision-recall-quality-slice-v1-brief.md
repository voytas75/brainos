# BrainOS decision recall quality slice v1 — brief

## Status
Planning brief for the next bounded quality slice focused on decision-object reachability in `recall` / `retrieval-explain`.

This brief follows the diagnostic result that decision storage/inspect/history/check are already useful, but natural-question reachability for decision objects is still too weak.

## Problem
Current decision recall is not reliable enough for natural phrasing.

Observed pattern:
- direct phrase hits from option/argument wording can work,
- broader or paraphrased decision questions often miss entirely,
- this makes the decision layer operationally weaker than it should be.

So the problem is not decision storage.
The problem is **decision retrieval reachability**.

## Goal
Improve `recall` / `retrieval-explain` so stored decision briefs are easier to find from natural operator questions, without widening the product scope or adding heavy semantic machinery.

## Strong boundary
Do:
- improve decision-object retrieval using a better text representation,
- keep the path inspectable and deterministic,
- add bounded regression tests for natural-ish decision queries,
- preserve the existing decision object contract.

Do not:
- add LLM rewriting/generation,
- build a separate large semantic retrieval subsystem just for decisions,
- hide the problem behind broader embeddings-first claims,
- widen the decision product surface.

## Core idea
Treat each decision brief as a better retrieval document.

Instead of searching loosely across scattered raw fields, create a **canonical decision retrieval text projection** that combines the most important parts of the brief into one stable text surface.

## Proposed slice
### 1. Add decision retrieval text projection
Create a canonical text projection for each decision using at least:
- question
- recommended option id / label if available
- option labels
- argument text
- counterargument text
- risk text
- missing-information text
- uncertainty notes
- selected metadata refs when useful (for example `entity_id`)

This projection should be deterministic and inspectable.

### 2. Improve decision search over the projection
Replace or reduce the current shallow decision search path based on direct ad-hoc substring checks.

For v1, a good bounded path is:
- normalize query
- search against the projection text
- use token overlap / ranking that is slightly smarter than plain substring containment
- keep the algorithm understandable

### 3. Add regression cases for decision reachability
Protect at least these query types:
- natural paraphrase of the decision question
- query based on the recommended action
- query based on a deferred alternative
- query based on backlog framing / review wording
- query based on a risk/deprioritized path

## Why this is the right next quality slice
Because the current decision layer already has:
- storage
- inspect
- history
- conflict checking

What is underperforming is not breadth.
It is reachability.

Improving reachability strengthens the existing layer instead of expanding into new features.

## Candidate implementation shape
Primary likely files:
- `src/brainos/store.py`
- `src/brainos/retrieval.py`
- `src/brainos/explain.py`
- tests for operational recall / decision recall

Possible helper:
- a small decision projection helper inside `store.py` or a dedicated `decisions.py` helper if that keeps code cleaner

## Suggested minimal output expectations
No big contract rewrite is needed.

Success for this slice means:
- `recall` starts surfacing decision objects for more natural decision-related queries,
- `retrieval-explain` shows the same decision object in `top_decisions`,
- the retrieval path remains inspectable.

## Test expectations
Minimum useful tests:
1. natural paraphrase of a stored decision question finds the decision
2. query based on recommended action finds the decision
3. query based on a deferred alternative finds the decision
4. query based on risk/deprioritized language finds the decision
5. weak/noise query still does not create false positive success

## Done definition
This slice is done when:
- decision reachability improves for natural operator phrasing,
- retrieval/explain behavior is covered by small regression tests,
- the solution remains deterministic and reviewable,
- no broad semantic or product-scope expansion is introduced.

## Recommended follow-up after this slice
If this quality slice lands well, the next sensible move is not a new big feature.
It is either:
- small retrieval-quality cleanup from observed misses,
- or pause and real usage again.
