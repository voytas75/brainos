import sqlite3

from brainos.schema import detect_capabilities
from brainos.sqlite_vec import ENV_SQLITE_VEC_PATH, configured_sqlite_vec_path, sqlite_vec_readiness


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
    finally:
        conn.close()
