# BrainOS repo hygiene policy — draft for review

## Purpose
This document is a short draft for aligning BrainOS repo hygiene between contributors.

It is meant to answer four practical questions:
1. what should be tracked in git,
2. what should be ignored,
3. what counts as a canonical/SSOT artifact,
4. what should stay local-only even if it is useful during development.

This draft is intentionally small.
The goal is not process overhead.
The goal is to reduce drift between contributors and keep the public repo readable, trustworthy, and low-noise.

## Governing principle
Use a **curated-by-default** policy.

That means:
- keep small, durable, reviewable, community-useful artifacts in the repo,
- keep local runtime outputs, scratch material, and mass-generated files out of the repo,
- if something matters long-term, turn it into a curated doc, test, example, or script instead of committing raw output.

## What should normally be tracked
### 1. Canonical docs and contracts
Track docs that define current project posture, public interpretation, or operational contracts.

Examples:
- `README.md`
- `CONTRIBUTING.md`
- `docs/STATUS.md`
- `docs/evidence-map.md`
- `docs/api.md`
- `docs/*contract*.md`
- bounded SSOT/continuity docs when they reflect current project state and are intentionally public

### 2. Tests that protect important behavior
Track tests that:
- protect public/runtime behavior,
- protect retrieval semantics,
- protect operator interpretation,
- protect bounded eval anchors.

Examples:
- `tests/test_health_cli.py`
- `tests/test_explain_cli.py`
- `tests/test_retrieval_eval.py`
- `tests/test_retrieval_eval_anchor.py`

### 3. Small examples and scripts
Track examples/scripts that teach or verify the intended repo-local usage.

Examples:
- `scripts/canonical_e2e_demo.sh`
- `scripts/retrieval_smoke.sh`
- `scripts/operator_acceptance.sh`
- `examples/typed_ingest_flow.py`

### 4. Curated implementation notes
Track implementation notes only when they help contributors understand current design constraints, tradeoffs, or product boundaries.

Examples:
- `docs/implementation-notes.md`
- `docs/typed-ingest-and-corpus-hygiene.md`

## What should normally stay out of git
### 1. Local runtime outputs
Do not track:
- generated artifact directories,
- local DB files,
- tmp/example runtime outputs,
- benchmark output dumps,
- ad hoc JSON captures from local runs.

Examples:
- `artifacts/`
- `brain.db*`
- `examples/tmp/`

### 2. Secrets and local environment material
Do not track:
- `.env`
- machine-specific secret config
- local tokens / keys / credentials

### 3. Working scratch and private operator notes
Do not track:
- one-off review notes,
- local breadcrumbs,
- archived scratch docs,
- private or machine-local coordination notes.

Examples:
- `.local/`
- `docs/_archive_working/`
- ad hoc local-only markdown notes

### 4. Bulk-generated evidence
Do not track raw generated evidence just because it exists.
If evidence matters, promote it into a curated artifact instead.

Prefer:
- a short doc summarizing what the run proves,
- a test that protects the behavior,
- a script that reproduces the path,
- an example that demonstrates the expected usage.

Do not prefer:
- committing large raw output trees,
- dated JSON dumps,
- machine-specific run residue.

## SSOT / canonical artifact rule
A file should be treated as a canonical repo artifact if at least one of these is true:
- it defines the current public contract,
- it is the best current entrypoint for understanding a subsystem,
- it protects behavior through test coverage,\n- it provides a bounded reproducible evaluation or smoke path,
- it is intentionally part of contributor/operator workflow.

A file should usually stay local-only if it is mainly:
- a temporary note,
- a one-session reminder,
- a debugging scratchpad,
- machine-specific output,
- a mass-generated run artifact.

## `docs/` rule
`docs/` should stay focused on:
- canonical project docs,
- contracts,
- stable implementation notes,
- curated continuity/SSOT artifacts that are intentionally public.

`docs/` should not become a dumping ground for:
- scratch notes,
- private review notes,
- archived experiments that are no longer current,
- raw output copied from local runs.

If a note is useful only locally, prefer `.local/` or another ignored local path.

## `artifacts/` rule
`artifacts/` should remain ignored.

Reason:
- contents are generated,
- often machine-specific,
- often large/noisy,
- usually better treated as ephemeral run output than source-controlled project truth.

If an artifact becomes important long-term, convert it into one of:
- a curated doc,
- a test,
- an example,
- a smoke/acceptance script.

## `examples/` rule
Examples are public teaching artifacts.
They should be:
- small,
- readable,
- intentionally stable,
- reviewed like code/docs,
- free of local runtime residue.

Keep generated example outputs in ignored paths such as `examples/tmp/`.

## Practical review checklist for contributors
Before committing a new file, ask:
1. Is this canonical, reproducible, and useful to another contributor?
2. Is this the smallest good form of the artifact?
3. Should this be a doc/test/example/script instead of a raw output file?
4. Would this still belong in the repo one month from now?
5. Is this machine-local, secret, generated, or scratch material that should stay ignored instead?

## Current recommendation
For the current BrainOS repo, the existing direction looks mostly right:
- keep `.local/`, `artifacts/`, `examples/tmp/`, local DBs, and secret env files ignored,
- keep canonical docs/tests/examples/scripts in git,
- keep SSOT-like docs only when they are intentionally public and useful beyond one local session,
- avoid committing raw run output when a curated artifact would do the job better.

## Open questions for review with the second dev
These are the only questions that likely need explicit agreement:
1. Should dated execution SSOT docs under `docs/` stay tracked when they summarize a completed work window?
2. Should there be a dedicated `docs/ssot/` or `docs/continuity/` folder for intentional continuity artifacts?
3. Do we want one extra `.gitignore` rule for any future local review-note pattern beyond `.local/` and `docs/_archive_working/`?
4. Do we want to reserve a curated location for small sample outputs, or continue to require promotion into docs/tests/examples/scripts only?

## Proposed default answer unless contributors disagree
- yes, keep intentionally public SSOT/continuity docs tracked,
- no, do not track raw review notes,
- no, do not track generated artifacts,
- yes, promote durable value into docs/tests/examples/scripts,
- yes, keep the repo small and legible even if that means leaving some local material out of git.
