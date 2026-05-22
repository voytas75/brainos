# BrainOS embedding contract and vector metadata design v0

## Purpose

This document defines the first implementation contract for BrainOS native vector support.

It does **not** implement vector retrieval yet.
It defines:
- embedding boundary
- vector metadata model
- freshness / stale-state rules
- interaction with LiteLLM and Azure embeddings
- the minimal design needed before `sqlite-vec` integration work

---

## Verdict

Before integrating `sqlite-vec`, BrainOS should define a strict internal contract for:
- embedding generation
- vector metadata tracking
- freshness state
- re-embedding rules

Recommended posture:
- canonical memory objects remain authoritative
- embeddings are derived artifacts
- BrainOS uses **LiteLLM** as embedding execution layer
- Azure embedding deployment is the first operational provider
- vector storage is optional and capability-gated
- freshness metadata must exist even before full vector retrieval is implemented

---

## Design principles

### 1. Canonical object first
Text-bearing memory objects remain the source of truth.

Examples:
- `episodes.content`
- selected semantic node text representations

Embeddings are secondary data derived from those objects.

### 2. Provider-agnostic domain boundary
The BrainOS domain layer should not know Azure-specific request/response details.

BrainOS should depend on:
- logical embedding profiles
- normalized vector results

LiteLLM is the execution adapter, not the domain model.

### 3. Freshness is mandatory
Derived vector state can go stale.

That means BrainOS needs explicit metadata for:
- what text was embedded
- with what model/profile
- when
- whether the source changed later

### 4. Vector support must remain optional
The product must continue to work when vector support is unavailable.

That includes:
- init
- writes
- query
- promotion
- smoke testing

---

## Embedding contract

## Goal
Create one internal contract that the rest of BrainOS can depend on.

### Conceptual interface

```python
embed_texts(texts: list[str], profile: str) -> EmbeddingBatchResult
```

This is a conceptual contract, not a final code signature.

### Input
- `texts: list[str]`
- `profile: str`

Where `profile` is a logical embedding profile name, for example:
- `brainos-embedding-default`

### Output
The normalized result should contain:
- `vectors: list[list[float]]`
- `dimensions: int`
- `provider: str`
- `model: str`
- `profile: str`
- `requested_count: int`
- `returned_count: int`

Optional but useful:
- `raw_response_id`
- `latency_ms`
- `usage_metadata`

### Error model
Expected embedding failures should be normalized into BrainOS-level error types.

Examples:
- provider unavailable
- auth/config missing
- dimension mismatch
- partial batch failure
- rate limit / transient failure

### Strong recommendation
Do not allow raw provider payloads to leak upward from the embedding adapter.

---

## LiteLLM / Azure operational model

## Recommended execution path

BrainOS embedding flow should be:

**BrainOS -> internal embedding adapter -> LiteLLM -> Azure embedding deployment**

### Why LiteLLM
- keeps provider coupling out of core code
- supports logical profiles
- allows future provider changes without changing storage semantics
- matches broader platform direction already used elsewhere

### Why Azure first
Because that is the intended operational provider for this product path.

### Important rule
Domain logic should reference:
- logical profile name

Not:
- Azure deployment names directly
- Azure SDK types
- Azure request payload structures

---

## What should be embeddable first

Start narrow.

## Initial embeddable object families

### 1. Episodes
Source text:
- `episodes.content`

Why first:
- highest recall value
- simplest text source
- already central to recall flow

### 2. Semantic nodes (selected)
Source text should not blindly be just `name`.

Recommended initial rule:
- embed only selected semantic nodes
- derive a canonical text representation from:
  - `name`
  - `type`
  - selected stable properties

Why:
- `name` alone may be too thin
- properties may carry useful meaning

### Not first
Do not start with:
- procedures as a vector target
- ledger entries as a vector target
- raw metadata blobs indiscriminately

That would add noise too early.

---

## Canonical text derivation rules

This is important because vector freshness depends on stable text derivation.

## Episodes
Canonical embedding text for episodes v0:
- exactly `episodes.content`

Optional future extension:
- prepend bounded session or type context

But not yet.

## Semantic nodes
Canonical embedding text for semantic nodes v0 should be deterministic.

Recommended shape:

```text
{name}
Type: {type}
Properties: {stable selected properties in canonical order}
```

Rules:
- only include stable, meaningful properties
- sort keys deterministically
- do not include volatile operational fields
- do not include provenance timestamps in embedding text

Why:
- prevents noisy churn
- improves stale detection correctness

---

## Vector metadata model

This is the most important part of the design.

BrainOS needs metadata even before full vector search exists.

## Recommended conceptual fields

For each embeddable object, track:
- `object_type`
- `object_id`
- `source_text_hash`
- `source_text_preview`
- `embedding_profile`
- `embedding_provider`
- `embedding_model`
- `embedding_dimensions`
- `vector_status`
- `last_embedded_at`
- `last_error`
- `last_error_at`

### `object_type`
Examples:
- `episode`
- `semantic_node`

