# Contributing to BrainOS

Thanks for taking a look at BrainOS.

This project is still early-stage and local-first, so the best contributions are usually small, well-scoped, and easy to verify.

## Before you start

Please:
- read `README.md` for the project overview
- read `docs/api.md` for the current CLI and Python surface
- read `docs/implementation-notes.md` for design tradeoffs and known spec gaps

## Development setup

Install dependencies:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest -q
```

Run a minimal local smoke path:

```bash
uv run brainos --db ./brain.db init
uv run brainos --db ./brain.db wm-set agent_state '{"mode":"ready"}'
uv run brainos --db ./brain.db episode-add session-1 'BrainOS initialized' --metadata-json '{"source":"smoke"}'
uv run brainos --db ./brain.db episode-search BrainOS --limit 5
uv run brainos --db ./brain.db ledger
```

## Contribution guidelines

Prefer contributions that are:
- small and bounded
- easy to test locally
- consistent with the current local-first architecture
- honest about what is implemented versus deferred

Please avoid:
- broad speculative rewrites
- mixing unrelated changes in one PR
- overstating incomplete runtime capabilities in docs or code comments

## Pull requests

A good PR should include:
- a clear summary of what changed
- why the change is needed
- the smallest meaningful verification step (`pytest`, smoke path, or both)
- documentation updates when behavior or interfaces change

## Issues

If you open an issue, include:
- expected behavior
- observed behavior
- reproduction steps
- relevant CLI output or test failure
- environment notes when they matter (`uv`, Python version, sqlite-vec availability, embedding config path)

## Documentation policy

Tracked `docs/` should stay focused on canonical project docs.
Working notes, archives, dated experiments, and local-only material should not be added to the main tracked docs surface.
