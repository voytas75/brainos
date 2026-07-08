# Restart / continuation retrieval validation v0 — run 002

## Purpose

This was the second bounded execution pass for restart / continuation retrieval validation.

Run 002 kept the same query set as run 001, but improved the fixture wording to test a narrower question honestly:

> If the continuation artifacts encode currentness, previousness, direction, and next-step intent more explicitly, does the apparent failure shrink without changing retrieval policy?

## What changed from run 001

The fixture was reshaped to make these distinctions more explicit:
- `Current restart point:` vs `Previous restart point:`
- `Current direction:`
- `Next step:`

This was meant to reduce artifact-shape ambiguity before assuming a ranking-policy problem.

## Scoreboard

- **PASS:** 1
- **WEAK_PASS:** 0
- **LOW_EVIDENCE:** 0
- **FAIL:** 7
- **RUNTIME_BLOCKED:** 0

## Comparison with run 001

The headline result did **not** improve.

Most important comparison:
- run 001 already suggested continuation artifact shape was a likely first suspect
- run 002 improved artifact wording materially
- but the retrieval outcome stayed almost unchanged

That means the current weakness is **less likely to be explained only by thin artifact wording** than run 001 first suggested.

## Case reading

### Restart-point recall

#### `where do we resume BrainOS work now?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** even explicit `Current restart point:` wording did not ground natural resume phrasing

#### `where did we leave the BrainOS work?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** same result as run 001

#### `what is the current restart point for BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** the top hit was still the **previous** restart point
- **Reading:** this is the strongest signal in the slice so far; “currentness” wording by itself is not enough to stop the stale restart artifact from winning when it repeats the restart-point phrase lexically

### Current-direction recall

#### `what is the current BrainOS direction?`
- **Verdict:** `PASS`
- **Observed:** the current-direction decision carrier won again
- **Reading:** direct current-direction retrieval remains locally healthy

#### `what front is currently active in BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** wording generalization remains weak even when the stored artifact is clearly marked as current direction

### Next-step continuation recall

#### `what should we do next in BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** `Next step:` wording was still insufficient for this natural question

#### `what is the next continuation step for BrainOS?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** continuation-step wording still did not ground to the next-step artifact strongly enough

#### `what should I continue with in BrainOS now?`
- **Verdict:** `FAIL`
- **Observed:** no ranked hits
- **Reading:** same failure shape

## Explain-assisted diagnosis

Focused `retrieval-explain` checks were run again for representative cases.

Main reading:
- failures remained `no_matching_content`, not runtime degradation
- the stale restart artifact continued to win for the explicit restart-point query because it repeated the phrase `current restart point` inside a negated sentence (`no longer the current restart point`)
- current-direction retrieval still works when the query mirrors the stored wording closely
- next-step and natural continuation wording still do not lexicalize into ranked retrieval on this fixture

## Main conclusion

Run 002 weakens the earlier hypothesis that the problem is mostly artifact-shape only.

The stronger current reading is now:
1. artifact wording **does matter**, but it was **not sufficient** to fix the problem,
2. restart / continuation retrieval remains weak on realistic operator phrasing,
3. one concrete retrieval weakness now looks more credible:
   - lexical matching can reward a stale restart artifact that repeats the target phrase inside a negation,
4. current-direction remains the only locally healthy continuation sub-surface,
5. next-step retrieval remains weak even after clearer artifact wording.

## Recommended next step

The next best move is still bounded, but sharper than run 001:

1. do **one small diagnosis-first slice** around restart/continuation lexical failure shapes,
2. inspect whether negated/stale continuation phrases should be prevented from winning so easily,
3. inspect whether next-step wording needs a narrow retrieval-path improvement or just a different artifact class shape,
4. avoid broad ranking surgery unless the fix point stays narrow and explicit.

## Short verdict

**Run 002 did not rescue the slice through better artifact wording alone.**

That is useful.
It means the open problem is now more likely to include a real retrieval weakness, not just a corpus-shape weakness.

Still, the evidence remains narrow:
- the issue is specifically about restart/continuation phrasing,
- especially stale-vs-current lexical competition,
- not about retrieval quality in general.
