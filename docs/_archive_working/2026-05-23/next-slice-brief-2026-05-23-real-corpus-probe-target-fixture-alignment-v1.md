# Next slice brief — real-corpus probe target / fixture alignment v1

## Recommended slice
Align the real-corpus probe to a small actually-present local sample so probe runs produce meaningful live evidence instead of null results from a mismatched session target.

## Why this now
The first live run of the real-corpus probe was truthful but not yet useful: it showed absent/misaligned corpus evidence and disabled vector participation rather than retrieval-quality behavior. Before any ranking conclusions, the probe must target a real local sample.

## Goal
Make the real-corpus probe point at a tiny known-present local sample or clearly report when no suitable sample target exists.

## Scope

### Do now
1. Inspect the local BrainOS database for available session_ids / sampleable content.
2. Choose the smallest meaningful target-alignment rule.
3. Update the probe to use that aligned target or return a more explicit target-missing signal.
4. Add focused tests and rerun the live probe.

### Do later
- automated session sampling heuristics
- user-configurable probe target selection
- richer live-corpus coverage

## Acceptance checks
- probe no longer silently assumes `session_id=real` when no such sample exists.
- live probe result becomes more truthful/actionable.
- tests stay green.
- no ranking retune.

## Rollback
If this turns into generalized corpus discovery or sampling infrastructure, revert to a smaller explicit-target rule.

## Anti-goals
- do not ingest new data
- do not redesign the probe into a benchmark framework
- do not change retrieval behavior
