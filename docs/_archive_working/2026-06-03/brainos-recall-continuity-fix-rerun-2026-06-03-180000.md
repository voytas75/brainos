# BrainOS bounded rerun — continuity decision ranking after focused fix

## Status
Focused post-fix rerun for the bounded continuity-ranking slice in decision recall.

This rerun stays narrow:
- decision recall ranking only
- no ontology expansion
- no broad retrieval-policy redesign

## Artifact paths
- DB: `/tmp/brainos-recall-continuity-fix-rerun.db`
- Raw log: `/tmp/brainos-recall-continuity-fix-rerun.log`

## Rerun setup
Used the same small three-decision continuity chain shape as the earlier friction evidence:
- `dec-fix-first` = close docs / closeout first
- `dec-rerun` = rerun bounded real-data usage test
- `dec-current-direction` = continue bounded real usage with observation

## Queries checked
- `What was the first safe step after the false conflict in decision-check?`
- `After we finished the BrainOS decision-check closeout, what was the next bounded step?`
- `What should we keep doing now that the rerun passed?`
- `Which decision captured the current BrainOS direction after trust was restored?`

## Result summary
### Earlier-step query
PASS:
- top recall result = `dec-fix-first`
- `retrieval-explain` top decision = `dec-fix-first`

### Next-step-after-closeout query
PASS:
- top recall result = `dec-rerun`
- previous weak ordering (`dec-fix-first` first) no longer reproduced in this rerun
- `retrieval-explain` top decision = `dec-rerun`

### Keep-doing-now query
PASS:
- top recall result = `dec-current-direction`
- `dec-rerun` is still present, but no longer ahead of the current-direction decision
- `retrieval-explain` top decision = `dec-current-direction`

### Current-direction-after-restored-trust query
PASS:
- top recall result = `dec-current-direction`
- `retrieval-explain` top decision = `dec-current-direction`

## Interpretation
The fix improved the exact weak spot that triggered the slice:
- direct earlier-step ordering still holds
- next-step phrasing now prefers the follow-on decision
- current-direction phrasing now prefers the active continuation decision

## Bottom line
This bounded rerun supports the slice as a focused ranking improvement rather than a broader retrieval redesign.
