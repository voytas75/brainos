# BrainOS maturity review — 2026-05-23

## Purpose

This document gives a developer-facing review of current BrainOS maturity with three goals:
- identify what is currently risky
- identify what should be cut or deferred
- recommend the next changes that move BrainOS toward a more mature system while staying aligned to the project goal

The intended audience is the implementation owner and any reviewer shaping the next slice.

---

## Executive verdict

BrainOS has a strong architectural core and a credible implementation direction.

Current strengths:
- SQLite-first canonical storage is the right foundation for a local memory system
- the layered memory model is coherent
- retrieval quality already has bounded regression protection
- provenance and explicit promotion are good discipline signals
- the repository has moved beyond toy status and already contains real operational and retrieval work

Current reality:
- BrainOS is a solid memory-core and retrieval-slice project
- it is not yet a mature end-to-end memory system
- the main constraint is not lack of features, but incomplete operational and quality closure around retrieval

### Bottom line

The next phase should **not** be broad feature expansion.

The next phase should be:

**turn the current promising core into a reliable memory subsystem**

That means prioritizing:
- retrieval quality stability
- health/status clarity
- vector runtime operability
- tighter scope control on what gets embedded, promoted, and expanded

---

## What is currently risky

## 1. Retrieval behavior is still more heuristic than contractual

Current recall combines:
- episodic FTS
- semantic name matching
- optional vector similarity
- hand-tuned score bonuses and penalties

That is reasonable for a bounded v0, but it creates risk if further growth continues before the retrieval contract is stabilized.

### Why this is risky
- ranking behavior can become hard to predict
- tuning can silently break protected edge cases
- local improvements can accumulate into policy drift
- debugging becomes harder as more scoring exceptions are added

### Practical risk
BrainOS could grow around a retrieval layer that appears capable but behaves inconsistently under tuning pressure.

---

## 2. Native vector support exists architecturally, but not yet as a clean operational path

The project direction for vectors is coherent:
- keep canonical state in SQLite
- use vector support as a native optional capability
- degrade gracefully when unavailable

That is the right direction.

However, operational maturity is not closed yet.

Observed live runtime capability on current host:
- `fts5: true`
- `sqlite_vec: false`
- `sqlite_vec_error: "no such module: vec0"`

### Why this is risky
- the architecture already assumes vector capability matters
- health surfaces already report vector state
- retrieval tuning is already aware of vector participation
- but operator setup and runtime reliability are not yet simple and predictable

### Practical risk
The system can end up with a gap between declared architecture and dependable day-to-day operation.

---

## 3. Health/status reporting mixes different classes of truth

Current retrieval health reporting effectively combines multiple concerns:
- runtime capability health
- vector index state
- retrieval benchmark quality
- dataset readiness

These are not the same thing.

For example, a warning state on an empty database does not mean the same thing as:
- a broken runtime
- stale vectors
- a failed ranking policy

### Why this is risky
- operators and developers cannot quickly classify the problem
- warning output becomes less actionable
- confidence in health checks drops over time

### Practical risk
A noisy health surface will train people to ignore it.

---

## 4. Eval protection is real, but still too narrow to define mature retrieval quality

The repo already shows good discipline here:
- deterministic retrieval fixtures
- session-filter protection
- weak vector-noise suppression
- real-sample benchmark coverage

This is good and worth preserving.

But it is still a bounded regression baseline, not yet a broad quality gate.

### Why this is risky
- green tests can create false confidence
- the benchmark suite may not yet represent realistic retrieval ambiguity
- ranking changes can still overfit the fixture set

### Practical risk
The project may confuse “protected regression cases” with “mature retrieval quality”.

---

## 5. Surface area is expanding faster than core reliability

The repo already includes meaningful work across:
- retrieval tuning
- retrieval explainability
- retrieval health
- vector index sync/state
- embedding adapter work
- benchmark surface

This is not inherently bad.

The risk appears if further expansion continues before retrieval and vector operations are truly stable.

### Why this is risky
- every new surface creates more policy and compatibility burden
- bugs become harder to localize
- future refactors become more expensive
- the project can start optimizing for feature presence over dependable behavior

