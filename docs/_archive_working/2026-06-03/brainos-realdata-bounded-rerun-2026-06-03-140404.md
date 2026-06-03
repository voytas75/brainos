# BrainOS bounded real-data usage rerun — 2026-06-03 14:04:04

## Status
Bounded rerun of the same real-data usage slice after the narrow `decision-check` comparability-gate fix.

Goal:
- verify that the previous false-`conflict` pattern is gone on the same small real decision cluster,
- confirm that runtime/readiness remains stable after the fix.

## Artifact paths
- DB: `/tmp/brainos-realdata-bounded-rerun-1780488244.db`
- Raw log: `/tmp/brainos-realdata-bounded-rerun.log`

## Test slice
Same three real workstream decisions as the previous run:
- `dec-doc-closeout`
- `dec-realdata-test`
- `dec-no-retune-yet`

These decisions still share:
- `metadata.entity_id = "brainos/decision-check"`
- active status
- overlapping theme/workstream
- only generic local option ids (`A/B`)

That is exactly the cluster that previously over-triggered `conflict`.

## Runtime result
PASS:
- `capabilities` => `sqlite_vec: true`
- `sqlite-vec-readiness` => `ok: true`
- `retrieval-health` => overall `status: ok`
- runtime / dependency / DB posture stayed healthy

## decision-check result
PASS:
- `decision-check dec-doc-closeout` => `clear`
- `decision-check dec-realdata-test` => `clear`
- `decision-check dec-no-retune-yet` => `clear`

## Interpretation
The previous false-`conflict` pattern is gone on the same bounded real-data slice.

This is the right directional behavior:
- same workstream/entity alone no longer escalates to `conflict`,
- adjacent workflow decisions with generic local `A/B` option ids are no longer treated as if they share one meaningful comparable recommendation frame.

## Comparison vs previous run
Previous run:
- all three decisions overcalled as `conflict`

Current rerun:
- all three decisions return `clear`

This strongly suggests the narrow comparability-gate fix hit the real bug rather than only satisfying synthetic tests.

## Remaining caution
This rerun validates one important negative case:
- avoid false `conflict` for adjacent same-workstream decisions.

It does **not** by itself prove that all true conflicts are still caught under broader real usage.
The remaining tradeoff is still:
- a true conflict encoded only with generic local `A/B` ids and no stronger comparable-frame evidence could now undercall.

That is a bounded and currently acceptable tradeoff.

## Verdict
Overall verdict for this rerun:
- **PASS**

Why:
- runtime is healthy,
- readiness is healthy,
- the specific real-data false-positive pattern that blocked trust is no longer present,
- the fix behaves correctly on the same bounded real cluster that previously failed.

## Recommended next move
It is now reasonable to continue with the next bounded phase of real BrainOS usage.

Recommended posture:
- proceed with bounded real usage,
- keep watching for missed true conflicts,
- avoid broad claims until a few more real cases accumulate.

## Bottom line
This rerun removed the key blocker from the previous real-data validation pass.

Current posture:
- BrainOS runtime/retrieval/inspect/history: good,
- `decision-check`: good enough to continue bounded real usage with eyes open,
- next evidence should come from actual usage rather than more speculative tuning.
