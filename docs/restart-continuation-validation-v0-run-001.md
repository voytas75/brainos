# Restart / continuation retrieval validation v0 — run 001

## Purpose

This is the first bounded execution pass for the restart / continuation retrieval validation slice.

The goal was not to improve ranking.
The goal was to check whether BrainOS can recover the current continuation carrier reliably enough on a small realistic fixture, and to separate:
- retrieval weakness
- artifact weakness
- wording / lexical-grounding weakness

## Fixture shape

This run used one small session-bounded fixture with these artifact classes:
- one current canonical restart point
- one older restart point
- one active decision carrier for current direction
- one next-step / procedure carrier
- one nearby working note
- one generic status distractor

This was deliberately richer than the earlier tiny rerun, but still small enough to read manually.

## Query set

### Restart-point recall
1. `where do we resume BrainOS work now?`
2. `where did we leave the BrainOS work?`
3. `what is the current restart point for BrainOS?`

### Current-direction recall
4. `what is the current BrainOS direction?`
5. `what front is currently active in BrainOS?`

### Next-step continuation recall
6. `what should we do next in BrainOS?`
7. `what is the next continuation step for BrainOS?`
8. `what should I continue with in BrainOS now?`

## Raw outcome summary

- **PASS:** 1
- **WEAK_PASS:** 0
- **LOW_EVIDENCE:** 0
- **FAIL:** 7
- **RUNTIME_BLOCKED:** 0

Important reading:
- runtime was healthy (`sqlite_vec` ready)
- this was **not** a runtime-path failure
- the dominant problem in this run was poor lexical grounding for realistic continuation wording

## Case-by-case reading

### Restart-point recall

#### Query 1
- `where do we resume BrainOS work now?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** the current restart artifact did not ground strongly enough against natural resume wording

#### Query 2
- `where did we leave the BrainOS work?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** same failure shape as query 1; realistic “leave/resume” phrasing did not recover the continuation carrier

#### Query 3
- `what is the current restart point for BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** one ranked hit, but it was the **older restart point**, not the current one
- **Reading:** this is the strongest signal in the run; restart-shaped lexical match exists, but recency/currentness is not recovered correctly on this fixture

### Current-direction recall

#### Query 4
- `what is the current BrainOS direction?`
- **Verdict:** `PASS`
- **Observed:** the active decision carrier won
- **Reading:** direct current-direction wording is recoverable when the wording is close to the stored artifact

#### Query 5
- `what front is currently active in BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** this is likely wording fragility, not proof that the current-direction carrier class is conceptually wrong

### Next-step continuation recall

#### Query 6
- `what should we do next in BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** the procedure carrier did not lexicalize strongly enough for this wording

#### Query 7
- `what is the next continuation step for BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** even continuation-step phrasing did not recover the intended next-step artifact

#### Query 8
- `what should I continue with in BrainOS now?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** this is again consistent with wording fragility rather than runtime failure

## Explain-assisted diagnosis

Focused `retrieval-explain` checks were used on four representative failures/successes.

Main reading:
- zero-hit failures were reported as `no_matching_content`, not runtime degradation
- the restart query that did return a hit favored the older restart artifact because it matched the phrase `restart point` directly
- the current restart artifact contained the right intent, but did not lexicalize enough around `current restart point`
- direct current-direction wording worked because the artifact explicitly contained `current BrainOS direction`

## Main conclusion

This run does **not** justify ranking surgery yet.

The stronger reading is:
1. the richer fixture was worth doing,
2. restart / continuation retrieval is **not yet robust on realistic operator wording**,
3. the dominant weakness in this run looks more like **artifact wording / continuation-carrier shape** than a proven ranking-policy defect,
4. one especially important failure remains: an older restart artifact can beat the current restart artifact when the wording is too similar and “currentness” is not encoded strongly enough.

## Recommended next step

Do **not** jump straight to ranking changes.

The next best move is narrower:
1. improve the wording shape of the continuation artifacts in the fixture,
2. make “currentness” vs “older restart point” more explicit in the artifacts,
3. rerun the same query set,
4. only then decide whether a narrow ranking issue survives.

## Short verdict

**Run 001 found a real weakness, but not the one we should assume first.**

The problem currently looks less like “retrieval needs more policy” and more like:
- restart/continuation artifacts are still too thinly shaped for realistic wording,
- and current-vs-stale continuation boundaries are not encoded strongly enough yet.
