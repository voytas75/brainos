# Project Bounds — BrainOS

## Source of truth
`PLAN.md` and this file govern the stabilization cycle. Conflicts require user approval.

## Scope controls
- Implement only the accepted stabilization items in `PLAN.md`.
- New features, later work, and anti-scope require an explicit scope change.

## Technical constraints
- Runtime: Python `>=3.10`; dependencies and commands use `uv`; persistence remains SQLite local-first.
- New dependencies, public API changes, and schema changes require approval unless a minimal integrity fix is explicitly accepted.
- Provider-backed tests are case-by-case; secrets and runtime data stay outside tracked files and reports.

## Change budget
- Ordinary slice: at most 3 tracked files, 80 net lines, no new dependency.
- Before exceeding it, state the impact and obtain approval, including for `uv.lock`, CI, SSOT, or test exceptions.

## Operating rules
1. Work in named P0/P1 slices; keep each change reversible.
2. Run relevant tests plus `git diff --check`; report confirmed facts, uncertainty, and deferrals.
3. Make a local scoped commit only after verification; do not push or merge by default.
4. Stop for ambiguity, provider calls, contract migration, dependency change, or out-of-scope work.

## Require explicit approval
- Push, merge, branch protection/rulesets, and GitHub settings changes.
- Broad refactors, folder reorganization, new runtime surfaces, or provider-backed acceptance calls.
- Any claim of production scalability, concurrency, or broad retrieval quality.
