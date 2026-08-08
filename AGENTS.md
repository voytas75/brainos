# BrainOS Agent Contract

## Scope
Work only on the accepted stabilization cycle in `PLAN.md` and `BOUNDS.md`.

## Canonical commands
- `uv lock --check`
- `uv run --extra dev --group dev --frozen ruff check .`
- `uv run --extra dev --group dev --frozen ruff format --check .`
- `uv run --extra dev --group dev --frozen pyright`
- `uv run --extra dev --group dev --frozen pytest -q`

## Always
- Inspect repository state and the relevant control documents before a material change.
- Preserve documented CLI success formats; keep JSON outputs machine-readable and errors on stderr with a non-zero exit.
- Preserve local-first SQLite behavior, provenance, and honest degraded-runtime reporting.
- Add a focused regression test before changing proven behavior.

## Ask first
- New dependencies, schema/public API changes, provider-backed calls, or changes beyond the slice budget.
- Push, merge, GitHub settings, branch protection, or security-policy changes.

## Never
- Commit secrets, local databases, generated artifacts, or provider credentials.
- Add features, hosted/server surfaces, broad refactors, or cleanup unrelated to the active slice.

## Done
Report changed files, verification performed, confirmed outcome, and deferred suggestions.
