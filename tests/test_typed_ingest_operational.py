from brainos.store import BrainOSStore
from brainos.explain import explain_recall


def test_typed_ingest_mixed_type_operational_flow(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="ops",
        content="BrainOS should keep sqlite-vec runtime checks explicit and operator-facing.",
        metadata={"kind": "fact", "topic": "runtime", "source": "manual"},
    )
    store.add_episode(
        session_id="ops",
        content="Decision: keep retrieval smoke bounded and use it as a green-path operational check.",
        metadata={"kind": "decision", "topic": "retrieval", "source": "manual"},
    )
    store.add_episode(
        session_id="ops",
        content="Procedure: run init, add episodes, sync vectors, then run retrieval-explain.",
        metadata={"kind": "procedure", "topic": "smoke", "source": "manual"},
    )
    store.add_episode(
        session_id="ops",
        content="Observation: short flat entries reduce retrieval clarity.",
        metadata={"kind": "observation", "topic": "corpus", "source": "manual"},
    )

    episodes = store.list_episodes(session_id="ops", limit=10)
    kinds = {item["metadata"].get("kind") for item in episodes}
    assert {"fact", "decision", "procedure", "observation"}.issubset(kinds)
    assert all(item["metadata"].get("source") == "manual" for item in episodes)

    recall = store.recall("retrieval smoke check", session_id="ops", limit=5)
    assert recall["ranked_count"] >= 1
    assert recall["ranked_episodes"][0]["metadata"]["kind"] in {"decision", "procedure", "note", "observation", "fact"}

    explain = explain_recall(store, "retrieval smoke check", session_id="ops", limit=5)
    assert "operator_summary" in explain
    assert explain["top_ranked_episodes"]
