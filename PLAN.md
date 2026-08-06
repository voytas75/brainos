# Project Plan — BrainOS

## Goal
Stabilize BrainOS as a local-first, auditable memory core before new product work.

## Problem and users
- Problem: known security, delivery, integrity, and vector-runtime gaps weaken trust despite green local tests.
- Users: BrainOS maintainers, contributors, and local operators.

## First cycle — completed
- [x] Updated `aiohttp` to `3.14.3`; Dependabot REST and GraphQL report zero open alerts after dependency-graph indexing.
- [x] Added repeatable CI gates; the current default-branch SHA completed successfully.
- [x] Made episode promotion atomic and protected it with a failure-path test.
- [x] Defined and tested the vector-index dimension contract.
- [x] Made `operator_acceptance.sh` deterministic for its declared runtime scenario.
- [x] Synchronized status and control documents with verified local and remote evidence.

## Quality campaign — approved

- [ ] **P1 — Ruff baseline:** add repository-owned Ruff tooling/configuration and resolve its mechanical baseline before making it blocking.
- [ ] **P2 — strict Pyright debt:** remove strict typing errors in bounded module batches; do not use suppressions or lower strictness to manufacture a green gate.
- [ ] **P3 — required quality gate:** add Ruff and strict Pyright to frozen CI only after their full local baseline is green.

## Deferred / anti-scope
- New product features, retrieval/scoring work, HTTP/MCP/hosted runtime, and background workers.
- Broad `store.py` refactor, scalability/concurrency claims, and unsolicited provider-backed runs.

## Definition of done
- Local: lock/test gates and the bounded acceptance/regression checks are green; docs state only verified facts.
- Remote: after explicit push/settings approval, CI is green and remediation alerts/check protection are rechecked.
