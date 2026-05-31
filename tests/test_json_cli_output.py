import json
import os
import subprocess
from pathlib import Path


_ENV_KEYS = {
    "BRAINOS_EMBEDDING_MODEL",
    "AZURE_API_BASE",
    "AZURE_API_KEY",
    "AZURE_API_VERSION",
    "BRAINOS_SQLITE_VEC_PATH",
}


def _clean_cli_env() -> dict[str, str]:
    prefixes = ("AZURE_", "AZURE_OPENAI_", "OPENAI_", "LITELLM_")
    return {
        key: value
        for key, value in os.environ.items()
        if key not in _ENV_KEYS and not any(key.startswith(prefix) for prefix in prefixes)
    }


def _brainos_cli() -> str:
    return os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")


def _test_env() -> dict[str, str]:
    return {
        **_clean_cli_env(),
        "PATH": os.environ.get("PATH", ""),
        "BRAINOS_EMBEDDING_MODEL": "azure/test-embed",
        "AZURE_API_BASE": "https://example.openai.azure.com",
        "AZURE_API_KEY": "test-key",
        "AZURE_API_VERSION": "2024-10-21",
    }


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    if start == -1:
        raise AssertionError(f"No JSON object in stdout: {stdout!r}")
    return json.loads(stdout[start:])


def test_doctor_cli_keeps_json_output_when_embedding_auth_fails(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "doctor", "--benchmark-limit", "2"],
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout or proc.stderr)
    if "status" not in payload:
        assert payload["error_kind"] == "extension_load_failed"
        assert payload["action_hint"] == "runtime_fix"
        return
    assert payload["status"] in {"ok", "warn"}
    failed = payload["retrieval_health"]["quality"]["benchmark"]["failed_cases"]
    assert isinstance(failed, list)
    assert payload["retrieval_health"]["quality"]["benchmark"]["runtime_error"] is None or isinstance(
        payload["retrieval_health"]["quality"]["benchmark"]["runtime_error"], str
    )
