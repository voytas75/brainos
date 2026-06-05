from __future__ import annotations

import sqlite3
from typing import Any

from .sqlite_vec import ENV_SQLITE_VEC_PATH, configured_sqlite_vec_path, load_sqlite_vec_extension


def vector_runtime_preflight() -> dict[str, Any]:
    path = configured_sqlite_vec_path()
    if not path:
        return {
            "status": "misconfigured",
            "ok": False,
            "degraded": True,
            "action_hint": "configure_sqlite_vec_path",
            "target": ENV_SQLITE_VEC_PATH,
            "message": f"vector runtime unavailable: {ENV_SQLITE_VEC_PATH} is not configured",
            "detail": f"Set {ENV_SQLITE_VEC_PATH} to a loadable vec0 extension path.",
        }

    conn = sqlite3.connect(":memory:")
    try:
        try:
            loaded_path = load_sqlite_vec_extension(conn, path)
        except Exception as exc:
            return {
                "status": "runtime_failed",
                "ok": False,
                "degraded": True,
                "action_hint": "configure_sqlite_vec_path",
                "target": ENV_SQLITE_VEC_PATH,
                "message": "vector runtime unavailable: sqlite-vec extension failed to load",
                "detail": str(exc),
                "path": path,
            }
        return {
            "status": "ok",
            "ok": True,
            "degraded": False,
            "action_hint": "noop",
            "target": ENV_SQLITE_VEC_PATH,
            "message": "vector runtime ready",
            "detail": None,
            "path": loaded_path,
        }
    finally:
        conn.close()
