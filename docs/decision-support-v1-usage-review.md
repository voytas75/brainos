# BrainOS decision-support v1 usage review

## Status
Short usage review after three real-history-derived decision-support runs executed on a separate temporary BrainOS database.

This note is about observed usefulness, not a new spec.

## Scope of the three usage cases
The runs were based on real decision material from prior collaboration history, then exercised through the current BrainOS decision-support surface:
- `decision-log`
- `recall`
- `retrieval-explain`
- `inspect`
- `decision-check`

Test DB was isolated from the main BrainOS state.

## Cases used
### 1. BrainOS collaboration posture
Question:
- how BrainOS should be used in collaboration now

Recommended direction:
- use BrainOS as cautious decision-support / evidence layer
- do not treat it as an autonomous decision chooser yet

### 2. PromptManager next-slice direction
Question:
- what the next PromptManager slice should optimize for

Recommended direction:
- stay focused on local-first prompt asset capture/import and quick-capture-to-draft posture
- do not widen early into chains/analytics/workstation sprawl

### 3. OpenClaw memory follow-up direction
Question:
- what the safer next step is for memory follow-up

Recommended direction:
- prefer lightweight router/index and promoted knowledge buckets
- avoid heavy migration / separate KB expansion unless later pain justifies it

## What worked well
### 1. Decision brief storage felt real enough
The current decision object shape was sufficient to represent all three cases without immediately collapsing back into vague note-taking.

That is a good sign.
The structure is opinionated, but not yet overbearing.

### 2. Recall and explain were useful
For all three cases:
- `recall` surfaced the stored decision object,
- `retrieval-explain` returned the expected decision as the top compact result.

This means the new decision object is not just storable; it is actually reachable through the retrieval surface.

### 3. Inspect/provenance is already practically useful
`inspect` returned:
- the stored record,
- related ledger events,
- related refs.

This makes the decision-support layer more trustworthy and debuggable than a pure note blob.

### 4. Conflict-check can catch a real conflict
For the BrainOS posture case, a deliberately competing active decision with the same `entity_id` and different recommendation produced a `conflict` result.

That is the right kind of success.
It shows the checker can detect a meaningful clash, not just emit decorative warnings.

## What was weaker
### 1. `decision-check` is still noisy at the caution level
Outside the deliberately conflicting case, `decision-check` produced several `caution` findings driven by shallow lexical overlap.

Examples of weak signals:
- generic question overlap (`what`, `next`, `should`)
- broad option overlap (`and`, `pause`, `now`)

This does not make the checker useless.
But it does mean the current caution layer is still too eager and not selective enough.

### 2. The strongest value is still support, not choice automation
The runs reinforced the earlier conclusion:
- BrainOS is already useful as a decision-support layer,
- but not yet something that should pretend to own the final choice.

That confirms the current product boundary rather than challenging it.

## Practical verdict
Decision-support v1 passed this usage review.

Not perfectly.
But well enough to count as a useful, honest product slice.

### Strongest parts
- decision storage shape
- retrieval/explain reachability
- inspect/provenance drill-down
- conflict detection for obvious same-entity competing recommendations

### Weakest part
- caution-level precision in `decision-check`

## Recommended next move
If one technical follow-up is chosen after this review, it should be:
- narrow tuning of `decision-check`

Specifically:
- reduce the weight of generic lexical overlap,
- reduce weak option-overlap triggers,
- keep strong emphasis on shared entity + divergent recommendation,
- preserve inspectability of the rule reasons.

## What should not happen next
Do not respond to this review by:
- adding autonomous choice behavior,
- adding LLM-generated decision briefs,
- widening into broad workflow orchestration,
- pretending the current caution layer is already semantically smart.

## Bottom line
The current BrainOS decision-support layer is good enough to keep and use.

Its center of gravity is now clear:
- store decision briefs,
- retrieve them,
- inspect them,
- surface obvious conflicts,
- leave the final decision to the operator.

That is a credible v1.
