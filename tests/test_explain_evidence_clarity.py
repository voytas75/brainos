from brainos.store import BrainOSStore
from brainos.explain import explain_recall


def test_explain_exposes_top_hit_evidence_and_comparison_hint(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="Decision: the next bounded step is to rerun the real-data check.",
        metadata={"kind": "decision", "topic": "next-step"},
    )
    store.add_episode(
        session_id="s1",
        content="Procedure: rerun the real-data check after cleanup and inspect explain output.",
        metadata={"kind": "procedure", "topic": "next-step"},
    )
    store.add_episode(
        session_id="s1",
        content="Note: next bounded step discussions should stay operational and explicit.",
        metadata={"kind": "note", "topic": "next-step"},
    )

    payload = explain_recall(store, "What is the next bounded step?", session_id="s1", limit=5)
    assert payload["top_hit_evidence"] is not None
    assert payload["top_hit_evidence"]["kind"] in {"decision", "procedure"}
    assert isinstance(payload["top_hit_evidence"]["match_sources"], list)
    assert "score_components" in payload["top_hit_evidence"]
    assert payload["comparison_hint"] is not None
    assert "score_gap" in payload["comparison_hint"]


def test_explain_comparison_hint_absent_when_only_one_ranked_hit(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="Fact: BrainOS should keep explain output operator-readable.",
        metadata={"kind": "fact", "topic": "explain"},
    )

    payload = explain_recall(store, "operator-readable explain", session_id="s1", limit=5)
    assert payload["top_hit_evidence"] is not None
    assert payload["comparison_hint"] is None
