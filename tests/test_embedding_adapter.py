import os
import sqlite3
from pathlib import Path

from brainos.embedding import (
    ENV_AZURE_API_BASE,
    ENV_AZURE_API_KEY,
    ENV_AZURE_API_VERSION,
    ENV_EMBEDDING_MODEL,
    LiteLLMEmbeddingAdapter,
)
from brainos.errors import EmbeddingProviderNotConfiguredError
from brainos.store import BrainOSStore


def test_embedding_contract_exposes_required_env():
    adapter = LiteLLMEmbeddingAdapter()
    contract = adapter.contract()
    assert contract["profile"] == "brainos-embedding-default"
    assert contract["provider_path"] == "litellm"
    assert contract["operational_provider"] == "azure"
    assert ENV_EMBEDDING_MODEL in contract["required_env"]
    assert ENV_AZURE_API_BASE in contract["required_env"]
    assert ENV_AZURE_API_KEY in contract["required_env"]
    assert ENV_AZURE_API_VERSION in contract["required_env"]


def test_embedding_adapter_requires_env(monkeypatch):
    for name in [ENV_EMBEDDING_MODEL, ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION]:
        monkeypatch.delenv(name, raising=False)

    adapter = LiteLLMEmbeddingAdapter()
    try:
        adapter.embed_texts(["hello"])
        assert False, "expected EmbeddingProviderNotConfiguredError"
    except EmbeddingProviderNotConfiguredError as exc:
        assert "missing embedding environment variables" in str(exc)


def create_v3_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;
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
        CREATE TABLE vector_index_state (
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
        """
    )
    conn.execute("PRAGMA user_version=3")
    conn.commit()
    conn.close()


def test_generate_episode_embedding_records_error_state(monkeypatch, tmp_path):
    db = tmp_path / "brain_v3.db"
    create_v3_database(db)
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Needs embedding", metadata={})

    for name in [ENV_EMBEDDING_MODEL, ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION]:
        monkeypatch.delenv(name, raising=False)

    try:
        store.generate_episode_embedding(episode_id)
        assert False, "expected EmbeddingProviderNotConfiguredError"
    except EmbeddingProviderNotConfiguredError:
        pass

    state = store.get_vector_index_state("episode", episode_id)
    assert state is not None
    assert state["vector_status"] == "error"
    assert state["last_error"] is not None
    store.close()
