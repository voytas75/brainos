# BrainOS decision-check v2 — structured-signal brief

## Status
Planning brief for replacing the current rule-heavy lexical caution/conflict checker with a more structured, inspectable signal model.

This is a design brief, not an implementation claim.

## Why this brief exists
`decision-check v1` proved that a bounded checker can be useful.
It can catch obvious same-entity competing recommendations.

But the current v1 direction is weak as a long-term model because it leans too much on manually tuned lexical overlap rules.
That creates avoidable risks:
- brittle maintenance,
- overfitting to recent examples,
- hidden drift in stopword lists,
- a false sense of precision.

## Problem statement
The checker should answer a narrow question:

**Does this decision brief materially collide with another active decision brief in a way the operator should notice?**

That is not the same as:
- semantic similarity scoring,
- broad contradiction detection,
- freeform reasoning,
- strategic judgment.

## Product boundary
Decision-check v2 should:
- compare explicit structured decision signals first,
- stay inspectable,
- produce bounded `clear | caution | conflict` outcomes,
- preserve reason traceability,
- use lexical/text overlap only as a weak fallback signal.

Decision-check v2 should not:
- become an LLM-based decision critic,
- depend on large stopword inventories,
- pretend to infer hidden policy/preferences,
- auto-resolve conflicts,
- replace operator judgment.

## Core design principle
**Strong structured signals open findings. Weak lexical signals only support them.**

This is the central shift from v1.

## Signal hierarchy
### Tier 1 — strong signals
These may open a finding on their own.

Candidate strong signals:
- shared `entity_id`
- explicit shared scope reference in metadata
- same decision family / kind (if later added)
- same canonical question fingerprint (if later added)
- divergent `recommended_option_id` within a shared scope
- active statuses on both decisions

### Tier 2 — medium signals
These should usually reinforce a finding that already has at least one strong signal.

Candidate medium signals:
- option-id overlap
- explicit shared metadata tags
- overlap in structured argument refs/evidence refs
- matching review horizon / temporal frame
- similar decision status posture in the same scope

### Tier 3 — weak signals
These should not open a finding on their own.
They may only add context to an existing strong or medium case.

Candidate weak signals:
- lexical question overlap
- lexical option-label overlap
- free-text argument wording overlap
- general semantic similarity cues

## Minimal v2 input model
Decision-check v2 should prefer data already available in the stored decision-support object.

Existing likely-usable fields:
- `decision_id`
- `question`
- `status`
- `recommended_option_id`
- `operator_call_required`
- `options`
- `arguments`
- `counterarguments`
- `risks`
- `missing_information`
- `metadata`

Primary near-term structured anchors:
- `metadata.entity_id`
- `recommended_option_id`
- `status`
- option ids
- metadata refs/tags where present

## Recommended verdict logic
### `clear`
Return `clear` when:
- there is no strong shared scope signal,
- or there is no meaningful divergence,
- and any similarity is only weak lexical similarity.

### `caution`
Return `caution` when:
- there is at least one strong structured shared-context signal,
- but the divergence is incomplete, ambiguous, or only partly evidenced,
- or there are medium supporting signals that suggest operator review is prudent.

### `conflict`
Return `conflict` when:
- there is a strong shared scope signal,
- both decisions are active enough to matter,
- and there is explicit structured divergence that materially points in different directions.

The most obvious early `conflict` rule remains:
- same `entity_id`
- active/open statuses
- different `recommended_option_id`

## Inspectability contract
Every finding should remain explainable in plain JSON.

Recommended output shape:
```json
{
  "decision_id": "dec-123",
  "verdict": "caution",
  "finding_count": 1,
  "findings": [
    {
      "decision_id": "dec-456",
      "severity": "caution",
      "strong_signals": ["shared_entity_id"],
      "medium_signals": ["option_id_overlap"],
      "weak_signals": ["question_text_overlap"],
      "recommended_option_id": "B",
      "entity_id": "brainos"
    }
  ]
}
```

The important change is not the exact field names.
The important change is the explicit signal tiers.

## Migration plan from v1
### Step 1
Stop investing further in lexical stopword tuning as the primary path.

### Step 2
Refactor the checker around signal buckets:
- strong
- medium
- weak

### Step 3
Make the verdict depend primarily on strong + medium structured evidence.

### Step 4
Demote lexical overlap to weak contextual evidence only.

### Step 5
Update tests so they prove:
- structured same-scope divergence still triggers `conflict`,
- weak text overlap alone stays `clear`,
- medium evidence cannot silently masquerade as strong evidence.

## Recommended first implementation slice
Do **not** try to solve all future signal richness at once.

The best first v2 slice is:
1. define signal buckets in code,
2. use `entity_id`, `status`, `recommended_option_id`, and option ids as the primary structured inputs,
3. demote lexical overlap to weak-only context,
4. preserve the current CLI/output contract as much as practical.

## Explicit anti-goals
- no LLM classifier
- no semantic-embedding conflict engine
- no huge stopword dictionaries
- no broad metadata ontology before usage proves the need
- no hidden confidence theater

## Done definition for v2 direction
This direction is successful when:
- conflict/caution outcomes are driven mainly by structured decision facts,
- lexical similarity no longer drives most false positives,
- the output stays inspectable,
- and the checker remains a bounded operator aid rather than pseudo-strategic intelligence.
