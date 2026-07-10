# BrainOS restart point — 2026-07-10 repair-query alias bridge

## What was actually fixed
A real user-facing retrieval failure was closed for repair-style operator queries.

Previously, these natural phrasings could return `no_matching_content` even in runtime-ready CLI recall:
- `reindex stale vectors`
- `fix stale vectors`
- `how to fix stale vectors`
- `retrieval explain or reindex`
- `do I fix stale vectors by explain first or by reindexing`

The effective fix was **not** additional ranking pressure alone.
The working fix was a **bounded FTS query normalization bridge** in `src/brainos/store.py` so repair-style aliases can reach the right procedural content during source lookup.

## Final implementation shape
Two layers now cooperate:

1. `src/brainos/store.py`
   - `_normalize_fts_query(...)`
   - narrow alias bridge:
     - `fix -> repair, reindex`
     - `repair -> reindex`
     - `reindex -> repair`
     - `reindexing -> reindex, repair`
   - important constraint:
     - FTS fallback uses `OR` **only when alias expansion actually applied**
     - ordinary queries keep the narrower fallback behavior

2. `src/brainos/retrieval.py`
   - query-token alias expansion and procedure-intent bonus remain in place
   - this helps ranking once hits are present, but was not sufficient on its own

## Important failed path caught during work
A first version of the FTS fix was too broad.

Regression signal:
- `tests/test_retrieval_real_sample.py::test_real_sample_benchmark_pass`
- nonsense query `nonsense local dragons` began returning a hit

Interpretation:
- using `OR` as the default fallback for all normalized FTS queries widened recall too far
- this was corrected by limiting `OR` to alias-expanded cases only

## Verification that mattered
### Targeted tests
- `tests/test_fts_query_normalization_aliases.py`
- `tests/test_repair_query_alias_bridge.py`
- `tests/test_procedure_priority.py`

### Sanity pass
- `tests/test_retrieval_eval.py`
- `tests/test_retrieval_eval_anchor.py`
- `tests/test_retrieval_real_sample.py`
- `tests/test_benchmark_cli.py`

Result after narrowing the FTS fallback:
- `19 passed`

### Real CLI confirmation
On the repro DB, previously failing repair-query variants returned:
- runtime `ok`
- `zero_hit_reason = None`
- top hit = procedural repair/reindex guidance

## Commit pushed
- `c1e9af1` — `Fix repair-query retrieval alias bridging`

## What this front is now
Treat this slice as **closed** unless one of these appears:
- new false positives caused by alias-expanded FTS queries
- broader synonym classes needed beyond this bounded repair/reindex/fix cluster
- evidence that benchmark/real-sample coverage still misses an important operator phrasing family

## What was explicitly not done
- no broad retrieval redesign
- no large semantic thesaurus
- no major scoring-policy rewrite
- no attempt to solve all natural-language maintenance queries at once

## Best next front after this
If returning to BrainOS for the next bounded retrieval-quality slice, the strongest candidate is:
- **decision object recall quality**

Reason:
- this repair-query alias front is now closed enough
- authority/current-vs-legacy was already validated on bounded seeded corpus
- decision recall likely gives a fresher user-facing signal than more tuning on this exact path
