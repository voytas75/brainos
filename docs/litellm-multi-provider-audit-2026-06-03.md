# BrainOS LiteLLM multi-provider audit - 2026-06-03

## Status verdict

BrainOS is **architecturally prepared for provider indirection**, but the **current runtime implementation is effectively Azure-only** for embeddings.

That means:
- the design intent is compatible with multiple providers behind LiteLLM
- the persisted metadata model is already generic enough (`embedding_provider`, `embedding_model`, `embedding_profile`)
- but the active adapter, health checks, docs, and tests are currently bound to Azure-specific env names and Azure-specific validation rules

So the right framing is:

> **provider-agnostic in storage contract, single-provider in execution path**.

---

## Why this audit exists

Goal of this note:
- document the current repo truth
- identify where Azure is hardwired today
- capture proven LiteLLM multi-provider patterns worth borrowing instead of inventing custom logic
- give a clean next-step plan that works across sessions

This note is intended as a **multi-session working document**.

---

## Repo audit - current BrainOS posture

### 1. Current execution path is Azure-specific

The active embedding adapter is `LiteLLMEmbeddingAdapter` in:
- `src/brainos/embedding.py`

Observed facts:
- contract reports `provider_path = "litellm"`
- contract reports `operational_provider = "azure"`
- required env is hardcoded to:
  - `BRAINOS_EMBEDDING_MODEL`
  - `AZURE_API_BASE`
  - `AZURE_API_KEY`
  - `AZURE_API_VERSION`
- runtime call passes Azure-specific arguments into `litellm.embedding(...)`
- returned metadata hardcodes `provider: "azure"`

Consequence:
- changing only `BRAINOS_EMBEDDING_MODEL` to e.g. `openai/text-embedding-3-small` or `ollama/nomic-embed-text` is **not enough**
- the adapter will still require Azure env and still label the provider as Azure

Key files:
- `src/brainos/embedding.py`
- `src/brainos/store.py`

---

### 2. Store/schema contract is more generic than the adapter

The storage layer already carries generic metadata fields:
- `embedding_provider`
- `embedding_model`
- `embedding_profile`
- `embedding_dimensions`

This is good news.
It means the database contract does **not** force Azure.

In other words:
- storage semantics are reusable
- adapter/config semantics are not yet reusable

Relevant files:
- `src/brainos/schema.py`
- `src/brainos/store.py`
- `docs/embedding-contract-and-vector-metadata-design-v0.md`

---

### 3. Health/doctor surfaces are also Azure-bound

`src/brainos/health.py` imports the adapter contract and validates environment variables derived from that contract.

Today this means health checks assume:
- Azure env names
- Azure API base format rules
- Azure API version semantics
- model format rule tuned to the current path

Consequence:
- even if the adapter were made more generic, the health contract would still need refactor
- otherwise BrainOS would report false WARN states for non-Azure providers

---

### 4. Test suite encodes Azure as the default truth

Tests repeatedly assert:
- `operational_provider == "azure"`
- `provider == "azure"`
- required env contains only Azure keys
- example configs use `azure/<deployment>`

This is expected for the current implementation, but it means a multi-provider migration is **not** just one adapter edit.
It requires coordinated updates across:
- runtime adapter
- contract surface
- health checks
- docs
- tests/fixtures

---

### 5. Project docs already point toward provider abstraction

Internal docs explicitly describe Azure as:
- the **initial provider**
- the **current operational default**
- **not hardcoded architectural truth**

That is the right conceptual posture.
The implementation simply has not been lifted to match it yet.

Relevant files:
- `README.md`
- `docs/native-vector-architecture-brief-v0.md`
- `docs/implementation-notes.md`

---

## Precise gap summary

### What is already multi-provider-friendly

- database schema for vector metadata
- stored provider/model/profile fields
- overall "LiteLLM as execution adapter" direction
- separation between domain/store logic and provider execution boundary

### What is still Azure-coupled

- one concrete embedding adapter implementation
- env resolution logic
- health validation logic
- docs/examples
- tests and fixtures
- provider label returned from runtime

### Real current state

BrainOS does **not** yet support "swap provider by config only".
It currently supports:
- one logical profile
- one concrete operational provider path
- one provider-specific env contract

