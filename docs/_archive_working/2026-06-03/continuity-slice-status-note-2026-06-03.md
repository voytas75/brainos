# BrainOS continuity/current-direction slice status note — 2026-06-03

## Status
- area: `decision recall`
- slice: `continuity/current-direction ranking`
- verdict: `operationally stable`
- confidence: `medium-high`

## Why this note exists
This note records the current operator judgment after the continuity/current-direction retrieval weakness was fixed and then pressure-tested with repeated bounded real-usage runs.

## Current judgment
Treat the continuity/current-direction decision-recall slice as operationally stable for normal bounded usage.

That does **not** mean the broader retrieval system is finished.
It means this specific weakness is no longer the best next tuning target unless new real friction appears.

## Evidence basis
### 1. Original failure was real and repeated
- `docs/friction/2026-06-03-recall-continuity-ranking-weakness.md`
- `docs/brainos-recall-continuity-usage-2026-06-03-163928.md`
- `docs/brainos-recall-continuity-rerun-2026-06-03-164137.md`

### 2. Bounded fix was applied narrowly
- code path: `src/brainos/store.py`
- scope: decision recall ranking only
- anti-goals respected: no broad recall redesign, no ontology work, no `decision-check` changes

### 3. Focused regression gates stayed green
- `tests/test_operational_recall.py`
- `tests/test_explain_cli.py`
- `tests/test_retrieval_eval.py`
- `tests/test_retrieval_real_sample.py`
- latest focused result during closeout: `18 passed`

### 4. Repeated bounded real-usage runs passed
- `docs/brainos-real-usage-20260603-194037.md`
- `docs/brainos-real-usage-20260603-194509.md`
- `docs/brainos-real-usage-20260603-195948.md`

Across those runs, the key protected behaviors held:
- current-direction wording retrieved the current-direction decision first
- keep-doing wording retrieved the current-direction decision first
- next-step wording retrieved the rerun/follow-up decision first
- earlier-step wording still preferred the closeout-first decision when included in the chain
- retrieval health remained `ok`

## What this changes operationally
### Do now
- continue normal bounded real usage
- open new friction notes only for real trust-relevant failures
- keep protecting continuity/current-direction behavior in future retrieval tuning

### Do not do now
- do not reopen continuity tuning just because more improvements are imaginable
- do not widen into broad retrieval redesign without fresh evidence
- do not treat this slice as the main blocker anymore

## Return trigger
Reopen this slice only if one of the following appears in real usage:
- repeated wrong top-hit ordering for continuity/current-direction questions
- regression where earlier-step / next-step separation collapses
- strong evidence that a broader recall-scoring interaction is undoing this fix

## Bottom line
As of 2026-06-03, the continuity/current-direction retrieval slice should be considered good enough for normal bounded BrainOS usage.
