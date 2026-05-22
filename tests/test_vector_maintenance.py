from brainos.errors import VectorIndexContractError
from brainos.store import BrainOSStore


def test_refresh_vector_freshness_for_semantic_node_marks_stale(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.upsert_semantic_node(node_id="n1", name="Semantic fact", node_type="Fact", properties={"topic": "memory"})
    state = store.get_vector_index_state("semantic_node", "n1")
    assert state is not None
    assert state["vector_status"] == "missing"

    store.upsert_semantic_node(node_id="n1", name="Semantic fact", node_type="Fact", properties={"topic": "memory", "tier": "core"})
    refreshed = store.refresh_vector_freshness_for_semantic_node("n1")
    assert refreshed["vector_status"] == "stale"
    store.close()


def test_sync_vector_index_dispatches_to_episode_generator(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Need embedding", metadata={})

    monkeypatch.setattr(store, "refresh_vector_freshness_for_episode", lambda object_id, embedding_profile=None: {"vector_status": "missing"})
    monkeypatch.setattr(
        store,
        "generate_episode_embedding",
        lambda object_id, embedding_profile=None: {"ok": True, "object_type": "episode", "object_id": object_id, "vector_status": "fresh"},
    )

    result = store.sync_vector_index(object_type="episode", object_id=episode_id)
    assert result["ok"] is True
    assert result["object_id"] == episode_id
    assert result["vector_status"] == "fresh"
    store.close()


def test_sync_vector_index_batch_collects_dimension_contract_errors(monkeypatch, tmp_path):
    db = tmp_path / "brain_contract_error.db"
    store = BrainOSStore(db)
    store.initialize()
    e1 = store.add_episode(session_id="s1", content="Need embedding 1", metadata={})

    monkeypatch.setattr(
        store,
        "sync_vector_index",
        lambda object_type, object_id, embedding_profile=None, force=False: (_ for _ in ()).throw(
            VectorIndexContractError("vector index dimension mismatch: table=episodes_vec, expected=1536, got=3; rebuild required")
        ),
    )

    result = store.sync_vector_index_batch(object_type="episode", vector_status="missing", limit=10)
    assert result["ok"] is False
    assert result["requested"] >= 1
    assert result["synced"] == 0
    assert len(result["errors"]) >= 1
    assert result["errors"][0]["object_id"] == e1
    assert "dimension mismatch" in result["errors"][0]["error"]
    store.close()


def test_sync_vector_index_batch_filters_states(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    e1 = store.add_episode(session_id="s1", content="Need embedding 1", metadata={})
    e2 = store.add_episode(session_id="s1", content="Need embedding 2", metadata={})

    called = []
    monkeypatch.setattr(
        store,
        "sync_vector_index",
        lambda object_type, object_id, embedding_profile=None, force=False: called.append((object_type, object_id, force)) or {"ok": True, "object_type": object_type, "object_id": object_id, "vector_status": "fresh"},
    )

    result = store.sync_vector_index_batch(object_type="episode", vector_status="missing", limit=10)
    assert result["requested"] >= 2
    assert len(called) >= 2
    assert all(item[0] == "episode" for item in called)
    assert e1 in [item[1] for item in called]
    assert e2 in [item[1] for item in called]
    store.close()