---

## External pattern scan - GitHub / LiteLLM ecosystem

I looked for established LiteLLM multi-provider patterns worth copying.
The strongest signal is: **do not build a pile of provider-specific if/else around the domain code**.
Instead, keep a thin BrainOS-side contract and put provider specifics into a declarative routing/config layer.

### Pattern A - provider-prefixed model identifiers

Common LiteLLM pattern:
- `openai/text-embedding-3-small`
- `azure/<deployment>`
- `ollama/nomic-embed-text`
- `bedrock/...`
- `vertex_ai/...`

Why this matters for BrainOS:
- provider identity can be derived from model string prefix for many cases
- the app can stay centered on one field like `BRAINOS_EMBEDDING_MODEL`
- provider-specific SDK branching stays minimized

Observed in LiteLLM upstream docs/README.

### Pattern B - stable local alias -> provider-specific backend mapping

Strong recurring pattern in LiteLLM proxy/router configs:
- app calls a **stable logical model name**
- config maps that alias to one or more provider-backed deployments
- fallback/routing can change without changing app code

Example shape from LiteLLM config ecosystem:
- `model_name: brainos-embedding-default`
- backend route points to e.g. Azure today, OpenAI tomorrow

Why this is valuable:
- BrainOS can keep `embedding_profile = brainos-embedding-default`
- provider changes become mostly config changes
- test matrix can validate alias contract instead of provider-specific app behavior everywhere

### Pattern C - model_list / router config instead of app-level provider branching

LiteLLM Proxy examples commonly use declarative config with:
- `model_list`
- `litellm_params`
- fallbacks / routing metadata
- optional cost/quality annotations

This is the right direction when:
- multiple providers are needed
- fallback policy matters
- the team wants stable logical names in the app

It is a weaker fit when:
- BrainOS wants to stay library-only and avoid running a local proxy/gateway

### Pattern D - wildcard or generic OpenAI-compatible routes

There are configs in the LiteLLM ecosystem that expose patterns like:
- `model_name: "openai/*"`
- generic OpenAI-compatible `api_base` + `api_key`
- stable logical aliases with swapable backend definitions

Why it matters:
- BrainOS may not need bespoke per-provider adapter classes for every provider
- a generic "OpenAI-compatible" path may cover several targets cheaply

Caution:
- embeddings support varies by provider and compatibility claims are uneven
- do not assume all providers expose embedding endpoints equivalently

### Pattern E - fallback/router metadata exposed at the routing layer

Recent LiteLLM work shows emphasis on:
- fallback discovery through `/models`
- wildcard matching behavior
- adaptive router definitions
- stable public model names with hidden underlying deployments

For BrainOS this suggests:
- keep the app contract simple
- expose resolved provider/model in result metadata
- keep routing policy out of store/domain code

### Pattern F - adaptive router exists, but is probably overkill for BrainOS now

LiteLLM now has an adaptive router pattern with:
- `available_models`
- quality/cost weights
- per-session routing hints

This is interesting, but probably **too heavy** for the current BrainOS need.
For embeddings, BrainOS likely wants:
- deterministic provider choice
- maybe one fallback path later
- clear provenance for which provider/model produced vectors

So adaptive routing is useful as inspiration, not as the first implementation target.

---

## Best-practice recommendation for BrainOS

## Recommended direction: config-driven provider resolution, not provider-specific adapters everywhere

Best fit for BrainOS now:

### Option 1 - minimal good path (recommended)

Keep one BrainOS embedding adapter, but make it config-driven.

Proposed contract:
- `BRAINOS_EMBEDDING_MODEL`
- optional `BRAINOS_EMBEDDING_PROVIDER`
- optional `BRAINOS_EMBEDDING_API_BASE`
- optional `BRAINOS_EMBEDDING_API_KEY_ENV`
- optional `BRAINOS_EMBEDDING_API_VERSION`
- optional `BRAINOS_EMBEDDING_EXTRA_JSON`

Resolution rules:
1. if explicit BrainOS provider config exists, use it
2. else infer provider from `BRAINOS_EMBEDDING_MODEL` prefix
3. map provider -> required runtime params
4. pass only relevant params to LiteLLM
5. report resolved provider/model/profile in result metadata

