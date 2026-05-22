from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1

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

CREATE INDEX IF NOT EXISTS idx_episodes_session ON episodes(session_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON semantic_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp);
"""


def get_schema_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("PRAGMA user_version;").fetchone()
    return 0 if row is None else int(row[0])


def set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    conn.execute(f"PRAGMA user_version={int(version)};")


def initialize_schema(conn: sqlite3.Connection, *, enable_vector: bool = False) -> None:
    current_version = get_schema_version(conn)
    conn.executescript(SCHEMA_SQL)
    if enable_vector:
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS episodes_vec USING vec0(
                id TEXT PRIMARY KEY,
                embedding FLOAT[1536]
            );
            """
        )
    if current_version == 0:
        set_schema_version(conn, SCHEMA_VERSION)
    conn.commit()


def get_schema_status(conn: sqlite3.Connection) -> dict[str, int | bool]:
    current = get_schema_version(conn)
    return {
        "current_version": current,
        "expected_version": SCHEMA_VERSION,
        "is_initialized": current > 0,
        "is_current": current == SCHEMA_VERSION,
    }
