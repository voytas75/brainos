# Project Plan — BrainOS

## Goal
Stabilize BrainOS as a local-first, auditable memory core before new product work.

## Problem and users
- Problem: known security, delivery, integrity, and vector-runtime gaps weaken trust despite green local tests.
- Users: BrainOS maintainers, contributors, and local operators.

## First cycle — must have
- [ ] Remediate or formally accept the `aiohttp` dependency risk with owner and review trigger.
- [ ] Add repeatable CI gates and prepare a required check for `main`.
- [ ] Make episode promotion atomic and protect it with a failure-path test.
- [ ] Define and test the vector-index dimension contract.
- [ ] Make `operator_acceptance.sh` deterministic for its declared runtime scenario.
- [ ] Synchronize status and control documents with verified evidence.

## Deferred / anti-scope
- New product features, retrieval/scoring work, HTTP/MCP/hosted runtime, and background workers.
- Broad `store.py` refactor, scalability/concurrency claims, and unsolicited provider-backed runs.

## Definition of done
- Local: lock/test gates and the bounded acceptance/regression checks are green; docs state only verified facts.
- Remote: after explicit push/settings approval, CI is green and remediation alerts/check protection are rechecked.
