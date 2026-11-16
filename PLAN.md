# Project Plan — BrainOS

## Goal
Stabilize BrainOS as a local-first, auditable memory core before new product work.

## Problem and users
- Problem: known security, delivery, integrity, and vector-runtime gaps weaken trust despite green local tests.
- Users: BrainOS maintainers, contributors, and local operators.

## First cycle — completed
- [x] Historical first-cycle result: updated `aiohttp` to `3.14.3`; Dependabot REST and GraphQL reported zero open alerts after dependency-graph indexing at that checkpoint. This is not a current security-status assertion.
- [x] Added repeatable CI gates; the current default-branch SHA completed successfully.
- [x] Made episode promotion atomic and protected it with a failure-path test.
- [x] Defined and tested the vector-index dimension contract.
- [x] Made `operator_acceptance.sh` deterministic for its declared runtime scenario.
- [x] Synchronized status and control documents with verified local and remote evidence.

## Quality campaign — approved

- [x] **P1 — Ruff baseline:** repository-owned Ruff tooling/configuration and its mechanical baseline are green.
- [x] **P2 — strict Pyright debt:** strict type errors were removed in bounded module batches without suppressions or lowered strictness.
- [x] **P3 — required quality gate:** this branch's frozen CI requires Ruff lint/format, strict Pyright, and pytest after their full local baseline was green.

## Integrity closure — accepted

- [x] **P0.1 — Network-free diagnostics:** `retrieval-health`, `embedding-readiness`, `doctor`, and the default canonical walkthrough must not invoke an embedding provider. Provider-backed retrieval evaluation remains an explicit, separately approved action.
- [x] **P0.2 — Schema fail-closed:** an existing unknown or incomplete `user_version=0` SQLite database must not be reported as current.
- [x] **P0.3 — Canonical regression guard:** prove the default canonical walkthrough stays offline even when provider-like environment variables are present.
- [x] **P1 — Adapter and documentation integrity:** validate malformed embedding responses; synchronize current contracts, SSOT roles, and tracked documentation links.
- [x] **P2 — Controlled follow-up:** vector freshness is model-aware; LiteLLM remains mandatory pending an explicit optional-dependency transition with a BrainOS-specific missing-dependency error, core-only install matrix, isolated provider tests, and approved manifest/lock changes.

## Maintenance-only cycle — approved

- [x] **P0.1 — Developer setup alignment:** contributor and agent commands now install/run the same `uv` dependency groups as CI.
- [x] **P0.2 — Tracked documentation integrity:** public active documentation no longer links to local-only archives or a missing regression-report artifact.
- [x] **P1.1 — Evidence-gated maintenance intake closure:** P0.1/P0.2 were delivered and merged; the previous maintenance cycle is closed. This closure does not assert current CI/CodeQL status, absence of security alerts, or acceptance of new maintenance work.

## Deferred / anti-scope
- New product features, retrieval/scoring work, HTTP/MCP/hosted runtime, and background workers.
- Broad `store.py` refactor, scalability/concurrency claims, and unsolicited provider-backed runs.

## Definition of done
- Local: lock/test gates and the bounded acceptance/regression checks are green; docs state only verified facts.
- Remote: after explicit push/settings approval, CI is green and remediation alerts/check protection are rechecked.

## Dependency qualification checkpoint
- AnyIO 4.14.2, aiohttp 3.14.4, yarl 1.25.1: isolated frozen all-extras gates and offline smoke passed before publication. The lock changes were subsequently delivered through PR #14, merged as `d7aaae5`. Local runtime activation remains unverified; publication does not establish activation.

## Verified delivery checkpoint — 2026-11-16
- Maintenance closeout PR #15 merged as `5207022`; local `main` and `origin/main` matched this SHA at verification.
- CI and CodeQL for exact merge SHA `5207022006d2676be62c8aa11252ad1ec954ebf1` succeeded. CI ran lock-check, frozen dev installation, Ruff lint/format, strict Pyright and pytest.
- Earlier zero-alert receipts are historical. Security remediation and provider-backed retrieval acceptance remain separate scopes, not implied by maintenance closure.
