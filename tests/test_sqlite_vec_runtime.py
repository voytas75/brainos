import json
import os
import sqlite3
import subprocess
from pathlib import Path

from brainos.errors import SqliteVecReadinessError
from brainos.schema import detect_capabilities
from brainos.sqlite_vec import ENV_SQLITE_VEC_PATH, configured_sqlite_vec_path, sqlite_vec_readiness


def _clean_cli_env() -> dict[str, str]:
    prefixes = ("AZURE_", "AZURE_OPENAI_", "OPENAI_", "LITELLM_")
    return {
        key: value
        for key, value in os.environ.items()
        if key != ENV_SQLITE_VEC_PATH and not any(key.startswith(prefix) for prefix in prefixes)
    }


def test_configured_sqlite_vec_path_from_env(monkeypatch):
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, "/tmp/vec0.so")
    assert configured_sqlite_vec_path() == "/tmp/vec0.so"


def test_detect_capabilities_reports_missing_vec_path(monkeypatch):
    monkeypatch.delenv(ENV_SQLITE_VEC_PATH, raising=False)
    conn = sqlite3.connect(":memory:")
    try:
        caps = detect_capabilities(conn)
    finally:
        conn.close()
    assert caps["fts5"] is True
    assert caps["sqlite_vec"] is False
    assert caps["sqlite_vec_path"] is None


def test_sqlite_vec_readiness_with_real_extension(monkeypatch):
    vec_path = "/home/voytas/.bun/install/cache/sqlite-vec-linux-x64@0.1.7-dd4d9ab07e99b7ce@@@1/vec0.so"
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, vec_path)
    conn = sqlite3.connect(":memory:")
    try:
        caps = detect_capabilities(conn)
        assert caps["sqlite_vec"] is True
        assert caps["sqlite_vec_loaded"] is True
        assert caps["sqlite_vec_path"] == vec_path

        ready = sqlite_vec_readiness(conn)
        assert ready["ok"] is True
        assert ready["path"] == vec_path
        assert ready["rows"][0][0] == 1
        assert ready["rows"][0][1] == 0.0
        assert ready["action_hint"] == "noop"
    finally:
        conn.close()


def test_sqlite_vec_readiness_classifies_missing_path(monkeypatch):
    monkeypatch.delenv(ENV_SQLITE_VEC_PATH, raising=False)
    conn = sqlite3.connect(":memory:")
    try:
        try:
            sqlite_vec_readiness(conn)
            assert False, "expected readiness classification error"
        except SqliteVecReadinessError as exc:
            assert exc.error_kind == "path_not_configured"
            assert ENV_SQLITE_VEC_PATH in str(exc)
    finally:
        conn.close()


def test_sqlite_vec_readiness_cli_returns_json_payload(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_SQLITE_VEC_PATH, raising=False)
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"), "--db", str(db), "sqlite-vec-readiness"],
        capture_output=True,
        text=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    payload_text = proc.stderr if proc.stderr.strip() else proc.stdout
    payload = json.loads(payload_text)
    assert isinstance(payload, dict)
    assert "action_hint" in payload
    if proc.returncode == 2:
        assert payload["ok"] is False
        assert payload["error_kind"] in {"path_not_configured", "extension_load_failed"}
        assert "detail" in payload
        assert payload["action_hint"] == "runtime_fix"
        if payload["error_kind"] == "path_not_configured":
            assert ENV_SQLITE_VEC_PATH in payload["error"]
    else:
        assert proc.returncode == 0
        if payload["ok"] is True:
            assert payload["action_hint"] == "noop"
        else:
            assert payload["status"] == "warn"
            assert payload["error_kind"] in {"path_not_configured", "extension_load_failed", "readiness_probe_failed"}
            assert payload["action_hint"] in {"runtime_fix", "retry_or_runtime_fix"}


def test_detect_capabilities_reports_explicit_probe_mode_when_vec_path_configured(monkeypatch):
    vec_path = "/home/voytas/.bun/install/cache/sqlite-vec-linux-x64@0.1.7-dd4d9ab07e99b7ce@@@1/vec0.so"
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, vec_path)
    conn = sqlite3.connect(":memory:")
    try:
        caps = detect_capabilities(conn)
    finally:
        conn.close()
    assert caps["sqlite_vec_path"] == vec_path
    assert caps["sqlite_vec_probe_mode"] == "explicit_path"
