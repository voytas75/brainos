from brainos.store import BrainOSStore


def seed_eval_store(store: BrainOSStore) -> dict[str, str]:
    ids = {}
    ids["ep_semantic"] = store.add_episode(
        session_id="eval",
        content="Semantic memory edges connect concepts in BrainOS.",
        metadata={"kind": "graph"},
    )
    ids["ep_bootstrap"] = store.add_episode(
        session_id="eval",
        content="Bootstrap the store in two steps: init db and load state.",
        metadata={"kind": "procedure"},
    )
    ids["ep_vector"] = store.add_episode(
        session_id="eval",
        content="Azure embeddings improve semantic recall quality.",
        metadata={"kind": "embedding"},
    )

    store.upsert_semantic_node(
        node_id="sem-memory",
        name="Semantic Memory",
        node_type="Concept",
        properties={"area": "memory"},
    )
    store.upsert_semantic_node(
        node_id="sem-bootstrap",
        name="Bootstrap Procedure",
        node_type="Procedure",
        properties={"area": "ops"},
    )
    return ids


def test_eval_recall_expected_hits(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_eval_store(store)

    vector_episode_map = {
        "semantic graph": [
            {
                "id": ids["ep_semantic"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Semantic memory edges connect concepts in BrainOS.",
                "metadata": {"kind": "graph"},
                "distance": 0.02,
            }
        ],
        "initialize database": [
            {
                "id": ids["ep_bootstrap"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Bootstrap the store in two steps: init db and load state.",
                "metadata": {"kind": "procedure"},
                "distance": 0.08,
            }
        ],
        "embedding quality": [
            {
                "id": ids["ep_vector"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Azure embeddings improve semantic recall quality.",
                "metadata": {"kind": "embedding"},
                "distance": 0.04,
            }
        ],
    }
    vector_semantic_map = {
        "semantic graph": [
            {
                "id": "sem-memory",
                "name": "Semantic Memory",
                "type": "Concept",
                "properties": {"area": "memory"},
                "edges": [],
                "distance": 0.03,
            }
        ],
        "initialize database": [
            {
                "id": "sem-bootstrap",
                "name": "Bootstrap Procedure",
                "type": "Procedure",
                "properties": {"area": "ops"},
                "edges": [],
                "distance": 0.07,
            }
        ],
        "embedding quality": [
            {
                "id": "sem-memory",
                "name": "Semantic Memory",
                "type": "Concept",
                "properties": {"area": "memory"},
                "edges": [],
                "distance": 0.4,
            }
        ],
    }

    monkeypatch.setattr(
        store,
        "_sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[float(len(texts[0])) / 100.0, 0.2, 0.3]],
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
        "_vector_search_episodes",
        lambda query_vector, session_id=None, limit=10: vector_episode_map.get(current_query[0], []),
    )
    monkeypatch.setattr(
        store,
        "_vector_search_semantic_nodes",
        lambda query_vector, limit=10: vector_semantic_map.get(current_query[0], []),
    )

    cases = [
        {
            "query": "semantic graph",
            "expected_episode_id": ids["ep_semantic"],
            "expected_semantic_id": "sem-memory",
        },
        {
            "query": "initialize database",
            "expected_episode_id": ids["ep_bootstrap"],
            "expected_semantic_id": "sem-bootstrap",
        },
        {
            "query": "embedding quality",
            "expected_episode_id": ids["ep_vector"],
            "expected_semantic_id": "sem-memory",
        },
    ]

    current_query = [""]
    report = []
    for case in cases:
        current_query[0] = case["query"]
        recall = store.recall(case["query"], session_id="eval", limit=5)
        top_episode = recall["ranked_episodes"][0]["id"] if recall["ranked_episodes"] else None
        top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall["ranked_semantic_hits"] else None
        report.append((case["query"], top_episode, top_semantic))
        assert top_episode == case["expected_episode_id"]
        assert top_semantic == case["expected_semantic_id"]

    assert len(report) == 3
    store.close()
