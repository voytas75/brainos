# BrainOS real usage report — 20260603-195948

## Scope
Third bounded local real-usage validation on an isolated DB, using a slightly larger continuity chain with earlier-step, next-step, and current-direction queries.

## Artifact paths
- db: `/tmp/brainos-real-usage-20260603-195948.db`
- log: `/tmp/brainos-real-usage-20260603-195948.log`

## Queries used
- `What should BrainOS keep doing now that continuity retrieval is stable?`
- `Which bounded follow-up belongs after the closeout and rerun chain?`
- `What earlier step came before the rerun and current-direction decision?`
- `What should happen after these repeated bounded passes?`

## Top hits
- current-direction explain top decision: `dec-current-direction-3`
- next-step explain top decision: `dec-rerun-3`
- earlier-step explain top decision: `dec-fix-first-3`
- repeated-passes explain top decision: `dec-rerun-3`

## Health summary
- retrieval-health status: `ok`
- benchmark ok: `True`
- freshness status: `ok`

## Verdict
- result: `PASS`

## Weirdness / crashes
- none observed in this bounded run

## Notes
- This run used a unique /tmp DB and did not touch production data.
- Payload size was increased slightly to pressure ordering across earlier-step, next-step, and current-direction cases in one chain.
