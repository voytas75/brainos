# BrainOS bounded usage case — recall continuity rerun with alternate wording

## Status
Rerun of the continuity-style recall case using different English phrasing to check whether the previous weakness was only a wording artifact or a repeatable ranking pattern.

## Artifact paths
- DB: `/tmp/brainos-recall-continuity-rerun-1780497697.db`
- Raw log: `/tmp/brainos-recall-continuity-rerun.log`

## Queries used
- `After we finished the BrainOS decision-check closeout, what was the next bounded step?`
- `What should we keep doing now that the rerun passed?`
- `Which decision captured the current BrainOS direction after trust was restored?`

Also checked:
- `retrieval-explain` for all three queries

## Result summary
### Query A — next bounded step after closeout
FAIL for top-hit ranking:
- top result = `dec-fix-first`
- expected stronger result = `dec-rerun`
- `retrieval-explain` showed the same weak ordering

### Query B — what should we keep doing now that the rerun passed
FAIL for current-direction continuity:
- only result = `dec-rerun`
- expected stronger result = `dec-current-direction`
- `retrieval-explain` matched the same outcome

### Query C — which decision captured the current direction after trust recovery
FAIL for top-hit ranking:
- top result = `dec-fix-first`
- `dec-current-direction` appeared second
- `retrieval-explain` showed the same ordering problem

## Interpretation
This is no longer plausibly just a one-query wording artifact.

The repeated pattern is:
- BrainOS retrieves from the right continuity neighborhood,
- but ranking is still weak for sequence/current-direction questions,
- lexical anchor terms like `decision-check`, `closeout`, or generic `decision` appear to dominate too much over temporal/current-state relevance.

## Comparison vs previous continuity case
Previous continuity case:
- already showed weak ranking for “after closeout” and “current direction after rerun”

This rerun:
- repeats the same class of weakness under alternate phrasing
- in one query (`What should we keep doing now that the rerun passed?`) it is even sharper because the current-direction record is not surfaced first at all

## Verdict
Overall verdict:
- **FAIL for continuity top-hit trust**

This does not mean recall is broken globally.
It means continuity-style ranking is now a repeated, evidence-backed weakness.

## Recommended next move
The watch-only posture is no longer enough.

Recommended next action:
- open one bounded retrieval-quality slice focused specifically on continuity/current-direction ranking for decision recall

Boundaries for that slice:
- do not redesign all recall scoring
- do not widen into general ontology work
- target continuity-style decision ranking only

## Bottom line
The continuity-ranking weakness repeated under different wording.
That is enough evidence to justify a small focused follow-up slice rather than more passive observation.
