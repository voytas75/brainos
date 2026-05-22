from __future__ import annotations

import os
import sqlite3
from typing import Any

ENV_SQLITE_VEC_PATH = "BRAINOS_SQLITE_VEC_PATH"


def configured_sqlite_vec_path() -> str | None:
    value = os.getenv(ENV_SQLITE_VEC_PATH, "").strip()
    return value or None


def load_sqlite_vec_extension(conn: sqlite3.Connection, path: str | None = None) -> str:
    extension_path = path or configured_sqlite_vec_path()
    if not extension_path:
        raise sqlite3.OperationalError(
            f"sqlite-vec path not configured; set {ENV_SQLITE_VEC_PATH}"
        )
    conn.enable_load_extension(True)
    conn.load_extension(extension_path)
    return extension_path


def sqlite_vec_readiness(conn: sqlite3.Connection, path: str | None = None) -> dict[str, Any]:
    loaded_path = load_sqlite_vec_extension(conn, path=path)
    conn.execute("CREATE VIRTUAL TABLE temp.__brainos_vec_ready USING vec0(id INTEGER PRIMARY KEY, embedding FLOAT[3])")
    conn.execute("INSERT INTO temp.__brainos_vec_ready(id, embedding) VALUES (?, ?)", (1, "[0.1,0.2,0.3]"))
    conn.execute("INSERT INTO temp.__brainos_vec_ready(id, embedding) VALUES (?, ?)", (2, "[0.4,0.5,0.6]"))
    rows = conn.execute(
        "SELECT id, distance FROM temp.__brainos_vec_ready WHERE embedding MATCH ? ORDER BY distance LIMIT 2",
        ("[0.1,0.2,0.3]",),
    ).fetchall()
    conn.execute("DROP TABLE temp.__brainos_vec_ready")
    return {
        "ok": True,
        "path": loaded_path,
        "rows": [tuple(r) for r in rows],
    }
