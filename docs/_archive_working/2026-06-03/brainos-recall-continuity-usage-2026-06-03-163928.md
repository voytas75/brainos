# BrainOS bounded usage case — recall continuity across a small decision chain

## Status
Bounded real-usage case to test whether BrainOS can answer continuity-style questions across a small chain of related decisions, rather than only returning one fresh direct hit.

## Suggested case
Case chosen:
- create three related continuity decisions representing the recent BrainOS flow,
- then ask recall/retrieval-explain questions about earlier and current steps in that chain.

Why this case:
- it directly tests practical continuity usefulness,
- it is still bounded,
- it can reveal whether recall helps answer sequence questions or only matches surface keywords.

## Artifact paths
- DB: `/tmp/brainos-recall-continuity-1780497568.db`
- Raw log: `/tmp/brainos-recall-continuity.log`

## Decision chain used
1. `dec-fix-first`
   - first safe step after false-conflict detection = close docs / closeout first
2. `dec-rerun`
   - next bounded step after docs = rerun bounded real-data usage test
3. `dec-current-direction`
   - current direction after successful rerun = continue bounded real usage with observation

## Queries used
- `What was the first safe step after the false conflict in decision-check?`
- `What did we do after the documentation closeout in BrainOS?`
- `What is the current direction for BrainOS after the rerun?`

Also checked:
- `retrieval-explain` for query 1
- `retrieval-explain` for query 3

## Result summary
### Query 1 — first safe step after false conflict
PASS:
- top result = `dec-fix-first`
- retrieval-explain also surfaced `dec-fix-first` first

Interpretation:
- continuity retrieval can answer a direct earlier-step question reasonably well on this scale

### Query 2 — what happened after documentation closeout
WEAK:
- top result was still `dec-fix-first`
- the more sequence-relevant `dec-rerun` appeared, but not first

Interpretation:
- recall is still biased toward lexical overlap (`closeout`) more than sequence/causal continuity
- usable for browsing, but not yet strong enough to trust as a direct sequential answerer

### Query 3 — current direction after rerun
WEAK:
- top result was `dec-rerun`
- `dec-current-direction` was present but ranked second
- retrieval-explain showed the same ordering problem

Interpretation:
- the system sees the cluster, but ranking still overweights shallow query-term overlap relative to “current state” continuity

## Expected vs actual
### Expected
- earlier-step query should return the earlier-step decision first
- after-closeout query should prefer the rerun decision
- current-direction query should prefer the current-direction decision

### Actual
- first-step query behaved well
- the other two continuity queries returned the right cluster but not the best top ordering

## Friction-note decision
Yes — this is worth a friction note.

Why:
- the issue affects trust in answer quality for continuity-style usage,
- there are concrete queries and outputs,
- it is not a crash, but it can mislead next action if the top hit is read too literally.

## Verdict
Overall verdict:
- **WEAK**

This is not a failure of storage or basic retrieval.
It is a ranking/continuity usefulness weakness.

## Recommended next move
Do not redesign recall broadly.

Instead:
- record this as a friction note,
- keep bounded usage going,
- only open a bounded retrieval-quality slice if this same continuity-ranking weakness repeats.

## Bottom line
BrainOS can retrieve the relevant continuity cluster.
But for sequence-style questions, top-hit ranking is still not trustworthy enough to treat as a direct answer without operator review.
