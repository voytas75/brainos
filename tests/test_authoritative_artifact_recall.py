from brainos.store import BrainOSStore


def test_ssot_canonical_artifact_beats_related_supporting_note_on_source_of_truth_query(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="SSOT: source of truth for BrainOS retrieval quality lives in retrieval-quality-contract-v1.",
        metadata={"kind": "fact", "topic": "retrieval", "authority": "canonical", "source": "manual"},
    )
    store.add_episode(
        session_id="s1",
        content="Supporting note: BrainOS does not claim broad retrieval quality across arbitrary corpora.",
        metadata={"kind": "fact", "topic": "retrieval", "authority": "supporting", "source": "manual"},
    )

    recall = store.recall("what is the source of truth for BrainOS retrieval quality?", session_id="s1", limit=5)
    top = recall["ranked_episodes"][0]

    assert top["content"] == "SSOT: source of truth for BrainOS retrieval quality lives in retrieval-quality-contract-v1."
    assert top["metadata"]["authority"] == "canonical"

    store.close()
