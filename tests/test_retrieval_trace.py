from brainos.explain import explain_recall
from brainos.store import BrainOSStore


def test_explain_retrieval_trace_exposes_candidate_and_ranking_state(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    store.add_episode(
        session_id="s1",
        content="SQLite WAL mode helps BrainOS keep local writes safe and concurrent.",
        metadata={"kind": "storage"},
    )

    payload = explain_recall(store, "local writes safe", session_id="s1", limit=5)

    trace = payload["retrieval_trace"]
    assert trace["query"] == "local writes safe"
    assert trace["session_id"] == "s1"
    assert "candidate_generation" in trace
    assert trace["candidate_generation"]["episodes_text_count"] >= 0
    assert "ranking" in trace
    assert trace["ranking"]["ranked_episode_count"] >= 1
    assert trace["ranking"]["top_episode_id"] is not None
    assert "result_interpretation" in trace
    assert trace["result_interpretation"]["summary"] is not None
