# BrainOS multi-provider LiteLLM implementation brief - 2026-06-03

## Status
Drafted for execution.

## Why this exists

This brief turns the audit in `docs/litellm-multi-provider-audit-2026-06-03.md` into an implementation-ready slice plan.

It is intentionally short, operational, and suitable for multi-session continuation.

---

## Goal

Refactor BrainOS embedding configuration so that:
- Azure remains fully backward compatible
- at least one second provider can be added without changing store/domain code
- provider resolution becomes config-driven instead of Azure-hardcoded
- health/docs/tests reflect the resolved provider contract

---

## Non-goals

- no full LiteLLM proxy/gateway adoption in this slice
- no adaptive routing
- no broad LLM/chat/completion abstraction redesign
- no schema redesign unless a real gap appears
- no commit/push in this slice

---

## Current checkpoint

Verified from repo:
- `src/brainos/embedding.py` hardcodes Azure env + provider label
- `src/brainos/health.py` validates Azure-specific env semantics
- `src/brainos/store.py` uses the adapter via a narrow boundary and is reusable
- storage schema already supports generic `embedding_provider`, `embedding_model`, `embedding_profile`
- audit doc created: `docs/litellm-multi-provider-audit-2026-06-03.md`

---

## Recommended implementation strategy

### Principle

Keep one embedding boundary.
Move provider-specific logic into one normalized config resolver.

### Recommended new module

Create:
- `src/brainos/embedding_config.py`

This module should be the only place that knows:
- how provider is inferred
- which env names are accepted
- how compatibility aliases map into normalized config
- which LiteLLM kwargs are relevant per provider family

---

## Proposed execution slices

## Slice 1 - normalized embedding config resolver

### Deliverable
A resolver returning normalized runtime config for the active embedding path.

### Suggested interface

```python
resolve_embedding_config(profile: str | None = None) -> dict[str, Any]
```

### Minimum output contract

```python
{
  "profile": "brainos-embedding-default",
  "provider_path": "litellm",
  "operational_provider": "azure" | "openai" | "ollama" | "unknown",
  "model": "...",
  "required_env": [...],
  "present_env": [...],
  "missing_env": [...],
  "call_params": {...},
  "config_source": {...},
}
```

### Rules

1. Read `BRAINOS_EMBEDDING_MODEL`
2. Infer provider from model prefix unless explicitly overridden later
3. Support Azure compatibility env mapping
4. Build only relevant LiteLLM kwargs
5. Fail with explicit missing-config errors

### Minimum supported providers in this slice
- Azure (backward compatible)
- OpenAI **or** Ollama

Recommendation: **OpenAI first**

---

## Slice 2 - adapter refactor

### Files
- `src/brainos/embedding.py`

### Change
Make `LiteLLMEmbeddingAdapter` consume normalized resolver output instead of Azure-specific env lookups.

### Required outcomes
- `contract()` becomes provider-aware
- `embed_texts()` passes normalized kwargs into LiteLLM
- result metadata reports resolved provider/model/profile
- Azure string constants stop being the execution truth inside the adapter

---

## Slice 3 - health refactor

### Files
- `src/brainos/health.py`

### Change
Replace Azure-only validation with provider-aware validation based on normalized config.

### Required outcomes
- health output reports active provider
- only relevant required envs are validated
- Azure version validation runs only for Azure-like paths
- non-Azure providers do not produce false warnings

---

## Slice 4 - docs update

### Files
- `README.md`
- optional short note in `docs/implementation-notes.md`

### Change
Replace Azure-only operator guidance with:
- generic contract first
- Azure compatibility path second
- one second provider example

### Minimum examples
- Azure
- OpenAI or Ollama

---

## Slice 5 - tests

### Files likely affected
- `tests/test_embedding_adapter.py`
- `tests/test_health_cli.py`
- `tests/test_doctor_cli.py`
- `tests/test_json_cli_output.py`
- `tests/test_env_loading.py`
- any tests asserting fixed `provider == "azure"`

### Additions
- provider inference tests
- compatibility alias tests
- second-provider happy-path tests
- health validation tests per provider family

### Keep
- one strong Azure backward-compatibility test path

---

## Recommended config contract

### Public BrainOS contract

