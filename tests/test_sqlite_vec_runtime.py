import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

from brainos.errors import SqliteVecReadinessError
from brainos.schema import detect_capabilities
from brainos.sqlite_vec import (
    ENV_SQLITE_VEC_PATH,
    configured_sqlite_vec_path,
    sqlite_vec_readiness,
)
from brainos.store import BrainOSStore


def _real_vec_path_or_skip() -> str:
    vec_path = configured_sqlite_vec_path()
    if not vec_path or not Path(vec_path).is_file():
        pytest.skip(
            "requires BRAINOS_SQLITE_VEC_PATH pointing to a real vec0 extension"
        )
    assert vec_path is not None
    return vec_path


def _clean_cli_env() -> dict[str, str]:
    prefixes = ("AZURE_", "AZURE_OPENAI_", "OPENAI_", "LITELLM_")
    return {
        key: value
        for key, value in os.environ.items()
        if key != ENV_SQLITE_VEC_PATH
        and not any(key.startswith(prefix) for prefix in prefixes)
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
    assert caps["sqlite_vec_runtime_origin"] == "disabled_without_explicit_path"
    assert (
        caps["sqlite_vec_error"]
        == f"{ENV_SQLITE_VEC_PATH} not configured; ambient sqlite-vec probe disabled"
    )


def test_sqlite_vec_readiness_with_real_extension(monkeypatch):
    vec_path = _real_vec_path_or_skip()
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


def test_store_vector_searches_with_real_extension_and_mock_embedding(
    monkeypatch, tmp_path
):
    vec_path = _real_vec_path_or_skip()
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, vec_path)
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()
    episode_id = store.add_episode(
        session_id="s1", content="Vector episode", metadata={}
    )
    store.upsert_semantic_node(
        node_id="node-1", name="Vector node", node_type="Concept", properties={}
    )
    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.1, 0.2, 0.3] for _ in texts],
            "dimensions": 3,
            "provider": "mock",
            "model": "mock/embedding",
            "profile": profile or "brainos-embedding-default",
            "requested_count": len(texts),
            "returned_count": len(texts),
        },
    )

    episode_sync = store.generate_episode_embedding(episode_id)
    node_sync = store.generate_semantic_node_embedding("node-1")
    episode_hits = store.vector_search_episodes([0.1, 0.2, 0.3], session_id="s1")
    node_hits = store.vector_search_semantic_nodes([0.1, 0.2, 0.3])

    assert episode_sync["storage"] == "sqlite-vec"
    assert node_sync["storage"] == "sqlite-vec"
    assert episode_hits[0]["id"] == episode_id
    assert node_hits[0]["id"] == "node-1"
    store.close()


def test_sqlite_vec_readiness_classifies_missing_path(monkeypatch):
    monkeypatch.delenv(ENV_SQLITE_VEC_PATH, raising=False)
    conn = sqlite3.connect(":memory:")
    try:
        try:
            sqlite_vec_readiness(conn)
            raise AssertionError("expected readiness classification error")
        except SqliteVecReadinessError as exc:
            assert exc.error_kind == "path_not_configured"
            assert ENV_SQLITE_VEC_PATH in str(exc)
    finally:
        conn.close()


def test_sqlite_vec_readiness_cli_returns_json_payload(tmp_path, monkeypatch):
    monkeypatch.delenv(ENV_SQLITE_VEC_PATH, raising=False)
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [
            os.fspath(
                Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"
            ),
            "--db",
            str(db),
            "sqlite-vec-readiness",
        ],
        capture_output=True,
        text=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
        check=False,
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
            assert payload["error_kind"] in {
                "path_not_configured",
                "extension_load_failed",
                "readiness_probe_failed",
            }
            assert payload["action_hint"] in {"runtime_fix", "retry_or_runtime_fix"}


def test_detect_capabilities_reports_explicit_probe_mode_when_vec_path_configured(
    monkeypatch,
):
    vec_path = _real_vec_path_or_skip()
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, vec_path)
    conn = sqlite3.connect(":memory:")
    try:
        caps = detect_capabilities(conn)
    finally:
        conn.close()
    assert caps["sqlite_vec_path"] == vec_path
    assert caps["sqlite_vec_runtime_origin"] == "explicit_path"
