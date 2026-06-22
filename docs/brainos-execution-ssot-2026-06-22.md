# BrainOS execution SSOT — 2026-06-22

## Purpose
This document is the current SSOT-backed execution list for the next BrainOS work window.

It is meant to preserve only the state needed to:
- resume safely after interruption,
- pick the next bounded slice correctly,
- avoid rediscovering the same repo posture,
- keep implementation aligned with the current product/trust posture.

It is **not** a changelog and not a full work log.

## Current repo posture
BrainOS is currently a **local SQLite storage and retrieval core** with:
- Python API and local CLI,
- working memory, episodes, semantic nodes/edges, procedures, decisions, and provenance,
- bounded retrieval surfaces (`recall`, `retrieval-explain`, `retrieval-health`, `retrieval-benchmark`, `real-corpus-probe`),
- vector maintenance/runtime diagnostics (`vector-index-*`, `capabilities`, `sqlite-vec-readiness`, `embedding-readiness`, `doctor`).

BrainOS does **not** currently claim:
- HTTP/MCP/server APIs,
- broad open-ended retrieval guarantees,
- autonomous execution-loop behavior.

## Governing judgment
The right near-term direction is **contract cleanup + runtime credibility closeout**, not feature expansion.

Why:
1. repo breadth is already sufficient for the current product posture,
2. the main risk is no longer missing capability but **interpretation drift**,
3. current friction is concentrated in **schema/tests/docs/runtime contract clarity**,
4. retrieval credibility should be made calmer before any additional "brain" surface expansion.

## Evidence snapshot
### Verified repo-level evidence
- Current branch: `main`
- Trust-layer closeout sequence completed on 2026-06-22 with commits:
  - `d661937` Align runtime contracts and health semantics
  - `069167e` Clarify degraded runtime messaging
  - `23ce94b` Add operator acceptance pack
  - `380a450` Document typed ingest as quality lever
  - `87f477b` Anchor realistic retrieval eval set
- Current full test posture on 2026-06-22:
  - `119 passed`
  - `0 failed`

### Completed outcomes from this execution window
1. migration-test drift removed
2. embedding contract/test/docs alignment landed
3. runtime truth table landed
4. degraded runtime messaging clarified in code and tests
5. operator acceptance pack added and documented
6. typed-ingest quality lever documented with example/test coverage
7. realistic retrieval eval anchor added and documented

## Core decision
Treat the current BrainOS backlog in this order:
1. **contract truth**
2. **runtime truth**
3. **operator evidence path**
4. **corpus/ingest quality improvements**
5. only then optional broader product expansion

---

# Active execution list

## P0 — Contract cleanup and truth alignment

### Task P0.1 — Fix schema-version migration test drift
**Goal**
Make migration tests reflect the current schema contract instead of historical slice-specific version assumptions.

**Why this matters**
A red migration test undermines trust in the whole storage layer even when the underlying product behavior is likely fine.

**Scope**
- inspect migration-related tests, especially `tests/test_vector_metadata.py`
- update assertions so they validate the **current migration contract**
- prefer checking the presence and correctness of required migrated structures over freezing the repo to an old schema milestone unless a specific historical migration guarantee is intentionally preserved

**Likely files**
- `tests/test_vector_metadata.py`
- `tests/test_migration_and_cli.py`
- `src/brainos/schema.py`
- `docs/implementation-notes.md` (only if wording needs to reflect the clarified contract)

**Definition of done**
- migration-related tests are green
- test intent is explicit: historical step verification vs current-state verification
- no hidden assumption remains that vector metadata is still the terminal schema milestone

**Rollback**
- revert test changes only; do not change schema versioning semantics casually

---

### Task P0.2 — Unify embedding provider contract
**Goal**
Choose and enforce one truthful contract for `operational_provider` across code, tests, and docs.

**Recommended decision**
Adopt: **`unknown` until the provider/model/config is actually inferable/configured**.

**Why this matters**
Pretending Azure is the active operational provider when config is absent makes runtime diagnostics less honest and increases operator confusion.

**Scope**
- explicitly decide the expected contract for `get_embedding_profile_contract()`
- align CLI/runtime surfaces using the same interpretation
- update tests that still encode an older Azure-default expectation
- update docs if they imply Azure as effective default rather than current recommended config path

