# Realistic usage confidence pack v0

## Purpose

This document defines a **small, realistic usage review pack** for BrainOS.

Its job is to answer one bounded question honestly:

> Does BrainOS currently help on practical operator-style retrieval questions beyond the seeded fixture benchmark?

This pack is intentionally small.
It is not a broad eval framework, not a production scorecard, and not a substitute for retrieval benchmarking or runtime smoke tests.

## Why this exists

BrainOS already has:
- bounded fixture retrieval benchmark coverage
- runtime/readiness diagnostics
- canonical end-to-end demo coverage
- local operator-facing trust and health surfaces

That is useful, but it leaves a real gap:
- fixture success is not the same thing as practical usefulness on realistic query classes
- green runtime is not the same thing as trustworthy retrieval behavior on operator phrasing
- docs can define the boundary clearly without proving real usage value

This pack exists to tighten that gap without expanding product scope.

## What this pack is

This pack is:
- a small set of realistic query classes
- a compact interpretation contract
- a minimal repeatable review procedure
- a bridge between seeded retrieval proof and practical retrieval trust

## What this pack is not

This pack is not:
- a broad retrieval-quality claim
- a hosted or production readiness claim
- a replacement for `retrieval-benchmark`
- a replacement for `real-corpus-probe`
- a long-running evaluation framework
- a justification to casually expand the benchmark anchor

## Relationship to existing BrainOS evidence

Read current evidence in this order:
1. runtime truth
2. fixture benchmark truth
3. realistic usage confidence truth
4. broader product interpretation

Use existing repo surfaces for the other layers:
- runtime path: [`retrieval-green-path-smoke-test.md`](./retrieval-green-path-smoke-test.md)
- canonical trust walkthrough: [`canonical-e2e-demo.md`](./canonical-e2e-demo.md)
- seeded benchmark truth: `retrieval-benchmark-v0`
- bounded evidence map: [`evidence-map.md`](./evidence-map.md)
- retrieval interpretation rules: [`retrieval-quality-contract-v1.md`](./retrieval-quality-contract-v1.md)

This pack adds one extra question:
- do realistic operator-style phrasings still retrieve the right kind of thing?

## Evaluation categories

Each case should end in exactly one of these categories:

### PASS
- the intended object class is retrieved clearly
- success rule is met
- no major ambiguity changes the interpretation

### WEAK_PASS
- the intended object appears in an acceptable place
- result is usable, but ranking or evidence quality is weaker than ideal
- still good enough for practical operator use

### LOW_EVIDENCE
- the corpus is too thin, too fresh, or too weakly typed to read the result as a meaningful retrieval-quality signal
- this is not the same as an ordinary ranking failure

### FAIL
- the intended object class should have been retrievable under the case assumptions but was not retrieved acceptably
- or a clearly wrong competing hit displaced the expected one

### RUNTIME_BLOCKED
- runtime, env, or readiness issues prevented fair interpretation
- classify runtime first; do not misread this as quality failure

## Review method

For each case:
1. state the operator intent
2. run `recall`
3. inspect `retrieval-explain` when ranking is unclear
4. inspect `retrieval-health` when runtime, freshness, or degraded-path interpretation may matter
5. classify the outcome using the five categories above
6. record only the shortest explanation needed for the verdict

## Minimal operator rule

Do not over-interpret one result.
The purpose of this pack is to surface:
- practical confidence
- practical weakness
- practical ambiguity

It is not meant to manufacture a single score.

## Query class design rules

All cases in this pack should stay within these rules:
- phrasing should sound like a real operator question
- the expected success rule should be narrow and inspectable
- the number of cases should stay small
- each case should test one useful retrieval intention
- cases should prefer practical usage over synthetic cleverness
- if a case becomes too artificial or too broad, rewrite or remove it

## Current v0 case set

The current pack uses 10 query classes.
They are grouped to reflect realistic operator work rather than broad benchmark taxonomy.

---

## Case 1 — Restart point recall

- **Class:** restart-point
- **Intent:** find where work should resume in a project
- **Example query:** `where do we resume BrainOS work now?`
- **Expected object class:** restart note, resume brief, or bounded continuation anchor
- **Success rule:** a valid restart artifact or equivalent continuation pointer appears in top-3
- **Acceptable evidence:** project restart note, session restart brief, bounded continuation anchor
- **Common failure shape:** generic README or generic status page outranks the actual continuation source
- **Default interpretation note:** if no real restart artifact exists in the corpus, classify as `LOW_EVIDENCE`, not `FAIL`

## Case 2 — SSOT lookup

- **Class:** ssot-lookup
- **Intent:** find the correct source-of-truth document for a specific topic
- **Example query:** `what is the source of truth for BrainOS retrieval quality?`
- **Expected object class:** contract/SSOT-style document
- **Success rule:** the correct contract or equivalent source-of-truth document appears in top-1 or top-3
- **Acceptable evidence:** retrieval contract, quality contract, evidence-map style pointer
- **Common failure shape:** nearby implementation note outranks the authoritative contract

## Case 3 — Decision recall

- **Class:** decision-recall
- **Intent:** recover a previously made bounded decision
- **Example query:** `what did we decide about BrainOS next slice?`
- **Expected object class:** decision record, explicit operator note, or clearly decision-like entry
- **Success rule:** the answer retrieves a decision-like object or its nearest explicit durable carrier
- **Acceptable evidence:** decision entry, durable note, bounded planning artifact
- **Common failure shape:** generic discussion notes appear without the decision boundary
- **Default interpretation note:** if decisions are not captured durably in the tested corpus, prefer `LOW_EVIDENCE`

## Case 4 — Policy / guardrail lookup

