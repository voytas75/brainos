from brainos.store import BrainOSStore


def test_normalize_fts_query_expands_repair_aliases(tmp_path):
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()

    assert store._normalize_fts_query("fix stale vectors") == "fix OR repair OR reindex OR stale OR vectors"
    assert store._normalize_fts_query("reindex stale vectors") == "reindex OR repair OR stale OR vectors"
    assert store._normalize_fts_query("how to fix stale vectors") == "fix OR repair OR reindex OR stale OR vectors"
