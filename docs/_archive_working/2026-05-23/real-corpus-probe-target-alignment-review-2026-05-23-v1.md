# Real-corpus probe target alignment review — 2026-05-23 v1

## Verdict
The probe is now materially more truthful and useful.

It no longer assumes a nonexistent `session_id="real"`. It aligns to an actually present local session sample and now produces mixed live results instead of all-null output.

## What changed
Current live probe now reports:
- `target_status=aligned_to_available_session_sample`
- `target_session_id="session-1"`
- `available_session_ids=["session-1", "session-c"]`

This is a clear improvement over the earlier mismatched-target run.

## Observed live result
Case 1:
- query: `brainos initialized with wal`
- top episode found
- `ranked_count=1`
- vector modes still `disabled`

Case 2:
- query: `store semantic fact`
- no episode or semantic hit returned for `session-1`
- vector modes still `disabled`

## Interpretation

### 1. Probe alignment is fixed enough for bounded use
The probe now targets a real local sample instead of a fictional one.

That means null results are no longer dominated by target mismatch.

### 2. Retrieval evidence is still sparse
Only one of the two current aligned probe queries returned an episodic hit.

So the live corpus is still too small or too uneven to support stronger retrieval-quality conclusions.

### 3. Vector-disabled posture still limits conclusions
Vector participation remains disabled in the live run.

So this probe can currently tell us something about lexical/session-filtered retrieval behavior on a tiny live sample, but not much yet about vector-capable real-corpus retrieval quality.

## Reviewer judgment
This slice succeeded.

It converted the probe from:
- truthful but mostly unusable

to:
- truthful and at least minimally informative

That is enough progress for the current bounded goal.

## Best next move
### Recommendation
**stop here unless you want to grow the live sample on purpose**

If continuing, the best bounded next move is:
- add one tiny explicit local sample note/harness for the probe
- or wait until the real database accumulates more naturally useful material

## What not to do next
- do not retune ranking from this tiny mixed result
- do not claim broad real-corpus quality from this probe yet
- do not widen the probe aggressively without a stronger reason
