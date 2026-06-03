# BrainOS friction note — decision-check false conflict on adjacent workflow decisions

## Status
- date: 2026-06-03
- area: `decision-check`
- severity: `high`
- verdict: `closed`

## Real case
- operator task: verify whether BrainOS decision-check was trustworthy enough for bounded real usage after the documentation/closeout block
- expected BrainOS help: flag only real same-frame caution/conflict, not adjacent workflow decisions in the same workstream
- actual behavior: `decision-check` returned `conflict` for a small cluster of related workstream decisions that were sequential/adjacent rather than clearly contradictory within one comparable decision frame

## Reproduction
- db path: `/tmp/brainos-realdata-bounded-1780474190.db`
- commands used:
  - `uv run brainos --db /tmp/brainos-realdata-bounded-1780474190.db decision-check dec-doc-closeout`
  - `uv run brainos --db /tmp/brainos-realdata-bounded-1780474190.db decision-check dec-realdata-test`
  - `uv run brainos --db /tmp/brainos-realdata-bounded-1780474190.db decision-check dec-no-retune-yet`
- minimal decision/query sample:
  - same `metadata.entity_id = "brainos/decision-check"`
  - active statuses
  - generic local shared option ids `A/B`
  - different recommendations across adjacent workstream decisions

## Expected vs actual
### Expected
- adjacent workflow decisions in the same workstream should stay `clear` unless there is evidence of one meaningful shared comparable option frame

### Actual
- all three decisions overcalled as `conflict`
- conflict was triggered by `shared_entity_id + active_pair + different_recommendations`
- generic local `A/B` option ids still functioned as a comparability gate even though they were only local placeholders

## Why this matters
- trust impact: high; this was the main blocker preventing wider bounded real usage of `decision-check`
- frequency guess: `possible-repeat`

## Evidence
- report/log paths:
  - `docs/brainos-realdata-bounded-usage-2026-06-03-100950.md`
  - `/tmp/brainos-realdata-bounded-run.log`
- relevant outputs:
  - pre-fix: `dec-doc-closeout => conflict`
  - pre-fix: `dec-realdata-test => conflict`
  - pre-fix: `dec-no-retune-yet => conflict`
- fix/verification artifacts:
  - `src/brainos/decision_checks.py`
  - `tests/test_decision_conflicts.py`
  - `docs/brainos-realdata-bounded-rerun-2026-06-03-140404.md`

## Working judgment
- likely class: `false-positive`
- smallest next move: tighten comparability so `different_recommendations` only counts when both recommendations sit inside `meaningful_shared_option_ids`
- not doing now: broad redesign of decision-check or metadata model

## Close condition
- close when the same bounded real-data cluster reruns cleanly and returns `clear` instead of `conflict`

## Closeout
Closed on 2026-06-03 after the narrow comparability-gate fix.

Post-fix rerun result:
- `dec-doc-closeout => clear`
- `dec-realdata-test => clear`
- `dec-no-retune-yet => clear`

Reference:
- `docs/brainos-realdata-bounded-rerun-2026-06-03-140404.md`
