import json
import subprocess
import sys

from brainos.store import BrainOSStore


def run_cli(tmp_path, *args):
    db = tmp_path / "brain.db"
    cmd = [sys.executable, "-m", "brainos.cli", "--db", str(db), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_decision_log_get_and_list(tmp_path):
    create = run_cli(
        tmp_path,
        "decision-log",
        "Which next slice should we choose?",
        "--decision-id",
        "dec-1",
        "--status",
        "draft",
        "--recommended-option-id",
        "A",
        "--options-json",
        json.dumps(
            [
                {"option_id": "A", "label": "Fix retrieval credibility first", "summary": "Smallest reversible trust fix"},
                {"option_id": "B", "label": "Build dashboard first"},
            ]
        ),
        "--arguments-json",
        json.dumps([
            {"option_id": "A", "kind": "support", "text": "Matches the time constraint", "evidence_refs": []}
        ]),
        "--counterarguments-json",
        json.dumps([
            {"option_id": "A", "kind": "counter", "text": "Does not improve UI immediately"}
        ]),
        "--risks-json",
        json.dumps([
            {"option_id": "B", "kind": "risk", "text": "Could polish the wrong layer first"}
        ]),
        "--missing-information-json",
        json.dumps([
            {"text": "Need clearer expected impact estimate for each option"}
        ]),
        "--uncertainty-notes-json",
        json.dumps([
            {"text": "Ranking confidence is medium because options are semantically close"}
        ]),
        "--metadata-json",
        json.dumps({"entity_id": "brainos"}),
    )
    assert create.returncode == 0, create.stderr
    created = json.loads(create.stdout)
    assert created["decision_id"] == "dec-1"
    assert created["question"] == "Which next slice should we choose?"
    assert created["recommended_option_id"] == "A"
    assert created["operator_call_required"] is True
    assert len(created["options"]) == 2

    fetched = run_cli(tmp_path, "decision-get", "dec-1")
    assert fetched.returncode == 0, fetched.stderr
    got = json.loads(fetched.stdout)
    assert got["decision_id"] == "dec-1"
    assert got["arguments"][0]["option_id"] == "A"
    assert got["metadata"]["entity_id"] == "brainos"

    listed = run_cli(tmp_path, "decision-list")
    assert listed.returncode == 0, listed.stderr
    items = json.loads(listed.stdout)
    assert len(items) == 1
    assert items[0]["decision_id"] == "dec-1"
    assert items[0]["operator_call_required"] is True
    assert items[0]["recommended_option_id"] == "A"


def test_decision_log_rejects_unknown_recommended_option(tmp_path):
    result = run_cli(
        tmp_path,
        "decision-log",
        "Which option?",
        "--recommended-option-id",
        "Z",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Option A"}
        ]),
    )
    assert result.returncode == 2
    assert "recommended_option_id must match one declared option_id" in result.stderr


def test_decision_log_rejects_invalid_json(tmp_path):
    result = run_cli(
        tmp_path,
        "decision-log",
        "Which option?",
        "--options-json",
        "not-json",
    )
    assert result.returncode == 2
    assert 'Expecting value' in result.stderr


def test_decision_log_defaults_operator_boundary_and_writes_ledger(tmp_path):
    result = run_cli(
        tmp_path,
        "decision-log",
        "Which option?",
        "--decision-id",
        "dec-ledger",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Option A"}
        ]),
    )
    assert result.returncode == 0, result.stderr
    created = json.loads(result.stdout)
    assert created["operator_call_required"] is True

    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()
    ledger = store.list_ledger()
    decision_events = [entry for entry in ledger if entry["layer"] == "decision"]
    assert len(decision_events) == 1
    payload = json.loads(decision_events[0]["payload"])
    assert payload["decision_id"] == "dec-ledger"
    assert payload["operator_call_required"] is True
    store.close()


def test_decision_log_update_keeps_identity(tmp_path):
    first = run_cli(
        tmp_path,
        "decision-log",
        "Which option?",
        "--decision-id",
        "dec-keep",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Option A"}
        ]),
    )
    assert first.returncode == 0, first.stderr

    second = run_cli(
        tmp_path,
        "decision-log",
        "Which option now?",
        "--decision-id",
        "dec-keep",
        "--status",
        "active",
        "--recommended-option-id",
        "A",
        "--operator-call-required",
        "false",
        "--options-json",
        json.dumps([
            {"option_id": "A", "label": "Option A"}
        ]),
    )
    assert second.returncode == 0, second.stderr
    updated = json.loads(second.stdout)
    assert updated["decision_id"] == "dec-keep"
    assert updated["question"] == "Which option now?"
    assert updated["status"] == "active"
    assert updated["operator_call_required"] is False
