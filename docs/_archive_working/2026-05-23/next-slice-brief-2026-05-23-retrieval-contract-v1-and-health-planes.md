# Next slice brief — retrieval contract v1 + health planes

## Recommended slice
Introduce an explicit `retrieval-contract-v1` document and reshape `retrieval-health` into three explicit planes: `runtime`, `freshness`, and `quality`.

## Why this now
BrainOS already has a real retrieval subsystem, but the main maturity gap is still contract clarity and diagnostic clarity. This slice improves trustworthiness without widening product scope or changing retrieval behavior.

## Goal
Turn retrieval from an implemented capability into a more governable subsystem by making expected behavior and health semantics explicit.

## Scope

### Do now
1. Add `docs/retrieval-contract-v1.md` as a short SSOT for current retrieval behavior.
2. Reshape `retrieval-health` JSON into three explicit sections:
   - `runtime`
   - `freshness`
   - `quality`
3. Keep a compact top-level summary (`status`, `issues`) for operator convenience.
4. Preserve current retrieval behavior; this slice is not a ranking-tuning change.
5. Add/update focused health CLI tests for the new shape.

### Do later
- versioned scoring-policy surface
- broader ambiguity eval corpus
- narrower retrieval backend/store contract
- richer failure classifications and remediation hints

## Acceptance checks
- `docs/retrieval-contract-v1.md` exists and describes current behavior, not aspirational future behavior.
- `uv run brainos --db <tmp> retrieval-health` returns explicit `runtime`, `freshness`, and `quality` sections.
- top-level `status` and `issues` remain present.
- health output clearly distinguishes:
  - runtime capability problems
  - stale/error vector state
  - benchmark quality failures
- targeted retrieval health / benchmark / eval tests stay green.

## Rollback
If the health refactor starts spreading into unrelated code, revert to the previous output shape and keep only the retrieval contract doc.

## Anti-goals
- do not change retrieval ranking behavior
- do not add new score heuristics
- do not widen embeddable object families
- do not add HTTP/API/platform work
- do not expand procedural-memory scope
- do not combine this slice with a large backend-contract refactor

## Notes
This is a reliability-and-governance slice, not a feature slice.
