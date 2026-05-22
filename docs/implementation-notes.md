# BrainOS implementation notes

This document is for development-facing details that do not belong in the main README.

Use this file for:
- implementation decisions
- spec gaps
- tradeoffs
- next-slice engineering notes

## What was implemented from the PDF

### Included now
- SQLite single-file storage core
- WAL mode
- foreign keys
- JSON validation for JSON-bearing columns
- working / episodic / semantic / procedural / ledger layers
- FTS5 full-text search for episodes
- chained ledger hashes with `previous_hash`
- indexes named in the PDF excerpt

### Deferred or made optional
- `sqlite-vec` is optional because the runtime extension may be unavailable
- full cognitive execution loop is not fully specifiable from the provided PDF excerpt
- session-based vector partitioning for >100k episodes is noted but not yet implemented

## Spec gaps noticed
- excerpt ends before the execution flow is fully defined
- the PDF DDL for `episodes_fts` and `episodes` does not specify a trigger strategy; this implementation mirrors rows in application code
- the PDF ledger schema did not include `previous_hash`, but the narrative requires cryptographic chaining; this field was added explicitly
- accepted edge predicates in code are not hard-enforced yet; the PDF presents them as vocabulary examples rather than a strict enum

## Why the repo does not use `.env` yet

Current implementation is local-only and does not require:
- secrets
- API keys
- remote endpoints
- runtime service configuration

That keeps the initial repo simpler and cleaner.

Introduce `.env` only when there is an actual external-integration need.

## Why the repo uses `uv`

This repo uses `uv` for local development because it keeps the workflow small and repeatable:
- local virtualenv management
- dependency install
- locked dependency resolution via `uv.lock`
- clean command execution with `uv run ...`

## Suggested next slice
1. optional embedding provider abstraction
2. vector table integration with runtime capability detection
3. retrieval API combining FTS + vector + graph neighborhood
4. explicit cognitive loop orchestration
5. migration/versioning support


## Hardening added after first e2e pass

- added `episode_promotions` table
- explicit duplicate-promotion blocking
- explicit validation errors for promotion metadata
- added official `scripts/e2e_smoke.sh` smoke path


## Migration + CLI polish notes

- added explicit migration coverage for v1 -> v2
- CLI now returns compact JSON errors for expected user-facing failures
- missing-object reads now fail clearly instead of printing `null`


## Vector metadata slice added

- added schema v3 with `vector_index_state`
- added embedding contract surface without provider execution
- added stale/missing lifecycle tracking for episodes and semantic nodes


## Embedding adapter slice added

- added `litellm` runtime dependency
- added real embedding adapter boundary for Azure-through-LiteLLM
- added episode embedding execution path with vector-state updates
- semantic-node execution path still intentionally deferred