**Likely files**
- `src/brainos/embedding.py`
- `src/brainos/embedding_config.py`
- `src/brainos/doctor.py`
- `src/brainos/health.py`
- `tests/test_vector_metadata.py`
- `tests/test_health_cli.py`
- `tests/test_embedding_adapter.py`
- `docs/README-DEV.md`
- `docs/implementation-notes.md`

**Definition of done**
- one consistent meaning of `operational_provider`
- `doctor`, `retrieval-health`, and direct contract surfaces agree
- tests express the same contract as runtime
- docs describe configured-provider vs unknown-provider posture plainly

**Rollback**
- revert contract wording/tests together if the chosen semantics prove inconsistent; do not leave partial mixed semantics behind

---

### Task P0.3 — Add one explicit runtime truth table
**Goal**
Give operators one short canonical explanation of what each runtime/diagnostic surface proves and what it does not prove.

**Why this matters**
Current repo knowledge is spread across multiple docs; the model is there, but the operator path is still too interpretive.

**Scope**
Add a small section or standalone doc that distinguishes at least:
- ambient capability,
- explicit readiness,
- embedding config contract,
- runtime operational health,
- retrieval quality signal.

**Minimum content**
A compact table like:
- surface
- what it tells you
- what it does not tell you
- next action when red/degraded

**Likely files**
- `docs/README-DEV.md`
- optionally `docs/runtime-posture-contract-v1.md`
- optionally `docs/STATUS.md` with a pointer only

**Definition of done**
- one canonical runtime interpretation table exists
- the table is linked from the main operator-facing doc path
- degraded/broken/unknown/configured language is consistent with code and tests

**Rollback**
- if the section adds confusion, move it to a dedicated short doc instead of deleting the clarification entirely

---

## P1 — Runtime credibility closeout

### Task P1.1 — Tighten runtime preflight semantics across recall/explain/health
**Goal**
Ensure that runtime problems are surfaced as runtime problems, not as vague retrieval weakness.

**Why this matters**
This was already identified as a priority direction and recent commits moved toward it, but the story should be finished, not half-finished.

**Scope**
- review degraded-path behavior in `retrieval`, `retrieval_runtime`, `explain`, and `health`
- verify that missing `sqlite-vec` config, readiness failure, low evidence, and ranking failure remain clearly separated
- ensure action hints are operator-usable

**Likely files**
- `src/brainos/retrieval_runtime.py`
- `src/brainos/explain.py`
- `src/brainos/health.py`
- `src/brainos/retrieval.py`
- relevant CLI/integration tests

**Definition of done**
- no common degraded path is semantically misclassified
- operator-facing wording clearly distinguishes:
  - runtime/config issue,
  - degraded non-vector mode,
  - low-evidence corpus,
  - bounded quality regression
- tests protect the distinctions

**Rollback**
- revert wording/behavior slice together if it collapses previously distinct health semantics

---

### Task P1.2 — Create a small operator acceptance pack
**Goal**
Protect the real operator journey, not just internal unit behavior.

**Why this matters**
BrainOS is an operator-facing local tool. Acceptance truth should include a few canonical diagnostic journeys.

**Recommended scenarios**
1. fresh DB, no vector config
2. explicit sqlite-vec path configured, embeddings not ready
3. vector-ready path available
4. low-evidence corpus
5. stale vector metadata after source-text change

**Possible implementation forms**
- one shell script,
- a few CLI integration tests,
- or both (preferred if kept small).

**Likely files**
- `scripts/`
- `tests/test_health_cli.py`
- `tests/test_explain_cli.py`
- `tests/test_retrieval_runtime_slice.py`
- `docs/README-DEV.md`

**Definition of done**
- the five scenarios are executable and documented
- expected PASS / DEGRADED / WARN interpretation is explicit
- this pack becomes the practical operator smoke SSOT for runtime understanding

**Rollback**
- keep the existing smoke paths if the acceptance pack becomes too broad; reduce, don’t expand

---

### Task P1.3 — Tighten degraded-mode wording and action hints
**Goal**
Preserve the important contract: **degraded ≠ broken**.

**Why this matters**
This is one of the most valuable truths in the repo, and one of the easiest to accidentally blur.

**Scope**
- inspect wording across health/explain/runtime outputs
- ensure `degraded-non-vector`, `low_evidence`, and actual failure states stay separate
- ensure recommended next steps match the class of problem

**Likely files**
- `src/brainos/health.py`
- `src/brainos/explain.py`
- `src/brainos/retrieval_runtime.py`
- `docs/retrieval-quality-contract-v1.md`
- `docs/README-DEV.md`

