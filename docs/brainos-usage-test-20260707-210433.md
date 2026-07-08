# BrainOS usage test — 20260707-210433

- DB path: `/tmp/brainos-usage-20260707-210433.db`
- Repo: `/home/openclaw/projects/brainos`
- CLI: `/home/openclaw/projects/brainos/.venv/bin/brainos`
- Queries: `sqlite durability`, `explicit sqlite-vec runtime loading`, `BRAINOS_SQLITE_VEC_PATH`
- Overall: **PASS**

## Results

### init — OK

```
Initialized /tmp/brainos-usage-20260707-210433.db

```

### capabilities — OK

```
{
  "fts5": true,
  "sqlite_vec": true,
  "sqlite_vec_error": null,
  "sqlite_vec_path": "/home/openclaw/.npm-global/lib/node_modules/openclaw/node_modules/sqlite-vec-linux-x64/vec0.so",
  "sqlite_vec_loaded": true,
  "sqlite_vec_runtime_origin": "explicit_path"
}

```

### sqlite_vec — OK

```
{
  "ok": true,
  "path": "/home/openclaw/.npm-global/lib/node_modules/openclaw/node_modules/sqlite-vec-linux-x64/vec0.so",
  "rows": [
    [
      1,
      0.0
    ],
    [
      2,
      0.5196152329444885
    ]
  ],
  "action_hint": "noop"
}

```

### ep1 — OK

```
b71430b9-c081-442d-ad7c-072217ef2119

```

### ep2 — OK

```
a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f

```

### ep3 — OK

```
5070530b-e107-495e-8179-5407ed42a1dc

```

### episodes_list — OK

```
[
  {
    "id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "session_id": "usage-test",
    "timestamp": "2026-07-07 19:04:33",
    "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
    "metadata": {
      "source": "brainos_usage_test",
      "kind": "fact"
    },
    "vector_state": {
      "object_type": "episode",
      "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
      "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "embedding_profile": "brainos-embedding-default",
      "embedding_provider": null,
      "embedding_model": null,
      "embedding_dimensions": null,
      "vector_status": "missing",
      "last_embedded_at": null,
      "last_error": null,
      "last_error_at": null,
      "updated_at": "2026-07-07 19:04:33"
    }
  },
  {
    "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
    "session_id": "usage-test",
    "timestamp": "2026-07-07 19:04:33",
    "content": "SQLite WAL improves durability and concurrent access behavior.",
    "metadata": {
      "source": "brainos_usage_test",
      "kind": "fact"
    },
    "vector_state": {
      "object_type": "episode",
      "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "source_text_hash": "a8e586703754a83c107344b6135e4d3b8515085ae9f4ede0701156a65d7f514a",
      "source_text_preview": "SQLite WAL improves durability and concurrent access behavior.",
      "embedding_profile": "brainos-embedding-default",
      "embedding_provider": null,
      "embedding_model": null,
      "embedding_dimensions": null,
      "vector_status": "missing",
      "last_embedded_at": null,
      "last_error": null,
      "last_error_at": null,
      "updated_at": "2026-07-07 19:04:33"
    }
  },
  {
    "id": "b71430b9-c081-442d-ad7c-072217ef2119",
    "session_id": "usage-test",
    "timestamp": "2026-07-07 19:04:33",
    "content": "BrainOS stores retrieval evidence and vector freshness state.",
    "metadata": {
      "source": "brainos_usage_test",
      "kind": "fact"
    },
    "vector_state": {
      "object_type": "episode",
      "object_id": "b71430b9-c081-442d-ad7c-072217ef2119",
      "source_text_hash": "47425cfe2204234ddc580c374f56dd9621632aca61e3f4fb97feac93bf0f0203",
      "source_text_preview": "BrainOS stores retrieval evidence and vector freshness state.",
      "embedding_profile": "brainos-embedding-default",
      "embedding_provider": null,
      "embedding_model": null,
      "embedding_dimensions": null,
      "vector_status": "missing",
      "last_embedded_at": null,
      "last_error": null,
      "last_error_at": null,
      "updated_at": "2026-07-07 19:04:33"
    }
  }
]

```

### vector_sync — OK

