import json
import subprocess


def test_retrieval_benchmark_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["suite"] == "retrieval-benchmark-v0"
    assert payload["evidence_kind"] == "seeded_fixture"
    assert "truthfulness_note" in payload
    assert payload["mode"] in {"vector-ready", "degraded-non-vector"}
    assert "degraded" in payload
    assert "degraded_reason" in payload
    assert payload["case_count"] == 10
    assert "results" in payload
    assert len(payload["results"]) == 10


def test_retrieval_benchmark_cli_exposes_failed_case_drilldown(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert "failed_cases" in payload
    assert isinstance(payload["failed_cases"], list)


def test_retrieval_benchmark_failed_cases_expose_next_debug_handoff(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert "failed_cases" in payload
    for item in payload["failed_cases"]:
        assert item["next_debug"]["tool"] == "retrieval-explain"
        assert item["next_debug"]["query"] == item["query"]
        assert item["next_debug"]["session_id"] == "bench"