### Practical risk
BrainOS could become broader before it becomes trustworthy.

---

## 6. Procedural memory can degrade into a generic JSON container

Procedural memory is useful in the architecture, but only if its contract stays narrow.

Without a tighter definition of:
- what a procedure is
- what execution model it serves
- what validation guarantees exist
- how it differs from notes/config/metadata

it risks becoming a loosely structured storage bucket.

### Why this is risky
- poor signal quality
- weak retrieval value
- weak future execution semantics
- harder cleanup later

### Practical risk
The project could carry a layer that looks rich structurally but contributes little operational value.

---

## 7. Promotion can create the appearance of consolidation before consolidation quality is truly controlled

Current promotion discipline is good:
- explicit preview
- explicit promotion
- duplicate-promotion protection
- ledger visibility

But promotion is still only as good as the promotion rules and target representations.

### Why this is risky
- low-value episodes may be promoted into long-lived memory
- important episodes may remain unpromoted
- semantic storage can become a secondary episode dump
- procedural promotion can encode unstable or low-value structure

### Practical risk
BrainOS may accumulate long-lived memory that is structured but not actually curated.

---

## What should be cut, deferred, or constrained now

## 1. Do not expand broad product surface until retrieval is reliable

Defer for now:
- HTTP API
- broad runtime orchestration layer
- larger external interfaces
- broad platformization work

### Reason
These add weight, but they do not solve the current maturity bottleneck.

The main problem is not exposure.
The main problem is retrieval trustworthiness and operational closure.

---

## 2. Stop adding ranking cleverness unless it strengthens a defined retrieval contract

Constrain further work on:
- ad hoc bonuses
- ad hoc penalties
- query-specific special handling
- narrow score hacks that only fix one fixture shape

### Reason
This increases local accuracy in the short term but weakens system predictability over time.

Any ranking change should now justify itself against a documented contract and protected eval set.

---

## 3. Keep embeddable object families narrow

Do not broaden vector targets yet to include:
- procedures
- ledger entries
- raw metadata blobs
- semantically weak or operationally noisy fields

Keep first-class embedding scope limited to:
- `episodes.content`
- selected `semantic_nodes` with deterministic canonical text derivation

### Reason
This preserves signal quality and keeps freshness/reindex logic manageable.

---

## 4. Do not attempt a full cognitive execution loop in the next slice

Defer broad loop/orchestration ambitions until memory retrieval is stable enough to deserve that layer.

### Reason
A more autonomous loop built on unstable memory quality only amplifies error and noise.

---

## 5. Constrain procedural memory ambition

For the next phase, procedural memory should remain minimal and disciplined.

Avoid:
- turning procedures into a universal structured blob format
- embedding procedures now
- building advanced procedural retrieval before episodic + semantic retrieval is stronger

### Reason
Procedural memory should stay useful, not merely available.

---

## What changes should be introduced next

## 1. Split health into explicit planes

Introduce separate, explicit health/status surfaces for:

### A. Runtime capability health
Questions answered:
- is FTS available?
- is sqlite-vec loadable?
- is embedding execution configured?
- is degraded non-vector mode valid?

### B. Vector index freshness health
Questions answered:
- how many objects are fresh?
- how many are stale?
- how many are missing?
- how many are in error?

### C. Retrieval quality health
Questions answered:
- does the protected eval suite pass?
- does the real-sample mini benchmark pass?
- what retrieval mode was active during evaluation?

### Why this matters
This makes diagnosis fast and keeps warning states actionable.

---

## 2. Define and freeze a retrieval contract v1 for a while

Create one explicit retrieval contract document or SSOT that defines:
- retrieval inputs and result shape
- fallback order
- session filtering rules
- vector participation rules
- vector-only suppression rules
- explainability fields
- what counts as a successful top hit in protected cases

### Why this matters
The retrieval layer should stop changing implicitly across commits.

This contract does not need to be perfect.
It needs to be stable enough to support disciplined tuning.

---

## 3. Move scoring policy into a visible, versioned tuning layer

The scoring policy should become an explicit policy surface instead of a growing set of hidden constants.

