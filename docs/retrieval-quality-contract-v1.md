# Retrieval quality contract v1

## Purpose
This document defines how to interpret the current BrainOS retrieval quality signals.

It does **not** define broad relevance quality for all future queries.
It defines what the current bounded eval/benchmark suite is intended to prove and how its failures should be read.

## Current quality surfaces
BrainOS currently exposes two main bounded quality surfaces:
- deterministic eval fixtures
- local retrieval benchmark cases

These surfaces are related, but they do not mean the same thing.

## Eval fixture purpose
Primary purpose:
- protect specific retrieval behaviors from silent regression

Current role:
- deterministic regression guard
- narrow behavioral anchor for ranking/scoring changes
- protection for known edge cases

Eval is best read as:
- “did we preserve important expected behavior?”

Eval is **not** best read as:
- “is retrieval broadly mature now?”
- “is general relevance solved?”
- “does this prove production-quality ranking across open-ended query space?”

## Benchmark purpose
Primary purpose:
- give an operator-visible local quality snapshot across a small bounded set of realistic retrieval cases

Current truthfulness posture:
- the current benchmark is a seeded fixture benchmark, not a direct readout of the live user corpus
- it is strongest as implementation-level evidence about retrieval behavior under bounded conditions
- it should not be presented as proof that the current live database corpus is healthy or sufficient

Current role:
- compact top-hit sanity check
- local confidence signal for current retrieval posture
- quick check that benchmark-like phrasing still retrieves the intended canonical hits

Benchmark is best read as:
- “does the current bounded retrieval slice still behave coherently on representative phrasing?”

Benchmark is **not** best read as:
- a full retrieval scorecard
- a substitute for broader corpus evaluation
- proof that all ambiguity classes are covered

## What current top-hit success means
A protected case is considered successful when:
- the expected canonical top episode remains top-ranked
- and the expected canonical top semantic hit remains top-ranked

This is a bounded success criterion.
It is intentionally stricter than “something relevant appeared somewhere in the list,” but narrower than a full relevance judgment framework.

## Low-evidence qualification
If the current database is effectively empty or too sparse to support meaningful bounded retrieval-quality interpretation, health should report a low-evidence posture rather than treating the result as an ordinary quality regression.

This is meant for fresh or minimally populated databases, not for masking real regressions in a populated corpus.

## Failure interpretation

### Eval failure
Interpret first as:
- regression risk
- scoring/policy drift risk
- possible retrieval-boundary behavior change

Treat seriously even when the corpus is small, because eval is meant to protect known behaviors.

### Benchmark failure in `vector-ready` mode
Interpret first as:
- bounded quality regression signal
- ranking/scoring behavior worth inspection
- possible retrieval semantics drift

This is the strongest current quality-failure signal in day-to-day local use.

### Benchmark failure in `degraded-non-vector` mode
Interpret first as:
- degraded-path evidence
- possibly expected quality reduction due to runtime posture
- not automatically the same class of failure as a vector-ready benchmark regression

Before treating this as a ranking problem, classify runtime posture first.

## Runtime-first rule
Always interpret retrieval benchmark output together with:
- benchmark `mode`
- benchmark `degraded`
- retrieval health `runtime`
- retrieval health `freshness`

Do not read a degraded-path benchmark red result as if it were equivalent to a vector-ready benchmark red result.

## Freshness-first qualification
If freshness signals show:
- `stale`
- `error`

then benchmark oddities may be partly explained by maintenance/data state rather than ranking policy alone.

If freshness only shows notes such as:
- `missing`
- `disabled`

that is still relevant, but it is not the same class of signal as freshness failure.

## Current bounded coverage
The current bounded corpus now covers at least:
- lexical semantic graph retrieval
- bootstrap/procedural retrieval
- embedding/semantic retrieval
- competing similar-hit disambiguation
- session-filter protection for vector results
- weak vector-only noise suppression
- policy-version retrieval wording
- disabled-runtime vs stale-data wording
- maintenance/reindex phrasing

## Out of scope
This contract does not claim:
- broad retrieval completeness
- human-grade relevance evaluation
- large ambiguity coverage
- robust long-tail query guarantees
- production-wide ranking confidence outside the bounded corpus

## Practical operator rule
Read current retrieval quality in this order:
1. runtime posture
2. freshness posture
3. benchmark mode (`vector-ready` vs `degraded-non-vector`)
4. eval/benchmark pass-fail
5. explain output for hit-level diagnosis

## Stability note
This contract should stay small and explicit.
If the corpus meaning changes materially, revise this document instead of letting interpretation drift through commit history.
