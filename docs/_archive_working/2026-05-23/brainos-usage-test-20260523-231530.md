# BrainOS usage test

- DB path: `/tmp/brainos-usage-1779570925.db`

## Recall 1
```
--- recall 1 ---
{
  "query": "sqlite durability",
  "session_id": "e2e",
  "episodes": [
    {
      "id": "44aac74d-f0f3-429b-a10e-f061e07859b0",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "44aac74d-f0f3-429b-a10e-f061e07859b0",
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
        "updated_at": "2026-05-23 21:15:28"
      }
    }
  ],
  "vector_episodes": [],
  "ranked_episodes": [
    {
      "id": "44aac74d-f0f3-429b-a10e-f061e07859b0",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "44aac74d-f0f3-429b-a10e-f061e07859b0",
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
        "updated_at": "2026-05-23 21:15:28"
      },
      "match_sources": [
        "fts"
      ],
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      }
    }
  ],
  "semantic_hits": [],
  "vector_semantic_hits": [],
  "ranked_semantic_hits": [],
  "count": 1,
  "vector_count": 0,
  "ranked_count": 1,
  "semantic_count": 0,
  "vector_semantic_count": 0,
  "ranked_semantic_count": 0,
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "vector_mode": "error",
  "vector_error": "missing embedding environmen
```

## Recall 2
```
--- recall 2 ---
{
  "query": "explicit sqlite-vec runtime loading",
  "session_id": "e2e",
  "episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
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
        "updated_at": "2026-05-23 21:15:28"
      }
    }
  ],
  "vector_episodes": [],
  "ranked_episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
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
        "updated_at": "2026-05-23 21:15:28"
      },
      "match_sources": [
        "fts"
      ],
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      }
    }
  ],
  "semantic_hits": [],
  "vector_semantic_hits": [],
  "ranked_semantic_hits": [],
  "count": 1,
  "vector_count": 0,
  "ranked_count": 1,
  "semantic_count": 0,
  "vector_semantic_count": 0,
  "ranked_semantic_count": 0,
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "vector_mode": "error",
  "ve
```

## Recall 3
```
--- recall 3 ---
{
  "query": "BRAINOS_SQLITE_VEC_PATH",
  "session_id": "e2e",
  "episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
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
        "updated_at": "2026-05-23 21:15:28"
      }
    }
  ],
  "vector_episodes": [],
  "ranked_episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "session_id": "e2e",
      "timestamp": "2026-05-23 21:15:28",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "metadata": {},
      "vector_state": {
        "object_type": "episode",
        "object_id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
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
        "updated_at": "2026-05-23 21:15:28"
      },
      "match_sources": [
        "fts"
      ],
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      }
    }
  ],
  "semantic_hits": [],
  "vector_semantic_hits": [],
  "ranked_semantic_hits": [],
  "count": 1,
  "vector_count": 0,
  "ranked_count": 1,
  "semantic_count": 0,
  "vector_semantic_count": 0,
  "ranked_semantic_count": 0,
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "vector_mode": "error",
  "vector_error":
```

## Explain 1
```
--- explain 1 ---
{
  "query": "sqlite durability",
  "session_id": "e2e",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "summary": "episodes:1, ranked_episodes:1",
  "episode_vector_mode": "error",
  "episode_vector_error": "missing embedding environment variables: BRAINOS_EMBEDDING_MODEL, AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION",
  "semantic_vector_mode": "disabled",
  "semantic_vector_error": null,
  "diagnostic_hint": "inspect_vector_participation",
  "top_ranked_episodes": [
    {
      "id": "44aac74d-f0f3-429b-a10e-f061e07859b0",
      "content": "SQLite WAL improves durability and concurrent access behavior.",
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      },
      "match_sources": [
        "fts"
      ]
    }
  ],
  "top_ranked_semantic_hits": []
}
```

