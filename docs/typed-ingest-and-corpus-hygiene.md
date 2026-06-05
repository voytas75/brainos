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

## Design rule
This is a small hygiene slice.
The system should improve new-entry quality without making capture slower or more ceremonial.
