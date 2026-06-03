# BrainOS Retrieval Eval Status

## Latest operator/runtime slice
- project-local `.env` is now supported as the preferred project-scoped runtime config surface; shell env still overrides it.
- operator-first check is now `doctor`.
- LiteLLM noise is suppressed so operator CLI stays JSON-first.
- Azure embedding config validation now accepts real Azure API version shapes.
- vector sync now persists `vector_index_state` correctly under transaction.
- benchmark seeded DB now syncs vector state before scoring, so benchmark green/red reflects the seeded retrieval path instead of an unseeded fixture artifact.
- retrieval scoring constants are now grouped under an explicit `retrieval-scoring-v1` policy surface.
- retrieval/explain output now reports the active scoring policy version and bounded diagnostic/debug hints.
- retrieval quality/reporting now separates runtime, freshness, and quality planes more explicitly.
- sqlite-vec readiness/runtime semantics are documented more honestly, including explicit-path vs ambient capability posture and bounded action hints.
- a small real-corpus probe surface now exists for read-only local quality checks, without overstating it as broad corpus evidence.
- decision-support object v1 now exists as a first-class local surface (`decision-log`, `decision-list`, `decision-get`).
- recall/explain now surface stored decision briefs in bounded form.
- inspect/provenance drill-down now supports `decision` and `episode` objects.
- decision conflict checking now exists as a structured-signal-first `decision-check` surface with `clear` / `caution` / `conflict` outcomes.
- the latest bounded `decision-check` closeout is complete: structural conflict correction plus generic `option_id_overlap` calibration are documented and ready for real-data validation pressure.
- the first bounded real-data rerun after the comparability-gate fix passed: the previous false-`conflict` cluster now returns `clear`, so the current posture is bounded real usage with observation rather than immediate retuning.
- decision revision/history inspection now exists through `decision-history` with `current`, `previous`, `changed_fields`, and revision timeline output.
- decision recall quality improved through a canonical decision retrieval projection, bounded natural-query regression coverage, and a validated continuity/current-direction ranking fix for decision recall.
- repeated bounded real-usage runs now support treating the continuity/current-direction slice as operationally stable for normal usage, pending only new friction evidence.
- current verified operator state on local `brain.db`: vector freshness `fresh:30`, retrieval benchmark `5/5`, retrieval-health `status: ok`.

## Scope
Deterministic regression fixtures for unified retrieval quality, plus the first bounded decision-support operational layer.

## Current protected case classes
- lexical semantic graph query
- procedural/bootstrap query
- embedding/semantic quality query
- competing similar hits (`reset runtime`)
- session filter protection for vector results
- weak vector-only noise suppression

## Current gate
- `tests/test_retrieval_eval.py`

## Notes
- This is a bounded regression baseline, not a full ranking benchmark suite.
- Current fixtures are deterministic and monkeypatched by design.
- Future tuning should preserve or intentionally revise these expectations.
- Benchmark interpretation now distinguishes `vector-ready` from `degraded-non-vector` runs so degraded-path output is not read as the same class of signal as a vector-ready pass/fail.
- Decision support is intentionally scoped as operator-facing recommendation support, not autonomous choice.
- Retrieval quality interpretation SSOT: `docs/retrieval-quality-contract-v1.md`.
- Retrieval contract SSOT: `docs/retrieval-contract-v1.md`.
- Runtime posture SSOT: `docs/runtime-posture-contract-v1.md`.
- Vector-state / maintenance semantics SSOT: `docs/vector-state-contract-v1.md`.
- Decision-support SSOT: `docs/decision-support-contract-v1.md`.
- Review closeout note: `docs/decision-support-v1-review.md`.
- Usage review note: `docs/decision-support-v1-usage-review.md`.
- Decision-check v2 direction brief: `docs/decision-check-v2-structured-signal-brief.md`.
- Decision-check v2 closeout note: `docs/decision-check-v2-closeout-2026-06-03.md`.
- Bounded real-data rerun note: `docs/brainos-realdata-bounded-rerun-2026-06-03-140404.md`.
- Decision recall quality brief: `docs/decision-recall-quality-slice-v1-brief.md`.
- Continuity-ranking friction note (closed/fixed): `docs/friction/2026-06-03-recall-continuity-ranking-weakness.md`.
- Real-usage validation reports: `docs/brainos-real-usage-20260603-194037.md`, `docs/brainos-real-usage-20260603-194509.md`, `docs/brainos-real-usage-20260603-195948.md`.

## gate_reason
Expanded eval fixture baseline must stay green before scoring changes are trusted.

- lexical-overlap preference when similar vector hits compete


## Real-sample benchmark pass v0
- queries now include more natural BrainOS-like phrasing
- protects session filtering on vector hits
- checks maintenance/reindex retrieval wording
- keeps nonsense/noise suppression as a hard gate
- score components are now surfaced on ranked hits for operator/debug visibility
- benchmark mode should be read together with runtime capability: `vector-ready` and `degraded-non-vector` are intentionally different operator states
