import json
import os
import sqlite3
import subprocess
from pathlib import Path

from brainos.errors import BrainOSError
from brainos.schema import get_schema_version
from brainos.sqlite_vec import ENV_SQLITE_VEC_PATH
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


def create_incomplete_v0_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE episodes (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content TEXT NOT NULL
        )
        """
    )
    conn.execute("PRAGMA user_version=0")
    conn.commit()
    conn.close()


def _assert_unversioned_database_is_rejected(db: Path) -> None:
    store = BrainOSStore(db)
    try:
        try:
            store.initialize()
            raise AssertionError("expected incomplete unversioned schema rejection")
        except BrainOSError as exc:
            assert "unversioned database already contains schema objects" in str(exc)
        assert store.schema_status()["current_version"] == 0
    finally:
        store.close()


def test_rejects_incomplete_unversioned_database(tmp_path):
    db = tmp_path / "incomplete_v0.db"
    create_incomplete_v0_database(db)

    _assert_unversioned_database_is_rejected(db)


def test_rejects_unversioned_database_with_sqlite_like_user_table(tmp_path):
    db = tmp_path / "sqlite_like_v0.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE sqliteX_untrusted (id TEXT PRIMARY KEY)")
    conn.execute("PRAGMA user_version=0")
    conn.commit()
    conn.close()

    _assert_unversioned_database_is_rejected(db)


def test_migrates_v1_to_current(tmp_path):
    db = tmp_path / "brain_v1.db"
    create_v1_database(db)

    store = BrainOSStore(db)
    store.initialize()

    assert store.schema_status()["current_version"] >= 3
    promotion_tables = store.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='episode_promotions'"
    ).fetchall()
    assert len(promotion_tables) == 1
    assert get_schema_version(store.conn) >= 3
    store.close()


def test_enable_vector_defers_tables_until_first_embedding(monkeypatch, tmp_path):
    db = tmp_path / "brain.db"
    vec_path = "/tmp/vec0.so"
    loaded_paths = []
    monkeypatch.setenv(ENV_SQLITE_VEC_PATH, vec_path)
    monkeypatch.setattr(
        "brainos.schema.load_sqlite_vec_extension",
        lambda conn, path: loaded_paths.append(path),
    )

    store = BrainOSStore(db, enable_vector=True)
    store.initialize()

    tables = {
        row[0]
        for row in store.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    assert loaded_paths == [vec_path]
    assert "episodes_vec" not in tables
    assert "semantic_nodes_vec" not in tables
    store.close()


def test_cli_enable_vector_defers_tables_when_runtime_is_unconfigured(tmp_path):
    db = tmp_path / "brain.db"
    env = os.environ.copy()
    env.pop(ENV_SQLITE_VEC_PATH, None)

    subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "init", "--enable-vector"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    conn = sqlite3.connect(db)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    conn.close()
    assert "episodes_vec" not in tables
    assert "semantic_nodes_vec" not in tables


def test_cli_not_found_and_validation_errors(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "init"],
        check=True,
        capture_output=True,
        text=True,
    )

    missing_node = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "semantic-node-get", "missing"],
        capture_output=True,
        text=True,
        check=False,
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
        check=False,
    )
    assert bad_preview.returncode == 2
    err = json.loads(bad_preview.stderr)
    assert err["ok"] is False
    assert "procedure_steps must be a JSON array of objects" in err["error"]


def test_cli_episode_promotion_get(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "init"],
        check=True,
        capture_output=True,
        text=True,
    )
    episode = subprocess.run(
        [
            "uv",
            "run",
            "brainos",
            "--db",
            str(db),
            "episode-add",
            "s1",
            "Semantic fact",
            "--metadata-json",
            '{"promotion_type":"semantic","semantic_name":"Semantic fact","semantic_type":"Fact"}',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    episode_id = episode.stdout.strip()

    subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "promote-episode", episode_id],
        check=True,
        capture_output=True,
        text=True,
    )

    promotion = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "episode-promotion-get", episode_id],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(promotion.stdout)
    assert payload["episode_id"] == episode_id
    assert payload["target_layer"] == "semantic"

    missing = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "episode-promotion-get", "missing"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode == 2
    err = json.loads(missing.stderr)
    assert "episode promotion not found" in err["error"]
