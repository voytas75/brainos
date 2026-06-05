from brainos.ingest import prepare_episode_ingest
from brainos.store import BrainOSStore


def test_prepare_episode_ingest_applies_defaults():
    content, metadata = prepare_episode_ingest("  Hello   world  ", {})
    assert content == "Hello world"
    assert metadata["kind"] == "note"
    assert metadata["source"] == "manual"
    assert "topic" not in metadata


def test_prepare_episode_ingest_preserves_optional_fields_and_falls_back_unknown_kind():
    content, metadata = prepare_episode_ingest(
        "  Decision note  ",
        {"kind": "weird-kind", "topic": "brainos", "source": "web"},
    )
    assert content == "Decision note"
    assert metadata["kind"] == "note"
    assert metadata["original_kind"] == "weird-kind"
    assert metadata["topic"] == "brainos"
    assert metadata["source"] == "web"


def test_store_add_episode_normalizes_new_entries(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    episode_id = store.add_episode(
        session_id="s1",
        content="  BrainOS   typed ingest   ",
        metadata={"kind": "other", "topic": "brainos"},
    )

    item = store.get_episode(episode_id)
    assert item is not None
    assert item["content"] == "BrainOS typed ingest"
    assert item["metadata"]["kind"] == "note"
    assert item["metadata"]["topic"] == "brainos"
    assert item["metadata"]["source"] == "manual"