```
{
  "ok": true,
  "requested": 3,
  "synced": 3,
  "errors": [],
  "results": [
    {
      "ok": true,
      "object_type": "episode",
      "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "vector_status": "fresh",
      "embedding_profile": "brainos-embedding-default",
      "dimensions": 3072,
      "provider": "azure",
      "model": "azure/UDTEMBED3L",
      "storage": "sqlite-vec",
      "action_hint": "reindex"
    },
    {
      "ok": true,
      "object_type": "episode",
      "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "vector_status": "fresh",
      "embedding_profile": "brainos-embedding-default",
      "dimensions": 3072,
      "provider": "azure",
      "model": "azure/UDTEMBED3L",
      "storage": "sqlite-vec",
      "action_hint": "reindex"
    },
    {
      "ok": true,
      "object_type": "episode",
      "object_id": "b71430b9-c081-442d-ad7c-072217ef2119",
      "vector_status": "fresh",
      "embedding_profile": "brainos-embedding-default",
      "dimensions": 3072,
      "provider": "azure",
      "model": "azure/UDTEMBED3L",
      "storage": "sqlite-vec",
      "action_hint": "reindex"
    }
  ]
}

```

### recall_1 — OK

```
{
  "query": "sqlite durability",
  "session_id": "usage-test",
  "episodes": [
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "vector_state": {
        "object_type": "episode",
        "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
        "source_text_hash": "a8e586703754a83c107344b6135e4d3b8515085ae9f4ede0701156a65d7f514a",
        "source_text_preview": "SQLite WAL improves durability and concurrent access behavior.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    }
  ],
  "vector_episodes": [
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 0.812137246131897,
      "vector_state": {
        "object_type": "episode",
        "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
        "source_text_hash": "a8e586703754a83c107344b6135e4d3b8515085ae9f4ede0701156a65d7f514a",
        "source_text_preview": "SQLite WAL improves durability and concurrent access behavior.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    },
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 1.1484826803207397,
      "vector_state": {
        "object_type": "episode",
        "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
        "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
        "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,

```

### recall_2 — OK

```
{
  "query": "explicit sqlite-vec runtime loading",
  "session_id": "usage-test",
  "episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "vector_state": {
        "object_type": "episode",
        "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
        "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
        "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    }
  ],
  "vector_episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 0.8006044626235962,
      "vector_state": {
        "object_type": "episode",
        "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
        "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
        "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    },
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 1.1399996280670166,
      "vector_state": {
        "object_type": "episode",
        "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
        "source_text_hash": "a8e586703754a83c107344b6135e4d3b8515085ae9f4ede0701156a65d7f514a",
        "source_text_preview": "SQLite WAL improves durability and concurrent access behavior.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,

```

### recall_3 — OK

```
{
  "query": "BRAINOS_SQLITE_VEC_PATH",
  "session_id": "usage-test",
  "episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "vector_state": {
        "object_type": "episode",
        "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
        "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
        "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    }
  ],
  "vector_episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 0.5776490569114685,
      "vector_state": {
        "object_type": "episode",
        "object_id": "5070530b-e107-495e-8179-5407ed42a1dc",
        "source_text_hash": "e56ed0ed7c97ba8e05983a3ce9509f7f64fe46851dade0b9690bba356cedb727",
        "source_text_preview": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,
        "updated_at": "2026-07-07 19:04:35"
      }
    },
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "session_id": "usage-test",
      "timestamp": "2026-07-07 19:04:33",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "distance": 1.1222225427627563,
      "vector_state": {
        "object_type": "episode",
        "object_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
        "source_text_hash": "a8e586703754a83c107344b6135e4d3b8515085ae9f4ede0701156a65d7f514a",
        "source_text_preview": "SQLite WAL improves durability and concurrent access behavior.",
        "embedding_profile": "brainos-embedding-default",
        "embedding_provider": "azure",
        "embedding_model": "azure/UDTEMBED3L",
        "embedding_dimensions": 3072,
        "vector_status": "fresh",
        "last_embedded_at": "2026-07-07T19:04:35+00:00",
        "last_error": null,
        "last_error_at": null,

```

### explain_1 — OK

