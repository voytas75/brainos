import sqlite3
from pathlib import Path

from brainos.errors import EmbeddingRuntimeError
from brainos.schema import get_schema_version
from brainos.store import BrainOSStore, EmbeddingProviderNotConfiguredError


def create_v2_database(path: Path) -> None:
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
        CREATE TABLE episode_promotions (
            episode_id TEXT PRIMARY KEY,
            target_layer TEXT NOT NULL,
            target_id TEXT NOT NULL,
            status TEXT NOT NULL,
            promoted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ledger_event_id TEXT
        );
        """
    )
    conn.execute("PRAGMA user_version=2")
    conn.commit()
    conn.close()


def test_migrates_v2_to_current_and_preserves_vector_state_table(tmp_path):
    db = tmp_path / "brain_v2.db"
    create_v2_database(db)

    store = BrainOSStore(db)
    store.initialize()

    status = store.schema_status()
    assert status["current_version"] == status["expected_version"]
    tables = store.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='vector_index_state'"
    ).fetchall()
    assert len(tables) == 1
    decision_tables = store.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='decisions'"
    ).fetchall()
    assert len(decision_tables) == 1
    assert get_schema_version(store.conn) == status["expected_version"]
    store.close()


def test_episode_and_semantic_node_vector_states(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    episode_id = store.add_episode(session_id="s1", content="Vector candidate episode", metadata={})
    episode_state = store.get_vector_index_state("episode", episode_id)
    assert episode_state is not None
    assert episode_state["vector_status"] == "missing"
    assert episode_state["embedding_profile"] == "brainos-embedding-default"

    store.upsert_semantic_node(node_id="n1", name="Semantic fact", node_type="Fact", properties={"topic": "memory"})
    node_state = store.get_vector_index_state("semantic_node", "n1")
    assert node_state is not None
    assert node_state["vector_status"] == "missing"

    store.upsert_semantic_node(node_id="n1", name="Semantic fact", node_type="Fact", properties={"topic": "memory", "tier": "core"})
    node_state_updated = store.get_vector_index_state("semantic_node", "n1")
    assert node_state_updated is not None
    assert node_state_updated["vector_status"] == "stale"
    store.close()


def test_refresh_episode_vector_freshness_marks_stale_on_text_change(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    episode_id = store.add_episode(session_id="s1", content="Original content", metadata={})
    original_state = store.get_vector_index_state("episode", episode_id)
    assert original_state is not None
    assert original_state["vector_status"] == "missing"

    store.conn.execute("UPDATE episodes SET content = ? WHERE id = ?", ("Updated content", episode_id))
    store.conn.commit()

    refreshed = store.refresh_vector_freshness_for_episode(episode_id)
    assert refreshed["vector_status"] == "stale"
    store.close()


def test_embedding_contract_is_declared_but_not_executed(tmp_path, monkeypatch):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    monkeypatch.delenv("BRAINOS_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("AZURE_API_BASE", raising=False)
    monkeypatch.delenv("AZURE_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_API_VERSION", raising=False)

    contract = store.get_embedding_profile_contract()
    assert contract["profile"] == "brainos-embedding-default"
    assert contract["provider_path"] == "litellm"
    assert contract["operational_provider"] == "unknown"
    assert contract["required_env"] == ["BRAINOS_EMBEDDING_MODEL"]

    try:
        store.embed_texts(["hello world"])
        assert False, "expected embedding configuration or runtime error"
    except (EmbeddingProviderNotConfiguredError, EmbeddingRuntimeError):
        pass
    store.close()


def test_health_freshness_notes_distinguish_missing_from_warn(tmp_path):
    from brainos.health import retrieval_health_summary

    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    episode_id = store.add_episode(session_id="s1", content="Vector candidate episode", metadata={})
    summary = retrieval_health_summary(store, benchmark_limit=1)

    assert summary["freshness"]["status"] == "ok"
    assert "missing_vectors_present" in summary["freshness"]["notes"]
    assert summary["freshness"]["vector_index"]["by_status"]["missing"] >= 1
    assert episode_id is not None
    store.close()