Benefits:
- no local proxy required
- minimal code churn
- preserves current architecture
- can add providers incrementally

Cost:
- BrainOS still owns some provider mapping logic
- health validation becomes more complex

### Option 2 - logical alias + LiteLLM Proxy/Gateway (stronger long-term, heavier now)

Move provider-specific routing almost entirely outside BrainOS.

BrainOS would call:
- one stable model alias (e.g. `openai/brainos-embedding-default` or proxy-native alias depending on chosen path)
- one configured local/proxied LiteLLM endpoint

Then LiteLLM config owns:
- real provider selection
- auth
- fallback
- routing policy
- future provider additions

Benefits:
- strongest separation of concerns
- most scalable for many providers and environments
- follows the mainstream LiteLLM ecosystem pattern

Cost:
- operationally heavier
- introduces proxy service lifecycle and config surface
- probably too much for current BrainOS maturity unless multi-provider becomes a central product feature

### Option 3 - per-provider adapter subclasses (not recommended first)

Example:
- `AzureEmbeddingAdapter`
- `OpenAIEmbeddingAdapter`
- `OllamaEmbeddingAdapter`
- factory selection layer

Why I do **not** recommend this first:
- duplicates logic fast
- invites drift in validation/error behavior
- BrainOS ends up rebuilding what LiteLLM is supposed to abstract

This is the classic trap.

---

## My recommendation

Use **Option 1 now**, while keeping the design compatible with **Option 2 later**.

That means:
- BrainOS keeps a single embedding boundary
- config becomes provider-aware rather than Azure-hardcoded
- provider-specific env names move behind a small resolution layer
- storage contract remains unchanged
- if needed later, the same abstraction can be redirected to a LiteLLM proxy alias without rewriting the store layer

In plain terms:

> **Do not rewrite BrainOS around many provider adapters.**
> **Do not jump to a full LiteLLM gateway unless multi-provider routing becomes a real operational need.**
> **Refactor the current Azure-only adapter into a small config-driven resolver first.**

---

## Proposed target contract for BrainOS vNext

### Public BrainOS contract

Prefer a BrainOS-owned config contract, not raw Azure naming as the primary product surface.

Suggested env surface:
- `BRAINOS_EMBEDDING_MODEL`
- `BRAINOS_EMBEDDING_PROVIDER` (optional override)
- `BRAINOS_EMBEDDING_API_BASE` (optional generic endpoint)
- `BRAINOS_EMBEDDING_API_KEY` (optional direct key)
- `BRAINOS_EMBEDDING_API_VERSION` (optional, only used where relevant)
- `BRAINOS_EMBEDDING_HEADERS_JSON` (optional, advanced)
- `BRAINOS_EMBEDDING_PROFILE` (optional, if multiple profiles ever matter)

### Backward compatibility posture

Keep Azure env support for now as compatibility input:
- `AZURE_API_BASE`
- `AZURE_API_KEY`
- `AZURE_API_VERSION`

But treat them as:
- compatibility aliases
- not the long-term primary BrainOS product contract

### Resolution model

Pseudo-order:
1. read BrainOS generic envs
2. if missing, read provider-specific compatibility envs
3. infer provider from model prefix if no explicit provider
4. build LiteLLM call kwargs from resolved provider
5. validate only the params relevant to that provider
6. return resolved provider/model in metadata

---

## Concrete refactor scope

### Slice 1 - config resolver extraction

Add a small module, e.g.:
- `src/brainos/embedding_config.py`

Responsibilities:
- parse env
- infer provider from model prefix
- map compatibility envs
- expose normalized contract like:

```python
{
  "provider_path": "litellm",
  "operational_provider": "openai" | "azure" | "ollama" | ...,
  "model": "...",
  "call_params": {...},
  "required_env": [...],
  "missing_env": [...],
}
```

### Slice 2 - adapter uses normalized resolver output

`LiteLLMEmbeddingAdapter` should:
- stop hardcoding Azure in `contract()`
- stop hardcoding Azure args in `embed_texts()`
- stop hardcoding `provider = "azure"` in result

### Slice 3 - health becomes provider-aware

