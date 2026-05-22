import json
import subprocess


def test_retrieval_health_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert "status" in payload
    assert "capabilities" in payload
    assert "vector_index" in payload
    assert "benchmark" in payload
    assert "issues" in payload
