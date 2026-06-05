# BrainOS real test — stoicism corpus

> Note (post-fix, 2026-06-04): this report was generated before the explain diagnostic alignment patch. At that time, mixed vector-led wins with lexical overlap still showed `diagnostic_hint=lexical_grounded_top_hit`. A later rerun after the patch confirmed the aligned hint `vector_primary_with_lexical_support` for this class of case.

- DB: `/tmp/brainos-stoicism-real-20260604-214412.db`
- Verdict: **PASS**
- Corpus: 5 short internet-grounded / operator-shaped entries about stoicism

## Key results
- emotions query top kind: `procedure`
- emotions query top hit: Procedure: gdy oceniasz tekst o stoicyzmie, sprawdź najpierw czy mówi o cnocie, sądach i rzeczach zależnych od nas, a potem czy nie myli regulacji emocji z ich tłumieniem.
- interpretation query top kind: `decision`
- interpretation query top hit: Decision: w praktycznym czytaniu stoicyzmu trzeba odróżniać klasyczne źródła od pop-stoicyzmu, bo współczesne uproszczenia często zamieniają etykę cnót w poradnik odporności psychi
- runtime status: `ok`
- retrieval health: `ok`

## Explain evidence snapshots
### Emotions
- operator_summary: top hit is primarily vector-led; kind=procedure
- diagnostic_hint: lexical_grounded_top_hit
- confidence_hint: None
- top_hit_evidence: {"id": "a3d0796d-a97c-4a5d-ac6c-cc1b6250d32b", "kind": "procedure", "match_sources": ["vector"], "lexical_overlap": 2, "vector_distance": 0.7970711588859558, "score_components": {"episode_vector": 625.2928841114044, "lexical_overlap_bonus": 160.0, "anchor_term_bonus": 0.0, "kind_bonus": 90.0}}
- comparison_hint: {"top_id": "a3d0796d-a97c-4a5d-ac6c-cc1b6250d32b", "runner_up_id": "f39cf9fa-b50c-48e1-afc2-3af7f09bffb4", "score_gap": 75.066, "top_kind": "procedure", "runner_up_kind": "decision"}

### Interpretation
- operator_summary: top hit is primarily vector-led; kind=decision
- diagnostic_hint: lexical_grounded_top_hit
- confidence_hint: None
- top_hit_evidence: {"id": "f39cf9fa-b50c-48e1-afc2-3af7f09bffb4", "kind": "decision", "match_sources": ["vector"], "lexical_overlap": 2, "vector_distance": 0.7332692742347717, "score_components": {"episode_vector": 666.6730725765228, "lexical_overlap_bonus": 160.0, "anchor_term_bonus": 0.0, "kind_bonus": 120.0}}
- comparison_hint: {"top_id": "f39cf9fa-b50c-48e1-afc2-3af7f09bffb4", "runner_up_id": "fa5f046d-657a-471c-b62b-74b9ab42d30d", "score_gap": 175.032, "top_kind": "decision", "runner_up_kind": "fact"}

## Verdict note
- Real-use retrieval works on a small philosophy corpus.
- Typed ingest helps by surfacing decision/procedure entries for interpretation-style questions.
- Explain evidence clarity is materially useful: top-hit evidence and comparison hint make diagnosis easier.
