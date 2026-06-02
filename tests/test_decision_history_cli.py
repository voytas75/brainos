import json
import subprocess
import sys


def run_cli(tmp_path, *args):
    db = tmp_path / "brain.db"
    cmd = [sys.executable, "-m", "brainos.cli", "--db", str(db), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_decision_history_shows_previous_snapshot_and_changed_fields(tmp_path):
    first = run_cli(
        tmp_path,
        "decision-log",
        "Which next slice should we choose?",
        "--decision-id",
        "dec-hist",
        "--status",
        "draft",
        "--recommended-option-id",
        "A",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Fix retrieval first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ]),
        "--arguments-json",
        json.dumps([
            {"option_id": "A", "kind": "support", "text": "Trust impact first"}
        ]),
    )
    assert first.returncode == 0, first.stderr

    second = run_cli(
        tmp_path,
        "decision-log",
        "Which next slice should we choose now?",
        "--decision-id",
        "dec-hist",
        "--status",
        "active",
        "--recommended-option-id",
        "B",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Fix retrieval first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ]),
        "--arguments-json",
        json.dumps([
            {"option_id": "B", "kind": "support", "text": "Need visible operator feedback sooner"}
        ]),
        "--review-after",
        "2026-06-09T09:00:00Z",
    )
    assert second.returncode == 0, second.stderr

    history = run_cli(tmp_path, "decision-history", "dec-hist")
    assert history.returncode == 0, history.stderr
    payload = json.loads(history.stdout)
    assert payload["decision_id"] == "dec-hist"
    assert payload["revision_count"] == 2
    assert payload["current"]["recommended_option_id"] == "B"
    assert payload["previous"]["recommended_option_id"] == "A"
    assert "question" in payload["changed_fields"]
    assert "status" in payload["changed_fields"]
    assert "recommended_option_id" in payload["changed_fields"]
    assert "arguments" in payload["changed_fields"]
    assert payload["revisions"][0]["action"] == "CREATE"
    assert payload["revisions"][1]["action"] == "UPDATE"


def test_decision_history_single_revision_has_no_previous_snapshot(tmp_path):
    created = run_cli(
        tmp_path,
        "decision-log",
        "Should we keep current direction?",
        "--decision-id",
        "dec-single",
        "--recommended-option-id",
        "A",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Keep direction"}
        ]),
    )
    assert created.returncode == 0, created.stderr

    history = run_cli(tmp_path, "decision-history", "dec-single")
    assert history.returncode == 0, history.stderr
    payload = json.loads(history.stdout)
    assert payload["revision_count"] == 1
    assert payload["previous"] is None
    assert payload["changed_fields"] == []
