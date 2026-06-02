# BrainOS decision-support object v1 — implementation brief

## Status
Planning brief for the first bounded implementation slice after the decision-support contract rewrite.

This brief is intentionally narrow.
It defines the smallest useful implementation that aligns code, schema, CLI, and tests with the new decision-support boundary.

Related docs:
- `docs/decision-support-contract-v1.md`
- `docs/roadmap-product-and-operational-layer-v1.md`

## Slice goal
Implement a first-class `decision` object that stores an operator-facing decision brief.

The object should support:
- framing a decision question,
- storing candidate options,
- storing recommendation + uncertainty,
- storing explicit support / objections / risks / missing information,
- provenance through ledger writes,
- future retrieval/explain integration.

It should **not** attempt to automatically generate or optimize the decision brief in v1.

## Strong boundary
This slice is about **structured storage + CLI surface**, not autonomous choice.

Do:
- create/store/read/list decision-support objects,
- preserve operator boundary explicitly,
- keep JSON fields inspectable and stable,
- make later retrieval integration possible.

Do not:
- add LLM generation,
- add automatic scoring/chooser logic,
- add execution handoff,
- redesign retrieval,
- over-model workflow/state machine semantics.

## Why this slice first
The spec is now clear, but the codebase still has no first-class decision-support object.

Without this slice:
- future implementation will drift back into vague episode metadata,
- decision support will remain implicit and hard to inspect,
- later conflict checks and retrieval support will have no clean object boundary.

This slice creates the minimal durable product surface.

## Proposed data model v1
Add one new table for decision-support objects.

Suggested fields:
- `decision_id` TEXT PRIMARY KEY
- `question` TEXT NOT NULL
- `status` TEXT NOT NULL
- `recommended_option_id` TEXT NULL
- `operator_call_required` INTEGER NOT NULL DEFAULT 1
- `options_json` TEXT NOT NULL
- `arguments_json` TEXT NOT NULL
- `counterarguments_json` TEXT NOT NULL
- `risks_json` TEXT NOT NULL
- `missing_information_json` TEXT NOT NULL
- `uncertainty_notes_json` TEXT NOT NULL
- `review_after` TEXT NULL
- `metadata_json` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

### Field intent
- `question`: the decision question being worked.
- `status`: minimal lifecycle only, e.g. `draft | active | superseded | closed`.
- `recommended_option_id`: recommendation is allowed, finality is not.
- `operator_call_required`: should default to true and remain visible in outputs.
- `options_json`: list of candidate options with ids, labels, and summaries.
- `arguments_json`: supporting arguments tied to option ids where possible.
- `counterarguments_json`: objections / tradeoffs.
- `risks_json`: distinct from generic objections when there is downside exposure.
- `missing_information_json`: unresolved data that could change the choice.
- `uncertainty_notes_json`: explicit ambiguity notes.
- `metadata_json`: narrow escape hatch for refs/tags/entity links.

### Keep v1 intentionally simple
Do not normalize options/arguments into many child tables yet.
JSON fields are acceptable in v1 because:
- shape is still settling,
- the slice is about a bounded product surface,
- later normalization remains possible once real usage stabilizes.

## JSON shape guidance
### `options_json`
Expected list shape:
```json
[
  {
    "option_id": "A",
    "label": "Improve retrieval credibility first",
    "summary": "Smallest reversible slice with direct trust impact"
  }
]
```

### `arguments_json`
Expected list shape:
```json
[
  {
    "option_id": "A",
    "kind": "support",
    "text": "Matches current time constraint",
    "evidence_refs": []
  }
]
```

### `counterarguments_json`, `risks_json`, `missing_information_json`, `uncertainty_notes_json`
Use list-of-objects or list-of-strings, but pick one stable contract in code/tests.
Recommendation: list-of-objects for future extensibility.

## Minimal CLI surface v1
Add three commands only:

### `decision-log`
Create or replace a decision-support artifact.

Expected use:
- operator or tool writes a structured decision brief,
- output returns created/updated object JSON,
- write is ledger-backed.

### `decision-list`
List decision-support objects in compact form.

Should show at least:
- `decision_id`
- `question`
- `status`
- `recommended_option_id`
- `operator_call_required`
- timestamps

### `decision-get`
Return full decision-support object.

Should show all stored fields in JSON-first output.

## CLI design recommendation
Prefer explicit JSON parameters over many ad-hoc flags.

Good v1 direction:
- `--options-json`
- `--arguments-json`
- `--counterarguments-json`
- `--risks-json`
- `--missing-information-json`
- `--uncertainty-notes-json`
- `--metadata-json`

Why:
- avoids brittle positional argument growth,
- keeps the contract close to the stored shape,
- makes tests more deterministic,
- is easier to expose later via MCP/tool wrappers.

## Store/module recommendation
Add a dedicated module, e.g. `src/brainos/decisions.py`, responsible for:
- validation helpers,
- create/update shape preparation,
- row → JSON object mapping,
- compact list view mapping.

Keep DB access patterns consistent with existing store conventions.

## Validation rules v1
Keep validation narrow and honest.

Required:
- `question` non-empty
- `status` in allowed enum
- `options_json` must parse and be a non-empty list
- each option must have `option_id` and `label`
- `recommended_option_id`, if present, must exist in `options_json`
- `operator_call_required` must be boolean-ish and default true
- JSON fields must contain valid JSON arrays/objects as expected

Do not add heavy semantic validation yet.

## Ledger expectation
Every create/update mutation should write one ledger event.

Minimal event intent:
- object type: `decision`
- object id: `decision_id`
- mutation type: create/update
- enough payload to preserve provenance expectations consistent with the rest of BrainOS

No special ledger redesign in this slice.

## Retrieval/explain posture for this slice
Do not implement recall/explain support here.

But do preserve forward compatibility:
- stable object id
- stable question field
- stable option ids
- metadata hooks for future refs

This slice should unblock later retrieval/explain support rather than partially implementing it badly.

## Primary files
- `src/brainos/schema.py`
- `src/brainos/store.py`
- `src/brainos/cli.py`
- new `src/brainos/decisions.py`
- new `tests/test_decision_cli.py`
- `README.md`
- `docs/implementation-notes.md`

## Suggested implementation order
1. schema/table addition
2. store read/write helpers
3. `decisions.py` validation + mapping helpers
4. CLI commands
5. tests
6. minimal docs closeout notes

## Test plan v1
### Required tests
1. `decision-log` creates a valid object with minimal required fields.
2. `decision-get` returns the stored full object.
3. `decision-list` returns compact summaries.
4. `recommended_option_id` must match one declared option.
5. invalid JSON input is rejected cleanly.
6. `operator_call_required` defaults to true.
7. create/update writes corresponding ledger entries.

### Nice-to-have test
- update existing `decision_id` preserves identity and refreshes `updated_at`.

## Done definition
This slice is done when:
- BrainOS can persist and return a structured operator-facing decision brief,
- the object shape clearly reflects decision support rather than auto-decision,
- ledger/provenance behavior remains intact,
- tests cover the minimal contract,
- future retrieval/explain integration is unblocked.

## Explicit anti-goals
- no decision auto-generation
- no hidden ranking engine
- no conflict checker in this slice
- no focus/overview coupling yet
- no MCP work yet
- no README product repositioning beyond bounded closeout if needed

## Recommended next slice after this one
After `decision-support object v1`, the next most sensible slice is:
- retrieval/explain support for operational objects,

not:
- autonomous decision scoring.

That keeps the architecture honest: first store the brief cleanly, then make it retrievable and inspectable.
