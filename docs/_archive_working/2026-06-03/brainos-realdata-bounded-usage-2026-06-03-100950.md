# BrainOS bounded real-data usage test — 2026-06-03 10:09:50

## Status
Bounded local real-data usage test run after the `decision-check` documentation/closeout sync.

This run used a fresh isolated DB and a tiny real decision slice derived from the actual current BrainOS work sequence:
- close out decision-check docs,
- choose bounded real-data validation next,
- avoid another speculative retuning pass before usage.

This is not broad product validation.
It is a narrow operator-level check of whether the current decision layer behaves sanely on a small real case cluster.

## Artifact paths
- DB: `/tmp/brainos-realdata-bounded-1780474190.db`
- Raw log: `/tmp/brainos-realdata-bounded-run.log`

## Runtime precondition
The repo-local `.env` was loaded for the run.

Effective sqlite-vec path:
- `/home/openclaw/.npm-global/lib/node_modules/openclaw/node_modules/sqlite-vec-linux-x64/vec0.so`

## Flow run
Executed successfully:
- `init`
- `capabilities`
- `sqlite-vec-readiness`
- `decision-log` x3
- `decision-list`
- `decision-check` x3
- `inspect decision dec-realdata-test`
- `decision-history dec-realdata-test`
- `recall` x3
- `retrieval-explain` x2
- `retrieval-health`

## Test decisions used
### 1. `dec-doc-closeout`
Question:
- whether documentation/closeout should be finished before real-data validation

Recommended:
- `A` = close docs first

### 2. `dec-realdata-test`
Question:
- what should happen next after documentation closeout

Recommended:
- `A` = run bounded real-data usage test

### 3. `dec-no-retune-yet`
Question:
- whether to retune `decision-check` again before real usage

Recommended:
- `B` = do not retune yet; validate current state first

All three decisions intentionally shared:
- `metadata.entity_id = "brainos/decision-check"`
- active status
- overlapping theme space

This was deliberate pressure on the current conflict logic.

## Result summary
## Runtime / health
PASS:
- `capabilities` showed `sqlite_vec = true`
- `sqlite-vec-readiness` returned `ok: true`
- `retrieval-health` returned overall `status: ok`
- runtime / embedding / sqlite-vec / DB runtime planes were all healthy

Interpretation:
- runtime posture is fine for bounded local usage on an isolated DB
- no crash or setup instability appeared in the flow

## Recall / explain
PASS with the expected limitation:
- recall returned the three decision objects consistently
- retrieval-explain surfaced the expected top decisions
- retrieval-health correctly reported `low_evidence` for database quality because the DB is intentionally tiny

Interpretation:
- retrieval surface behaved coherently
- the low-evidence warning is honest, not a failure

## decision-history / inspect
PASS:
- `inspect` returned a clear record plus related ledger events
- `decision-history` returned coherent `current`, `previous`, `changed_fields`, and revision timeline output

Interpretation:
- inspectability remains one of the stronger parts of the layer

## decision-check
WEAK / NOT YET TRUSTWORTHY for this real-case cluster.

Observed behavior:
- `dec-doc-closeout` => `conflict` against `dec-no-retune-yet`
- `dec-realdata-test` => `conflict` against `dec-no-retune-yet`
- `dec-no-retune-yet` => `conflict` against both other decisions

Why this is weak:
These three decisions are related, but they are **not obviously mutually contradictory decisions over one comparable option space**.
They are closer to:
- sequential workflow decisions,
- adjacent validation decisions,
- different questions inside one workstream.

The current checker still escalated them to `conflict` because the strong-signal path considered the following sufficient:
- `shared_entity_id`
- `active_pair`
- `different_recommendations`

That is structurally too eager for this cluster.

## Main finding
The earlier structural fix was real and useful, but this run shows another remaining logic gap:

> `different_recommendations` is still being treated as conflict-grade divergence too early when decisions share an entity/workstream but do not clearly share one comparable decision frame.

In plain language:
- same entity/workstream is not the same thing as same decision,
- different recommended options across adjacent decisions should not auto-upgrade to `conflict`.

## What passed vs failed
### Passed
- isolated DB flow
- sqlite-vec runtime
- readiness
- decision logging
- decision listing
- inspect
- decision history
- recall
- retrieval explain
- retrieval health honesty

### Weak / failed for correctness
- `decision-check` overcalled `conflict` on a realistic small cluster of related but non-equivalent decisions

## Classification
Overall verdict for this run:
- **WEAK**

Reason:
- the core product/runtime flow is operational,
- but the main target of this run — correctness trust in `decision-check` logic on a real small case cluster — did not hold strongly enough.

## Recommended next move
Do **not** broaden real-data usage of `decision-check` yet.

Instead, open one more bounded correction slice focused specifically on:
- distinguishing shared workstream/entity from shared comparable decision frame,
- preventing `different_recommendations` from acting as conflict-grade evidence unless the option space is demonstrably comparable.

Good likely directions:
1. require stronger evidence for comparability before `different_recommendations` contributes to `conflict`
2. possibly add an explicit same-decision-frame signal instead of relying mainly on `entity_id`
3. keep adjacent workflow decisions in `clear` or at most `caution`, not `conflict`

## Bottom line
BrainOS runtime and decision-layer plumbing behaved well.
The weak point is still `decision-check` calibration.

So the result is not “BrainOS failed”.
The result is:
- **runtime yes**,
- **retrieval/inspect/history yes**,
- **decision-check conflict logic still too eager for bounded real usage on adjacent real decisions**.