Recommended direction:
- centralize scoring constants and their meaning
- version the retrieval policy
- make explain output reference policy components clearly

### Why this matters
This turns retrieval tuning into a managed engineering activity rather than a hidden behavioral drift.

---

## 4. Add a small durable eval corpus that reflects realistic ambiguity

Add a compact but representative evaluation set covering:
- competing similar episodic hits
- strong lexical recall cases
- weak lexical / stronger semantic cases
- vector-noise suppression
- session isolation protection
- stale-vector vs fresh-text conditions
- semantic-node-helpful vs semantic-node-misleading cases

### Why this matters
The project needs a better quality anchor before more recall tuning is added.

---

## 5. Close the operational green path for vector runtime

If native vector support is part of the intended architecture, it needs one clearly documented and testable operational path.

That path should define:
- required environment variables
- loader path expectations
- readiness command
- expected success output
- expected degraded fallback behavior
- common failure classifications

### Why this matters
The system should behave predictably in either of two valid states:
- vector-ready
- degraded-but-healthy non-vector mode

Anything between those states should be classified clearly.

---

## 6. Tighten canonical text derivation for semantic embeddings

Define deterministic canonical text derivation for selected semantic nodes.

This should specify:
- which fields participate
- which properties are allowed
- key ordering
- excluded volatile fields
- how content hashes are derived

### Why this matters
Without deterministic text derivation, freshness tracking and semantic vector quality both become unstable.

---

## 7. Keep promotion as controlled curation, not pseudo-autonomy

Promotion should remain:
- explicit
- bounded
- auditable
- deterministic by rule

Do not add too much automatic intelligence to promotion in the next phase.

### Why this matters
Long-lived memory quality matters more than promotion cleverness.

---

## 8. Tighten the role of procedural memory

Add a short procedural contract describing:
- what a procedure is for
- what structure is required
- what is intentionally out of scope
- what retrieval expectations are realistic for this layer now

### Why this matters
This prevents the layer from collapsing into a generic JSON archive.

---

## Recommended next-phase sequence

## Phase 1 — retrieval reliability

Primary goal:
- make recall behavior stable, inspectable, and test-governed

Recommended work:
- split health planes
- define retrieval contract v1
- extract/version scoring policy
- strengthen eval corpus
- keep explain output focused on operator debugging

### Definition of done
- retrieval changes can be evaluated against stable expectations
- health output explains what kind of problem exists
- ranking behavior is easier to inspect and tune without guesswork

---

## Phase 2 — vector runtime operability

Primary goal:
- make vector support operationally predictable

Recommended work:
- define one canonical runtime setup path
- improve readiness/failure classification
- verify degraded-mode correctness
- verify fresh/stale/missing/error vector states explicitly

### Definition of done
- operator can distinguish environment failure from data freshness issues
- vector-ready and degraded non-vector mode are both legitimate, intelligible states

---

## Phase 3 — semantic representation and freshness discipline

Primary goal:
- make embeddings a reliable derived artifact rather than a loose side-channel

Recommended work:
- tighten canonical text derivation
- formalize freshness semantics
- formalize reindex triggers and expectations
- keep embeddable semantic targets narrowly selected

### Definition of done
- source text changes produce predictable stale/fresh transitions
- reindex behavior is deterministic and diagnosable

---

## Phase 4 — only then consider broader platform expansion

Consider only after earlier phases are stable:
- HTTP API
- wider runtime loop/orchestration
- broader automation around promotion
- wider embeddable object families
- larger external integration surface

---

## Final recommendation

The correct next move is not to make BrainOS broader.

The correct next move is to make BrainOS more trustworthy at its core.

### Recommended posture for the next slice

Treat the next slice as:

**transition from a promising storage-and-retrieval core to a reliable memory subsystem**

That means:
- prioritize retrieval stability over feature count
- prioritize health clarity over interface expansion
- prioritize operational vector closure over architectural elaboration
- prioritize curation quality over more autonomous memory behavior

If this discipline is held for the next phase, BrainOS should reach a much stronger maturity threshold without losing architectural coherence.
