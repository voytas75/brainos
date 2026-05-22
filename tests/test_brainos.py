import json
import sqlite3

from brainos.store import BrainOSStore


def test_initialize_and_core_tables(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    tables = {
        row[0]
        for row in store.conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table', 'index')"
        ).fetchall()
    }
    assert "wm" in tables
    assert "episodes" in tables
    assert "episodes_fts" in tables
    assert "semantic_nodes" in tables
    assert "semantic_edges" in tables
    assert "procedures" in tables
    assert "ledger" in tables
    store.close()


def test_working_memory_and_ledger_chain(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    e1 = store.set_working_memory("agent_state", {"mode": "ready"})
    e2 = store.set_working_memory("agent_state", {"mode": "busy"}, causal_event_id=e1)

    value = store.get_working_memory("agent_state")
    assert value == {"mode": "busy"}

    ledger = store.list_ledger()
    assert len(ledger) == 2
    assert ledger[1]["causal_event_id"] == e1
    assert ledger[1]["previous_hash"] == ledger[0]["crypto_hash"]
    assert ledger[0]["event_id"] == e1
    assert ledger[1]["event_id"] != e1
    assert ledger[1]["event_id"] == e2
    store.close()


def test_episode_fts_search(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.add_episode(session_id="s1", content="Agent learned SQLite WAL mode", metadata={"kind": "note"})
    store.add_episode(session_id="s1", content="Different memory fragment", metadata={"kind": "other"})

    results = store.search_episodes_text("SQLite", limit=5)
    assert len(results) == 1
    assert "SQLite" in results[0]["content"]
    assert json.loads(results[0]["metadata"])["kind"] == "note"
    store.close()


def test_semantic_edges_enforce_foreign_keys(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.upsert_semantic_node(node_id="n1", name="SQLite", node_type="Concept")
    store.upsert_semantic_node(node_id="n2", name="BrainOS", node_type="Entity")
    store.upsert_semantic_edge(source_id="n2", target_id="n1", predicate="USES")

    with_store = sqlite3.connect(db)
    with_store.execute("PRAGMA foreign_keys=ON")
    count = with_store.execute("SELECT COUNT(*) FROM semantic_edges").fetchone()[0]
    assert count == 1
    with_store.close()
    store.close()
