# BrainOS decision-check round 2 — corrected calibration retest

## Scope
Retest the same two failure classes after the structural fix to `decision-check`:
- false caution
- missed conflict

Repo: `/home/voytas/projects/brainos`
DB: `/tmp/brainos-decision-check-round2-1780435393.db`

## Cases
- `fc1_same_scope_distinct_queue` — same entity, distinct queue items, no shared option space
- `fc2_shared_scope_weak_text_only` — same entity, weak lexical overlap, reused generic option ids
- `fc3_noncomparable_recommendations` — same entity, different local option spaces, reused generic option ids
- `mc1_shared_options_divergent_recommendations` — same entity, same option space, divergent recommendations
- `mc2_shared_option_space_with_review_overlap` — same entity, same option space, divergent recommendations, same `review_after`
- `mc3_same_scope_same_option_ids_reversed` — same entity, same option ids, reversed recommendation

## Result summary
- Overall: **4 / 6 pass**
- False caution: **1 / 3 pass**
- Missed conflict: **3 / 3 pass**

## Findings

### PASS — false caution
#### `fc1_same_scope_distinct_queue`
Expected: `clear`
Actual: `clear`

The tightened caution gate and comparable-recommendation check removed the earlier false positive when two active decisions shared only entity scope.

### FAIL — false caution
#### `fc2_shared_scope_weak_text_only`
Expected: `clear`
Actual: `caution`

Observed signals:
- strong: `shared_entity_id`, `active_pair`
- medium: `option_id_overlap`
- weak: `question_text_overlap`, `option_text_overlap`
- shared option ids: `A`, `B`

Interpretation:
This is still a false caution. The checker is being pulled upward by **generic local option ids** (`A/B`) that are not semantically meaningful across decisions.

### FAIL — false caution
#### `fc3_noncomparable_recommendations`
Expected: `clear`
Actual: `caution`

Observed signals came from previously inserted same-entity cases using the same generic local option ids (`A/B`).

Interpretation:
The structural fix successfully removed false `conflict` from non-comparable recommendation spaces, but the checker still emits **false caution** because `option_id_overlap` remains too noisy when option ids are local placeholders rather than canonical cross-decision identifiers.

### PASS — missed conflict
#### `mc1_shared_options_divergent_recommendations`
Expected: `conflict`
Actual: `conflict`

Healthy behavior: same entity + active pair + comparable shared option space + divergent recommendations still reaches conflict.

### PASS — missed conflict
#### `mc2_shared_option_space_with_review_overlap`
Expected: `conflict`
Actual: `conflict`

Healthy behavior: review overlap remains secondary; conflict is driven by comparable divergent recommendations.

### PASS — missed conflict
#### `mc3_same_scope_same_option_ids_reversed`
Expected: `conflict`
Actual: `conflict`

Healthy behavior preserved.

## Verdict
The structural fix was correct and necessary, but it **did not improve the aggregate score** on this real-case retest.

What improved:
- false `conflict` from non-comparable recommendation spaces is fixed
- bare shared scope no longer triggers warning by itself

What still fails:
- false `caution` remains dominated by `option_id_overlap` when option ids are generic local placeholders like `A/B`

## Updated recommendation
Next calibration step should be:
1. **demote or gate `option_id_overlap` further**
   - do not treat generic placeholder ids (`A/B/C/...`) as meaningful cross-decision overlap
   - or require an additional structured condition before `option_id_overlap` can contribute to `caution`
2. keep the current comparable-recommendation rule for `conflict`
3. keep `same_entity` as a scope relation, not a warning by itself
4. add this round-2 suite (or a trimmed deterministic version) as a persistent calibration fixture

## Minimal implementation direction
Best next patch candidate:
- tighten `option_id_overlap` so it only counts when the shared option ids look canonical/meaningful, or when there is another reinforcing structured signal besides bare same-scope activity.

## Validation commands
- `.venv/bin/python -m pytest -q tests/test_decision_conflicts.py tests/test_decision_history_cli.py tests/test_operational_recall.py`
- custom round-2 CLI retest on `/tmp/brainos-decision-check-round2-1780435393.db`
