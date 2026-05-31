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


def test_embedding_readiness_cli_exposes_runtime_prereqs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "embedding-readiness"],
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout or proc.stderr)
    assert payload["status"] in {"ok", "warn"}
    assert payload["action_hint"] in {"noop", "fix_embedding_runtime", "runtime_fix"}
    assert payload["profile_contract"]["profile"] == "brainos-embedding-default"
    assert "embedding_config" in payload
    assert "sqlite_vec_env" in payload
    assert payload["sqlite_vec_env"]["source"] in {"explicit_configured", "ambient_detected", "not_configured"}
    assert "dependencies" in payload
    assert "capabilities" in payload
    assert isinstance(payload["issues"], list)


def test_doctor_cli_exposes_compact_operator_checks(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "doctor", "--benchmark-limit", "3"],
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
    assert payload["action_hint"] in {"noop", "fix_failed_checks", "runtime_fix"}
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
