# Next slice brief — ambient vs explicit runtime posture contract v1

## Recommended slice
Define and document the contract between ambient capability detection and explicit-path readiness so BrainOS operator surfaces stop feeling contradictory and instead report two intentionally different runtime truths.

## Why this now
Manual smoke testing showed that `capabilities` / `retrieval-health` and `sqlite-vec-readiness` can report different runtime states for valid reasons, but the system does not yet explain that difference clearly enough.

## Goal
Make the runtime-posture contract explicit: what ambient capability means, what explicit readiness means, and which signal each operator surface should report.

## Scope

### Do now
1. Write one short contract doc for ambient vs explicit runtime posture.
2. Lightly align README/API/runtime surfaces so the distinction is visible.
3. Avoid further behavior changes in this slice.

### Do later
- optional unified combined runtime summary
- richer provenance fields
- configurable health-runtime source-of-truth policy

## Acceptance checks
- one explicit contract doc exists.
- docs explain why `capabilities` and `sqlite-vec-readiness` can differ.
- current surface behavior is described honestly.
- no new runtime behavior is introduced.

## Rollback
If this turns into a runtime redesign, revert to a smaller verdict-only doc.

## Anti-goals
- do not retune retrieval
- do not redesign readiness flow
- do not change health behavior in this slice
