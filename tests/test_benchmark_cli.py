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
    assert payload["case_count"] == 3
    assert "results" in payload
    assert len(payload["results"]) == 3
