# BrainOS follow-ups from internet-grounded usage test (2026-06-04)

## Context
A bounded local BrainOS usage test was run on a fresh temporary DB using a tiny internet-grounded corpus about the state of AI in Poland (regulation, adoption, infrastructure). The end-to-end flow passed after loading the expected runtime environment.

Reference artifact:
- `docs/brainos-usage-test-internet-20260604-124820.md`

## Recommended tickets

### 1. Harden runtime preflight before recall / retrieval-explain
**Why**
The first pass produced empty results not because retrieval quality failed, but because the runtime env for sqlite-vec was not loaded for the recall/explain step. This creates a false "retrieval is broken" signal.

**Goal**
Make runtime misconfiguration fail loudly and specifically before normal retrieval output is shown.

**Definition of Done**
- `recall` and `retrieval-explain` explicitly check vector runtime prerequisites before retrieval.
- Missing or invalid `BRAINOS_SQLITE_VEC_PATH` is surfaced as a runtime/config error, not as ordinary `no_hits`.
- CLI output clearly distinguishes:
  - runtime misconfiguration
  - embedding/runtime failure
  - true zero-hit retrieval result

**Notes**
Prefer small guardrail changes over broad retrieval changes.

### 2. Add bounded real-use retrieval smoke test
**Why**
The existing health/benchmark path was green, but the real-use test still caught an operator/runtime issue. A small realistic smoke test would catch this class of regression earlier.

**Goal**
Add one compact test that exercises the same path a real operator uses on a fresh DB.

**Definition of Done**
- Test creates a unique temporary DB.
- Test adds 3-5 short entries.
- Test runs vector sync, recall, and retrieval-explain.
- Test fails on runtime regressions or empty retrieval caused by setup drift.
- Test remains bounded and fast; it is not a broad benchmark suite.

**Suggested shape**
- short corpus with semantically adjacent facts
- 2-3 queries
- assertions focused on operability and reasonable top-hit presence, not perfect global ranking

### 3. Improve retrieval diagnostics wording
**Why**
Current CLI wording makes it too easy to confuse degraded runtime with normal retrieval failure.

**Goal**
Make BrainOS operator-facing diagnostics more explicit and actionable.

**Definition of Done**
- When vector retrieval is unavailable, CLI wording says retrieval is degraded because vector runtime is unavailable.
- Diagnostic output points to the relevant fix path.
- Explain output makes it clearer whether a result won via vector similarity, lexical overlap, or both.
- If ranking confidence is weak/tight, diagnostics leave a hint instead of presenting a brittle top hit as fully decisive.

## Priority recommendation
If only one item is taken now, do **Ticket 1** first.

Reason: the biggest practical risk exposed by the test was not ranking quality but operator-facing false negatives caused by runtime/env drift.