### `object_id`
Canonical id from the authoritative table.

### `source_text_hash`
Hash of the exact canonical text used for embedding.

Purpose:
- detect staleness
- avoid redundant re-embedding
- support deterministic refresh decisions

### `source_text_preview`
Optional bounded preview for debugging.

Purpose:
- make diagnostics easier
- avoid reading the source object every time during investigation

Keep it bounded and non-authoritative.

### `embedding_profile`
Logical profile name used by BrainOS.

Example:
- `brainos-embedding-default`

### `embedding_provider`
Operational provider label.

Example:
- `azure`
- or `litellm/azure`

### `embedding_model`
Resolved provider/model identity actually used.

Purpose:
- auditability
- future migration/re-embed logic

### `embedding_dimensions`
Actual vector dimensionality returned.

Purpose:
- validation
- migration planning
- safe retrieval assumptions

### `vector_status`
Recommended values:
- `missing`
- `fresh`
- `stale`
- `error`
- `disabled`

### `last_embedded_at`
When the latest successful embedding was produced.

### `last_error`
Optional compact error summary.

### `last_error_at`
Timestamp of latest embedding failure.

---

## Suggested storage direction

Because `vec0` may be narrow, split metadata from vector storage when needed.

## Recommended structure

### Metadata table
A relational metadata table should track vector lifecycle state.

Example conceptual table:
- `vector_index_state`

### Vector table(s)
Actual vector storage should remain specialized.

Likely direction:
- one vector table for episodes
- later one vector table for semantic nodes

Example conceptual names:
- `episodes_vec`
- `semantic_nodes_vec`

### Why split them
Because metadata lifecycle and vector similarity storage have different needs.

That split helps with:
- freshness checks
- debugging
- migration
- provider/model tracking
- stale-state handling without overloading the vector table

---

## Freshness / stale-state rules

## Fresh at write time?
Not necessarily.

Recommended first posture:
- canonical write happens first
- vector state becomes `missing` or `stale`
- refresh happens explicitly later

This avoids coupling ordinary writes directly to provider calls.

## Freshness rule
An embedding is `fresh` if:
- vector exists
- `source_text_hash` matches current canonical text hash
- vector was produced with the active embedding profile policy

An embedding is `stale` if:
- source text changed
- profile/model policy changed
- vector exists but dimensions/provider metadata no longer match active policy

An embedding is `missing` if:
- no vector exists yet

An embedding is `error` if:
- latest generation attempt failed

---

## Re-embedding rules

## Trigger classes

### 1. New object
When a new embeddable object is created:
- state becomes `missing`

### 2. Source object changed
When canonical embedding text changes:
- state becomes `stale`

### 3. Embedding policy changed
When the active embedding profile/model changes:
- existing vectors may become `stale`

### 4. Failed embedding attempt
If provider call fails:
- state becomes `error`
- error metadata should be stored

## First implementation recommendation
Do not auto-re-embed synchronously on ordinary writes.

Preferred first approach:
- mark missing/stale
- add explicit refresh path later

---

## Retrieval contract implications

The future recall layer should be able to inspect vector availability without guessing.

That means retrieval logic should know:
- whether vector support exists
- whether a given object family has fresh vectors
- whether fallback mode is required

## Recommended future retrieval order
1. FTS candidates
2. vector candidates when available and fresh
3. semantic graph expansion
4. merged scoring
5. provenance-aware output

This design depends on explicit freshness metadata.

---

## Operational profiles

## Recommended initial logical embedding profile
Use one logical profile name inside BrainOS, for example:
- `brainos-embedding-default`

That profile should resolve through LiteLLM to:
- your Azure embedding deployment

### Why one profile first
- simpler migration story
- smaller policy surface
- easier debugging

Later versions may add:
- alternate profiles
- lower-cost profile
- high-accuracy profile
- migration/re-embed tooling

---

## What not to do yet

Do not do these yet:
- do not couple embeddings to every write path synchronously
- do not store opaque provider blobs as the main metadata model
- do not mix canonical object state with vector lifecycle metadata indiscriminately
- do not generalize backend switching before the native path exists
- do not expose Azure-specific SDK details to the BrainOS domain layer

---

## Recommended next implementation slice

## Slice: vector metadata + embedding boundary v0
Deliver:
- internal embedding adapter interface
- logical profile configuration contract for LiteLLM
- metadata table for vector freshness lifecycle
- source text hashing rules
- status transitions: `missing`, `fresh`, `stale`, `error`, `disabled`
- tests for deterministic text hashing and stale detection

Not required yet:
- full `sqlite-vec` retrieval
- live embedding provider calls in all normal workflows

---

## Final recommendation

BrainOS should move next toward:
- **embedding contract first**
- **vector metadata lifecycle second**
- **`sqlite-vec` storage integration third**
- **hybrid vector-aware recall after that**

Use:
- **LiteLLM** as the embedding execution boundary
- **Azure embedding model** as the initial operational provider

This preserves product coherence while keeping the vector layer native to BrainOS.
