# BrainOS bounded usage case — decision-history on a real revision

## Status
Bounded real-usage case to test whether `decision-history` is useful when a real operator-facing decision is revised, not just initially created.

## Suggested case
Case chosen:
- revise one real next-step decision after new evidence appears,
- then check whether `decision-history`, `inspect`, `recall`, and `retrieval-explain` still make the revision understandable.

Why this case:
- it is the next most relevant surface after restoring trust in `decision-check`,
- it is still bounded,
- it directly probes a known likely next friction area: history readability.

## Artifact paths
- DB: `/tmp/brainos-history-case-1780497207.db`
- Raw log: `/tmp/brainos-history-case.log`

## Flow run
Executed:
- `init`
- `decision-log` create v1
- `decision-history` after create
- `decision-log` update v2
- `decision-history` after update
- `inspect decision dec-next-slice`
- `recall 'next bounded step for BrainOS after decision-check trust recovery'`
- `retrieval-explain 'next bounded step for BrainOS after decision-check trust recovery'`

## Real decision used
Decision id:
- `dec-next-slice`

Question:
- `Jaki powinien być następny bounded krok dla BrainOS po odzyskaniu zaufania do decision-check?`

Revision sequence:
- v1 recommendation: `A` = continue bounded real usage with observation
- v2 recommendation: `B` = do a small bounded decision-history readability slice

This gave a real revision rather than a synthetic no-op update.

## Result summary
### decision-history
PASS, with one mild readability caution.

Good:
- clearly shows `current`
- clearly shows `previous`
- correctly reports `changed_fields`
- revision timeline is understandable
- recommendation change `A -> B` is visible

Mild friction:
- field-level output is still somewhat raw for `options`, `arguments`, and `metadata`
- readable enough at this size, but likely to get noisy on larger decisions

### inspect
PASS:
- ledger linkage is strong
- related events are easy to verify
- provenance posture is credible

### recall / retrieval-explain
PASS:
- the revised decision is retrieved cleanly
- retrieval-explain surfaces the decision as the top result

## Expected vs actual
### Expected
- decision revision should remain understandable after one real update
- history should make the change visible enough to support operator review

### Actual
- yes, the change is visible and usable
- no trust-relevant break appeared
- the only noticeable weakness is presentation rawness, not correctness

## Friction-note decision
No separate friction note created.

Why:
- there is no trust-relevant failure,
- the readability weakness is real but mild,
- current evidence fits `watch-only` better than immediate backlog escalation.

## Verdict
Overall verdict:
- **PASS with watch-only readability caution**

## Recommended next move
Keep using BrainOS in bounded real cases.

Current posture after this case:
- `decision-check` = usable again for bounded usage
- `decision-history` = useful enough now, but likely next improvement target if larger revisions become common

## Bottom line
This case supports the current direction:
- continue bounded real usage,
- do not open another immediate implementation loop,
- keep watching whether `decision-history` readability becomes a repeated real operator problem.
