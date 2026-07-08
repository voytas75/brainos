# Typed ingest and corpus hygiene

## Purpose
This slice improves the quality of **new** BrainOS episode entries with near-zero extra operator burden.

It adds:
- lightweight content normalization
- lightweight canonical episode kinds
- simple metadata defaults for new entries

It does **not** add a heavy schema system or require migration of existing data.

## Canonical kinds
Supported canonical kinds for new entries:
- `fact`
- `decision`
- `procedure`
- `note`
- `observation`

Default:
- `kind: note`

Unknown or legacy kinds fall back safely to `note`.

## Metadata defaults
For new entries, BrainOS now defaults:
- `kind: note`
- `source: manual`

Optional supported metadata:
- `topic`
- `source`
- `authority`

Recommended `authority` values for new authoritative artifacts:
- `canonical`
- `working`
- `supporting`

## CLI examples
Simple usage still works:
```bash
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized'
```

Optional lightweight typed usage:
```bash
uv run brainos --db ./brain.db episode-add session-1 'Operator decided to keep retrieval smoke bounded' --kind decision --topic retrieval --source manual
```

JSON metadata still works and remains backward compatible.

## When to use typed ingest
Use typed ingest when a new entry would benefit from one more bit of retrieval context without slowing capture much.

Good fits:
- a stable fact worth finding later
- a decision or bounded next-step note
- a reusable procedure fragment
- an observation about runtime, corpus quality, or operator handling

Not the goal:
- turning every note into a formal schema exercise
- backfilling the historical corpus aggressively
- forcing operators to choose from many fields before they can save a thought

## Minimum recommended operator path
If you want the smallest useful typed-ingest habit, add only:
- `kind`
- `topic` when it is obvious
- `source` when it matters

Add `authority` only when the artifact is intentionally authoritative enough that retrieval should prefer it for source-of-truth style queries.

Recommended mental model:
- `kind` helps classify the role of the entry
- `topic` helps cluster related retrieval intent
- `source` helps preserve provenance without ceremony
- `authority` helps distinguish canonical source-of-truth entries from working or supporting notes

## Practical examples
Smallest typed path:
```bash
uv run brainos --db ./brain.db episode-add session-1 'Decision: keep retrieval smoke bounded.' --kind decision
```

Slightly richer path when topic/source are obvious:
```bash
uv run brainos --db ./brain.db episode-add session-1 'Procedure: run init, add episodes, sync vectors, then run retrieval-explain.' --kind procedure --topic smoke --source manual
```

Python example:
- [`examples/typed_ingest_flow.py`](../examples/typed_ingest_flow.py)

## Authoritative artifact mini-runbook

Use these lightweight patterns when you want retrieval to recover the *right kind* of artifact, not just a vaguely relevant one.

### When to use `authority=canonical`
Use it for entries intentionally meant to win on queries like:
- `what is the source of truth for X?`
- `which note is canonical here?`
- `what should we treat as the authoritative rule?`

Good fits:
- SSOT notes
- explicit restart points
- bounded decision carriers that define the current direction
- short reusable procedure carriers

Do **not** use `authority=canonical` for ordinary working notes just because they are useful.

### Recommended content prefixes
- `SSOT:` for source-of-truth carriers
- `Restart point:` for continuation anchors
- `Decision:` for bounded decision carriers
- `Procedure:` for short action-oriented reusable steps

These are writing conventions, not a heavy schema layer.
Their job is to improve lexical grounding and make authoritativeness easier to recover.

### Minimal examples

Canonical SSOT example:
```bash
uv run brainos --db ./brain.db episode-add session-1 'SSOT: retrieval quality interpretation lives in retrieval-quality-contract-v1.' --kind fact --topic retrieval --source manual --authority canonical
```

Working note example:
```bash
uv run brainos --db ./brain.db episode-add session-1 'Working note: compare retrieval-quality-contract-v1 with the latest pack run before changing ranking.' --kind note --topic retrieval --source manual --authority working
```

Supporting note example:
```bash
uv run brainos --db ./brain.db episode-add session-1 'Supporting note: one nearby boundary statement also mentions bounded local quality proof.' --kind fact --topic retrieval --source manual --authority supporting
```

## Design rule
This is a small hygiene slice.
The system should improve new-entry quality without making capture slower or more ceremonial.
