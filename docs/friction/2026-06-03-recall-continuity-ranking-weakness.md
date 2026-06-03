# BrainOS friction note — recall continuity ranking weakness on small decision chain

## Status
- date: 2026-06-03
- area: `recall`
- severity: `medium`
- verdict: `fixed-validated`

## Real case
- operator task: ask BrainOS continuity-style questions about the recent sequence of BrainOS decisions
- expected BrainOS help: return the most sequence-relevant decision first, not just the most lexically overlapping one
- actual behavior: BrainOS retrieved the correct cluster of related decisions, but top-hit ranking was weak for sequence-style questions such as “what happened after X?” and “what is the current direction after Y?”

## Reproduction
- db path: `/tmp/brainos-recall-continuity-1780497568.db`
- commands used:
  - `uv run brainos --db /tmp/brainos-recall-continuity-1780497568.db recall 'What did we do after the documentation closeout in BrainOS?'`
  - `uv run brainos --db /tmp/brainos-recall-continuity-1780497568.db recall 'What is the current direction for BrainOS after the rerun?'`
  - `uv run brainos --db /tmp/brainos-recall-continuity-1780497568.db retrieval-explain 'What is the current direction for BrainOS after the rerun?'`
- minimal decision/query sample:
  - `dec-fix-first` = close docs / closeout first
  - `dec-rerun` = rerun bounded real-data usage test
  - `dec-current-direction` = continue bounded real usage with observation

## Expected vs actual
### Expected
- after-closeout query should prefer `dec-rerun`
- current-direction query should prefer `dec-current-direction`

### Actual
- after-closeout query ranked `dec-fix-first` first and `dec-rerun` below it
- current-direction query ranked `dec-rerun` first and `dec-current-direction` second
- retrieval-explain showed the same ordering pattern

## Why this matters
- trust impact: medium; the relevant continuity set is present, but top ordering is not reliable enough to read as a direct answer
- frequency guess: `repeated`

## Evidence
- report/log paths:
  - `docs/brainos-recall-continuity-usage-2026-06-03-163928.md`
  - `/tmp/brainos-recall-continuity.log`
- relevant outputs:
  - query `What did we do after the documentation closeout in BrainOS?` => top result `dec-fix-first`
  - query `What is the current direction for BrainOS after the rerun?` => top result `dec-rerun`, second `dec-current-direction`

## Working judgment
- likely class: `retrieval-quality`
- smallest next move: open one bounded retrieval-quality slice focused specifically on continuity/current-direction ranking for decision recall
- not doing now: broad recall redesign, ontology growth, or premature scoring overhaul

## Close condition
- close when continuity-style questions repeatedly rank the sequence-relevant current/next decision first across more than one small decision chain

## Follow-up evidence
Confirmed on rerun with alternate wording:
- `docs/brainos-recall-continuity-rerun-2026-06-03-164137.md`
- `/tmp/brainos-recall-continuity-rerun.log`

## Resolution
A narrow continuity-ranking fix was applied in `src/brainos/store.py` for decision recall only.

Validated with:
- focused regression suite:
  - `tests/test_operational_recall.py`
  - `tests/test_explain_cli.py`
  - `tests/test_retrieval_eval.py`
  - `tests/test_retrieval_real_sample.py`
- result: `18 passed`
- isolated continuity rerun after the fix:
  - after-closeout query => top result `dec-rerun`
  - keep-doing-now query => top result `dec-current-direction`
  - current-direction-after-restored-trust query => top result `dec-current-direction`

## Final judgment
- status moved from `confirmed` to `fixed-validated`
- no broader retrieval redesign was needed
- keep watching continuity/current-direction wording in future bounded usage, but this friction note is closed for now
