from brainos.real_corpus_probe import run_real_corpus_probe
from brainos.store import BrainOSStore


def seed_real_sample_store(store: BrainOSStore) -> dict[str, str]:
    ids = {}
    ids["ep_sqlite_wal"] = store.add_episode(
        session_id="real",
        content="SQLite WAL mode helps BrainOS keep local writes safe and concurrent.",
        metadata={"kind": "storage"},
    )
    ids["ep_embedding_azure"] = store.add_episode(
        session_id="real",
        content="Azure embeddings are executed through LiteLLM in the current BrainOS path.",
        metadata={"kind": "embedding"},
    )
    ids["ep_reindex_runtime"] = store.add_episode(
        session_id="real",
        content="Reindex stale vectors after runtime changes or source text updates.",
        metadata={"kind": "maintenance"},
    )
    ids["ep_browser_noise"] = store.add_episode(
        session_id="real",
        content="Browser relay sessions can fail when the attached tab is stale.",
        metadata={"kind": "browser"},
    )
    ids["ep_cross_session_noise"] = store.add_episode(
        session_id="other",
        content="Azure embeddings were tested in another session and should not leak into filtered recall.",
        metadata={"kind": "embedding"},
    )
    ids["ep_policy_surface"] = store.add_episode(
        session_id="real",
        content="Explain output should include the active retrieval scoring policy version.",
        metadata={"kind": "policy"},
    )

    store.upsert_semantic_node(
        node_id="sem-wal",
        name="SQLite WAL",
        node_type="Concept",
        properties={"area": "storage"},
    )
    store.upsert_semantic_node(
        node_id="sem-azure-embed",
        name="Azure Embeddings",
        node_type="Capability",
        properties={"area": "embedding"},
    )
    store.upsert_semantic_node(
        node_id="sem-reindex",
        name="Vector Reindex",
        node_type="Procedure",
        properties={"area": "maintenance"},
    )
    store.upsert_semantic_node(
        node_id="sem-policy-surface",
        name="Retrieval Scoring Policy Version",
        node_type="Capability",
        properties={"area": "retrieval"},
    )
    return ids