Preferred long-term config surface:
- `BRAINOS_EMBEDDING_MODEL`
- `BRAINOS_EMBEDDING_PROVIDER` (optional)
- `BRAINOS_EMBEDDING_API_BASE` (optional)
- `BRAINOS_EMBEDDING_API_KEY` (optional)
- `BRAINOS_EMBEDDING_API_VERSION` (optional)
- `BRAINOS_EMBEDDING_HEADERS_JSON` (optional, advanced)

### Compatibility inputs to preserve

Accept during migration:
- `AZURE_API_BASE`
- `AZURE_API_KEY`
- `AZURE_API_VERSION`

Potential future compatibility aliases if needed:
- `OPENAI_API_KEY`
- provider-local base URL envs

Important: compatibility aliases should remain **inputs**, not the primary BrainOS-facing public contract.

---

## Definition of done

This slice is done when all are true:

1. Azure path still works with existing config shape.
2. A second provider works without code edits outside the new normalized resolver path.
3. Health/doctor/json surfaces reflect the active provider contract.
4. README shows generic config first and Azure compatibility second.
5. Tests cover Azure compatibility plus one second provider.
6. No store/schema refactor is required.

---

## Rollback

Rollback is straightforward if needed:
- revert resolver/adapter/health/doc/test changes together
- restore Azure-only adapter path
- preserve audit + brief docs as historical notes

No schema rollback should be necessary.

---

## Risks

### Risk 1 - accidental pseudo-generic contract
Resolver becomes generic in naming but still Azure-shaped in assumptions.

Mitigation:
- add at least one second-provider test early

### Risk 2 - health drift
Runtime works but health still warns incorrectly.

Mitigation:
- refactor health in the same implementation track, not later

### Risk 3 - too many provider branches too soon
Trying to support too many providers at once will sprawl.

Mitigation:
- ship Azure + one second provider only

### Risk 4 - docs drift from runtime
README becomes aspirational again.

Mitigation:
- update docs only after tests pass for the chosen second provider

---

## Explicit recommendation

Implement in this order:
1. `embedding_config.py`
2. adapter refactor
3. health refactor
4. tests
5. docs closeout

Do not start with docs-only or provider-subclass expansion.

---

## Work log

### 2026-06-03
- Created audit doc: `docs/litellm-multi-provider-audit-2026-06-03.md`
- Converted audit into this implementation brief
- Chosen posture: **one config-driven resolver, preserve Azure compatibility, add one second provider, avoid full gateway for now**

---

## Next recommended action

Create the execution task/brief for the actual code slice:
- `brainos-multi-provider-embedding-config-v1`

And then implement only:
- resolver
- adapter
- health
- tests
- README

- Implementation started:
  - added `src/brainos/embedding_config.py`
  - refactored `src/brainos/embedding.py` to use normalized resolver output
  - refactored `src/brainos/health.py` to validate per resolved provider path
  - updated `README.md` with Azure compatibility path + OpenAI example
  - updated targeted tests for new contract shape
- Verification:
  - `./.venv/bin/pytest tests/test_embedding_adapter.py tests/test_health_cli.py tests/test_doctor_cli.py -q`
  - result: `17 passed`
- Follow-up hardening started:
  - added explicit OpenAI-path adapter test
  - added explicit OpenAI-path retrieval-health CLI contract test
  - scanned repo for remaining Azure-only assumptions

- Broadened verification:
  - added explicit OpenAI adapter path proof
  - added explicit OpenAI retrieval-health CLI proof
  - ran broader targeted suite:
    - `./.venv/bin/pytest tests/test_embedding_adapter.py tests/test_health_cli.py tests/test_doctor_cli.py tests/test_json_cli_output.py tests/test_env_loading.py tests/test_embedding_runtime_error.py -q`
    - result: `23 passed`
- Residual findings from repo scan:
  - active runtime path is no longer Azure-only
  - remaining Azure-first assumptions are mostly in docs/history fixtures and benchmark text
  - additional cleanup is still warranted in secondary docs and broader tests if we want a cleaner provider-agnostic repo posture

- Cleanup pass:
  - archived dated usage/continuity working reports under `docs/_archive_working/2026-06-03/`
  - intentionally kept active implementation docs (`litellm-multi-provider-*`) in docs root
  - intentionally kept active operational docs (`decision-check-v2-closeout-2026-06-03.md`, `brainos-bounded-usage-friction-note-template.md`, `docs/friction/`) in place
- Cleanup verdict:
  - docs root is less noisy
  - working tree is not clean yet because real code/test/docs changes remain
  - remaining dirty state is substantive work, not just report clutter
