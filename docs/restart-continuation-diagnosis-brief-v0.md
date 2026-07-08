# Restart / continuation retrieval diagnosis — brief v0

## Verdict

There is now enough bounded evidence to justify a **diagnosis-first retrieval slice**.

Do **not** jump to a broad ranking rewrite.
But do stop treating this as only an artifact-shape problem.

After two bounded validation runs:
- better continuation artifact wording did **not** materially improve outcomes,
- the same narrow failure shapes survived,
- so the next honest move is code-path diagnosis focused on lexical handling and continuation-specific phrasing.

## What the evidence now says

### Stable bounded observations
1. direct `current direction` wording is recoverable
2. natural `resume / leave / continue` wording often returns no hits
3. explicit `current restart point` wording can still prefer a **stale** artifact
4. the stale artifact wins because it repeats the target phrase lexically inside a negated sentence
5. runtime posture is healthy during these failures

That makes the current problem narrow and specific:
- **restart / continuation lexical failure shapes**
- not general retrieval collapse
- not a runtime issue
- not only a corpus-shape issue anymore

## Critical code-path observations

### 1. FTS gate is the first hard bottleneck
`search_episodes_text()` uses `_normalize_fts_query()` and then runs FTS `MATCH` directly.

Current behavior:
- question fillers are stripped,
- but continuation phrases such as `resume`, `leave`, `continue`, `next`, `front`, `active` are **not expanded**,
- no continuation-specific query aliasing exists on the episode side,
- if FTS returns nothing, lexical episode ranking has no material to work with.

Practical consequence:
- many natural operator phrasings die before ranking even starts.

This explains the repeated `ranked_count = 0` / `zero_hit_reason = no_matching_content` cases better than any score-tuning theory.

### 2. Episode lexical ranking has no notion of negation or staleness
In `_rank_episode_hits()`:
- FTS hits get a base rank from retrieval order,
- plus anchor bonus,
- plus kind bonus,
- plus authority bonus only for SSOT-style queries.

What is missing for this failure mode:
- no penalty for phrases like `previous`, `earlier`, `obsolete`, `no longer current`
- no bonus for `current` in continuation/restart-shaped queries
- no continuation-aware disambiguation between current vs stale restart artifacts

Practical consequence:
- if a stale artifact contains the full target phrase lexically, it can win cleanly
- especially when the current artifact is semantically right but phrase-shape is thinner or different

### 3. Anchor terms do not cover continuation wording well
Current `_anchor_terms()` includes items like:
- `restart`
- `anchor`
- `memory`
- `maintenance`
- `brainos`
- `workspace`

What is missing for the observed failures:
- `resume`
- `continue`
- `continuation`
- `next`
- `direction`
- `active`
- `current` is intentionally removed from FTS normalization and not treated as a lexical anchor here

Practical consequence:
- natural continuation phrasing gets little or no additional score support
- direct mirrored wording works only when the stored artifact already uses nearly the same surface form

### 4. Vector path is not rescuing these cases
During the runs:
- runtime was healthy,
- mode included `sqlite_vec_episode_similarity`,
- but the failure cases still ended with zero ranked results or purely lexical winners.

Likely reading:
- vector search is either too weak on this tiny fixture to rescue the natural wording,
- or the scoring/gating path does not give it enough leverage once lexical grounding is absent.

This does **not** yet prove vector policy is wrong.
It only means vector participation is not currently solving continuation-language gaps.

## Strongest diagnosis hypotheses

### Hypothesis A — continuation query alias gap
The episode retrieval path lacks lightweight continuation-language aliasing.

Example gap:
- `resume` / `leave` / `continue with` / `next step`
  do not bridge to artifact labels like:
- `Restart point:`
- `Current direction:`
- `Next step:`

This is the best explanation for the repeated zero-hit failures.

### Hypothesis B — stale negation lexical trap
A stale artifact that says some variant of:
- `no longer the current restart point`
can still win because the ranker sees token overlap, not semantic polarity.

This is the best explanation for the stale artifact beating the current one.

### Hypothesis C — continuation classes are under-modeled in the ranking surface
Current ranking knows about:
- anchor terms,
- kind bonuses,
- SSOT authority bonus,

but it does **not** have any narrow notion of continuation-specific intent.

That does not automatically mean “add a continuation ranking framework”.
It only means a very small continuation-aware hook may be justified if A/B survive inspection.

## Recommended next inspection targets

### Target 1 — `_normalize_fts_query()`
Question:
- should a **very small alias map** be introduced for continuation wording before FTS?

Candidates to inspect carefully:
- `resume` -> maybe `restart`
- `leave` -> maybe `restart`
- `continue` -> maybe `continuation`
- `next step` -> maybe `procedure` / `next`

Risk:
- over-expansion could create noisy false positives

### Target 2 — `_rank_episode_hits()`
Question:
- should there be a **very narrow stale/negation penalty** for continuation-shaped queries?

Candidates to inspect carefully:
- `previous`
- `earlier`
- `obsolete`
- `no longer`
- `not current`

Risk:
- broad negation heuristics can become brittle and surprising

### Target 3 — continuation-aware query intent detector
Question:
- is there room for a **tiny helper** analogous in spirit to the decision-query intent path, but only for continuation classes?

Potential bounded outputs:
- `restart_point`
- `current_direction`
- `next_step`

Risk:
- this is useful only if it stays tiny and explicit
- if it grows into a taxonomy, the slice has failed

## What not to do next

Do not:
- add a general ranking framework for continuation
- create many new metadata fields
- infer “stale” from timestamps or heavy state machines
- broaden this into generic semantic understanding work
- pretend the issue is solved by docs or artifact wording alone

## Best next move

Do one **minimal code-inspection-to-fixpoint pass** and choose between these two bounded directions:

1. **query-bridging first**
   - if zero-hit failures are the dominant pain
2. **stale-negation penalty first**
   - if wrong-winner failures are the dominant pain

Given current evidence, the honest ordering is:
1. inspect query bridging for `resume/leave/continue/next`
2. inspect stale-negation handling for restart-point queries
3. patch only the smallest fix point that directly addresses one proven failure shape

## Short recommendation

**The next slice should be a tiny diagnosis-to-fixpoint slice, not another validation run and not a broad ranking rewrite.**

The code now points to two concrete suspects:
- missing continuation query bridging before FTS
- missing stale/negation handling when lexical overlap is misleading
