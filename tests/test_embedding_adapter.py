import os
import sqlite3
from pathlib import Path

from brainos.embedding import LiteLLMEmbeddingAdapter
from brainos.embedding_config import (
    ENV_AZURE_API_BASE,
    ENV_AZURE_API_KEY,
    ENV_AZURE_API_VERSION,
    ENV_EMBEDDING_MODEL,
    ENV_OPENAI_API_KEY,
)
from brainos.errors import EmbeddingProviderNotConfiguredError, VectorIndexContractError
from brainos.store import BrainOSStore


class _DummyEmbeddingResponse:
    def __init__(self, vectors):
        self.data = [{"embedding": v} for v in vectors]


class _CaptureLiteLLM:
    last_kwargs = None

    @staticmethod
    def embedding(**kwargs):
        _CaptureLiteLLM.last_kwargs = kwargs
        return _DummyEmbeddingResponse([[0.1, 0.2, 0.3]])


def test_embedding_contract_exposes_required_env():
    adapter = LiteLLMEmbeddingAdapter()
    contract = adapter.contract()
    assert contract["profile"] == "brainos-embedding-default"
    assert contract["provider_path"] == "litellm"
    assert contract["operational_provider"] == "unknown"
    assert contract["required_env"] == [ENV_EMBEDDING_MODEL]


def test_embedding_adapter_requires_env(monkeypatch):
    for name in [ENV_EMBEDDING_MODEL, ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION, ENV_OPENAI_API_KEY]:
        monkeypatch.delenv(name, raising=False)

    adapter = LiteLLMEmbeddingAdapter()
    try:
        adapter.embed_texts(["hello"])
        assert False, "expected EmbeddingProviderNotConfiguredError"
    except EmbeddingProviderNotConfiguredError as exc:
        assert "missing embedding environment variables" in str(exc)


def test_embedding_adapter_openai_path_uses_openai_key_without_azure_env(monkeypatch):
    for name in [ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(ENV_EMBEDDING_MODEL, "openai/text-embedding-3-small")
    monkeypatch.setenv(ENV_OPENAI_API_KEY, "openai-key")
    monkeypatch.setitem(__import__("sys").modules, "litellm", _CaptureLiteLLM)

    adapter = LiteLLMEmbeddingAdapter()
    result = adapter.embed_texts(["hello"])

    assert result["provider"] == "openai"
    assert result["model"] == "openai/text-embedding-3-small"
    assert _CaptureLiteLLM.last_kwargs["model"] == "openai/text-embedding-3-small"
    assert _CaptureLiteLLM.last_kwargs["api_key"] == "openai-key"
    assert "api_base" not in _CaptureLiteLLM.last_kwargs
    assert "api_version" not in _CaptureLiteLLM.last_kwargs


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

    for name in [ENV_EMBEDDING_MODEL, ENV_AZURE_API_BASE, ENV_AZURE_API_KEY, ENV_AZURE_API_VERSION, ENV_OPENAI_API_KEY]:
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


def test_generate_episode_embedding_marks_disabled_when_sqlite_vec_unavailable(monkeypatch, tmp_path):
    db = tmp_path / "brain_v3_disabled.db"
    create_v3_database(db)
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Needs vector storage", metadata={})

    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.1, 0.2, 0.3]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure-embed-test",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "_sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": False, "sqlite_vec_error": "no such module: vec0"},
    )

    result = store.generate_episode_embedding(episode_id)
    assert result["vector_status"] == "disabled"
    assert result["storage"] == "disabled"

    state = store.get_vector_index_state("episode", episode_id)
    assert state is not None
    assert state["vector_status"] == "disabled"
    assert state["embedding_dimensions"] == 3
    assert state["last_error"] == "no such module: vec0"
    store.close()


def test_generate_episode_embedding_stores_vector_when_sqlite_vec_available(monkeypatch, tmp_path):
    db = tmp_path / "brain_v3_store.db"
    create_v3_database(db)
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Store this vector", metadata={})

    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.11, 0.22, 0.33]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure-embed-test",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "_sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )

    created = []
    inserted = []

    monkeypatch.setattr(store, "_ensure_episode_vec_table", lambda dimensions: created.append(dimensions))
    monkeypatch.setattr(
        store,
        "_upsert_episode_vector",
        lambda eid, vector, dimensions: inserted.append((eid, vector, dimensions)),
    )

    result = store.generate_episode_embedding(episode_id)
    assert result["vector_status"] == "fresh"
    assert result["storage"] == "sqlite-vec"
    assert inserted == [(episode_id, [0.11, 0.22, 0.33], 3)]

    state = store.get_vector_index_state("episode", episode_id)
    assert state is not None
    assert state["vector_status"] == "fresh"
    assert state["embedding_dimensions"] == 3
    assert state["embedding_model"] == "azure-embed-test"
    store.close()


def test_generate_episode_embedding_fails_fast_on_dimension_mismatch(monkeypatch, tmp_path):
    db = tmp_path / "brain_v3_dimension_mismatch.db"
    create_v3_database(db)
    store = BrainOSStore(db)
    store.initialize()
    episode_id = store.add_episode(session_id="s1", content="Dimension-sensitive vector", metadata={})

    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.1, 0.2, 0.3]],
            "dimensions": 3,
            "provider": "synthetic",
            "model": "synthetic-3d",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "_sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )
    monkeypatch.setattr(store, "_vec_table_dimensions", lambda table_name: 1536 if table_name == "episodes_vec" else None)

    try:
        store.generate_episode_embedding(episode_id)
        assert False, "expected VectorIndexContractError"
    except VectorIndexContractError as exc:
        assert "table=episodes_vec" in str(exc)
        assert "expected=1536" in str(exc)
        assert "got=3" in str(exc)

    state = store.get_vector_index_state("episode", episode_id)
    assert state is not None
    assert state["vector_status"] == "error"
    assert "expected=1536" in (state["last_error"] or "")
    store.close()


def test_generate_semantic_node_embedding_stores_vector_when_sqlite_vec_available(monkeypatch, tmp_path):
    db = tmp_path / "brain_v3_semantic_store.db"
    create_v3_database(db)
    store = BrainOSStore(db)
    store.initialize()
    store.upsert_semantic_node(node_id="n1", name="Semantic Memory", node_type="Concept", properties={"area": "memory"})

    monkeypatch.setattr(
        store,
        "embed_texts",
        lambda texts, profile=None: {
            "vectors": [[0.11, 0.22, 0.33]],
            "dimensions": 3,
            "provider": "azure",
            "model": "azure-embed-test",
            "profile": profile or "brainos-embedding-default",
            "requested_count": 1,
            "returned_count": 1,
        },
    )
    monkeypatch.setattr(
        store,
        "_sqlite_vec_capability",
        lambda: {"fts5": True, "sqlite_vec": True, "sqlite_vec_error": None},
    )

    inserted = []
    monkeypatch.setattr(
        store,
        "_upsert_semantic_node_vector",
        lambda nid, vector, dimensions: inserted.append((nid, vector, dimensions)),
    )

    result = store.generate_semantic_node_embedding("n1")
    assert result["vector_status"] == "fresh"
    assert result["storage"] == "sqlite-vec"
    assert inserted == [("n1", [0.11, 0.22, 0.33], 3)]

    state = store.get_vector_index_state("semantic_node", "n1")
    assert state is not None
    assert state["vector_status"] == "fresh"
    assert state["embedding_dimensions"] == 3
    store.close()
