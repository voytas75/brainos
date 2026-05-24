from __future__ import annotations

import os
import sqlite3
from typing import Any

from .errors import SqliteVecReadinessError

ENV_SQLITE_VEC_PATH = "BRAINOS_SQLITE_VEC_PATH"


def configured_sqlite_vec_path() -> str | None:
    value = os.getenv(ENV_SQLITE_VEC_PATH, "").strip()
    return value or None


def load_sqlite_vec_extension(conn: sqlite3.Connection, path: str | None = None) -> str:
    extension_path = path or configured_sqlite_vec_path()
    if not extension_path:
        raise SqliteVecReadinessError(
            f"sqlite-vec path not configured; set {ENV_SQLITE_VEC_PATH}",
            error_kind="path_not_configured",
            detail=f"Set {ENV_SQLITE_VEC_PATH} to a loadable vec0 extension path.",
        )
    conn.enable_load_extension(True)
    try:
        conn.load_extension(extension_path)
    except sqlite3.OperationalError as exc:
        raise SqliteVecReadinessError(
            f"sqlite-vec extension failed to load: {exc}",
            error_kind="extension_load_failed",
            detail=str(exc),
        ) from exc
    return extension_path


def sqlite_vec_readiness(conn: sqlite3.Connection, path: str | None = None) -> dict[str, Any]:
    loaded_path = load_sqlite_vec_extension(conn, path=path)
    try:
        conn.execute("CREATE VIRTUAL TABLE temp.__brainos_vec_ready USING vec0(id INTEGER PRIMARY KEY, embedding FLOAT[3])")
        conn.execute("INSERT INTO temp.__brainos_vec_ready(id, embedding) VALUES (?, ?)", (1, "[0.1,0.2,0.3]"))
        conn.execute("INSERT INTO temp.__brainos_vec_ready(id, embedding) VALUES (?, ?)", (2, "[0.4,0.5,0.6]"))
        rows = conn.execute(
            "SELECT id, distance FROM temp.__brainos_vec_ready WHERE embedding MATCH ? ORDER BY distance LIMIT 2",
            ("[0.1,0.2,0.3]",),
        ).fetchall()
    except sqlite3.Error as exc:
        raise SqliteVecReadinessError(
            f"sqlite-vec readiness probe failed: {exc}",
            error_kind="readiness_probe_failed",
            detail=str(exc),
        ) from exc
    finally:
        try:
            conn.execute("DROP TABLE temp.__brainos_vec_ready")
        except sqlite3.Error:
            pass
    return {
        "ok": True,
        "path": loaded_path,
        "rows": [tuple(r) for r in rows],
        "action_hint": "noop",
    }
