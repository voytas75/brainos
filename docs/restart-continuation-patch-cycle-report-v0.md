# Restart / continuation retrieval patch cycle — final report v0

## Scope

This report closes the bounded restart / continuation retrieval patch cycle that followed the restart-continuation validation runs.

The goal was **not** to redesign retrieval.
The goal was to move from broad suspicion to a small set of explicit failure shapes, then address only the smallest credible fix points.

## Starting point

Before the patch cycle:
- restart / continuation validation run 001 showed broad weakness on realistic operator wording
- run 002 showed that better artifact wording alone did **not** materially improve outcomes
- the problem narrowed to two practical failure shapes:
  1. zero-hit continuation phrasing (`resume`, `leave`, `continue`, `next step`, `active front`)
  2. stale-vs-current restart competition where the stale restart artifact could win lexically

## Critical questions asked during the cycle

### 1. Was this mainly a ranking problem from the start?
No.
The first hard bottleneck was earlier:
- episode FTS query normalization did not bridge natural continuation wording into artifact language strongly enough
- many realistic continuation queries died before ranking meaningfully participated

### 2. Was broad OR-style continuation bridging acceptable?
No.
It reduced zero-hit failures, but it also caused class bleed:
- next-step queries could fall into restart artifacts
- recall improved at the cost of precision

### 3. Was class-aware continuation handling justified?
Yes.
Validation and diagnosis showed the issue was not “continuity in general”, but distinct query classes:
- restart-point
- current-direction
- next-step

### 4. Was full negation handling needed to fix stale-vs-current restart?
No.
The stale-vs-current failure was near-tied, so a very small positive hint for the explicit current restart carrier was safer than trying to model negation broadly.

## Changes made

### 1. Narrow continuation query bridging in episode FTS normalization
The episode-side FTS normalization path was adjusted so realistic continuation phrasing has a small, class-aware bridge into artifact labels.

Bounded intent classes used:
- restart-point
- current-direction
- next-step

Important constraint:
- the bridging was kept class-aware after the broader OR variant proved too loose.

### 2. Minimal continuation intent hint for next-step queries
A narrow next-step intent bonus/penalty path was added in episodic ranking to:
- lightly favor procedure-like / `Next step:` carriers
- lightly demote restart-point carriers when the query is clearly next-step shaped

This was intentionally narrow and did not become a general continuation framework.

### 3. Minimal restart-specific current-carrier hint
A small restart-only hint was added so:
- `Current restart point:` gains a bounded bonus
- only for restart-point-shaped queries

This was chosen instead of a broad negation penalty because it had a smaller blast radius and addressed the observed near-tie directly.

## Verification performed

### Existing focused gate
Executed:
- `pytest -q tests/test_ingest_normalization.py tests/test_authoritative_artifact_recall.py`

Result:
- `6 passed in 0.28s`

### Focused restart / continuation checks
Repeated bounded fixture-based verification across:
- restart-point queries
- current-direction queries
- next-step queries
- explain-based inspection on representative cases

## What improved

### Restart-point
Improved materially.

Observed reading after the last narrow restart hint:
- `where do we resume BrainOS work now?` -> current restart artifact wins
- `what is the current restart point for BrainOS?` -> current restart artifact wins
- `where did we leave the BrainOS work?` -> current restart artifact also wins in the final bounded check

Most important change:
- stale-vs-current restart no longer behaves like an uncontrolled lexical near-tie in the tested fixture

### Current-direction
Healthy enough in the bounded slice.

Observed reading:
- direct current-direction wording still works
- the broader `active front` style wording also now retrieves the intended current-direction carrier

### Next-step
Improved in diagnosis, but **not fully closed** in the same way as restart-point.

Observed reading across the cycle:
- next-step was the main place where broader bridging caused class bleed
- the narrow next-step intent hint improved the shape of the fix, but this front remains the least clean of the three continuation classes

## Main conclusion

This patch cycle succeeded in the way it was supposed to:
1. it avoided broad retrieval surgery
2. it turned a vague continuation weakness into a few explicit failure shapes
3. it fixed the highest-value restart-currentness issue with a very small bounded hint
4. it preserved the existing focused gate

## What is now "done enough"

Treat as **done enough**:
- restart-point retrieval in the bounded continuation fixture
- current-direction retrieval in the bounded continuation fixture
- the broader claim that the continuation problem has been reduced from a fuzzy “retrieval feels weak” complaint to specific, inspectable sub-cases

## What remains narrow and open

Do **not** overclaim closure on:
- general continuation retrieval quality
- robust next-step retrieval across varied natural phrasing
- semantic negation handling in general

If this topic is reopened later, the most honest remaining frontier is:
- next-step precision/recall under realistic phrasing,
- but only if it causes real operator friction again.

## Recommendation

Stop here.

Do not continue tuning this front speculatively.
Use the current bounded result as the new local truth:
- restart-point is in better shape,
- current-direction is acceptable in the bounded slice,
- next-step is the only continuation sub-surface that still looks less settled,
- and no broader retrieval-policy rewrite is justified.

## Later follow-through

After this patch cycle was treated as done enough, one later protective follow-through was added:
- `tests/test_continuation_regression_guardrail.py`

That guardrail intentionally stays narrow. It protects only two already-stabilized behaviors:
- `current restart point` should beat the stale restart carrier
- `current direction` should remain recoverable from natural wording

It does **not** widen the claim to all continuation behavior and does **not** treat `next-step` as closed.

## Short verdict

**This patch cycle is done enough.**

It produced a credible, bounded improvement without turning continuation retrieval into a sprawling scoring project.
