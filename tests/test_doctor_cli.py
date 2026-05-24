import json
import os
import subprocess


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    if start == -1:
        raise AssertionError(f"No JSON object in stdout: {stdout!r}")
    return json.loads(stdout[start:])


TEST_ENV = {
    **os.environ,
    "BRAINOS_EMBEDDING_MODEL": "azure/test-embed",
    "AZURE_API_BASE": "https://example.openai.azure.com",
    "AZURE_API_KEY": "test-key",
    "AZURE_API_VERSION": "2024-10-21",
}


def test_embedding_readiness_cli_exposes_runtime_prereqs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "embedding-readiness"],
        capture_output=True,
        text=True,
        check=True,
        env=TEST_ENV,
    )
    payload = _extract_json(proc.stdout)
    assert payload["status"] in {"ok", "warn"}
    assert payload["action_hint"] in {"noop", "fix_embedding_runtime"}
    assert payload["profile_contract"]["profile"] == "brainos-embedding-default"
    assert "embedding_config" in payload
    assert "sqlite_vec_env" in payload
    assert "dependencies" in payload
    assert "capabilities" in payload
    assert isinstance(payload["issues"], list)


def test_doctor_cli_exposes_compact_operator_checks(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "doctor", "--benchmark-limit", "3"],
        capture_output=True,
        text=True,
        check=True,
        env=TEST_ENV,
    )
    payload = _extract_json(proc.stdout)
    assert payload["status"] in {"ok", "warn"}
    assert payload["action_hint"] in {"noop", "fix_failed_checks"}
    assert "checks" in payload
    assert "failed_checks" in payload
    assert "embedding" in payload
    assert "retrieval_health" in payload
    assert set(payload["checks"].keys()) == {
        "retrieval_health",
        "embedding_runtime",
        "sqlite_vec_capability",
        "sqlite_wal",
        "dependencies",
    }