## Explain 2
```
--- explain 2 ---
{
  "query": "explicit sqlite-vec runtime loading",
  "session_id": "e2e",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "summary": "episodes:1, ranked_episodes:1",
  "episode_vector_mode": "error",
  "episode_vector_error": "missing embedding environment variables: BRAINOS_EMBEDDING_MODEL, AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION",
  "semantic_vector_mode": "disabled",
  "semantic_vector_error": null,
  "diagnostic_hint": "inspect_vector_participation",
  "top_ranked_episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      },
      "match_sources": [
        "fts"
      ]
    }
  ],
  "top_ranked_semantic_hits": []
}
```

## Explain 3
```
--- explain 3 ---
{
  "query": "BRAINOS_SQLITE_VEC_PATH",
  "session_id": "e2e",
  "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
  "scoring_policy_version": "retrieval-scoring-v1",
  "summary": "episodes:1, ranked_episodes:1",
  "episode_vector_mode": "error",
  "episode_vector_error": "missing embedding environment variables: BRAINOS_EMBEDDING_MODEL, AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION",
  "semantic_vector_mode": "disabled",
  "semantic_vector_error": null,
  "diagnostic_hint": "inspect_vector_participation",
  "top_ranked_episodes": [
    {
      "id": "a8bf9cdb-f035-40ae-bfd5-4df8b7e972c9",
      "content": "BRAINOS_SQLITE_VEC_PATH enables explicit sqlite-vec runtime loading.",
      "rank_score": 1000.0,
      "score_components": {
        "fts_rank": 1000.0
      },
      "match_sources": [
        "fts"
      ]
    }
  ],
  "top_ranked_semantic_hits": []
}
```

## Health
```
--- health ---
{
  "status": "warn",
  "summary": "benchmark failure needs explain-side inspection",
  "action_hint": "inspect_notes",
  "runtime": {
    "status": "ok",
    "issues": [],
    "action_hint": "noop",
    "capabilities": {
      "fts5": true,
      "sqlite_vec": true,
      "sqlite_vec_error": null,
      "sqlite_vec_path": "/home/voytas/.bun/install/cache/sqlite-vec-linux-x64@0.1.7-dd4d9ab07e99b7ce@@@1/vec0.so",
      "sqlite_vec_loaded": true,
      "sqlite_vec_probe_mode": "explicit_path"
    }
  },
  "freshness": {
    "status": "ok",
    "issues": [],
    "notes": [
      "missing_vectors_present"
    ],
    "action_hint": "inspect_notes",
    "vector_index": {
      "total": 3,
      "by_status": {
        "missing": 3
      },
      "by_type": {
        "episode": 3
      }
    }
  },
  "quality": {
    "status": "warn",
    "issues": [
      "benchmark_not_green"
    ],
    "notes": [],
    "action_hint": "inspect_benchmark_failure",
    "benchmark": {
      "suite": "retrieval-benchmark-v0",
      "evidence_kind": "seeded_fixture",
      "truthfulness_note": "This benchmark uses an internal seeded fixture corpus and should be read as implementation-level evidence, not direct evidence about the current live database corpus.",
      "ok": false,
      "mode": "vector-ready",
      "degraded": false,
      "degraded_reason": null,
      "case_count": 5,
      "passed": 0,
      "failed": 5,
      "failed_cases": [
        {
          "query": "sqlite wal durability",
          "failure_hint": "likely_freshness_or_vector_path_related",
          "expected_episode_id": "5de0043c-79f8-4f76-aed5-c6c150924e60",
          "top_episode_id": null,
          "expected_semantic_id": "sem-wal",
          "top_semantic_id": null,
          "next_debug": {
            "tool": "retrieval-explain",
            "query": "sqlite wal durability",
            "session_id": "bench"
          }
        },
        {
          "query": "azure embedding model",
          "failure_hint": "likely_freshness_or_vector_path_related",
          "expected_episode_id": "650ca227-76c2-4df7-b82e-0a2ac990089c",
          "top_episode_id": null,
          "expected_semantic_id": "sem-azure-embed",
          "top_semantic_id": null,
          "next_debug": {
            "tool": "retrieval-explain",
            "query": "azure embedding model",
            "session_id": "bench"
          }
        },
        {
          "query": "how to repair stale vectors",
          "fai
```

## Result
- Result: **WEAK**
- Crash or weirdness: Health still reports benchmark/freshness warnings