```
{
  "query": "sqlite durability",
  "session_id": "usage-test",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match_plus_decision_text",
  "scoring_policy_version": "retrieval-scoring-v1a",
  "summary": "episodes:1, vector_episodes:3, ranked_episodes:2",
  "retrieval_runtime": {
    "status": "ok",
    "degraded": false,
    "message": "vector runtime ready",
    "detail": null,
    "action_hint": "noop",
    "target": null
  },
  "zero_hit_reason": null,
  "episode_vector_mode": "sqlite_vec_episode_similarity",
  "episode_vector_error": null,
  "semantic_vector_mode": "sqlite_vec_semantic_similarity",
  "semantic_vector_error": null,
  "diagnostic_hint": "dual_source_agreement",
  "operator_summary": "top hit supported by lexical and vector evidence; kind=fact",
  "confidence_hint": null,
  "top_hit_evidence": {
    "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
    "kind": "fact",
    "match_sources": [
      "fts",
      "vector"
    ],
    "lexical_overlap": 2,
    "vector_distance": 0.812137246131897,
    "score_components": {
      "fts_rank": 1000.0,
      "anchor_term_bonus": 0.0,
      "kind_bonus": 40.0,
      "weak_anchor_penalty": 0.0,
      "episode_vector": 578.7862753868103,
      "dual_source_bonus": 150.0,
      "lexical_overlap_bonus": 160.0
    }
  },
  "comparison_hint": {
    "top_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
    "runner_up_id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "score_gap": 1308.635,
    "top_kind": "fact",
    "runner_up_kind": "fact"
  },
  "top_ranked_episodes": [
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "rank_score": 1768.7862753868103,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "score_components": {
        "fts_rank": 1000.0,
        "anchor_term_bonus": 0.0,
        "kind_bonus": 40.0,
        "weak_anchor_penalty": 0.0,
        "episode_vector": 578.7862753868103,
        "dual_source_bonus": 150.0,
        "lexical_overlap_bonus": 160.0
      },
      "match_sources": [
        "fts",
        "vector"
      ],
      "vector_distance": 0.812137246131897,
      "lexical_overlap": 2
    },
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "rank_score": 460.151731967926,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"

```

### explain_2 — OK

```
{
  "query": "explicit sqlite-vec runtime loading",
  "session_id": "usage-test",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match_plus_decision_text",
  "scoring_policy_version": "retrieval-scoring-v1a",
  "summary": "episodes:1, vector_episodes:3, ranked_episodes:2",
  "retrieval_runtime": {
    "status": "ok",
    "degraded": false,
    "message": "vector runtime ready",
    "detail": null,
    "action_hint": "noop",
    "target": null
  },
  "zero_hit_reason": null,
  "episode_vector_mode": "sqlite_vec_episode_similarity",
  "episode_vector_error": null,
  "semantic_vector_mode": "sqlite_vec_semantic_similarity",
  "semantic_vector_error": null,
  "diagnostic_hint": "dual_source_agreement",
  "operator_summary": "top hit supported by lexical and vector evidence; kind=fact",
  "confidence_hint": null,
  "top_hit_evidence": {
    "id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "kind": "fact",
    "match_sources": [
      "fts",
      "vector"
    ],
    "lexical_overlap": 5,
    "vector_distance": 0.8006044626235962,
    "score_components": {
      "fts_rank": 1000.0,
      "anchor_term_bonus": 0.0,
      "kind_bonus": 40.0,
      "weak_anchor_penalty": 0.0,
      "episode_vector": 659.9395537376404,
      "dual_source_bonus": 150.0,
      "lexical_overlap_bonus": 240.0
    }
  },
  "comparison_hint": {
    "top_id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "runner_up_id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
    "score_gap": 1388.94,
    "top_kind": "fact",
    "runner_up_kind": "fact"
  },
  "top_ranked_episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "rank_score": 1849.9395537376404,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "score_components": {
        "fts_rank": 1000.0,
        "anchor_term_bonus": 0.0,
        "kind_bonus": 40.0,
        "weak_anchor_penalty": 0.0,
        "episode_vector": 659.9395537376404,
        "dual_source_bonus": 150.0,
        "lexical_overlap_bonus": 240.0
      },
      "match_sources": [
        "fts",
        "vector"
      ],
      "vector_distance": 0.8006044626235962,
      "lexical_overlap": 5
    },
    {
      "id": "a6ddd845-1ff0-4a62-b668-bd1b1ec33e9f",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "rank_score": 461.00003719329834,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"

```

### explain_3 — OK

