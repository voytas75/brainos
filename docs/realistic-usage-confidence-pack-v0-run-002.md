# Realistic usage confidence pack v0 — run 002

## Purpose

This is the second recorded run of the realistic usage confidence pack for BrainOS.

Unlike run 001, this run was executed under a **vector-ready** runtime posture with project env loaded correctly.
That makes it the first useful comparison point for deciding whether the observed weakness is mainly runtime contamination, corpus wording weakness, or retrieval behavior weakness.

This run is still intentionally small and local.
It is stronger than run 001 for ranking interpretation, but it is still **not** broad live-corpus proof.

## Run metadata

- **Run id:** `run-002`
- **Pack:** `realistic-usage-confidence-pack-v0`
- **Corpus kind:** `small_seeded_realistic_local_review_vector_ready`
- **DB path:** `/tmp/brainos-realistic-usage-v0-run002.db`
- **Truthfulness note:** this is a small realistic local review run under vector-ready posture. It is stronger than run 001 for ranking interpretation, but it should still not be presented as broad live-corpus quality proof.

## Runtime / health posture during run

- **Health status:** `ok`
- **Health summary:** `benchmark green in vector-ready mode`
- **Benchmark mode:** `vector-ready`
- **Benchmark ok:** `true`

Interpretation:
- the runtime ambiguity from run 001 is removed here,
- so the result is materially cleaner for judging retrieval behavior on this small corpus,
- especially for the five non-green cases from run 001.

## Scoreboard

- **PASS:** 8
- **WEAK_PASS:** 1
- **LOW_EVIDENCE:** 1
- **FAIL:** 0
- **RUNTIME_BLOCKED:** 0

## Case results

### Case 01 — Restart point recall
- **Query:** `where do we resume BrainOS work now?`
- **Verdict:** `PASS`
- **Observed behavior:** the restart-point decision-like episode ranked top.
- **Reading:** continuity/restart phrasing becomes usable once vector-ready posture is available.

### Case 02 — SSOT lookup
- **Query:** `what is the source of truth for BrainOS retrieval quality?`
- **Verdict:** `WEAK_PASS`
- **Observed behavior:** the top hit was a correct boundary statement, but not the cleanest SSOT-style source-of-truth statement.
- **Reading:** this is the one remaining practical weak spot.
- **Why weak rather than fail:** the answer direction is relevant, but it does not cleanly return the intended authoritative wording.

### Case 03 — Decision recall
- **Query:** `what did we decide about BrainOS next slice?`
- **Verdict:** `PASS`
- **Observed behavior:** the correct decision object was returned again.
- **Reading:** decision recall remains one of the strongest practical surfaces.

### Case 04 — Policy lookup
- **Query:** `how should degraded runtime benchmark failures be interpreted?`
- **Verdict:** `PASS`
- **Observed behavior:** the runtime-first interpretation policy ranked top.
- **Reading:** the runtime block from run 001 was environmental, not conceptual.

### Case 05 — Operational fact recall
- **Query:** `what env path does BrainOS use for sqlite-vec?`
- **Verdict:** `PASS`
- **Observed behavior:** the explicit `BRAINOS_SQLITE_VEC_PATH` fact ranked top.
- **Reading:** this was also blocked by runtime posture in run 001 rather than by retrieval design alone.

### Case 06 — Capability boundary lookup
- **Query:** `does BrainOS claim broad retrieval quality across arbitrary corpora?`
- **Verdict:** `PASS`
- **Observed behavior:** the correct non-claim remained top.
- **Reading:** BrainOS boundary retrieval is now clearly reliable on this small corpus.

### Case 07 — Competing hit disambiguation
- **Query:** `what should retrieval explain show?`
- **Verdict:** `PASS`
- **Observed behavior:** the explain-contract fact stayed specific and ranked correctly.
- **Reading:** explain specificity looks healthy here.

### Case 08 — Session-bounded recall
- **Query:** `what is the current BrainOS embedding path?`
- **Verdict:** `PASS`
- **Observed behavior:** the in-session embedding fact stayed above the cross-session distractor.
- **Reading:** session-bounded retrieval remains healthy in vector-ready mode.

### Case 09 — Procedure recall
- **Query:** `what should I do after runtime changes to vectors?`
- **Verdict:** `PASS`
- **Observed behavior:** the reindex procedure ranked top.
- **Reading:** the procedure failure from run 001 was mostly runtime-related on this corpus.

### Case 10 — Low-evidence honesty check
- **Query:** `what do we know about rare unsupported dragon runtime failures?`
- **Verdict:** `LOW_EVIDENCE`
- **Observed behavior:** a noisy but non-credible policy hit appeared.
- **Reading:** this is still acceptable as a low-evidence outcome, but it shows that vector-ready mode can still produce semantically plausible noise.
- **Important note:** this case should stay as an honesty guard.

## Comparison with run 001

### Run 001
- PASS: 4
- WEAK_PASS: 0
- LOW_EVIDENCE: 1
- FAIL: 3
- RUNTIME_BLOCKED: 2
- health: degraded non-vector

### Run 002
- PASS: 8
- WEAK_PASS: 1
- LOW_EVIDENCE: 1
- FAIL: 0
- RUNTIME_BLOCKED: 0
- health: vector-ready green

## What changed materially

### Direct runtime contamination was real
The biggest uncertainty from run 001 is now resolved.
At least four problematic cases improved materially once the run used the correct project env and vector-ready posture.

That means the run-001 picture was indeed partially distorted by environment/runtime posture.

### Retrieval is stronger than run 001 suggested
On this small realistic corpus, BrainOS now looks:
- strong on decision recall,
- strong on restart recall,
- strong on procedure recall,
- strong on policy and operational fact lookup,
- healthy on session-bounded retrieval.

### One practical weakness remains
The remaining non-green case is:
- **SSOT/source-of-truth lookup phrasing**

This does **not** look like a deep retrieval-policy failure.
It looks more like:
- corpus wording / authoritativeness expression,
- typed-ingest / topic labeling opportunity,
- or a mild ranking preference issue among several semantically related facts.

### Honesty guard should remain
The low-evidence dragon case still matters.
Even in vector-ready mode, BrainOS can surface semantically nearby noise.
The right interpretation is still `LOW_EVIDENCE`, not confident support.

## Main conclusion

The best current reading is:

1. **Do not change retrieval policy yet.**
2. **Do not treat restart/procedure recall as major current weaknesses anymore.**
3. **Treat SSOT/source-of-truth phrasing as the main remaining practical weak spot in this pack.**
4. **Keep low-evidence honesty checks in the pack, because vector-ready retrieval can still produce plausible noise.**

## Recommended next step

The next best move is now smaller and sharper than before:

1. improve the corpus wording or typed-ingest shape for SSOT-style artifacts,
2. rerun just the SSOT and low-evidence cases,
3. only then decide whether any retrieval-policy tuning is justified.

## Practical recommendation

The likely highest-leverage next slice is:
- **typed ingest / corpus hygiene for authoritative artifacts and restart points**

not:
- broad retrieval-policy surgery.

## Short verdict

**Run 002 materially improved the picture.**
The main story is no longer “retrieval is uneven.”
The cleaner story is:

- runtime contamination explained much of run 001,
- BrainOS retrieval is already pretty solid on this small realistic pack,
- the main remaining issue is authoritative SSOT phrasing,
- and low-evidence honesty still needs to stay guarded.
