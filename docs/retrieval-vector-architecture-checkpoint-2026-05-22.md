# Retrieval / Vector Architecture Checkpoint — 2026-05-22

## Verdict

BrainOS has crossed the line from **planned native vector support** into a **real local retrieval subsystem**.

The current state is good enough to treat as a coherent **v0/v1 retrieval foundation**:
- SQLite-first remains intact
- vector support is integrated, not bolted on
- fallback behavior exists
- operator/debug surfaces exist
- retrieval quality has at least a bounded regression/benchmark gate

The subsystem is **not fragile in the "toy prototype" sense anymore**, but it is still **structurally young**.
The main remaining issue is no longer "does native vector retrieval exist?"
The main issue is now **how cleanly the retrieval/vector logic is bounded inside the codebase**.

---

## Current state

What is in place now:
- LiteLLM + Azure embedding execution adapter
- vector metadata lifecycle and freshness/error state
- sqlite-vec runtime enablement + readiness detection
- episode vector storage + retrieval
- semantic-node vector storage + retrieval
- unified recall ranking across FTS + vector + semantic name matches
- retrieval benchmark / explain / health CLI
- vector maintenance and sync surface

Recent stabilization step completed in this session:
- retrieval/vector orchestration was extracted from `BrainOSStore.recall()` into `src/brainos/retrieval.py`
- `BrainOSStore` now delegates recall behavior to `RetrievalService`
- behavior was preserved and the test suite stayed green

Verification at checkpoint:
- `uv run pytest -q`
- result: `37 passed`

---

## What is solid

- **Product coherence** — vector retrieval is still native to BrainOS, not split into a second primary subsystem.
- **Canonical-storage discipline** — SQLite objects remain the source of truth; vectors act as derived/indexed state.
- **Fallback posture** — non-vector operation still works when sqlite-vec is unavailable.
- **Operator surface** — explain, benchmark, health, and maintenance commands exist already.
- **Test posture** — retrieval eval, migration, metadata, maintenance, and CLI paths are covered enough to trust bounded refactors.
- **Recent refactor direction** — retrieval logic now has a first explicit code boundary.

---

## What is still weak / provisional

- Ranking policy is still heuristic-heavy and encoded through local scoring constants.
- Semantic recall fallback is still shallow; it is closer to semantic-name matching than true graph-aware semantic retrieval.
- `RetrievalService` is a better boundary than before, but it still depends heavily on `BrainOSStore` internals rather than a narrower backend contract.
- Runtime/config assumptions around embeddings and vector dimensions are still operationally sensitive.
- Top-level docs are slightly behind reality; at least `README.md` still understates the implemented retrieval/vector state.

---

## Main risks

- **God-object relapse risk**: if more retrieval/vector logic flows back into `BrainOSStore`, architecture quality will degrade again.
- **Heuristic drift risk**: ranking quality may change faster than the current benchmark set can fully protect.
- **False-green risk**: the suite is green, but benchmark coverage is still intentionally bounded and not equivalent to broad retrieval confidence.
- **Scope-creep risk**: the easiest tempting next moves are wider memory/runtime features before the retrieval subsystem boundary is fully stabilized.

---

## Recommended next step

Do one more **stabilization-only** slice:

**Introduce a narrower retrieval backend contract so `RetrievalService` stops depending directly on broad `BrainOSStore` internals.**

Practical meaning:
- keep current behavior
- keep current CLI surface
- keep current tests
- reduce direct coupling between retrieval orchestration and the full store object

This is the best next step because it improves architectural integrity without widening product scope.

---

## Do not touch yet

- Do not add external vector backends.
- Do not broaden embeddable object families beyond episodes and semantic nodes.
- Do not expand into larger cognitive/runtime orchestration work yet.
- Do not do broad ranking retuning without preserving the current eval/benchmark gates.
- Do not start feature-creep work disguised as retrieval improvement.

---

## Restart anchor

We are past the "can BrainOS have native vector retrieval at all?" phase.
That part is effectively closed for this stage.

What is now done:
- native embedding execution exists
- sqlite-vec readiness + optional behavior exists
- episode and semantic-node vector paths exist
- unified retrieval ranking exists
- operator/debug/maintenance surfaces exist
- retrieval orchestration has its first extracted boundary in `src/brainos/retrieval.py`

If the next session starts cold, begin here:
1. read this file
2. inspect `src/brainos/retrieval.py` and its dependence on `src/brainos/store.py`
3. decide the smallest backend-contract slice that reduces coupling **without changing retrieval behavior**

That is the right restart point.
