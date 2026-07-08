# Realistic usage confidence pack v0 — run 001

## Purpose

This is the first recorded run of the realistic usage confidence pack for BrainOS.

It is meant to answer a bounded question:

> On a small realistic local corpus, which operator-style query classes already work, which fail, and which are blocked by runtime posture?

This run is intentionally small.
It is stronger than a pure fixture benchmark for operator phrasing, but it is still **not** broad live-corpus proof.

## Run metadata

- **Run id:** `run-001`
- **Pack:** `realistic-usage-confidence-pack-v0`
- **Corpus kind:** `small_seeded_realistic_local_review`
- **DB path:** `/tmp/brainos-realistic-usage-v0-run001.db`
- **Truthfulness note:** this run uses a small realistic local review corpus. It is useful for practical retrieval diagnosis, but it should not be presented as a broad live-corpus quality claim.

## Runtime / health posture during run

- **Health status:** `warn`
- **Health summary:** `runtime fix needed before vector-quality interpretation`
- **Benchmark mode:** `degraded-non-vector`
- **Benchmark ok:** `false`

Interpretation:
- this run was executed under a degraded non-vector posture,
- so some misses must be read as runtime-sensitive rather than pure ranking failures,
- but lexical-only wins and losses are still informative enough to diagnose practical weakness.

## Scoreboard

- **PASS:** 4
- **WEAK_PASS:** 0
- **LOW_EVIDENCE:** 1
- **FAIL:** 3
- **RUNTIME_BLOCKED:** 2

## Case results

### Case 01 — Restart point recall
- **Query:** `where do we resume BrainOS work now?`
- **Verdict:** `FAIL`
- **Observed behavior:** no ranked episodic hit was returned; only a decision object was present in the background.
- **Reading:** restart/continuity phrasing is not strong enough yet on this corpus when retrieval is degraded.
- **Most likely weakness:** continuity/restart phrasing is under-supported by the current lexical surface.

### Case 02 — SSOT lookup
- **Query:** `what is the source of truth for BrainOS retrieval quality?`
- **Verdict:** `FAIL`
- **Observed behavior:** no ranked episodic hit was returned.
- **Reading:** SSOT phrasing did not ground strongly enough despite the corpus containing a relevant fact.
- **Most likely weakness:** the corpus wording and the retrieval lexical path are still too brittle for this operator-style phrasing.

### Case 03 — Decision recall
- **Query:** `what did we decide about BrainOS next slice?`
- **Verdict:** `PASS`
- **Observed behavior:** the correct decision object `dec-brainos-next-slice` was returned.
- **Reading:** decision retrieval is already materially useful on natural operator phrasing.
- **Why this matters:** this is one of the most practically valuable paths in the current BrainOS shape.

### Case 04 — Policy lookup
- **Query:** `how should degraded runtime benchmark failures be interpreted?`
- **Verdict:** `RUNTIME_BLOCKED`
- **Observed behavior:** degraded runtime posture prevented fair interpretation; no ranked hit returned.
- **Reading:** do not treat this as an ordinary quality miss.
- **Next debug:** restore vector/runtime posture first, then rerun.

### Case 05 — Operational fact recall
- **Query:** `what env path does BrainOS use for sqlite-vec?`
- **Verdict:** `RUNTIME_BLOCKED`
- **Observed behavior:** degraded runtime posture prevented fair interpretation; no ranked hit returned.
- **Reading:** this is runtime-sensitive enough that the current degraded state blocks a clean read.
- **Next debug:** restore runtime first, then rerun.

### Case 06 — Capability boundary lookup
- **Query:** `does BrainOS claim broad retrieval quality across arbitrary corpora?`
- **Verdict:** `PASS`
- **Observed behavior:** the correct boundary statement ranked top lexically.
- **Reading:** BrainOS currently retrieves product-boundary non-claims well enough on direct phrasing.

### Case 07 — Competing hit disambiguation
- **Query:** `what should retrieval explain show?`
- **Verdict:** `PASS`
- **Observed behavior:** the explain-contract fact ranked top and stayed specific.
- **Reading:** explain-surface specificity is good enough in this case even without vector participation.

### Case 08 — Session-bounded recall
- **Query:** `what is the current BrainOS embedding path?`
- **Verdict:** `PASS`
- **Observed behavior:** the in-session Azure-through-LiteLLM fact won, while the cross-session distractor did not outrank it.
- **Reading:** session-bounded recall looks healthy on this small corpus.

### Case 09 — Procedure recall
- **Query:** `what should I do after runtime changes to vectors?`
- **Verdict:** `FAIL`
- **Observed behavior:** no ranked episodic hit was returned.
- **Reading:** practical how-to phrasing is still weaker than it should be.
- **Most likely weakness:** procedure wording is not yet robust enough under degraded lexical-only conditions.

### Case 10 — Low-evidence honesty check
- **Query:** `what do we know about rare unsupported dragon runtime failures?`
- **Verdict:** `LOW_EVIDENCE`
- **Observed behavior:** no ranked episodic hit was returned.
- **Reading:** this is the correct honest behavior; the system did not fabricate confident support.

## Main findings

### What already works
- decision recall on natural operator phrasing
- explicit product-boundary recall
- explain-contract lookup
- session-bounded embedding-path recall

### What does not work yet
- restart/continuity phrasing
- SSOT/source-of-truth lookup phrasing
- procedure/how-to recall under degraded runtime posture

### What is blocked by runtime posture
- policy lookup in this run
- runtime-path operational fact recall in this run

### What the run suggests
The current pain is **not** “BrainOS retrieval is generally bad.”
The more precise reading is:

1. BrainOS already handles some high-value operator queries well.
2. It is still brittle on restart, SSOT, and procedure-style phrasing.
3. Degraded runtime posture muddies interpretation and should be removed before making stronger retrieval-policy judgments.
4. Decision recall may currently be the strongest practical surface.

## Best next action

The next best move is:

1. rerun this pack in a **vector-ready** runtime posture,
2. compare the 5 currently non-green cases,
3. then decide whether the dominant problem is:
   - wording / corpus shape,
   - typed ingest and topic/kind hygiene,
   - lexical ranking brittleness,
   - or actual retrieval-policy weakness.

## Practical recommendation

Do **not** change retrieval policy yet.
That would be premature.

First do:
- one clean rerun with vector-ready runtime,
- then compare run 001 vs run 002,
- then decide whether to fix corpus wording/typed ingest first or ranking logic first.

## Short verdict

**Run 001 was useful.**
It exposed real practical weakness without widening scope.

The main signal is:
- BrainOS already has islands of practical usefulness,
- but restart/SSOT/procedure retrieval is not trustworthy enough yet,
- and current degraded runtime posture is still contaminating the picture.
