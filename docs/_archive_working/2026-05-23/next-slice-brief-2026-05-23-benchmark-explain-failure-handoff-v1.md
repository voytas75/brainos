# Next slice brief — benchmark/explain failure handoff v1

## Recommended slice
Add a small handoff surface from benchmark failures to explain-oriented debugging so an operator can move from `failed_cases` to the next diagnostic step without reconstructing the query manually.

## Why this now
BrainOS now exposes benchmark failed-case drilldown and explain-side diagnostic hints. The next small maturity gain is to connect those two surfaces more directly.

## Goal
Reduce manual friction between benchmark failure output and explain/debug follow-up.

## Scope

### Do now
1. Add a compact explain/debug handoff field to failed benchmark cases.
2. Surface the same handoff through retrieval health quality output.
3. Add focused tests and light docs alignment.

### Do later
- auto-generated explain commands
- richer expected-vs-actual compare views
- interactive debugging workflows

## Acceptance checks
- benchmark failed cases expose a clear next debug query/handoff.
- retrieval health surfaces the same handoff.
- tests stay green.
- no behavior retune.

## Rollback
If this turns into an interactive diagnostics layer, revert to the simpler benchmark drilldown output and keep only the brief.

## Anti-goals
- do not embed explain results inside benchmark
- do not add command generators with environment assumptions
- do not redesign retrieval explain
