# BrainOS native vector architecture brief v0

## Verdict

BrainOS should keep a **native vector layer inside the product architecture**.

Recommended posture for the next phase:
- canonical storage remains SQLite-first
- vector retrieval is treated as a native BrainOS capability, not an external primary subsystem
- embedding generation should use **LiteLLM** as the execution layer
- the initial embedding provider should be **Azure OpenAI embedding model behind LiteLLM**
- `sqlite-vec` is the preferred local vector storage/retrieval path when runtime support is available
- when `sqlite-vec` is unavailable, BrainOS should degrade gracefully to non-vector recall instead of forcing an external vector backend

This keeps the product coherent and avoids architectural split-brain between relational/graph memory and semantic retrieval.

---

## Why this direction

### Product reason
The current BrainOS direction is:
- local-first
- SQLite-first
- one coherent memory product
- minimal architectural drift between layers

If vector search becomes a separate primary subsystem too early, the product turns into:
- one storage model in SQLite
- another retrieval model elsewhere
- two operational surfaces
- two debugging paths
- two backup/restore concerns

That would weaken the main product idea.

### Engineering reason
The current codebase already has:
- schema discipline
- ledger integrity checks
- promotion rules
- query/recall shape
- CLI and smoke-test surface

That means the right next move is not to split architecture, but to extend it carefully.

---

## Decision

### Primary architecture decision
BrainOS should use:

**native optional vector layer inside BrainOS**

not:

**SQLite core + external vector system as the main retrieval path**

### Provider/execution decision
Embedding generation should use:

**LiteLLM -> Azure embedding model**

Why:
- preserves provider indirection
- fits the broader platform posture already used elsewhere
- avoids binding BrainOS internals directly to one vendor SDK
- allows later profile/routing control without changing BrainOS storage contract

---

## Architecture shape

## Layer 1 — canonical memory storage
This remains the source of truth.

Canonical tables:
- `wm`
- `episodes`
- `semantic_nodes`
- `semantic_edges`
- `procedures`
- `ledger`
- `episode_promotions`

Rule:
- embeddings are derived artifacts, not the canonical source of truth
- the text-bearing object remains authoritative

## Layer 2 — embedding generation
Embeddings should be generated from canonical text-bearing entities.

Initial target objects:
- `episodes.content`
- selected semantic nodes, especially `Fact` / `Concept`-like nodes

Execution path:
- BrainOS -> LiteLLM -> Azure embedding model

Recommended design rule:
- BrainOS should request embeddings through one internal embedding service boundary
- the internal service boundary should not expose Azure-specific payload shape to the rest of the codebase

## Layer 3 — native vector storage/indexing
Preferred path:
- `sqlite-vec`

Initial posture:
- optional capability
- gated by runtime detection
- must not be required for core system operation

## Layer 4 — hybrid recall
Final retrieval should combine:
- FTS5
- vector similarity
- semantic graph neighborhood
- explicit session and provenance context

This should appear as one BrainOS recall result, not as separate retrieval systems the caller must manually merge.

---

## Recommended data model direction

Current code already has the idea of:
- `episodes_vec`

That should evolve into a more explicit vector storage contract.

### Recommendation
Do not make vector rows the primary object store.

Instead, store vectors as secondary indexes keyed by canonical object ids.

Possible direction:
- vector rows for `episodes`
- later vector rows for `semantic_nodes`

Recommended conceptual model:
- `object_type` — e.g. `episode`, `semantic_node`
- `object_id` — canonical id from main tables
- `embedding_model` — model/profile identifier
- `embedding_dim` — explicit dimension
- `content_hash` — hash of embedded content to detect stale embeddings
- `updated_at`

For SQLite-native implementation, this may require:
- one `vec0` table per object family
- companion metadata table if `vec0` itself is too narrow

### Strong recommendation
Keep metadata for vector rows outside the vector payload when practical.

That makes it easier to:
- detect stale embeddings
- re-embed after content changes
- support model changes later
- audit retrieval provenance

---

## Embedding generation contract

## Goal
Make embedding generation replaceable without making vector storage replaceable yet.

### Internal contract
BrainOS should expose one internal operation conceptually like:
- `embed_texts(texts, model_profile)`

Inputs:
- list of texts
- logical embedding profile

