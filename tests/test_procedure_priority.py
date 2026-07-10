from brainos.store import BrainOSStore



def _mock_runtime_ok(monkeypatch):
    monkeypatch.setattr(
        "brainos.retrieval.vector_runtime_preflight",
        lambda: {"status": "ok", "ok": True, "degraded": False, "action_hint": "noop"},
    )



def test_recall_prefers_procedure_over_explanatory_note_for_repair_query(monkeypatch, tmp_path):
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
    store.add_episode(
        session_id="ops",
        content="After a retrieval regression, inspect retrieval-explain before changing scoring policy; policy edits are not the first move.",
        metadata={"kind": "continuation", "topic": "next-step", "authority": "secondary"},
    )
    store.add_episode(
        session_id="ops",
        content="An older BrainOS setup used openai/text-embedding-3-small, but that is not the current runtime on this machine.",
        metadata={"kind": "history", "topic": "embedding", "authority": "legacy"},
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

    recall = store.recall("do I fix stale vectors by explain first or by reindexing", session_id="ops", limit=5)

    assert recall["ranked_episodes"], "expected ranked episodes"
    assert recall["ranked_episodes"][0]["id"] == procedure_id
    assert recall["ranked_episodes"][0]["metadata"]["kind"] == "procedure"
