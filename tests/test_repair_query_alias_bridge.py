from brainos.store import BrainOSStore


def _mock_runtime_ok(monkeypatch):
    monkeypatch.setattr(
        "brainos.retrieval.vector_runtime_preflight",
        lambda: {"status": "ok", "ok": True, "degraded": False, "action_hint": "noop"},
    )


def test_recall_repair_alias_bridge_prefers_procedure(monkeypatch, tmp_path):
    _mock_runtime_ok(monkeypatch)
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    procedure_id = store.add_episode(
        session_id="ops",
        content="To repair stale vectors after runtime changes, run vector-index-sync-batch for objects in missing, stale, or error state and verify they return to fresh status.",
        metadata={"kind": "procedure", "topic": "reindex", "authority": "current"},
    )
    note_id = store.add_episode(
        session_id="ops",
        content="If vectors look odd, you can inspect retrieval-explain first, but that does not replace reindexing stale vectors after runtime changes.",
        metadata={"kind": "note", "topic": "reindex", "authority": "secondary"},
    )

    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.19, 0.27, 0.33]],
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
                "id": note_id,
                "session_id": "ops",
                "timestamp": "2026-05-22 00:00:00",
                "content": "If vectors look odd, you can inspect retrieval-explain first, but that does not replace reindexing stale vectors after runtime changes.",
                "metadata": {"kind": "note", "topic": "reindex", "authority": "secondary"},
                "distance": 0.06,
            },
            {
                "id": procedure_id,
                "session_id": "ops",
                "timestamp": "2026-05-22 00:00:00",
                "content": "To repair stale vectors after runtime changes, run vector-index-sync-batch for objects in missing, stale, or error state and verify they return to fresh status.",
                "metadata": {"kind": "procedure", "topic": "reindex", "authority": "current"},
                "distance": 0.14,
            },
        ],
    )

    for query in ("fix stale vectors", "reindex stale vectors", "how to fix stale vectors"):
        recall = store.recall(query, session_id="ops", limit=5)
        assert recall["ranked_episodes"], f"expected ranked episodes for {query!r}"
        assert recall["ranked_episodes"][0]["id"] == procedure_id
        assert recall["ranked_episodes"][0]["metadata"]["kind"] == "procedure"
