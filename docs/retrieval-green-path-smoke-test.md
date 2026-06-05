# Retrieval green-path smoke test

## Purpose
This is the official bounded operational smoke test for BrainOS retrieval on a fresh database.

It exists to verify the green path for:
- vector runtime readiness
- vector index sync for new episodes
- `recall`
- `retrieval-explain`
- `retrieval-health`

It is intended to catch runtime/env regressions that may otherwise look like ordinary retrieval weakness.

## What it is not
This is **not** a broad retrieval-quality benchmark.
It does not prove that ranking is globally optimal.
It proves only that the bounded runtime + retrieval path is operational on this machine.

## When to run it
Run this smoke test when:
- retrieval/runtime behavior was changed
- sqlite-vec loading behavior was changed
- embedding/runtime env changed
- a local environment issue is suspected
- before/after a bounded retrieval slice when you want a quick green-path check

## Command
```bash
source .env
./scripts/retrieval_smoke.sh
```

Optional explicit paths:
```bash
./scripts/retrieval_smoke.sh /tmp/brainos-retrieval-smoke.db ./artifacts/retrieval-smoke
```

## PASS / FAIL meaning
### PASS
- runtime status is `ok`
- at least one ranked retrieval hit is returned
- retrieval health is readable and normally `ok`

### FAIL
Usually means one of:
- `BRAINOS_SQLITE_VEC_PATH` missing or invalid
- sqlite-vec extension cannot load
- vector sync did not establish the expected path
- bounded retrieval returned no ranked hits

## Artifacts
The script writes:
- `vector-sync.json`
- `recall.json`
- `explain.json`
- `health.json`
- `summary.json`

## Current operator reading rule
If this test fails with runtime misconfiguration, treat that as a runtime/env issue first, not as evidence that retrieval ranking is broken.