`health.py` should validate based on resolved provider/config.
Examples:
- Azure may require api version
- OpenAI may not
- Ollama may need only local base URL, maybe no key

### Slice 4 - docs switch from Azure-only to Azure-first but multi-provider-capable

Docs should say:
- current tested default = Azure
- supported contract = provider-aware LiteLLM path
- provider examples = at least Azure + one non-Azure example

### Slice 5 - tests move from single fixed provider to provider matrix

Keep:
- one Azure compatibility test

Add:
- provider inference tests
- generic config resolution tests
- at least one non-Azure happy-path fixture
- health contract tests per provider family

---

## Acceptance criteria for a good multi-provider slice

A slice is good enough when all of this is true:

1. BrainOS can run embeddings with Azure exactly as before.
2. BrainOS can run at least one second provider without code edits.
3. Health output reflects the active provider contract instead of Azure assumptions.
4. Runtime result metadata reports the actual resolved provider and model.
5. README documents the generic contract and Azure compatibility path.
6. Tests cover Azure compatibility plus at least one non-Azure path.

---

## Suggested first non-Azure target

Best first extra provider candidates:

### OpenAI embeddings
Pros:
- conceptually closest to current path
- strong LiteLLM support
- low conceptual change

### Ollama embeddings
Pros:
- local/dev-friendly
- good for offline or low-cost testing
- proves the abstraction really is provider-flexible

My recommendation:
- **first add OpenAI or Ollama**
- if the goal is product realism, choose **OpenAI**
- if the goal is local/dev flexibility and abstraction proof, choose **Ollama**

If only one should be added first, I would lean:
- **Ollama for proving the design**, or
- **OpenAI for proving production-style portability**

Given BrainOS current posture, **OpenAI is probably the cleaner first external target**.

---

## What not to do

- do not spread provider-specific `if provider == ...` logic through store/domain code
- do not encode Azure naming as the permanent public BrainOS product contract
- do not add many provider subclasses before a normalized config contract exists
- do not introduce full adaptive routing for embeddings before basic multi-provider resolution works
- do not change storage metadata schema unless a real gap appears; current schema already looks sufficient

---

## External references captured during scan

### LiteLLM upstream
- Main repo / README: `https://github.com/BerriAI/litellm`
  - strong evidence for provider-prefixed model naming
  - strong evidence for Python SDK + Proxy dual posture
  - strong evidence for many providers behind one interface

### LiteLLM adaptive router example
- `https://raw.githubusercontent.com/BerriAI/litellm/main/litellm/proxy/example_config_yaml/adaptive_router_example.yaml`
  - useful as proof of stable alias -> routed backend pattern
  - useful as proof that LiteLLM expects declarative model/routing config
  - probably too heavy for BrainOS first slice

### LiteLLM ecosystem/config-generation examples
Observed patterns from GitHub search:
- config generators / config packs for `model_list`, fallbacks, aliases
- generic OpenAI-compatible base URL patterns
- routing metadata surfaced at config level, not application domain level

These are useful mainly as directional evidence:
- stable aliasing
- declarative routing
- keep app code thin

---

## Recommended next implementation brief

### Name
`brainos-multi-provider-embedding-config-v1`

### Goal
Refactor the current Azure-only LiteLLM embedding adapter into a provider-aware config-driven path while preserving Azure backward compatibility.

### Non-goals
- no full LiteLLM proxy adoption yet
- no adaptive router
- no broad chat/completion routing redesign
- no schema redesign unless required

### Deliverables
- normalized embedding config resolver
- provider-aware adapter contract
- provider-aware health validation
- updated README section
- tests for Azure + one second provider
- short migration note

### Recommended order
1. add resolver module
2. refactor adapter to use resolver
3. refactor health checks
4. update docs
5. update/add tests

---

## Final recommendation

Do **not** invent an elaborate provider abstraction stack.
Do **not** stay Azure-hardcoded either.

The sensible move is:

1. keep the current single embedding boundary
2. introduce a **normalized provider-aware config resolver**
3. preserve Azure compatibility
4. prove it with one second provider
5. only later decide whether a LiteLLM proxy/gateway is worth the operational cost

That gets BrainOS out of the current Azure lock-in without overengineering the next layer.
