# Authoritative artifact hygiene — slice brief v0

## Verdict

This is the smallest sensible next slice after realistic usage pack run 002.

Do **not** change retrieval policy yet.
The stronger move is to improve the quality of the artifacts that retrieval is supposed to recover.

The current trigger is specific:
- realistic usage pack run 002 removed runtime contamination,
- retrieval looked solid on most practical query classes,
- the main remaining non-green case was **SSOT / source-of-truth lookup phrasing**.

That makes this a corpus and authoritativeness hygiene slice first, not a ranking-engine slice.

## Goal

Improve retrieval reliability for **authoritative artifacts** without widening product scope.

In particular, make these artifact classes easier to recover with natural operator phrasing:
- SSOT / source-of-truth artifacts
- restart / continuation anchors
- decision carriers
- procedure carriers

## Problem statement

BrainOS currently has lightweight typed ingest:
- `kind`
- `topic`
- `source`

That is useful, but it does not yet make **authoritative intent** explicit enough.

Result:
- semantically relevant hits can outrank more authoritative hits,
- source-of-truth phrasing is weaker than direct boundary phrasing,
- continuity artifacts depend too much on wording accidents,
- retrieval can find the right neighborhood without clearly preferring the right authority level.

## Non-goals

Do not use this slice to:
- redesign retrieval ranking globally
- add a heavy schema layer
- backfill the full historical corpus
- create many new metadata fields casually
- introduce autonomous document curation behavior
- widen BrainOS into a content-management system

## Desired outcome

After this slice:
- authoritative artifacts are easier to phrase and easier to retrieve,
- SSOT-style queries have a better chance of returning the right artifact first,
- restart and continuation carriers are more explicit,
- decision/procedure entries remain lightweight but more recoverable,
- we can rerun the pack and judge whether the remaining weakness was mostly artifact-shape related.

## Highest-leverage changes

### 1. Add one lightweight `authority` metadata field for new episode ingest

Recommended allowed values:
- `canonical`
- `working`
- `supporting`

Default:
- absent / unset

Purpose:
- distinguish whether an artifact is meant to be the source of truth,
- keep the field small and interpretable,
- avoid inventing a large ontology.

Why this is worth doing:
- `kind` tells us what role a note plays,
- `topic` tells us what it is about,
- `authority` would tell us whether this artifact should win when a source-of-truth style query appears.

DoD for this change:
- ingest normalization accepts `authority`
- unknown values are dropped or normalized safely
- examples/docs show one SSOT-style and one working-note style usage

### 2. Standardize explicit content prefixes for authoritative carriers

Recommended prefixes:
- `SSOT:` for canonical source-of-truth notes
- `Restart point:` for continuation anchors
- `Decision:` for bounded decision carriers
- `Procedure:` for action-oriented reusable steps

Purpose:
- improve lexical grounding for practical operator phrasing,
- reduce ambiguity between “relevant” and “authoritative”.

Important constraint:
- this is a writing convention, not a mandatory schema migration.

DoD for this change:
- docs state the preferred prefixes clearly
- examples include at least one `SSOT:` example
- the convention is framed as lightweight and recommended, not ceremonial

### 3. Extend typed-ingest guidance with an authoritative artifact mini-runbook

Add one short section to typed-ingest docs:
- when to use `authority=canonical`
- when to leave authority unset
- how to encode SSOT vs working note vs supporting note
- how to write restart / decision / procedure entries so retrieval has a better chance to recover them

Purpose:
- move the improvement into normal operator capture behavior,
- avoid requiring a later cleanup campaign.

DoD for this change:
- one compact section in docs
- one minimal example per artifact class
- no big theory block

### 4. Add one focused test for authoritative SSOT phrasing

Add a small test that checks something like:
- an `SSOT:` canonical artifact should beat a semantically related but merely descriptive fact on a source-of-truth query.

Purpose:
- protect the exact remaining weak spot that run 002 exposed,
- avoid broad benchmark drift.

DoD for this change:
- one bounded test only
- the test is explicitly about authority-shaped retrieval, not general ranking ambition
- benchmark anchor does not sprawl casually

### 5. Add one focused pack rerun target instead of broad retesting

After the slice lands, rerun only:
- SSOT/source-of-truth lookup
- low-evidence honesty check
- optionally restart-point recall as a regression sanity check

Purpose:
- verify the targeted improvement without reopening the whole project surface.

DoD for this change:
- one short follow-up report or addendum
- explicit comparison to run 002

## Recommended implementation order

1. add `authority` metadata normalization support
2. update typed-ingest docs with authoritative artifact guidance
3. add examples using `SSOT:` and `authority=canonical`
4. add one focused retrieval test for SSOT phrasing
5. rerun the narrow pack subset

## Why this order

Because it fixes the likely highest-leverage layer first:
- artifact shape,
- not ranking policy.

If the SSOT case improves after this slice, we have evidence that the remaining weakness was mainly corpus/authoritativeness shape.
If it does not improve, *then* ranking logic becomes a more serious candidate.

## Rollback

If this slice starts expanding:
- keep only the docs + convention changes,
- do not add more than one metadata field,
- do not create a broad artifact taxonomy,
- do not widen the benchmark suite beyond the one authority-shaped test.

The smallest acceptable version of this slice is:
- lightweight `authority` field,
- one doc update,
- one focused test.

## Short recommendation

**Do this slice now.**

It is the smallest move that directly addresses the only remaining practical weakness exposed by run 002, and it does so without pretending the engine needs surgery before the artifacts themselves are shaped clearly enough.
