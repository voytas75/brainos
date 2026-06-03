# BrainOS bounded usage friction note template

## Purpose
Use this note only when a real bounded BrainOS usage case produces signal worth keeping.

Do **not** log routine success noise.
Log only when one of these happens:
- false `caution`
- false `conflict`
- missed `caution`/`conflict`
- recall miss or weak retrieval result
- decision-history readability problem
- inspect/provenance confusion
- runtime/readiness surprise

This is a lightweight evidence artifact, not a backlog substitute.

## File naming
Create notes under:
- `docs/friction/`

Recommended filename:
- `YYYY-MM-DD-short-slug.md`

Example:
- `2026-06-03-decision-check-false-conflict-adjacent-workflow.md`

## Template

```md
# BrainOS friction note — <short title>

## Status
- date:
- area: `decision-check|recall|retrieval-explain|decision-history|inspect|runtime`
- severity: `low|medium|high`
- verdict: `open|confirmed|watch-only|closed`

## Real case
- operator task:
- expected BrainOS help:
- actual behavior:

## Reproduction
- db path:
- commands used:
  - `...`
  - `...`
- minimal decision/query sample:

## Expected vs actual
### Expected
- ...

### Actual
- ...

## Why this matters
- trust impact:
- frequency guess: `one-off|possible-repeat|repeated`

## Evidence
- report/log paths:
- relevant outputs:
- screenshots/snippets if needed:

## Working judgment
- likely class: `false-positive|false-negative|readability|retrieval-quality|runtime|unknown`
- smallest next move:
- not doing now:

## Close condition
- what evidence would let us close this:
```

## Minimum bar before creating a note
Do not create a friction note unless all three are true:
1. it came from a real bounded usage case,
2. there is at least one concrete command/query/decision example,
3. the result could plausibly affect trust or next action.

## Triaging rule
After creating a note, classify it immediately:
- `watch-only` = keep observing, no immediate code change
- `confirmed` = bounded follow-up slice justified
- `closed` = explained or fixed

Default to `watch-only` unless the problem is clearly reproducible and trust-relevant.

## Anti-goals
- do not log every successful use
- do not create broad product notes from one case
- do not jump from one friction note to feature expansion
- do not mix multiple unrelated issues into one note
