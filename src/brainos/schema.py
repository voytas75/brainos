from __future__ import annotations

import sqlite3
from typing import Any

from .sqlite_vec import configured_sqlite_vec_path, load_sqlite_vec_extension

SCHEMA_VERSION = 3

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS wm (
    key TEXT PRIMARY KEY,
    value TEXT CHECK(json_valid(value)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    metadata TEXT CHECK(json_valid(metadata))
);

CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
    content,
    content_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS semantic_nodes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    properties TEXT CHECK(json_valid(properties))
);

CREATE TABLE IF NOT EXISTS semantic_edges (
    source_id TEXT,
    target_id TEXT,
    predicate TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (source_id, target_id, predicate),
    FOREIGN KEY (source_id) REFERENCES semantic_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES semantic_nodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS procedures (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    steps_json TEXT CHECK(json_valid(steps_json)),
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ledger (
    event_id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    layer TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT CHECK(json_valid(payload)),
    causal_event_id TEXT,
    previous_hash TEXT,
    crypto_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episode_promotions (
    episode_id TEXT PRIMARY KEY,
    target_layer TEXT NOT NULL,
    target_id TEXT NOT NULL,
    status TEXT NOT NULL,
    promoted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ledger_event_id TEXT,
    FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vector_index_state (
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    source_text_hash TEXT NOT NULL,
    source_text_preview TEXT,
    embedding_profile TEXT NOT NULL,
    embedding_provider TEXT,
    embedding_model TEXT,
    embedding_dimensions INTEGER,
    vector_status TEXT NOT NULL,
    last_embedded_at TIMESTAMP,
    last_error TEXT,
    last_error_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (object_type, object_id)
);

CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON semantic_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp);
CREATE INDEX IF NOT EXISTS idx_episode_promotions_target ON episode_promotions(target_layer, target_id);
CREATE INDEX IF NOT EXISTS idx_vector_index_status ON vector_index_state(vector_status, object_type);
"""

def get_vec_table_sql(dimensions: int) -> str:
    return f"""
CREATE VIRTUAL TABLE IF NOT EXISTS episodes_vec USING vec0(
    id TEXT PRIMARY KEY,
    embedding FLOAT[{int(dimensions)}]
);
"""


def get_schema_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("PRAGMA user_version;").fetchone()
    return 0 if row is None else int(row[0])


def set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(f"PRAGMA user_version={int(version)};")


def detect_capabilities(conn: sqlite3.Connection) -> dict[str, Any]:
    fts5_available = True
    vec_available = True
    vec_error = None
    vec_path = configured_sqlite_vec_path()
    vec_loaded = False

    try:
        conn.execute("CREATE VIRTUAL TABLE temp.__brainos_fts_probe USING fts5(content);")
        conn.execute("DROP TABLE temp.__brainos_fts_probe;")
    except sqlite3.Error:
        fts5_available = False

    try:
        if vec_path:
            load_sqlite_vec_extension(conn, vec_path)
            vec_loaded = True
        conn.execute(get_vec_table_sql(1536).replace("episodes_vec", "temp.__brainos_vec_probe"))
        conn.execute("DROP TABLE temp.__brainos_vec_probe;")
    except sqlite3.Error as exc:
        vec_available = False
        vec_error = str(exc)

    return {
        "fts5": fts5_available,
        "sqlite_vec": vec_available,
        "sqlite_vec_error": vec_error,
        "sqlite_vec_path": vec_path,
        "sqlite_vec_loaded": vec_loaded,
    }


def run_migrations(conn: sqlite3.Connection, current_version: int) -> int:
    version = current_version

    if version < 2:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS episode_promotions (
                episode_id TEXT PRIMARY KEY,
                target_layer TEXT NOT NULL,
                target_id TEXT NOT NULL,
                status TEXT NOT NULL,
                promoted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ledger_event_id TEXT,
                FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_episode_promotions_target ON episode_promotions(target_layer, target_id);
            """
        )
        version = 2

    if version < 3:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS vector_index_state (
                object_type TEXT NOT NULL,
                object_id TEXT NOT NULL,
                source_text_hash TEXT NOT NULL,
                source_text_preview TEXT,
                embedding_profile TEXT NOT NULL,
                embedding_provider TEXT,
                embedding_model TEXT,
                embedding_dimensions INTEGER,
                vector_status TEXT NOT NULL,
                last_embedded_at TIMESTAMP,
                last_error TEXT,
                last_error_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (object_type, object_id)
            );
            CREATE INDEX IF NOT EXISTS idx_vector_index_status ON vector_index_state(vector_status, object_type);
            """
        )
        version = 3

    return version


def initialize_schema(conn: sqlite3.Connection, *, enable_vector: bool = False) -> None:
    current_version = get_schema_version(conn)
    conn.executescript(SCHEMA_SQL)
    migrated_version = run_migrations(conn, current_version)
    if enable_vector:
        vec_path = configured_sqlite_vec_path()
        if vec_path:
            load_sqlite_vec_extension(conn, vec_path)
        conn.execute(get_vec_table_sql(1536))
    if current_version == 0:
        set_schema_version(conn, SCHEMA_VERSION)
    elif migrated_version != current_version:
        set_schema_version(conn, migrated_version)
    conn.commit()


def get_schema_status(conn: sqlite3.Connection) -> dict[str, int | bool]:
    current = get_schema_version(conn)
    return {
        "current_version": current,
        "expected_version": SCHEMA_VERSION,
        "is_initialized": current > 0,
        "is_current": current == SCHEMA_VERSION,
    }
