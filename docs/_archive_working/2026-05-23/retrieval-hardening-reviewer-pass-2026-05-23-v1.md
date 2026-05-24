# Retrieval hardening reviewer pass — 2026-05-23 v1

## Verdict
The recent retrieval hardening block materially improved BrainOS from a promising retrieval slice into a more governable and operator-readable retrieval subsystem.

This block is now **coherent enough to pause implementation expansion** and treat the current retrieval/health/vector surfaces as a bounded v1 hardening layer.

The work did **not** make retrieval broadly mature.
It did make the current retrieval slice significantly less ambiguous, less misleading, and easier to operate.

## What is now materially covered

### 1. Retrieval behavior is more contractual than ad hoc
Covered improvements:
- retrieval-facing contract is explicit
- retrieval backend boundary is narrower and more public-facing
- scoring policy is surfaced as `retrieval-scoring-v1`
- explain output names the active scoring policy version

Reviewer judgment:
- this meaningfully reduces policy drift risk for the current bounded retrieval slice
- ranking is still heuristic, but it is less implicit than before

### 2. Runtime / freshness / quality are more correctly separated
Covered improvements:
- retrieval health now uses explicit planes: `runtime`, `freshness`, `quality`
- freshness distinguishes `issues` from non-alarming `notes`
- `disabled` is no longer conflated with `stale` or `error`
- degraded non-vector benchmark semantics are explicit
- low-evidence database posture is now explicit

Reviewer judgment:
- this directly addresses one of the biggest maturity-review risks: mixed truth classes in health output
- the health surface is now materially more trustworthy

### 3. Vector operability is substantially better bounded
Covered improvements:
- sqlite-vec readiness failures are classified
- readiness output now carries bounded action hints
- vector-state contract exists as SSOT
- sync semantics now make `fresh -> noop` explicit and interpretable
- readiness/runbook docs match the real host posture

Reviewer judgment:
- vector support is still not universally smooth operationally, but it is now much more diagnosable and less magical

### 4. Retrieval quality interpretation is much safer
Covered improvements:
- quality contract distinguishes eval from benchmark
- benchmark mode is explicitly interpreted
- benchmark failed cases now include compact failure drilldown
- benchmark failures now hand off to explain via `next_debug`
- explain now adds bounded `diagnostic_hint`
- seeded benchmark truthfulness is now explicit

Reviewer judgment:
- this is a strong improvement in operator honesty
- the system now does a better job of saying what its evidence really means

### 5. Quality protection is better, but still intentionally narrow
Covered improvements:
- benchmark corpus was tightened with a few additional ambiguity cases
- eval includes stronger wording-disambiguation protection
- docs now consistently describe the bounded nature of this protection

Reviewer judgment:
- this is enough for bounded regression protection
- it is not enough to claim mature retrieval quality outside the protected slice

## What is still meaningfully uncovered

### 1. Real-corpus quality remains under-measured
Current gap:
- current benchmark is seeded-fixture evidence, not live-corpus evidence
- eval remains narrow by design
- there is still no strong read on how retrieval behaves on a messier, naturally accumulated local corpus

Why this matters:
- the current subsystem is now easier to interpret, but not yet strongly validated against realistic corpus messiness

### 2. Retrieval ranking is governed, but not deeply justified
Current gap:
- scoring policy is visible, but still mostly heuristic
- current contract protects behavior more than it explains ranking theory
- future tuning could still create fixture-friendly but globally weak behavior

Why this matters:
- the system is safer than before, but still vulnerable to local-optimum scoring evolution

### 3. Promotion/curation quality remains a downstream risk
Current gap:
- retrieval hardening improved interpretation of stored material
- it did not yet solve whether promoted/embedded material remains high-signal over time

Why this matters:
- even good retrieval contracts cannot fully compensate for weak long-lived memory curation

## Strongest current conclusion
The biggest remaining gap is **not** more operator metadata.
The biggest remaining gap is **better evidence about retrieval behavior on realistic corpus conditions**.

That means the next best implementation gap is no longer another health/explain field.
It is a bounded step toward **realer corpus quality validation**.

## Recommended next gap
### Recommendation
**real-corpus retrieval quality probe v1**

### Why this is the best next move
Because the current hardening block has already done most of the important contract/operability cleanup. The next highest-value uncertainty is whether those improved contracts still hold under more realistic local-corpus conditions.

### Bounded shape
One small slice, for example:
- define a tiny real-corpus probe set or local-sample harness
- keep it read-only and deterministic where possible
- do not redesign benchmarking broadly
- do not retune ranking in the same slice

## Reviewer close
This hardening run was worth doing.

It reduced ambiguity.
It improved truthfulness.
It improved operator actionability.
It reduced the chance that BrainOS will confuse seeded benchmark green with real retrieval maturity.

That is a real maturity gain.
