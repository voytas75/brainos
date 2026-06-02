# BrainOS decision-support contract v1

## Status
Planning / contract draft.

This document defines the intended product boundary for the future `decision` layer.
It is not evidence that the CLI/model already exists.

Use this contract to keep future implementation aligned with the real product promise.

## Core claim
BrainOS decision support helps an operator think and choose more clearly.
It does **not** claim autonomous authority to make the final decision.

## Product boundary
BrainOS should:
- surface candidate options relevant to a decision question,
- show supporting arguments and counterarguments,
- preserve visible constraints, risks, and missing information,
- produce a recommendation when support is strong enough,
- keep provenance and inspectability visible,
- leave the final choice to the operator.

BrainOS should not:
- present one opaque score as unquestionable truth,
- equate retrieval similarity with a valid decision,
- auto-execute from a recommendation without separate confirmation,
- pretend hidden preferences or values were resolved when they were not,
- market suggestion quality as autonomous strategic thinking.

## Core operator rule
`decision` is a decision-support artifact, not an auto-decider.

The minimal honest promise is:
1. frame the question,
2. show options,
3. show why each option is supported or risky,
4. show what is still unknown,
5. recommend cautiously when evidence is sufficient,
6. require an operator call for the final choice.

## Separation of responsibilities
### Retrieval layer
Responsible for finding relevant evidence, prior records, constraints, heuristics, and related operational objects.

### Decision-support layer
Responsible for structuring the decision brief from that evidence.

### Operator layer
Responsible for the final commitment / approval / choice.

This separation must stay visible in code, CLI shape, and docs.

## Minimal output contract
A future `decision-get` / `decision-brief` style surface should return a shape equivalent to:

```json
{
  "decision_id": "dec-123",
  "question": "Which next slice should we choose?",
  "status": "draft",
  "operator_call_required": true,
  "recommended_option_id": "A",
  "recommendation_confidence": "medium",
  "options": [
    {
      "option_id": "A",
      "label": "Improve retrieval credibility first",
      "summary": "Smallest reversible slice with direct trust impact",
      "supporting_arguments": [
        "Matches time constraint",
        "Directly improves trustworthiness"
      ],
      "counterarguments": [
        "Does not improve UI immediately"
      ],
      "risks": [
        "May not visibly change user experience right away"
      ],
      "fit_signals": [
        "small_effort",
        "high_trust_impact"
      ],
      "confidence": "medium"
    }
  ],
  "constraints": [],
  "missing_information": [],
  "uncertainty_notes": [],
  "evidence_refs": []
}
```

Exact field names may change during implementation, but the contract must preserve these ideas:
- question framing,
- multiple options,
- explicit support and objections,
- visible uncertainty,
- explicit recommendation,
- explicit operator boundary.

## Required semantics
### `operator_call_required`
Must default to `true` for decision-support outputs.

This field exists to prevent future drift toward implicit autonomous authority.

### `recommended_option_id`
Recommendation is allowed.
Finality is not.

### `confidence`
Confidence describes support quality, not certainty of truth.
Allowed values may be enum/string/number later, but they must remain interpretable.

### `missing_information`
Absence of key data must stay explicit.
The system should not silently collapse uncertainty into recommendation tone.

## Evidence mapping rule
Future implementation should distinguish at least these categories when building a decision brief:
- option
- constraint
- risk
- heuristic
- evidence
- prior decision
- blocker
- entity context

A recommendation should be traceable back to these categories.

## Evaluation rule
Do not evaluate the decision layer only by top-1 choice accuracy.

Primary evaluation questions should be:
- Were the relevant options surfaced?
- Were critical constraints preserved?
- Were supporting arguments grounded in evidence?
- Were counterarguments and risks visible?
- Was uncertainty shown honestly?
- Was the recommendation directionally sensible?
- Could an operator inspect why the recommendation appeared?

Top-1 choice can still be a secondary metric, but it must not define success by itself.

## Non-goals for v1
- autonomous final decision making
- hidden policy engine over implicit user values
- opaque single-score optimizer as the public contract
- automatic transition from recommendation to execution
- replacing operator judgment in ambiguous situations

## Design consequence
If retrieval quality is strong but automatic choice quality is weak, the product should still succeed as decision support.

That is not a fallback story.
That is the intended honest product boundary.
