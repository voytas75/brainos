# BrainOS decision-check round 2b — option-id overlap calibration patch

## Scope
Retest the real-case calibration suite after tightening `option_id_overlap` so generic local placeholder ids (`A/B/C/...`) no longer count as a medium cross-decision signal.

Repo: `/home/voytas/projects/brainos`
DB: `/tmp/brainos-decision-check-round2b-1780435393.db`

## Patch applied
File: `src/brainos/decision_checks.py`

Change:
- added `_meaningful_shared_option_ids(...)`
- treat `option_id_overlap` as a medium signal only when the shared option ids are **not** generic single-letter placeholders like `A/B/C`
- preserve comparable recommendation logic for `different_recommendations`
- expose `meaningful_shared_option_ids` in findings for inspectability

Rationale:
- generic local option ids are too noisy to act as structured cross-decision overlap
- they are often just per-decision labels, not canonical shared semantics

## Regression coverage
File: `tests/test_decision_conflicts.py`

Added/updated coverage for:
- caution when overlap uses meaningful canonical option ids
- clear when overlap is only generic placeholder ids in same entity scope

Focused pytest result:
- `.venv/bin/python -m pytest -q tests/test_decision_conflicts.py tests/test_decision_history_cli.py tests/test_operational_recall.py`
- **13 passed**

## Cases
- `fc1_same_scope_distinct_queue`
- `fc2_shared_scope_weak_text_only`
- `fc3_noncomparable_recommendations`
- `mc1_shared_options_divergent_recommendations`
- `mc2_shared_option_space_with_review_overlap`
- `mc3_same_scope_same_option_ids_reversed`

## Result summary
- Overall: **6 / 6 pass**
- False caution: **3 / 3 pass**
- Missed conflict: **3 / 3 pass**

## Interpretation
The patch fixed the remaining practical false-caution issue in this suite without regressing the current missed-conflict cases.

Important nuance:
- conflict still works for shared generic option ids when recommendations are comparable, because conflict is driven by `different_recommendations` on the shared option space
- caution no longer opens just because two same-entity decisions both happen to use local placeholder ids like `A/B`

## Remaining caution
This is still a bounded calibration result, not proof of general correctness.
The next sensible step is to keep this suite as a persistent regression/calibration fixture and only broaden the checker if real usage reveals new miss patterns.

## Validation commands
- `.venv/bin/python -m pytest -q tests/test_decision_conflicts.py tests/test_decision_history_cli.py tests/test_operational_recall.py`
- custom real-case retest on `/tmp/brainos-decision-check-round2b-1780435393.db`
