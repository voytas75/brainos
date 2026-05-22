import json
import sqlite3
import subprocess
from pathlib import Path

from brainos.schema import get_schema_version
from brainos.store import BrainOSStore


def create_v1_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;

        CREATE TABLE wm (
            key TEXT PRIMARY KEY,
            value TEXT CHECK(json_valid(value)),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE episodes (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL,
            metadata TEXT CHECK(json_valid(metadata))
        );

        CREATE VIRTUAL TABLE episodes_fts USING fts5(content, content_id UNINDEXED);

        CREATE TABLE semantic_nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            properties TEXT CHECK(json_valid(properties))
        );

        CREATE TABLE semantic_edges (
            source_id TEXT,
            target_id TEXT,
            predicate TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            PRIMARY KEY (source_id, target_id, predicate)
        );

        CREATE TABLE procedures (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            steps_json TEXT CHECK(json_valid(steps_json)),
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE ledger (
            event_id TEXT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            layer TEXT NOT NULL,
            action TEXT NOT NULL,
            payload TEXT CHECK(json_valid(payload)),
            causal_event_id TEXT,
            previous_hash TEXT,
            crypto_hash TEXT NOT NULL
        );
        """
    )
    conn.execute("PRAGMA user_version=1")
    conn.commit()
    conn.close()


def test_migrates_v1_to_v2(tmp_path):
    db = tmp_path / "brain_v1.db"
    create_v1_database(db)

    store = BrainOSStore(db)
    store.initialize()

    assert store.schema_status()["current_version"] == 2
    promotion_tables = store.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='episode_promotions'"
    ).fetchall()
    assert len(promotion_tables) == 1
    assert get_schema_version(store.conn) == 2
    store.close()


def test_cli_not_found_and_validation_errors(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(["uv", "run", "brainos", "--db", str(db), "init"], check=True, capture_output=True, text=True)

    missing_node = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "semantic-node-get", "missing"],
        capture_output=True,
        text=True,
    )
    assert missing_node.returncode == 2
    err = json.loads(missing_node.stderr)
    assert err["ok"] is False
    assert "semantic node not found" in err["error"]

    episode = subprocess.run(
        [
            "uv",
            "run",
            "brainos",
            "--db",
            str(db),
            "episode-add",
            "s1",
            "Bad procedure",
            "--metadata-json",
            '{"promotion_type":"procedure","procedure_steps":["bad-step"]}',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    episode_id = episode.stdout.strip()

    bad_preview = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "consolidation-preview", episode_id],
        capture_output=True,
        text=True,
    )
    assert bad_preview.returncode == 2
    err = json.loads(bad_preview.stderr)
    assert err["ok"] is False
    assert "procedure_steps must be a JSON array of objects" in err["error"]
