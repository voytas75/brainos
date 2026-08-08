from brainos.store import BrainOSStore


def test_refresh_marks_vector_stale_when_embedding_model_changes(monkeypatch, tmp_path):
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()
    episode_id = store.add_episode(
        session_id="s1", content="Model-aware freshness", metadata={}
    )
    store._set_vector_index_state(
        object_type="episode",
        object_id=episode_id,
        source_text="Model-aware freshness",
        embedding_profile=store.DEFAULT_EMBEDDING_PROFILE,
        vector_status=store.VECTOR_STATUS_FRESH,
        embedding_provider="openai",
        embedding_model="openai/text-embedding-3-small",
        embedding_dimensions=1536,
    )
    monkeypatch.setattr(
        "brainos.store.LiteLLMEmbeddingAdapter.contract",
        lambda _self: {
            "operational_provider": "openai",
            "model": "openai/text-embedding-3-large",
        },
    )
    state = store.refresh_vector_freshness_for_episode(episode_id)

    assert state["vector_status"] == store.VECTOR_STATUS_STALE
    assert state["embedding_provider"] == "openai"
    assert state["embedding_model"] == "openai/text-embedding-3-small"
    store.close()


def test_refresh_keeps_nonfresh_vector_status_on_identity_change(monkeypatch, tmp_path):
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()
    episode_id = store.add_episode(
        session_id="s1", content="Nonfresh state", metadata={}
    )
    monkeypatch.setattr(
        "brainos.store.LiteLLMEmbeddingAdapter.contract",
        lambda _self: {"operational_provider": "openai", "model": "new-model"},
    )

    for status in ("missing", "error", "disabled"):
        store._set_vector_index_state(
            object_type="episode",
            object_id=episode_id,
            source_text="Nonfresh state",
            embedding_profile=store.DEFAULT_EMBEDDING_PROFILE,
            vector_status=status,
            embedding_provider="openai",
            embedding_model="old-model",
        )
        state = store.refresh_vector_freshness_for_episode(episode_id)
        assert state["vector_status"] == status

    store.close()
