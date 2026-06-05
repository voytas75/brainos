# BrainOS real test — skepticism corpus

> Note (post-fix, 2026-06-04): this report was generated before the explain diagnostic alignment patch. At that time, mixed vector-led wins with lexical overlap still showed `diagnostic_hint=lexical_grounded_top_hit`. A later rerun after the patch confirmed the aligned hint `vector_primary_with_lexical_support` for this class of case.

- DB: `/tmp/brainos-skepticism-real-20260604-215147.db`
- Verdict: **PASS**
- Corpus: 5 short internet-grounded / operator-shaped entries about philosophical skepticism

## Key results
- skepticism query top kind: `fact`
- skepticism query top hit: Sceptycyzm filozoficzny nie musi oznaczać prostego negowania wszystkiego; w klasycznej formie często oznacza raczej wstrzymanie sądu tam, gdzie brak wystarczających podstaw do pewn
- interpretation query top kind: `decision`
- interpretation query top hit: Decision: przy praktycznym czytaniu sceptycyzmu trzeba odróżniać sceptycyzm metodyczny i epistemiczny od potocznego cynizmu albo relatywizmu, bo to częsty błąd interpretacyjny.
- runtime status: `ok`
- retrieval health: `ok`

## Explain evidence snapshots
### Skepticism
- operator_summary: top hit is primarily vector-led; kind=fact
- diagnostic_hint: lexical_grounded_top_hit
- confidence_hint: None
- top_hit_evidence: {"id": "00cc6265-6fc9-48df-ae38-67b3736f8101", "kind": "fact", "match_sources": ["vector"], "lexical_overlap": 3, "vector_distance": 0.7586492300033569, "score_components": {"episode_vector": 664.1350769996643, "lexical_overlap_bonus": 240.0, "anchor_term_bonus": 0.0, "kind_bonus": 40.0}}
- comparison_hint: {"top_id": "00cc6265-6fc9-48df-ae38-67b3736f8101", "runner_up_id": "37acee83-7cfe-4322-b09e-6d7009ed8860", "score_gap": 47.191, "top_kind": "fact", "runner_up_kind": "procedure"}

### Interpretation
- operator_summary: top hit is primarily vector-led; kind=decision
- diagnostic_hint: lexical_grounded_top_hit
- confidence_hint: None
- top_hit_evidence: {"id": "74a94504-31ac-464f-9849-1f69ee6b98fe", "kind": "decision", "match_sources": ["vector"], "lexical_overlap": 4, "vector_distance": 0.7650582194328308, "score_components": {"episode_vector": 743.4941780567169, "lexical_overlap_bonus": 240.0, "anchor_term_bonus": 0.0, "kind_bonus": 120.0}}
- comparison_hint: {"top_id": "74a94504-31ac-464f-9849-1f69ee6b98fe", "runner_up_id": "37acee83-7cfe-4322-b09e-6d7009ed8860", "score_gap": 200.451, "top_kind": "decision", "runner_up_kind": "procedure"}

## Verdict note
- Real-use retrieval also works on a second non-technical philosophy corpus.
- Reachability again helps interpretation-style questions surface decision/procedure entries.
- Explain evidence clarity remains useful for diagnosing why the top hit won.
