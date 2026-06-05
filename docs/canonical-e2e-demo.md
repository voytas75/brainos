# Canonical E2E Demo

This is the one recommended repo-local walkthrough for evaluating BrainOS honestly in a few minutes.

## Purpose

The demo is meant to show that the current local core works end to end:
- initialize a fresh database
- write working memory and episodes
- run bounded retrieval and diagnostics
- promote one episode into semantic memory
- promote one episode into procedural memory
- verify ledger integrity

It is a trustworthiness demo, not a broad product benchmark.

## Default command

```bash
./scripts/canonical_e2e_demo.sh
```

Fallback if the script is not executable in your shell:

```bash
bash ./scripts/canonical_e2e_demo.sh
```

Artifacts are written to `./artifacts/canonical-e2e/` by default.
The demo also creates a local demo database at `./brain_canonical_e2e.db` unless you pass a different DB path.

Main outputs:
- `summary.json`
- `recall.json`
- `explain.json`
- `health.json`
- `doctor.json`
- `ledger-verify.json`

## Optional vector-ready pass

The default run does not force vector sync, because that can require real embedding credentials and may trigger remote embedding calls.

If your local `.env` is already configured for embeddings and `sqlite-vec`, you can ask the demo to include vector sync:

```bash
BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC=1 ./scripts/canonical_e2e_demo.sh
```

That gives stronger evidence for the vector-ready path on the current machine. If the environment is not ready, the demo will report a degraded result instead of pretending the vector path is proven.

If you need to override the exact CLI invocation, set `BRAINOS_CLI`, for example:

```bash
BRAINOS_CLI='./.venv/bin/brainos' ./scripts/canonical_e2e_demo.sh
```

## How to read the summary

- `PASS`: the local core path worked and the bounded retrieval/runtime surfaces were green.
- `DEGRADED`: the local core path worked, but vector-ready evidence was skipped or not available in the current environment.
- `FAIL`: a core check failed, such as recall returning no ranked hits, promotion failing, schema drift, or ledger verification failing.

The summary is intentionally conservative. It only reports `PASS` when the stronger signals are actually present.

## What this demo proves

- The repo can create and use a fresh local BrainOS database.
- The CLI surfaces used in the demo are wired together coherently.
- Retrieval, explain, health, promotion, and provenance surfaces are inspectable from one artifact directory.

## What this demo does not prove

- Broad retrieval quality across arbitrary corpora.
- Production readiness of the vector path on machines that are not configured locally.
- Any hosted/server deployment mode.