def test_real_sample_benchmark_pass(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_real_sample_store(store)

    vector_episode_map = {
        "sqlite wal durability": [
            {
                "id": ids["ep_sqlite_wal"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "SQLite WAL mode helps BrainOS keep local writes safe and concurrent.",
                "metadata": {"kind": "storage"},
                "distance": 0.03,
            }
        ],
        "azure embedding model": [
            {
                "id": ids["ep_cross_session_noise"],
                "session_id": "other",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Azure embeddings were tested in another session and should not leak into filtered recall.",
                "metadata": {"kind": "embedding"},
                "distance": 0.01,
            },
            {
                "id": ids["ep_embedding_azure"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Azure embeddings are executed through LiteLLM in the current BrainOS path.",
                "metadata": {"kind": "embedding"},
                "distance": 0.04,
            },
        ],
        "how to repair stale vectors": [
            {
                "id": ids["ep_reindex_runtime"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reindex stale vectors after runtime changes or source text updates.",
                "metadata": {"kind": "maintenance"},
                "distance": 0.06,
            },
            {
                "id": ids["ep_browser_noise"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Browser relay sessions can fail when the attached tab is stale.",
                "metadata": {"kind": "browser"},
                "distance": 0.09,
            },
        ],
        "policy version explain": [
            {
                "id": ids["ep_policy_surface"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Explain output should include the active retrieval scoring policy version.",
                "metadata": {"kind": "policy"},
                "distance": 0.03,
            }
        ],
        "nonsense local dragons": [
            {
                "id": "ghost-noise",
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Unrelated hallucinated dragon vector hit.",
                "metadata": {},
                "distance": 5.1,
            }
        ],
    }

    vector_semantic_map = {
        "sqlite wal durability": [
            {
                "id": "sem-wal",
                "name": "SQLite WAL",
                "type": "Concept",
                "properties": {"area": "storage"},
                "edges": [],
                "distance": 0.02,
            }
        ],
        "azure embedding model": [
            {
                "id": "sem-azure-embed",
                "name": "Azure Embeddings",
                "type": "Capability",
                "properties": {"area": "embedding"},
                "edges": [],
                "distance": 0.05,
            }
        ],
        "how to repair stale vectors": [
            {
                "id": "sem-reindex",
                "name": "Vector Reindex",
                "type": "Procedure",
                "properties": {"area": "maintenance"},
                "edges": [],
                "distance": 0.04,
            }
        ],
        "policy version explain": [
            {
                "id": "sem-policy-surface",
                "name": "Retrieval Scoring Policy Version",
                "type": "Capability",
                "properties": {"area": "retrieval"},
                "edges": [],
                "distance": 0.02,
            }
        ],
        "nonsense local dragons": [
            {
                "id": "sem-noise",
                "name": "Dragon Noise",
                "type": "Concept",
                "properties": {"area": "noise"},
                "edges": [],
                "distance": 4.6,
            }
        ],
    }

    monkeypatch.setattr(
        store,
        "sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[float(len(texts[0])) / 100.0, 0.21, 0.31]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure/UDTEMBED3L",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )

    current_query = [""]
    monkeypatch.setattr(
        store,
        "vector_search_episodes",
        lambda query_vector, session_id=None, limit=10: [
            item for item in vector_episode_map.get(current_query[0], []) if session_id is None or item["session_id"] == session_id
        ],
    )
    monkeypatch.setattr(
        store,
        "vector_search_semantic_nodes",
        lambda query_vector, limit=10: vector_semantic_map.get(current_query[0], []),
    )

    cases = [
        ("sqlite wal durability", ids["ep_sqlite_wal"], "sem-wal"),
        ("azure embedding model", ids["ep_embedding_azure"], "sem-azure-embed"),
        ("how to repair stale vectors", ids["ep_reindex_runtime"], "sem-reindex"),
    ]

    benchmark_report = []
    for query, expected_episode_id, expected_semantic_id in cases:
        current_query[0] = query
        recall = store.recall(query, session_id="real", limit=5)
        top_episode = recall["ranked_episodes"][0]["id"] if recall["ranked_episodes"] else None
        top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall["ranked_semantic_hits"] else None
        benchmark_report.append(
            {
                "query": query,
                "top_episode": top_episode,
                "top_semantic": top_semantic,
                "episode_vector_mode": recall["episode_vector_mode"],
                "semantic_vector_mode": recall["semantic_vector_mode"],
            }
        )
        assert top_episode == expected_episode_id
        assert top_semantic == expected_semantic_id

    current_query[0] = "nonsense local dragons"
    nonsense = store.recall("nonsense local dragons", session_id="real", limit=5)
    assert nonsense["ranked_count"] == 0
    assert nonsense["ranked_semantic_count"] == 0

    assert len(benchmark_report) == 3
    assert all(item["episode_vector_mode"] == "sqlite_vec_episode_similarity" for item in benchmark_report)
    assert all(item["semantic_vector_mode"] == "sqlite_vec_semantic_similarity" for item in benchmark_report)
    store.close()


def test_real_sample_scores_explain_top_hit(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_real_sample_store(store)

    monkeypatch.setattr(
        store,
        "sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.33, 0.21, 0.31]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure/UDTEMBED3L",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "vector_search_episodes",
        lambda query_vector, session_id=None, limit=10: [
            {
                "id": ids["ep_reindex_runtime"],
                "session_id": "real",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reindex stale vectors after runtime changes or source text updates.",
                "metadata": {"kind": "maintenance"},
                "distance": 0.04,
            }
        ],
    )
    monkeypatch.setattr(
        store,
        "vector_search_semantic_nodes",
        lambda query_vector, limit=10: [
            {
                "id": "sem-reindex",
                "name": "Vector Reindex",
                "type": "Procedure",
                "properties": {"area": "maintenance"},
                "edges": [],
                "distance": 0.03,
            }
        ],
    )

    recall = store.recall("how to repair stale vectors", session_id="real", limit=5)
    top_episode = recall["ranked_episodes"][0]
    top_semantic = recall["ranked_semantic_hits"][0]
    assert "score_components" in top_episode
    assert "episode_vector" in top_episode["score_components"] or "fts_rank" in top_episode["score_components"]
    assert "score_components" in top_semantic
    assert "semantic_vector" in top_semantic["score_components"] or "name_match_rank" in top_semantic["score_components"]
    store.close()


def test_real_sample_policy_version_case(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_real_sample_store(store)

    monkeypatch.setattr(store, "sqlite_vec_capability", lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None})
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.41, 0.11, 0.21]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure/UDTEMBED3L",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "vector_search_episodes",
        lambda query_vector, session_id=None, limit=10: [{
            "id": ids["ep_policy_surface"],
            "session_id": "real",
            "timestamp": "2026-05-22 00:00:00",
            "content": "Explain output should include the active retrieval scoring policy version.",
            "metadata": {"kind": "policy"},
            "distance": 0.03,
        }],
    )
    monkeypatch.setattr(
        store,
        "vector_search_semantic_nodes",
        lambda query_vector, limit=10: [{
            "id": "sem-policy-surface",
            "name": "Retrieval Scoring Policy Version",
            "type": "Capability",
            "properties": {"area": "retrieval"},
            "edges": [],
            "distance": 0.02,
        }],
    )

    recall = store.recall("policy version explain", session_id="real", limit=5)
    assert recall["ranked_episodes"][0]["id"] == ids["ep_policy_surface"]
    assert recall["ranked_semantic_hits"][0]["id"] == "sem-policy-surface"
    assert recall["scoring_policy_version"] == "retrieval-scoring-v1a"
    store.close()


def test_real_corpus_probe_reports_small_real_sample_truthfully(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_real_sample_store(store)

    vector_episode_map = {
        "sqlite wal durability": [{"id": ids["ep_sqlite_wal"], "session_id": "real", "timestamp": "2026-05-22 00:00:00", "content": "SQLite WAL mode helps BrainOS keep local writes safe and concurrent.", "metadata": {"kind": "storage"}, "distance": 0.03}],
        "azure embedding model": [{"id": ids["ep_embedding_azure"], "session_id": "real", "timestamp": "2026-05-22 00:00:00", "content": "Azure embeddings are executed through LiteLLM in the current BrainOS path.", "metadata": {"kind": "embedding"}, "distance": 0.04}],
        "how to repair stale vectors": [{"id": ids["ep_reindex_runtime"], "session_id": "real", "timestamp": "2026-05-22 00:00:00", "content": "Reindex stale vectors after runtime changes or source text updates.", "metadata": {"kind": "maintenance"}, "distance": 0.06}],
        "policy version explain": [{"id": ids["ep_policy_surface"], "session_id": "real", "timestamp": "2026-05-22 00:00:00", "content": "Explain output should include the active retrieval scoring policy version.", "metadata": {"kind": "policy"}, "distance": 0.03}],
    }
    vector_semantic_map = {
        "sqlite wal durability": [{"id": "sem-wal", "name": "SQLite WAL", "type": "Concept", "properties": {"area": "storage"}, "edges": [], "distance": 0.02}],
        "azure embedding model": [{"id": "sem-azure-embed", "name": "Azure Embeddings", "type": "Capability", "properties": {"area": "embedding"}, "edges": [], "distance": 0.05}],
        "how to repair stale vectors": [{"id": "sem-reindex", "name": "Vector Reindex", "type": "Procedure", "properties": {"area": "maintenance"}, "edges": [], "distance": 0.04}],
        "policy version explain": [{"id": "sem-policy-surface", "name": "Retrieval Scoring Policy Version", "type": "Capability", "properties": {"area": "retrieval"}, "edges": [], "distance": 0.02}],
    }

    monkeypatch.setattr(store, "sqlite_vec_capability", lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None})
    monkeypatch.setattr(store, "embed_texts", lambda texts, profile=None: {"vectors": [[float(len(texts[0])) / 100.0, 0.21, 0.31]], "dimensions": 3, "provider": "azure", "model": "azure/UDTEMBED3L", "profile": profile or "brainos-embedding-default", "requested_count": 1, "returned_count": 1})
    current_query = [""]
    monkeypatch.setattr(store, "vector_search_episodes", lambda query_vector, session_id=None, limit=10: [item for item in vector_episode_map.get(current_query[0], []) if session_id is None or item["session_id"] == session_id])
    monkeypatch.setattr(store, "vector_search_semantic_nodes", lambda query_vector, limit=10: vector_semantic_map.get(current_query[0], []))

    original_recall = store.recall
    def recall_with_query(query, session_id=None, limit=10):
        current_query[0] = query
        return original_recall(query, session_id=session_id, limit=limit)
    monkeypatch.setattr(store, "recall", recall_with_query)

    payload = run_real_corpus_probe(store, limit=5)
    assert payload["probe"] == "real-corpus-retrieval-quality-v1"
    assert payload["evidence_kind"] == "small_real_sample"
    assert "truthfulness_note" in payload
    assert payload["target_status"] == "aligned_to_available_session_sample"
    assert payload["target_session_id"] == "real"
    assert payload["case_count"] == 2
    assert len(payload["results"]) == 2
    store.close()


def test_real_corpus_probe_aligns_to_available_session_sample(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    store.add_episode(session_id="session-z", content="BrainOS initialized with WAL and ledger", metadata={})
    store.add_episode(session_id="session-a", content="Store a semantic fact", metadata={})

    payload = run_real_corpus_probe(store, limit=5)
    assert payload["target_status"] == "aligned_to_available_session_sample"
    assert payload["target_session_id"] == "session-a"
    assert payload["available_session_ids"] == ["session-a", "session-z"]
    assert payload["case_count"] == 2
    store.close()


def test_real_corpus_probe_reports_no_session_sample_available(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    payload = run_real_corpus_probe(store, limit=5)
    assert payload["target_status"] == "no_session_sample_available"
    assert payload["case_count"] == 0
    assert payload["results"] == []
    store.close()