**Definition of done**
- degraded-mode output reads as constrained capability, not generic failure
- low-evidence reads as insufficient evidence, not regression
- benchmark/runtime interpretation order remains explicit and test-protected

**Rollback**
- revert if wording cleanup weakens precise distinctions already encoded in tests/contracts

---

## P2 — Retrieval/corpus credibility after runtime closeout

### Task P2.1 — Make typed-ingest posture an explicit quality lever
**Goal**
Turn typed ingest from a good idea into a small but explicit operational quality tool.

**Why this matters**
The repo already has a useful lightweight hygiene slice; it now needs a clearer explanation of when and why to use it.

**Scope**
- define where typed metadata actually improves downstream retrieval/corpus hygiene
- define the minimum canonical operator path for new entries
- keep the slice lightweight; do not introduce ceremony-heavy schema workflows

**Likely files**
- `docs/typed-ingest-and-corpus-hygiene.md`
- `docs/api.md`
- maybe examples under `examples/`
- tests only if behavior or defaults are extended

**Definition of done**
- typed ingest is documented as a quality/hygiene aid, not grand architecture
- the minimum recommended usage path is concrete and small
- no broad migration of existing corpus is required

**Rollback**
- keep docs-level clarification only; avoid turning this into forced schema expansion

---

### Task P2.2 — Establish a small persistent real-corpus eval set
**Goal**
Create one stable bounded eval set that protects the most important retrieval/use classes.

**Why this matters**
This is a stronger next step than broad retuning. It gives a durable SSOT for future ranking discussions.

**Scope**
- define 8–15 realistic query classes
- keep them small and representative
- avoid synthetic benchmark inflation
- use them as a continuity anchor for future retrieval-quality discussion

**Possible categories**
- canonical posture / SSOT lookup
- similar-hit disambiguation
- session-filter protection
- runtime-vs-quality interpretation
- procedural/bootstrap phrasing
- decision/backlog retrieval phrasing

**Likely files**
- `tests/test_retrieval_eval.py`
- optional separate fixture/corpus file
- `docs/retrieval-quality-contract-v1.md`
- `docs/evidence-map.md`

**Definition of done**
- small eval set exists and is stable
- docs explain what it protects and what it does not prove
- future ranking changes can be discussed against this eval SSOT instead of intuition

**Rollback**
- if the set starts ballooning, cut it back to the smallest representative protected set

---

# Explicitly deferred for now

## Do not prioritize now
1. HTTP / MCP / hosted service surfaces
2. broad retrieval retuning without fresh friction evidence
3. wider decision/autonomy expansion
4. heavy typed-schema migration of historical corpus
5. large architectural expansion for its own sake

## Why deferred
These would widen surface area before the current trust/contract layer is fully calm.

---

# Recommended execution order

## Next bounded sprint
1. `P0.1` fix migration test drift
2. `P0.2` unify embedding provider contract
3. `P0.3` add runtime truth table
4. full green test run

## Sprint after that
1. `P1.1` tighten runtime preflight semantics
2. `P1.2` build small operator acceptance pack
3. `P1.3` polish degraded-mode wording/action hints

## Only after those are calm
1. `P2.1` typed-ingest as explicit hygiene lever
2. `P2.2` small persistent real-corpus eval set

---

# Resume shortcut
If resuming later, the first question should be:

**Did a new operator pain appear after the 2026-06-22 trust-layer closeout, or are we already in optional/post-closeout territory?**

Current answer at this checkpoint:
- the trust-layer closeout slice is complete
- repo is green at `119 passed`
- next work should be chosen by fresh product/operator need, not by unfinished cleanup debt

# Primary sources reviewed
- `README.md`
- `docs/STATUS.md`
- `docs/evidence-map.md`
- `docs/retrieval-contract-v1.md`
- `docs/retrieval-quality-contract-v1.md`
- `docs/runtime-posture-contract-v1.md`
- `docs/README-DEV.md`
- `docs/implementation-notes.md`
- `docs/typed-ingest-and-corpus-hygiene.md`
- `src/brainos/schema.py`
- `src/brainos/embedding.py`
- `src/brainos/embedding_config.py`
- `tests/test_vector_metadata.py`
- `tests/test_health_cli.py`

# Verification snapshot
- repo inspection completed
- test run executed with `uv sync --extra dev && uv run python -m pytest -q`
- observed result: `113 passed, 2 failed`
