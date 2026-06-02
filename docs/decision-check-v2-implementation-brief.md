# BrainOS decision-check v2 — implementation brief

## Status
Planning brief for the first bounded implementation slice of `decision-check v2`.

This brief follows:
- `docs/decision-check-v2-structured-signal-brief.md`
- `docs/decision-support-contract-v1.md`

It is intentionally narrow.
The goal is to improve precision by changing the structure of signal evaluation, not by widening product scope.

## Slice goal
Refactor `decision-check` so verdicts are driven mainly by structured signals already present in the decision-support object.

This first slice should:
- introduce explicit signal tiers in code/output,
- make structured signals primary,
- demote lexical overlap to weak context only,
- preserve the current CLI surface.

## Why this slice exists
The current checker proved there is value in bounded conflict/caution detection.
But the lexical-rule-heavy model is not a good long-term foundation.

This slice is the smallest useful move that changes the checker’s center of gravity without opening a large redesign.

## Strong boundary
Do:
- keep `decision-check` rule-based and inspectable,
- prefer existing structured fields over lexical heuristics,
- preserve `clear | caution | conflict`,
- keep output reviewable in JSON.

Do not:
- add LLM reasoning,
- add embedding-based contradiction detection,
- invent broad metadata ontologies,
- add new high-level workflow features,
- make text similarity the main driver again.

## Primary structured signals for slice 1
Use only signals already available or trivially derived from existing decision records.

### Strong signals
- shared `metadata.entity_id`
- active/open status on both decisions
- different `recommended_option_id` within shared scope

### Medium signals
- shared option ids across decision briefs
- overlap in explicit metadata tags/refs when already present
- matching review horizon / review_after if present

### Weak signals
- lexical question overlap
- lexical option-label overlap
- wording overlap in arguments/counterarguments

## Recommended verdict rules for slice 1
### Conflict
Emit `conflict` when all of the following are true:
- same `entity_id`
- both decisions are active enough to matter
- different `recommended_option_id`

### Caution
Emit `caution` when there is at least one strong shared-context signal, but the divergence is incomplete or only medium-supported.

Examples:
- same `entity_id`, same recommendation, but overlapping option structure suggests operator review
- same `entity_id`, no recommendation divergence yet, but overlapping option ids and active statuses exist

### Clear
Emit `clear` when there is no strong shared-context signal and only weak lexical similarity is present.

## Output contract adjustment
Preserve the current top-level shape as much as practical:

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

If exact field naming must stay backward-compatible, at minimum:
- keep existing `reasons`
- add explicit tiered signal detail alongside it

The key goal is to make the structure of the checker visible.

## Suggested code changes
Primary file:
- `src/brainos/decision_checks.py`

Likely companion files:
- `src/brainos/store.py` (only if output mapping needs adjustment)
- `src/brainos/cli.py` (only if output contract needs exposure tweaks)
- `tests/test_decision_conflicts.py`

Implementation direction:
1. add explicit signal-bucket helpers
2. compute strong/medium/weak signals separately
3. drive verdict from strong + medium signals
4. keep weak lexical overlap as contextual detail only
5. preserve inspectability in returned findings

## Test plan
### Required tests
1. same `entity_id` + active statuses + different recommendations => `conflict`
2. weak lexical similarity alone => `clear`
3. same scope with no recommendation divergence but overlapping structured option ids => `caution`
4. unrelated decisions with shared generic wording => `clear`
5. output includes tiered signal information or equivalent inspectable structure

### Nice-to-have test
- review_after / metadata ref overlap participates as medium evidence without overpowering missing strong context

## Done definition
This slice is done when:
- `decision-check` is no longer primarily driven by lexical heuristics,
- strong structured signals visibly control the verdict,
- weak text overlap no longer creates most false positives,
- output remains inspectable,
- tests prove the new center of gravity.

## Recommended next move after this slice
After this first v2 slice, the next sensible follow-up would be:
- decision revision/history inspection,

not:
- broader semantic conflict engines,
- LLM reasoning,
- workflow expansion.
