import json
import subprocess
import sys


def run_cli(tmp_path, *args):
    db = tmp_path / "brain.db"
    cmd = [sys.executable, "-m", "brainos.cli", "--db", str(db), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_inspect_decision_returns_record_and_related_ledger_events(tmp_path):
    create = run_cli(
        tmp_path,
        "decision-log",
        "Which next slice should we choose?",
        "--decision-id",
        "dec-inspect",
        "--recommended-option-id",
        "A",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Fix retrieval first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ]),
        "--metadata-json",
        json.dumps({"entity_id": "brainos"}),
    )
    assert create.returncode == 0, create.stderr

    inspect = run_cli(tmp_path, "inspect", "decision", "dec-inspect")
    assert inspect.returncode == 0, inspect.stderr
    payload = json.loads(inspect.stdout)
    assert payload["object_type"] == "decision"
    assert payload["object_id"] == "dec-inspect"
    assert payload["record"]["question"] == "Which next slice should we choose?"
    assert payload["record"]["metadata"]["entity_id"] == "brainos"
    assert len(payload["related_ledger_events"]) == 1
    assert payload["related_ledger_events"][0]["layer"] == "decision"
    assert payload["related_ledger_events"][0]["payload"]["decision_id"] == "dec-inspect"


def test_inspect_episode_returns_record_and_related_refs(tmp_path):
    add = run_cli(
        tmp_path,
        "episode-add",
        "s1",
        "BrainOS learned a useful retrieval lesson.",
        "--metadata-json",
        json.dumps({"kind": "lesson"}),
    )
    assert add.returncode == 0, add.stderr
    episode_id = add.stdout.strip()

    inspect = run_cli(tmp_path, "inspect", "episode", episode_id)
    assert inspect.returncode == 0, inspect.stderr
    payload = json.loads(inspect.stdout)
    assert payload["object_type"] == "episode"
    assert payload["object_id"] == episode_id
    assert payload["record"]["content"] == "BrainOS learned a useful retrieval lesson."
    assert payload["record"]["metadata"]["kind"] == "lesson"
    assert len(payload["related_ledger_events"]) == 1
    assert payload["related_ledger_events"][0]["layer"] == "episodic"
    assert payload["related_ledger_events"][0]["payload"]["id"] == episode_id
    assert "vector_state" in payload["related_refs"]


def test_inspect_rejects_unknown_object_type(tmp_path):
    result = run_cli(tmp_path, "inspect", "decision", "missing-id")
    assert result.returncode == 2
    assert "decision not found: missing-id" in result.stderr
