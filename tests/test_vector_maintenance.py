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


def test_sync_vector_index_returns_noop_for_fresh_state(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Already fresh", metadata={})

    monkeypatch.setattr(
        store,
        "refresh_vector_freshness_for_episode",
        lambda object_id, embedding_profile=None: {"vector_status": "fresh"},
    )

    called = {"generate": False}
    def fake_generate(object_id, embedding_profile=None):
        called["generate"] = True
        return {"ok": True, "object_type": "episode", "object_id": object_id, "vector_status": "fresh"}

    monkeypatch.setattr(store, "generate_episode_embedding", fake_generate)

    result = store.sync_vector_index(object_type="episode", object_id=episode_id)
    assert result["ok"] is True
    assert result["mode"] == "noop"
    assert result["action_hint"] == "noop"
    assert result["reason"] == "already_fresh"
    assert result["vector_status"] == "fresh"
    assert called["generate"] is False
    store.close()


def test_vector_search_episodes_returns_empty_when_vec_table_absent(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    results = store.vector_search_episodes([0.1, 0.2, 0.3], session_id="s1", limit=5)
    assert results == []
    store.close()


def test_vector_search_semantic_nodes_returns_empty_when_vec_table_absent(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    results = store.vector_search_semantic_nodes([0.1, 0.2, 0.3], limit=5)
    assert results == []
    store.close()

def test_sync_vector_index_batch_dedupes_duplicate_source_text_states(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    e1 = store.add_episode(session_id="s1", content="Duplicate text", metadata={})
    e2 = store.add_episode(session_id="s1", content="Duplicate text", metadata={})

    monkeypatch.setattr(
        store,
        "list_vector_index_states",
        lambda object_type=None, vector_status=None, limit=100: [
            {"object_type": "episode", "object_id": e1, "vector_status": "missing"},
            {"object_type": "episode", "object_id": e1, "vector_status": "missing"},
            {"object_type": "episode", "object_id": e2, "vector_status": "missing"},
        ],
    )

    calls = []
    monkeypatch.setattr(
        store,
        "sync_vector_index",
        lambda object_type, object_id, embedding_profile=None, force=False: calls.append((object_type, object_id)) or {"ok": True, "object_type": object_type, "object_id": object_id, "vector_status": "fresh"},
    )

    result = store.sync_vector_index_batch(object_type="episode", vector_status="missing", limit=20)
    assert result["ok"] is True
    assert result["requested"] == 3
    assert result["synced"] == 2
    ids = {item["object_id"] for item in result["results"]}
    assert ids == {e1, e2}
    assert calls == [("episode", e1), ("episode", e2)]
    store.close()