```
{
  "query": "BRAINOS_SQLITE_VEC_PATH",
  "session_id": "usage-test",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match_plus_decision_text",
  "scoring_policy_version": "retrieval-scoring-v1a",
  "summary": "episodes:1, vector_episodes:3, ranked_episodes:3",
  "retrieval_runtime": {
    "status": "ok",
    "degraded": false,
    "message": "vector runtime ready",
    "detail": null,
    "action_hint": "noop",
    "target": null
  },
  "zero_hit_reason": null,
  "episode_vector_mode": "sqlite_vec_episode_similarity",
  "episode_vector_error": null,
  "semantic_vector_mode": "sqlite_vec_semantic_similarity",
  "semantic_vector_error": null,
  "diagnostic_hint": "dual_source_agreement",
  "operator_summary": "top hit supported by lexical and vector evidence; kind=fact",
  "confidence_hint": null,
  "top_hit_evidence": {
    "id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "kind": "fact",
    "match_sources": [
      "fts",
      "vector"
    ],
    "lexical_overlap": 4,
    "vector_distance": 0.5776490569114685,
    "score_components": {
      "fts_rank": 1000.0,
      "anchor_term_bonus": 90.0,
      "kind_bonus": 40.0,
      "weak_anchor_penalty": 0.0,
      "episode_vector": 772.2350943088531,
      "dual_source_bonus": 150.0,
      "lexical_overlap_bonus": 240.0
    }
  },
  "comparison_hint": {
    "top_id": "5070530b-e107-495e-8179-5407ed42a1dc",
    "runner_up_id": "b71430b9-c081-442d-ad7c-072217ef2119",
    "score_gap": 1505.391,
    "top_kind": "fact",
    "runner_up_kind": "fact"
  },
  "top_ranked_episodes": [
    {
      "id": "5070530b-e107-495e-8179-5407ed42a1dc",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "rank_score": 2052.235094308853,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"
      },
      "score_components": {
        "fts_rank": 1000.0,
        "anchor_term_bonus": 90.0,
        "kind_bonus": 40.0,
        "weak_anchor_penalty": 0.0,
        "episode_vector": 772.2350943088531,
        "dual_source_bonus": 150.0,
        "lexical_overlap_bonus": 240.0
      },
      "match_sources": [
        "fts",
        "vector"
      ],
      "vector_distance": 0.5776490569114685,
      "lexical_overlap": 4
    },
    {
      "id": "b71430b9-c081-442d-ad7c-072217ef2119",
      "content": "BrainOS stores retrieval evidence and vector freshness state.",
      "rank_score": 546.8439555168152,
      "metadata": {
        "source": "brainos_usage_test",
        "kind": "fact"

```

### health — OK

```
{
  "status": "ok",
  "summary": "benchmark green in vector-ready mode",
  "action_hint": "noop",
  "runtime": {
    "status": "ok",
    "issues": [],
    "action_hint": "noop",
    "capabilities": {
      "fts5": true,
      "sqlite_vec": true,
      "sqlite_vec_error": null,
      "sqlite_vec_path": "/home/openclaw/.npm-global/lib/node_modules/openclaw/node_modules/sqlite-vec-linux-x64/vec0.so",
      "sqlite_vec_loaded": true,
      "sqlite_vec_runtime_origin": "explicit_path"
    },
    "embedding_config": {
      "status": "ok",
      "issues": [],
      "action_hint": "noop",
      "contract": {
        "profile": "brainos-embedding-default",
        "provider_path": "litellm",
        "operational_provider": "azure",
        "model": "azure/UDTEMBED3L",
        "required_env": [
          "BRAINOS_EMBEDDING_MODEL",
          "AZURE_API_BASE",
          "AZURE_API_KEY",
          "AZURE_API_VERSION"
        ],
        "present_env": [
          "BRAINOS_EMBEDDING_MODEL",
          "AZURE_API_BASE",
          "AZURE_API_KEY",
          "AZURE_API_VERSION"
        ],
        "missing_env": [],
        "call_params": {
          "model": "azure/UDTEMBED3L",
          "api_base": "https://udtazureopenai.openai.azure.com",
          "api_key": "[REDACTED]",
          "api_version": "2025-04-01-preview"
        },
        "config_source": {
          "BRAINOS_EMBEDDING_MODEL": "BRAINOS_EMBEDDING_MODEL",
          "api_base": "AZURE_API_BASE",
          "api_key": "AZURE_API_KEY",
          "api_version": "AZURE_API_VERSION"
        },
        "headers_env": "BRAINOS_EMBEDDING_HEADERS_JSON"
      },
      "required_env": [
        "BRAINOS_EMBEDDING_MODEL",
        "AZURE_API_BASE",
        "AZURE_API_KEY",
        "AZURE_API_VERSION"
      ],
      "present_env": [
        "BRAINOS_EMBEDDING_MODEL",
        "AZURE_API_BASE",
        "AZURE_API_KEY",
        "AZURE_API_VERSION"
      ],
      "missing_env": [],
      "invalid_env": []
    },
    "sqlite_vec_env": {
      "status": "ok",
      "issues": [],
      "notes": [
        "path_exists",
        "path_under_shared_runtime_prefix"
      ],
      "action_hint": "noop",
      "configured": true,
      "runtime_origin": "explicit_configured",
      "path": "/home/openclaw/.npm-global/lib/node_modules/openclaw/node_modules/sqlite-vec-linux-x64/vec0.so"
    },
    "dependencies": {

```

