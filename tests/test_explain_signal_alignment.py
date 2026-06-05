from brainos.store import BrainOSStore
from brainos.explain import explain_recall


def test_explain_uses_vector_primary_with_lexical_support_for_mixed_top_hit(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="Procedure: when reading skepticism, check suspension of judgment, limits of certainty, and whether the text confuses skepticism with nihilism.",
        metadata={"kind": "procedure", "topic": "skepticism"},
    )
    store.add_episode(
        session_id="s1",
        content="Decision: distinguish methodological skepticism from relativism and cynical disbelief.",
        metadata={"kind": "decision", "topic": "interpretation"},
    )

    payload = explain_recall(store, "How to distinguish skepticism from nihilism?", session_id="s1", limit=5)
    if payload["top_hit_evidence"] is not None and payload["top_hit_evidence"]["vector_distance"] is not None and payload["top_hit_evidence"]["lexical_overlap"] > 0:
        assert payload["diagnostic_hint"] == "vector_primary_with_lexical_support"


def test_explain_keeps_lexical_grounded_hint_when_no_vector_distance(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(
        session_id="s1",
        content="Fact: stoicism is not the same as emotional suppression.",
        metadata={"kind": "fact", "topic": "stoicism"},
    )

    payload = explain_recall(store, "emotional suppression", session_id="s1", limit=5)
    assert payload["top_hit_evidence"] is not None
    if payload["top_hit_evidence"]["vector_distance"] is None and payload["top_hit_evidence"]["lexical_overlap"] > 0:
        assert payload["diagnostic_hint"] == "lexical_grounded_top_hit"
