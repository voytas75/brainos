# BrainOS decision-support v1 review

## Status
Short review note after the initial decision-support implementation block.

This is a bounded review artifact, not a new product spec.

## Verdict
The current `decision-support` direction is good and should be kept.

The work is coherent because it now has:
- a clear product boundary,
- a first-class stored object,
- bounded retrieval/explain support,
- provenance drill-down,
- a simple conflict-check surface,
- repo-facing docs that no longer lag the implementation.

The result is not a full operational command center.
That is good.
It is a cleaner and more honest product slice than pushing prematurely toward autonomous decision-making.

## Must keep
### 1. Operator-first boundary
Keep the rule that BrainOS may recommend but does not make the final choice.

Why it matters:
- prevents fake authority,
- keeps uncertainty visible,
- matches the actual quality level of the system,
- protects future product trust.

Concrete keepers:
- `operator_call_required`
- `recommended_option_id` as recommendation only
- explicit `missing_information`
- explicit `uncertainty_notes`

### 2. First-class `decisions`
Keep the dedicated `decisions` table and CLI surface.

Why it matters:
- avoids drifting back into vague episode metadata,
- creates a clean object boundary for future retrieval/provenance/conflict work,
- makes the product surface inspectable.

Concrete keepers:
- `decision-log`
- `decision-list`
- `decision-get`

### 3. Provenance drill-down
Keep `inspect` as a first-class user-facing feature.

Why it matters:
- provenance is one of BrainOS’s real advantages,
- it turns storage discipline into visible product value,
- it helps debug recommendation quality without marketing language.

Concrete keeper:
- `inspect decision <id>`

### 4. Rule-based `decision-check`
Keep the checker as a bounded, inspectable operator aid.

Why it matters:
- it adds practical value without pretending to be strategic intelligence,
- it is inspectable and testable,
- it fits the current maturity level of the repo.

Concrete keeper:
- `decision-check`
- classes: `clear | caution | conflict`

Direction note:
- the v1 lexical/rule-heavy posture should not be treated as the long-term model,
- the intended next design direction is `decision-check v2` as a structured-signal checker,
- see `docs/decision-check-v2-structured-signal-brief.md`.

## Freeze / simplify for now
### 1. Do not add autonomous decision behavior
Do not move toward:
- system-owned final choice,
- hidden policy engines,
- opaque score-driven public behavior,
- auto-execution from recommendation.

Reason:
That would expand the claim faster than the evidence.

### 2. Do not overgrow `decision-check`
Do not turn it into:
- broad semantic contradiction analysis,
- LLM-based reasoning,
- a pseudo-strategic evaluator,
- a noisy warning engine.

Reason:
The current version is useful because it is small and legible.

### 3. Do not add LLM-generated decision briefs yet
Reason:
The storage/retrieval/provenance contract should stabilize before generation enters the loop.
Otherwise the product boundary becomes blurry too early.

### 4. Do not open `focus` yet
Reason:
Without `entity` and `blocker` being equally real objects, `focus` risks becoming a premature UX shell over incomplete operational state.

## Main risk
The main risk is not technical failure.
The main risk is **product over-claim**.

If the next slices imply that BrainOS now “decides” rather than “supports decisions”, the product will drift away from its strongest honest posture.

That drift would likely show up first in:
- too much confidence in recommendation wording,
- expanding `decision-check` beyond inspectable rules,
- introducing orchestration/focus surfaces before the underlying operational model is ready.

## Current quality assessment
Current state looks:
- coherent,
- appropriately scoped,
- honest about uncertainty,
- structurally useful.

This is a good v1 shape.
Not because it does everything, but because it does a small set of things clearly and inspectably.

## What should change only after real usage
Only revisit the next step after there is real operator usage against stored decisions.

Good future signals:
- repeated need to link multiple decisions to one shared entity,
- repeated need to inspect decision revisions over time,
- repeated false positives / false negatives in `decision-check`,
- repeated operator demand for “what is active now?” across multiple objects.

Those signals would justify the next layer.
Not roadmap enthusiasm alone.

## Recommended next move
Pause implementation briefly and use the current decision-support layer in real bounded cases.

Do not add another major slice immediately unless usage reveals a clear missing surface.

If one next technical move is still needed after usage, the best candidate is:
- better decision revision/history inspection,

not:
- autonomous choice,
- more hidden scoring,
- broader workflow theater.
