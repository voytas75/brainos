import json
import os
import subprocess


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    if start == -1:
        raise AssertionError(f"No JSON object in stdout: {stdout!r}")
    return json.loads(stdout[start:])


def test_doctor_cli_keeps_json_output_when_embedding_auth_fails(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "doctor", "--benchmark-limit", "2"],
        capture_output=True,
        text=True,
        check=True,
        env={
            **os.environ,
            "BRAINOS_EMBEDDING_MODEL": "azure/test-embed",
            "AZURE_API_BASE": "https://example.openai.azure.com",
            "AZURE_API_KEY": "test-key",
            "AZURE_API_VERSION": "2024-10-21",
        },
    )
    payload = _extract_json(proc.stdout)
    assert payload["status"] in {"ok", "warn"}
    failed = payload["retrieval_health"]["quality"]["benchmark"]["failed_cases"]
    assert isinstance(failed, list)
    assert payload["retrieval_health"]["quality"]["benchmark"]["runtime_error"] is None or isinstance(
        payload["retrieval_health"]["quality"]["benchmark"]["runtime_error"], str
    )
