# Next slice brief — capability/readiness consistency fix v1

## Recommended slice
Align capability detection and retrieval-health runtime reporting with the explicit sqlite-vec readiness path so BrainOS stops reporting contradictory vector-runtime states in normal operator use.

## Why this now
Manual smoke testing found the remaining major inconsistency: `sqlite-vec-readiness` succeeds with an explicit extension path, while `capabilities` and `retrieval-health.runtime.capabilities` can still report `sqlite_vec=false` and `sqlite_vec_path=null`.

## Goal
Make runtime capability reporting more consistent with the actual explicit-load readiness behavior already proven by the system.

## Scope

### Do now
1. Inspect current capability detection code path.
2. Align it with the configured sqlite-vec load path behavior where safe.
3. Re-run readiness + capabilities + retrieval-health.
4. Add focused tests.

### Do later
- more elaborate runtime provenance fields
- environment/debug surface expansion
- broader capability caching strategy

## Acceptance checks
- explicit configured sqlite-vec path is reflected consistently in runtime capability reporting.
- readiness/capabilities/health stop contradicting each other in the common path.
- tests stay green.

## Rollback
If the fix risks over-claiming runtime capability, revert to the prior reporting and keep the inconsistency note.

## Anti-goals
- do not redesign the readiness flow
- do not widen into generic env management
- do not retune retrieval behavior