- **Class:** policy-lookup
- **Intent:** recover a rule or interpretation guardrail
- **Example query:** `how should degraded runtime benchmark failures be interpreted?`
- **Expected object class:** policy, contract, or interpretation rule
- **Success rule:** the result surfaces the correct interpretation rule without collapsing runtime and quality failure into one class
- **Acceptable evidence:** retrieval quality contract, operator interpretation note, health semantics note
- **Common failure shape:** loosely related runtime note appears without the actual decision rule

## Case 5 — Operational fact recall

- **Class:** operational-fact
- **Intent:** retrieve a concrete runtime or environment fact
- **Example query:** `what env path does BrainOS use for sqlite-vec?`
- **Expected object class:** explicit operational fact
- **Success rule:** the correct runtime/config fact appears clearly enough to act on
- **Acceptable evidence:** runtime note, restart index, operator note, usage artifact
- **Common failure shape:** correct topic but vague or indirect answer that still forces manual hunting

## Case 6 — Capability / architecture lookup

- **Class:** capability-lookup
- **Intent:** recover what BrainOS currently is or is not supposed to do
- **Example query:** `does BrainOS claim broad retrieval quality across arbitrary corpora?`
- **Expected object class:** product boundary or evidence-boundary statement
- **Success rule:** a correct scope boundary is returned, including an explicit non-claim when relevant
- **Acceptable evidence:** README, STATUS, evidence map, contract docs
- **Common failure shape:** implementation detail is returned without the actual product boundary

## Case 7 — Competing similar-hit disambiguation

- **Class:** competing-hit-disambiguation
- **Intent:** retrieve the right result among nearby similar candidates
- **Example query:** `what should retrieval explain show?`
- **Expected object class:** specific policy/explain contract rather than a generic retrieval note
- **Success rule:** the intended specific hit wins or clearly appears above weaker nearby hits
- **Acceptable evidence:** policy-version explain note, explain contract, tight benchmark anchor
- **Common failure shape:** semantically adjacent but non-authoritative note outranks the intended hit

## Case 8 — Session-bounded recall

- **Class:** session-bounded-recall
- **Intent:** ensure filtered recall does not leak semantically similar material from another session
- **Example query:** `what is the current BrainOS embedding path?`
- **Expected object class:** session-appropriate hit only
- **Success rule:** the correct in-scope hit appears while out-of-scope but similar hits do not win
- **Acceptable evidence:** session-filtered episode hit, explain output showing boundary behavior
- **Common failure shape:** cross-session leakage outranks the intended in-session answer

## Case 9 — Procedure / how-to recall

- **Class:** procedure-recall
- **Intent:** recover a practical next action or short procedure
- **Example query:** `what should I do after runtime changes to vectors?`
- **Expected object class:** reusable operational procedure or step-like answer
- **Success rule:** the result returns the correct actionable procedure fragment, not only abstract commentary
- **Acceptable evidence:** reindex procedure, operator step note, maintenance-oriented semantic node
- **Common failure shape:** concept discussion appears without actionable next step

## Case 10 — Low-evidence honesty check

- **Class:** low-evidence-honesty
- **Intent:** verify that BrainOS does not overclaim retrieval quality when the corpus is too weak
- **Example query:** `what do we know about rare unsupported dragon runtime failures?`
- **Expected object class:** none, or explicitly low-evidence interpretation
- **Success rule:** the result is classified as `LOW_EVIDENCE` or yields no confident result rather than a false confident hit
- **Acceptable evidence:** low-evidence health signal, empty ranked result, explicit weak evidence handling
- **Common failure shape:** unrelated but semantically noisy hit is treated as valid support

---

## Suggested v0 coverage map

The 10 cases above are meant to cover these practical fronts:
- continuation / restart
- authority / SSOT
- decision memory
- policy interpretation
- runtime/config facts
- product boundary recall
- competing hit disambiguation
- session filtering
- actionable procedure recall
- honesty under weak evidence

This is enough for v0.
Do not broaden casually.

## Minimal execution procedure

### Option A — review-first, no new runner

Use this path first if the goal is simply to establish the pack without adding execution code.

1. choose one small test corpus or repo-local sample corpus
2. run the 10 queries manually through:
   - `recall`
   - `retrieval-explain` when needed
   - `retrieval-health` when interpretation needs runtime/freshness context
3. record one verdict per case
4. summarize the pack as:
   - count of `PASS`
   - count of `WEAK_PASS`
   - count of `LOW_EVIDENCE`
   - count of `FAIL`
   - count of `RUNTIME_BLOCKED`
5. only then decide whether a runner is worth adding

### Option B — small fixture-backed helper later

Only if review-first exposes stable recurring value:
- add one small fixture file or test helper
- keep the number of cases fixed or tightly justified
- do not turn this into a general scoring framework

## DoD for v0

This slice is complete when:
- this document exists as the pack definition
- the 10 realistic query classes are explicit
- the five outcome categories are explicit
- the execution procedure is repeatable without inventing new product surface
- the pack stays clearly separated from the seeded benchmark truth

## Anti-goals

Do not use this pack to:
- claim general retrieval quality
- replace runtime smoke checks
- replace seeded regression benchmark coverage
- expand BrainOS into a broad evaluation platform
- justify adding many new query classes without a practical reason
- hide weak corpus evidence behind vague scoring language

## Recommended next step after this doc

The next sensible move is:
1. pick one small realistic sample corpus,
2. run these 10 classes manually,
3. record the first honest v0 results,
4. then decide whether the weakness is mainly:
   - corpus quality,
   - typed ingest quality,
   - retrieval policy,
   - explain clarity,
   - or session-boundary behavior.

That decision should come **after** the first pack run, not before.
