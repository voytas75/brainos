from brainos.store import BrainOSStore


def test_continuation_guardrail_protects_current_restart_and_current_direction(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    session_id = "s1"
    fixture = [
        (
            "Current restart point: resume BrainOS by validating restart and continuation retrieval on the current realistic fixture before any further ranking changes.",
            {"kind": "decision", "topic": "restart", "source": "manual", "authority": "canonical"},
        ),
        (
            "Previous restart point: earlier BrainOS work focused on authoritative artifact hygiene for SSOT retrieval; this is no longer the current restart point.",
            {"kind": "decision", "topic": "restart", "source": "manual", "authority": "supporting"},
        ),
        (
            "Current direction: keep BrainOS focused on bounded validation and do not broaden ranking work until a realistic continuation failure survives better artifact shaping.",
            {"kind": "decision", "topic": "direction", "source": "manual", "authority": "canonical"},
        ),
        (
            "Next step: build the richer continuation fixture, run restart/current-direction/next-step queries again, and write a short verdict before touching ranking.",
            {"kind": "procedure", "topic": "continuation", "source": "manual", "authority": "canonical"},
        ),
    ]

    for content, metadata in fixture:
        store.add_episode(session_id=session_id, content=content, metadata=metadata)

    restart = store.recall("what is the current restart point for BrainOS?", session_id=session_id, limit=5)
    restart_top = restart["ranked_episodes"][0]
    assert restart_top["content"].startswith("Current restart point:")
    assert restart_top["metadata"]["authority"] == "canonical"

    direction = store.recall("what front is currently active in BrainOS?", session_id=session_id, limit=5)
    direction_top = direction["ranked_episodes"][0]
    assert direction_top["content"].startswith("Current direction:")
    assert direction_top["metadata"]["authority"] == "canonical"

    store.close()
