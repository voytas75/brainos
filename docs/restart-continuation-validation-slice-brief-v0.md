# Restart / continuation retrieval validation — slice brief v0

## Verdict

This is a sensible next slice **only as a validation slice**.

Do **not** frame it as a restart-retrieval improvement slice yet.
We do not currently have evidence that restart retrieval is broken.
We only have evidence that the minimal rerun after the authority/SSOT slice was too small and too weakly worded to meaningfully revalidate restart/continuation behavior.

That makes this a **better evidence** slice, not a ranking-tuning slice.

## Why now

After the authoritative-artifact hygiene slice:
- SSOT/source-of-truth retrieval got a narrow, evidence-backed closeout,
- focused regression is green,
- low-evidence posture stayed honest,
- but restart / continuation retrieval was **not strongly revalidated**.

Current best reading:
- there is **no proven restart regression**,
- there is **no new broad green proof** either,
- so the next honest move is a small realistic validation pass.

## Goal

Check whether BrainOS can recover the **current continuation carrier** reliably enough on a small, realistic corpus shape, without changing retrieval policy by default.

## Critical framing rule

This slice must distinguish three related but different query classes:

1. **restart-point recall**
   - where work should resume
2. **current-direction recall**
   - what the current direction/front actually is
3. **next-step continuation recall**
   - what the practical next move is

Do **not** collapse these into one generic “continuation” class.
If they are merged, results will be too soft to interpret.

## Problem statement

The current realistic usage pack has one restart-point case:
- `where do we resume BrainOS work now?`

That is useful, but insufficient for a credible conclusion because:
- one wording does not cover the nearby continuation classes,
- a tiny rerun fixture can under-test the real ambiguity,
- a result can look green or red for the wrong reason,
- artifact weakness can be mistaken for retrieval weakness.

## Non-goals

Do not use this slice to:
- add new ranking bonuses by default
- redesign retrieval policy
- introduce a larger continuation ontology into product code
- add more metadata fields casually
- expand the realistic usage pack into a large benchmark platform
- claim broad continuity retrieval quality across open-ended corpora

## Main failure modes to guard against

### 1. False regression framing
Treating “not revalidated” as if it already means “retrieval is broken”.

### 2. Category collapse
Treating restart-point, current-direction, and next-step retrieval as one behavior.

### 3. Sterile fixture
Using a too-clean fixture where one obvious canonical note wins only because there are no meaningful nearby distractors.

### 4. Over-hard success rules
Demanding exact top-1 for every wording, even when the query is really about current direction or next step rather than restart phrasing.

### 5. Over-soft success rules
Calling the slice green just because something vaguely similar appears in top-3.

### 6. Corpus-vs-retrieval confusion
Failing retrieval when the tested corpus never contained a real continuation carrier strongly enough in the first place.

## Recommended fixture shape

Use one small realistic fixture, not a toy two-item pair.

Minimum recommended artifacts:
- one **current canonical restart point**
- one **older/stale restart point**
- one **active decision carrier**
- one **nearby working note**
- one **nearby next-step / procedure-like note**
- one **generic status / README-like distractor**

Important rule:
- the artifacts should be close enough semantically that retrieval has to do real work,
- but not so vague that every outcome becomes subjective.

## Query classes

### A. Restart-point recall
Intent:
- recover the current place to resume work

Example wording set:
- `where do we resume BrainOS work now?`
- `where did we leave the BrainOS work?`
- `what is the current restart point for BrainOS?`

Expected winner class:
- current restart artifact or nearest valid continuation anchor

### B. Current-direction recall
Intent:
- recover the currently active direction/front

Example wording set:
- `what is the current BrainOS direction?`
- `what are we doing next in BrainOS now?`
- `what front is currently active in BrainOS?`

Expected winner class:
- active decision carrier or equivalent current-direction artifact

### C. Next-step continuation recall
Intent:
- recover the most practical immediate next move

Example wording set:
- `what should we do next in BrainOS?`
- `what is the next continuation step for BrainOS?`
- `what should I continue with in BrainOS now?`

Expected winner class:
- procedure-like next-step carrier or decision-backed next-step artifact

## Interpretation rules

### PASS
- the right artifact class wins clearly enough to act on
- or the canonical/nearest-valid continuation artifact appears in top-1/top-3 according to the class rule

### WEAK_PASS
- the answer neighborhood is right, but the best artifact does not win as clearly as it should

### LOW_EVIDENCE
- the corpus is too weak to support a fair continuation judgment
- or there is no strong continuation carrier to recover

### FAIL
- the corpus contains a strong valid continuation carrier, but retrieval returns the wrong class or wrong older artifact in a misleading way

### Optional analytic note: `ARTIFACT_GAP`
Use this note in the writeup if needed when:
- the main problem is not ranking,
- the main problem is that the corpus captured the continuation state too weakly or ambiguously.

This does **not** need to become a product enum.
It is just an analysis aid.

## Success rules by class

### Restart-point recall
Success when:
- the current restart artifact appears in top-1 or top-3,
- and no stale restart artifact wins in a misleading way.

### Current-direction recall
Success when:
- the current active direction carrier or nearest valid decision carrier appears in top-1 or top-3.

### Next-step continuation recall
Success when:
- the result surfaces a practical next-step artifact, not only a generic status or broad project summary.

## Recommended implementation order

1. define the fixture shape explicitly in docs
2. write the small continuation/restart corpus
3. run 2–3 wording variants per class through `recall`
4. use `retrieval-explain` only when ranking diagnosis is needed
5. write one short result note with verdicts and failure-shape reading
6. only then decide whether any retrieval-policy change is justified

## DoD

This slice is complete when:
- one brief defines the three continuation classes explicitly
- one small realistic fixture exists
- each class has 2–3 wordings max
- verdicts distinguish retrieval weakness from artifact weakness
- the writeup ends with one concrete reading:
  - retrieval looks fine,
  - artifact shape is weak,
  - or one narrow retrieval issue survives realistic validation

## Anti-goals

Do not leave this slice with:
- a new ranking bonus without fresh evidence
- a bloated continuation taxonomy
- a vague “mostly green” story unsupported by class-level readings
- a giant new benchmark pack
- broad product claims about continuity memory

## Short recommendation

**Do this slice now, but keep it strictly diagnostic.**

The right outcome is not “more ranking.”
The right outcome is a credible answer to one narrower question:

> Can BrainOS recover the current continuation carrier reliably enough on a small realistic corpus, and if not, is the weakness mainly in retrieval or in artifact shape?
