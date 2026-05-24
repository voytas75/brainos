# Vector state contract v1

## Purpose
This document defines the current contract for BrainOS vector index states and the maintenance semantics that operate on them.

It is a developer/operator SSOT for current behavior, not an aspirational redesign.

## Object families in scope
Current first-class vectorized object families:
- `episode`
- `semantic_node`

## State meanings

### `missing`
Meaning:
- the object exists in canonical storage
- no usable vector artifact has been recorded yet for the current source/profile state

Typical causes:
- new object created
- state row created for future embedding work
- source known, vector artifact not yet generated

Operator interpretation:
- visible and relevant
- not automatically a freshness failure on its own

### `fresh`
Meaning:
- vector artifact exists and matches the current source text hash and embedding profile

Operator interpretation:
- healthy derived state
- `sync_vector_index` may return `mode=noop` when forced regeneration is not requested

### `stale`
Meaning:
- canonical source text or embedding profile changed relative to the last stored vector state
- previous vector metadata may still exist, but it no longer matches the current source/profile contract

Operator interpretation:
- freshness problem
- should be eligible for refresh/sync

### `error`
Meaning:
- a vector generation/storage attempt failed and the failure was recorded

Operator interpretation:
- freshness/maintenance problem
- should be eligible for retry/sync once the underlying cause is addressed

### `disabled`
Meaning:
- embedding generation may have succeeded logically, but vector storage/use was capability-gated by runtime sqlite-vec unavailability

Operator interpretation:
- operator-relevant and visible
- not the same thing as stale/error freshness failure
- usually points first to runtime capability posture, not data corruption

## Transition rules

### Canonical object creation
- new `episode` or `semantic_node` starts as `missing`

### Canonical source/profile change
- if source text hash or embedding profile differs from the stored state, status becomes `stale`

### Successful vector generation + storage
- status becomes `fresh`
- last error fields are cleared

### Embedding/storage failure
- status becomes `error`
- failure detail is stored in `last_error`

### sqlite-vec capability unavailable during generation
- status becomes `disabled`
- capability failure is recorded in `last_error`

## Maintenance semantics

### `refresh_vector_freshness_*`
Intent:
- classify whether current stored vector state still matches current canonical source/profile state

Behavior:
- creates `missing` state if none exists yet
- marks `stale` when source/profile drift is detected
- preserves existing metadata fields where possible when marking stale

### `sync_vector_index`
Intent:
- move a vectorized object toward a usable derived state

Current dispatch behavior:
- `missing` → generate
- `stale` → generate
- `error` → retry generate
- `disabled` → retry generate (useful after runtime capability becomes available)
- `fresh` → `mode=noop` unless forced

### `sync_vector_index_batch`
Intent:
- apply `sync_vector_index` across a filtered state set

Behavior:
- returns per-object results
- collects `BrainOSError` failures into structured batch errors

## Health interpretation

### Freshness `issues`
Alarm-worthy freshness states:
- `stale`
- `error`

### Freshness `notes`
Visible but non-alarming-on-their-own states:
- `missing`
- `disabled`

## Boundary rule
Do not confuse these classes:
- runtime capability/setup problem
- vector freshness/data problem
- benchmark/quality problem

`disabled` usually starts as a runtime/capability interpretation problem.
`stale` and `error` are maintenance/freshness interpretations.

## Stability note
This contract describes current BrainOS behavior and should remain stable unless there is an intentional vector-state contract revision.
