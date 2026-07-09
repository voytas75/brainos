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
    ids["ep_similar_good"] = store.add_episode(
        session_id="eval",
        content="Reset runtime data safely before reindexing the store.",
        metadata={"kind": "ops"},
    )
    ids["ep_similar_bad"] = store.add_episode(
        session_id="eval",
        content="Reset browser window size for local UI testing.",
        metadata={"kind": "ui"},
    )
    ids["ep_other_session"] = store.add_episode(
        session_id="other",
        content="Reset runtime data for another isolated session.",
        metadata={"kind": "ops"},
    )
    ids["ep_policy"] = store.add_episode(
        session_id="eval",
        content="Retrieval scoring policy version should be visible in explain output.",
        metadata={"kind": "policy"},
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
    store.upsert_semantic_node(
        node_id="sem-runtime-reset",
        name="Runtime Reset",
        node_type="Procedure",
        properties={"area": "ops"},
    )
    store.upsert_semantic_node(
        node_id="sem-policy",
        name="Retrieval Scoring Policy",
        node_type="Concept",
        properties={"area": "retrieval"},
    )
    store.upsert_semantic_node(
        node_id="sem-policy-noise",
        name="Policy Noise",
        node_type="Concept",
        properties={"area": "noise"},
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
        "reset runtime": [
            {
                "id": ids["ep_similar_good"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reset runtime data safely before reindexing the store.",
                "metadata": {"kind": "ops"},
                "distance": 0.06,
            },
            {
                "id": ids["ep_similar_bad"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reset browser window size for local UI testing.",
                "metadata": {"kind": "ui"},
                "distance": 0.61,
            },
            {
                "id": ids["ep_other_session"],
                "session_id": "other",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reset runtime data for another isolated session.",
                "metadata": {"kind": "ops"},
                "distance": 0.03,
            },
        ],
        "policy version": [
            {
                "id": ids["ep_policy"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Retrieval scoring policy version should be visible in explain output.",
                "metadata": {"kind": "policy"},
                "distance": 0.05,
            }
        ],
        "nonsense request": [
            {
                "id": "ghost-weak",
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Weak unrelated vector-only result.",
                "metadata": {},
                "distance": 4.2,
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
        "reset runtime": [
            {
                "id": "sem-runtime-reset",
                "name": "Runtime Reset",
                "type": "Procedure",
                "properties": {"area": "ops"},
                "edges": [],
                "distance": 0.05,
            },
            {
                "id": "sem-bootstrap",
                "name": "Bootstrap Procedure",
                "type": "Procedure",
                "properties": {"area": "ops"},
                "edges": [],
                "distance": 0.7,
            },
        ],
        "policy version": [
            {
                "id": "sem-policy",
                "name": "Retrieval Scoring Policy",
                "type": "Concept",
                "properties": {"area": "retrieval"},
                "edges": [],
                "distance": 0.03,
            },
            {
                "id": "sem-policy-noise",
                "name": "Policy Noise",
                "type": "Concept",
                "properties": {"area": "noise"},
                "edges": [],
                "distance": 0.09,
            }
        ],
        "nonsense request": [
            {
                "id": "sem-noise",
                "name": "Noise Node",
                "type": "Concept",
                "properties": {"area": "noise"},
                "edges": [],
                "distance": 3.4,
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
        {
            "query": "semantic graph",
            "expected_episode_id": ids["ep_semantic"],
            "expected_semantic_id": "sem-memory",
            "session_id": "eval",
        },
        {
            "query": "initialize database",
            "expected_episode_id": ids["ep_bootstrap"],
            "expected_semantic_id": "sem-bootstrap",
            "session_id": "eval",
        },
        {
            "query": "embedding quality",
            "expected_episode_id": ids["ep_vector"],
            "expected_semantic_id": "sem-memory",
            "session_id": "eval",
        },
        {
            "query": "reset runtime",
            "expected_episode_id": ids["ep_similar_good"],
            "expected_semantic_id": "sem-runtime-reset",
            "session_id": "eval",
        },
        {
            "query": "policy version",
            "expected_episode_id": ids["ep_policy"],
            "expected_semantic_id": "sem-policy",
            "session_id": "eval",
        },
    ]

    current_query = [""]
    report = []
    for case in cases:
        current_query[0] = case["query"]
        recall = store.recall(case["query"], session_id=case["session_id"], limit=5)
        top_episode = recall["ranked_episodes"][0]["id"] if recall["ranked_episodes"] else None
        top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall["ranked_semantic_hits"] else None
        report.append((case["query"], top_episode, top_semantic))
        assert top_episode == case["expected_episode_id"]
        assert top_semantic == case["expected_semantic_id"]

    current_query[0] = "nonsense request"
    nonsense = store.recall("nonsense request", session_id="eval", limit=5)
    assert nonsense["ranked_count"] == 0
    assert nonsense["ranked_semantic_count"] == 0
    assert len(nonsense["vector_episodes"]) == 1
    assert len(nonsense["vector_semantic_hits"]) == 1

    assert len(report) == 5
    store.close()


def test_eval_prefers_overlap_when_similar_vector_hits_compete(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    ids = seed_eval_store(store)

    monkeypatch.setattr(
        store,
        "sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.5, 0.2, 0.3]],
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
                "id": ids["ep_similar_bad"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reset browser window size for local UI testing.",
                "metadata": {"kind": "ui"},
                "distance": 0.01,
            },
            {
                "id": ids["ep_similar_good"],
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Reset runtime data safely before reindexing the store.",
                "metadata": {"kind": "ops"},
                "distance": 0.03,
            },
        ],
    )
    monkeypatch.setattr(store, "vector_search_semantic_nodes", lambda query_vector, limit=10: [])

    recall = store.recall("reset runtime data", session_id="eval", limit=5)
    assert recall["ranked_episodes"][0]["id"] == ids["ep_similar_good"]
    assert recall["ranked_episodes"][0]["lexical_overlap"] > recall["ranked_episodes"][1]["lexical_overlap"]
    store.close()


def test_eval_distinguishes_disabled_runtime_from_stale_data_wording(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    good_id = store.add_episode(
        session_id="eval",
        content="Disabled vector state usually means sqlite-vec runtime is unavailable.",
        metadata={"kind": "runtime"},
    )
    bad_id = store.add_episode(
        session_id="eval",
        content="Stale vectors mean source text changed and reindex is needed.",
        metadata={"kind": "maintenance"},
    )

    monkeypatch.setattr(store, "sqlite_vec_capability", lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None})
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.55, 0.2, 0.3]],
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
                "id": bad_id,
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Stale vectors mean source text changed and reindex is needed.",
                "metadata": {"kind": "maintenance"},
                "distance": 0.02,
            },
            {
                "id": good_id,
                "session_id": "eval",
                "timestamp": "2026-05-22 00:00:00",
                "content": "Disabled vector state usually means sqlite-vec runtime is unavailable.",
                "metadata": {"kind": "runtime"},
                "distance": 0.04,
            },
        ],
    )
    monkeypatch.setattr(store, "vector_search_semantic_nodes", lambda query_vector, limit=10: [])

    recall = store.recall("disabled vector runtime", session_id="eval", limit=5)
    assert recall["ranked_episodes"][0]["id"] == good_id
    store.close()
