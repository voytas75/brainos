# Real-corpus probe review — 2026-05-23 v1

## Verdict
The first live run of `real-corpus-retrieval-quality-v1` did **not** reveal a ranking regression.

It revealed that the current local database does not yet contain meaningful probe-matching evidence for the selected `session_id="real"` sample, and vector participation is disabled in the current runtime posture.

So the correct reading is:
- **not enough live evidence yet**
- **not a retrieval-quality failure verdict**

## Observed live result
Current live probe returned:
- `case_count=4`
- all `top_episode_id=null`
- all `top_semantic_id=null`
- all `ranked_count=0`
- all `ranked_semantic_count=0`
- all `episode_vector_mode=disabled`
- all `semantic_vector_mode=disabled`

## Interpretation

### 1. Probe cases do not currently match real local corpus state
The selected real-sample probe cases are valid as realistic local-style examples, but they do not currently appear to exist in the live database under `session_id="real"`.

That means this run gives almost no useful evidence about ranking quality on live data yet.

### 2. Vector-disabled posture further limits probe usefulness
Current vector modes were uniformly `disabled`.

That means even if the live corpus had partial lexical overlap, this run would still not be a strong read on vector-capable retrieval quality.

### 3. This is mostly a corpus/readiness finding
The run is most usefully read as:
- live corpus for the chosen probe session is absent or too sparse
- vector runtime is not currently participating
- therefore the probe is behaving truthfully, but current evidence is weak

## Reviewer judgment
The probe itself is useful and honest.
The live result is not yet useful as a retrieval-quality verdict.

That is still progress, because it confirms the system is no longer pretending to know more than it does.

## Best next move
### Recommendation
**real-corpus probe target/fixture alignment v1**

### Why
Before any ranking changes, BrainOS should first ensure the real-corpus probe targets a small but actually present local sample.

### Bounded next shape
One small slice:
- either align probe queries/session target to a known present local sample
- or add a tiny explicit local sample note/harness used only for this probe
- keep read-only if possible
- do not retune ranking in the same slice

## What not to do next
- do not interpret this run as a ranking regression
- do not retune scoring based on these null results
- do not widen benchmarking again before probe target alignment is fixed
