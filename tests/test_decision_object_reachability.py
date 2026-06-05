from brainos.store import BrainOSStore
from brainos.explain import explain_recall


def test_decision_and_procedure_episodes_get_reachability_bonus(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="General note about next work after cleanup.",
        metadata={"kind": "note", "topic": "brainos"},
    )
    store.add_episode(
        session_id="s1",
        content="Decision: after cleanup, the next bounded step is a real-data rerun.",
        metadata={"kind": "decision", "topic": "next-step"},
    )
    store.add_episode(
        session_id="s1",
        content="Procedure: after cleanup run init, rerun the bounded real-data test, then inspect retrieval-explain.",
        metadata={"kind": "procedure", "topic": "next-step"},
    )

    recall = store.recall("What is the next bounded step after cleanup?", session_id="s1", limit=5)
    assert recall["ranked_count"] >= 1
    assert recall["ranked_episodes"][0]["metadata"]["kind"] in {"decision", "procedure"}

    explain = explain_recall(store, "What is the next bounded step after cleanup?", session_id="s1", limit=5)
    assert explain["top_ranked_episodes"]
    assert explain["top_ranked_episodes"][0]["metadata"]["kind"] in {"decision", "procedure"}
    assert "kind=" in explain["operator_summary"]


def test_structured_decision_object_still_reachable_from_natural_query(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.log_decision(
        decision_id="dec-next",
        question="Which bounded next step should happen after the cleanup?",
        status="active",
        recommended_option_id="A",
        options=[{"option_id": "A", "label": "Run the real-data rerun"}],
        arguments=[{"option_id": "A", "kind": "support", "text": "This is the bounded next step after cleanup."}],
        counterarguments=[],
        risks=[],
        missing_information=[],
        uncertainty_notes=[],
        metadata={"entity_id": "brainos", "source_case": "reachability"},
    )

    recall = store.recall("What should we do next after the cleanup?", limit=5)
    assert recall["decision_count"] == 1
    assert recall["decisions"][0]["decision_id"] == "dec-next"

    explain = explain_recall(store, "What should we do next after the cleanup?", limit=5)
    assert explain["top_decisions"][0]["decision_id"] == "dec-next"
