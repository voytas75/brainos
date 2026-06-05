# Post aiohttp update regression check — 2026-06-05

## Scope
Post-change regression check after bumping transitive dependency `aiohttp` in `uv.lock` from `3.13.5` to `3.14.0`.

Goal: verify that BrainOS still works end-to-end and that no obvious retrieval/runtime regression was introduced.

## Important note
The first attempt produced misleading degraded results because `.env` was sourced without exporting variables to child processes.

The valid runs below were executed with:

```bash
set -a
source .env
set +a
```

So the final verdict is based only on the corrected runs.

## Test 1 — retrieval green-path smoke
Result: **PASS**

Key signals:
- `runtime_status: ok`
- `top_ranked_count: 3`
- `health_status: ok`

Artifacts:
- `artifacts/retrieval-smoke-latest-2/summary.json`
- `artifacts/retrieval-smoke-latest-2/recall.json`
- `artifacts/retrieval-smoke-latest-2/explain.json`
- `artifacts/retrieval-smoke-latest-2/health.json`

## Test 2 — bounded usage test
Result: **PASS**

Fresh DB:
- `/tmp/brainos-usage-20260605-091755.db`

Flow covered:
- `init`
- `capabilities`
- `sqlite-vec-readiness`
- `episode-add`
- `episodes-list`
- `vector-index-sync-batch`
- `3x recall`
- `3x retrieval-explain`
- `retrieval-health`

Observed behavior:
- `sqlite durability` -> top hit matched `SQLite WAL improves durability and concurrent access behavior.`
- `explicit sqlite-vec runtime loading` -> top hit matched `BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.`
- `BRAINOS_SQLITE_VEC_PATH` -> top hit matched expected runtime-loading entry.
- `retrieval_runtime.status = ok`
- `retrieval-health.status = ok`
- benchmark in health: `10/10 passed`

## Test 3 — short real-usage regression check
Result: **PASS**

Fresh DB:
- `/tmp/brainos-real-usage-20260605-091755.db`

Seeded entries:
- one `decision`
- one `procedure`
- one `fact`

Queries checked:
1. `What should we keep doing now that the rerun passed?`
   - top hit: `procedure`
   - runner-up: `decision`
2. `What is the next bounded step after the rerun passed?`
   - top hit: `decision`
   - runner-up: `procedure`
   - `confidence_hint: tight_ranking`

Observed behavior:
- `retrieval_runtime.status = ok`
- `retrieval-health.status = ok`
- `operator_summary` and `top_hit_evidence` were present and interpretable
- type-sensitive ranking remained active (`decision` / `procedure` stayed near the top for action-oriented prompts)

## Verdict
**No functional regression detected** after the `aiohttp` lock update.

System status after the change:
- runtime path: OK
- vector path: OK
- retrieval: OK
- explain: OK
- health: OK

## One nuance worth noting
The real-usage check showed a tight ranking between `decision` and `procedure` for a next-step query.

This does **not** look like a bug or a new regression. It looks like a normal close semantic match between two intentionally similar, action-oriented entries.
