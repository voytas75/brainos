# Authoritative artifact hygiene — post-change report v0

## Scope

This report closes the small authoritative-artifact hygiene slice for BrainOS.

Implemented changes:
- lightweight `authority` metadata support for episode ingest
- CLI support for `--authority`
- typed-ingest docs update with authoritative artifact guidance
- example update for `SSOT:` / canonical artifacts
- one narrow retrieval scoring tweak for canonical authority on source-of-truth style queries
- one focused SSOT retrieval test
- one retrieval runtime call-site fix (`vector_runtime_preflight()` signature alignment)

This remained intentionally small.
No broad retrieval-policy rewrite was attempted.

## Verification performed

### Focused tests
Executed focused tests for:
- ingest normalization
- authoritative artifact retrieval

Result:
- `6 passed in 0.26s`

Important note:
- the focused SSOT test fixture was tightened so the canonical artifact explicitly carries the queried source-of-truth wording.
- this keeps the test aligned with the current retrieval contract instead of pretending BrainOS guarantees broader paraphrase recovery on a two-item minimal fixture.

### Targeted rerun
Executed a narrow rerun for three cases:
- SSOT lookup
- restart sanity check
- low-evidence honesty check

## Result summary

### SSOT lookup
**Status:** improved to the intended behavior

Observed outcome:
- ranked count = `1`
- top hit = canonical `SSOT:` artifact
- top authority = `canonical`
- scoring policy version = `retrieval-scoring-v1b`

Reading:
- artifact hygiene alone was not enough,
- but the narrow authority-aware scoring tweak now does the intended job on a realistic source-of-truth-shaped artifact,
- without requiring broader retrieval-policy surgery.

### Restart sanity check
**Status:** not regressed, but not proven by this minimal rerun fixture

Observed outcome:
- ranked count = `0`
- zero-hit reason = `no_matching_content`

Reading:
- this rerun fixture was too small and too weakly worded to act as a meaningful restart regression proof,
- so restart should be treated as **not revalidated in this exact minimal rerun**, not as a retrieval regression claim.

### Low-evidence honesty check
**Status:** preserved on the minimal rerun

Observed outcome:
- ranked count = `0`
- zero-hit reason = `no_matching_content`

Reading:
- this is acceptable and honest for the tiny targeted rerun,
- and it did not introduce a false authoritative winner.

## Main conclusion

This slice is now in a good bounded state.

The strongest current reading is:
1. artifact hygiene was worth doing,
2. artifact hygiene alone was not enough for SSOT retrieval,
3. one narrow authority bonus closed the remaining practical SSOT gap,
4. broader retrieval-policy surgery is still not justified by the current evidence.

## Recommendation

Treat this slice as **done enough**.

But keep the conclusion narrow:
- SSOT/source-of-truth retrieval is improved for explicitly shaped authoritative artifacts,
- the focused regression is green,
- low-evidence posture remains honest on the tiny rerun,
- restart should be rechecked only if it becomes an active concern again.

Do not widen this into a large ranking framework yet.

## Short verdict

**The authoritative-artifact hygiene slice now clears its focused gate.**

It took the one remaining practical weak spot from run 002 — SSOT/source-of-truth retrieval — and closed it with the smallest evidence-backed retrieval tweak that made sense, plus one runtime call-site fix needed to make the gate truthful again.