Outputs:
- vectors
- model/profile metadata
- dimension metadata

### Important rule
Use logical model/profile names through LiteLLM, not Azure-specific model ids in domain logic.

That preserves:
- portability
- testing flexibility
- future provider changes

### Initial provider
Recommended initial provider path:
- LiteLLM profile pointing to your Azure embedding deployment

This should be documented as:
- operational default
- not hardcoded architectural truth

---

## Fallback strategy

This is critical because current runtime capability detection showed:
- `fts5 = true`
- `sqlite_vec = false`

So BrainOS must behave correctly when vector support is unavailable.

### Required fallback behavior
If vector capability is unavailable:
- BrainOS still initializes normally
- write paths still work
- recall still works in non-vector mode
- promotion still works
- capability/status surfaces clearly report vector unavailable

### Retrieval fallback order
1. FTS5 episodic recall
2. semantic name/graph recall
3. optional promotion context
4. vector similarity only when available

### Design rule
Vector unavailability should reduce recall quality, not break product behavior.

---

## Synchronization rules

This is one of the biggest architectural risks.

If embeddings are derived from canonical content, BrainOS needs a clear freshness rule.

### Recommendation
Use explicit embedding freshness tracking.

For each embeddable object track conceptually:
- source text
- source content hash
- last embedded content hash
- embedding model/profile used
- last embedded timestamp

### Behavior
If source text changes:
- canonical object changes immediately
- vector state becomes stale
- BrainOS should either:
  - mark stale and re-embed later
  - or re-embed synchronously if the path requires freshness

### Current recommendation
Prefer **mark stale + explicit refresh path** in the first implementation.

Why:
- simpler failure model
- better CLI/testability
- avoids turning normal writes into provider-coupled operations too early

---

## Retrieval design direction

### Current recall state
Current recall combines:
- FTS on episodes
- lightweight semantic node name matching

### Next vector-aware recall state
When vector support is available, recall should conceptually do:
1. FTS recall candidates
2. vector similarity candidates
3. semantic neighborhood expansion
4. merge + score + trim
5. attach provenance

### Important rule
Do not expose raw retrieval internals as the public mental model.

Public API should still look like one BrainOS recall operation.

---

## What should not happen yet

Do not do these now:
- do not make Qdrant the main architecture for BrainOS
- do not add a broad pluggable vector-backend abstraction before the native path exists
- do not bind domain logic directly to Azure SDK payloads
- do not make vector support mandatory for init/write/read
- do not auto-trigger embeddings on every write in the first slice

That would add complexity too early and weaken product coherence.

---

## Recommended next implementation slices

## Slice 1 — embedding contract + metadata design
Deliver:
- internal embedding interface
- logical LiteLLM embedding profile contract
- vector metadata model for freshness tracking
- docs + tests for stale/fresh rules

No full provider write path required yet if contract is clear.

## Slice 2 — vector status + stale state model
Deliver:
- explicit vector status surface
- per-object vector freshness tracking
- CLI visibility for vector availability and stale state

## Slice 3 — sqlite-vec integration spike
Deliver:
- capability-gated `sqlite-vec` integration
- vector row creation for episodes
- bounded retrieval proof

This should remain optional and local-first.

## Slice 4 — hybrid recall v1
Deliver:
- FTS + vector + semantic merge
- stable scoring policy
- provenance-aware output shape

---

## Risks

### 1. Runtime support risk
Current environment does not expose `vec0`.

Implication:
- architecture can be chosen now
- implementation must stay capability-gated

### 2. Derived-state drift
Embeddings can go stale when canonical text changes.

Implication:
- freshness tracking is mandatory

### 3. Over-coupling provider and domain logic
If Azure-specific payloads leak into core domain code, the architecture will rot quickly.

Implication:
- LiteLLM boundary should stay explicit

### 4. Premature backend abstraction
A too-general backend layer before the native path is real will add complexity without value.

Implication:
- native path first, optional switch later

---

## Final recommendation

For BrainOS, the right posture is:
- **native vector architecture first**
- **LiteLLM as embedding execution layer**
- **Azure embedding model as initial operational provider**
- **`sqlite-vec` as preferred local vector storage path when available**
- **graceful non-vector fallback when unavailable**

This keeps BrainOS coherent as one product.
