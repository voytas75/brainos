from brainos.store import BrainOSStore
from brainos.explain import explain_recall


def test_recall_surfaces_decision_objects(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.log_decision(
        decision_id="dec-1",
        question="Which next slice should we choose for retrieval trust?",
        status="draft",
        recommended_option_id="A",
        options=[
            {"option_id": "A", "label": "Fix retrieval credibility first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ],
        arguments=[
            {"option_id": "A", "kind": "support", "text": "Direct trust impact"}
        ],
        counterarguments=[],
        risks=[],
        missing_information=[{"text": "Need cost estimate"}],
        uncertainty_notes=[{"text": "Medium confidence"}],
        metadata={"entity_id": "brainos"},
    )

    recall = store.recall("retrieval trust", limit=5)
    assert recall["decision_count"] == 1
    assert recall["decisions"][0]["decision_id"] == "dec-1"
    assert "decisions:1" in recall["summary"]
    assert recall["mode"].endswith("plus_decision_text")
    store.close()


def test_explain_surfaces_compact_decisions(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.log_decision(
        decision_id="dec-2",
        question="Should we improve retrieval credibility before UI work?",
        status="active",
        recommended_option_id="A",
        options=[
            {"option_id": "A", "label": "Yes, credibility first"},
            {"option_id": "B", "label": "No, UI first"},
        ],
        arguments=[
            {"option_id": "A", "kind": "support", "text": "UI polish does not fix weak retrieval"}
        ],
        counterarguments=[],
        risks=[],
        missing_information=[],
        uncertainty_notes=[],
        metadata={},
    )

    payload = explain_recall(store, "credibility before UI", limit=5)
    assert "top_decisions" in payload
    assert payload["top_decisions"][0]["decision_id"] == "dec-2"
    assert payload["top_decisions"][0]["recommended_option_id"] == "A"
    assert payload["top_decisions"][0]["operator_call_required"] is True
    store.close()


def test_decision_recall_handles_naturalish_backlog_paraphrase(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.log_decision(
        decision_id="dec-backlog",
        question="What should return to the BrainOS queue after the current usage and review cycle?",
        status="active",
        recommended_option_id="A",
        options=[
            {"option_id": "A", "label": "Calibrate decision-check from real usage before broader feature expansion"},
            {"option_id": "B", "label": "Jump to broader operational objects like entity and focus now"},
            {"option_id": "C", "label": "Add autonomous decision behavior and generated briefs"},
        ],
        arguments=[
            {"option_id": "A", "kind": "support", "text": "Post-usage backlog note explicitly prioritizes decision-check calibration first."},
            {"option_id": "A", "kind": "support", "text": "Decision-layer review says future changes should be driven by observed operator friction, not roadmap excitement."},
        ],
        counterarguments=[
            {"option_id": "B", "kind": "counter", "text": "Broader operational objects are explicitly deferred until repeated operator need appears."},
            {"option_id": "C", "kind": "counter", "text": "Autonomous decision behavior and generated briefs are explicitly deprioritized."},
        ],
        risks=[
            {"option_id": "B", "kind": "risk", "text": "Would widen the operational layer before current decision support is validated enough."},
            {"option_id": "C", "kind": "risk", "text": "Would overclaim the product boundary and damage trustworthiness."},
        ],
        missing_information=[
            {"text": "Need more real usage to decide whether decision-history readability or decision-check calibration should dominate next."},
        ],
        uncertainty_notes=[
            {"text": "Decision-check calibration is clearly first, but the ordering of the next two follow-ups may still depend on real usage friction."},
        ],
        metadata={"entity_id": "brainos", "source_case": "post-usage-backlog-note"},
    )

    recall = store.recall("What should return to the BrainOS queue after usage?", limit=5)
    assert recall["decision_count"] == 1
    assert recall["decisions"][0]["decision_id"] == "dec-backlog"

    explain = explain_recall(store, "broader operational objects", limit=5)
    assert explain["top_decisions"][0]["decision_id"] == "dec-backlog"

    explain_risk = explain_recall(store, "autonomous decision behavior generated briefs", limit=5)
    assert explain_risk["top_decisions"][0]["decision_id"] == "dec-backlog"
    store.close()
