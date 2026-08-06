# Project Plan — BrainOS

## Goal
Stabilize BrainOS as a local-first, auditable memory core before new product work.

## Problem and users
- Problem: known security, delivery, integrity, and vector-runtime gaps weaken trust despite green local tests.
- Users: BrainOS maintainers, contributors, and local operators.

## First cycle — local must have
- [x] Update the local `aiohttp` lock to a patched release; remote alert closure remains post-push.
- [x] Add repeatable CI gates; remote run and required-check configuration remain post-push.
- [x] Make episode promotion atomic and protect it with a failure-path test.
- [x] Define and test the vector-index dimension contract.
- [x] Make `operator_acceptance.sh` deterministic for its declared runtime scenario.
- [x] Synchronize status and control documents with verified local evidence.

## Deferred / anti-scope
- New product features, retrieval/scoring work, HTTP/MCP/hosted runtime, and background workers.
- Broad `store.py` refactor, scalability/concurrency claims, and unsolicited provider-backed runs.

## Definition of done
- Local: lock/test gates and the bounded acceptance/regression checks are green; docs state only verified facts.
- Remote: after explicit push/settings approval, CI is green and remediation alerts/check protection are rechecked.
