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


def test_schema_status_and_capabilities(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)

    status_before = store.schema_status()
    assert status_before["current_version"] == 0
    assert status_before["is_initialized"] is False
    assert status_before["is_current"] is False

    store.initialize()

    status_after = store.schema_status()
    assert status_after["current_version"] == 1
    assert status_after["expected_version"] == 1
    assert status_after["is_initialized"] is True
    assert status_after["is_current"] is True

    capabilities = store.capabilities()
    assert capabilities["fts5"] is True
    assert "sqlite_vec" in capabilities
    assert "sqlite_vec_error" in capabilities
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

    verification = store.verify_ledger()
    assert verification["ok"] is True
    assert verification["entry_count"] == 2
    assert verification["problems"] == []
    store.close()


def test_episode_listing_search_recall_and_consolidation(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    semantic_episode_id = store.add_episode(
        session_id="s1",
        content="Agent learned semantic edges",
        metadata={
            "kind": "graph",
            "promotion_type": "semantic",
            "semantic_name": "Semantic edges",
            "semantic_type": "Fact",
            "semantic_properties": {"topic": "memory"},
        },
    )
    procedure_episode_id = store.add_episode(
        session_id="s1",
        content="Bootstrap the store in two steps",
        metadata={
            "kind": "procedure",
            "promotion_type": "procedure",
            "procedure_name": "bootstrap_from_episode",
            "procedure_steps": [{"step": "init-db"}, {"step": "load-state"}],
        },
    )
    store.add_episode(session_id="s2", content="Different memory fragment", metadata={"kind": "other"})

    listed = store.list_episodes(session_id="s1", limit=10)
    assert len(listed) == 2
    assert all(item["session_id"] == "s1" for item in listed)
    assert isinstance(listed[0]["metadata"], dict)

    results = store.search_episodes_text("semantic", limit=5)
    assert len(results) == 1
    assert results[0]["metadata"]["kind"] == "graph"

    store.upsert_semantic_node(node_id="semantic-1", name="Semantic Memory", node_type="Concept", properties={"area": "memory"})

    recall = store.recall("semantic", session_id="s1", limit=5)
    assert recall["mode"] == "fts_plus_semantic_name_match"
    assert recall["count"] == 1
    assert recall["semantic_count"] == 1
    assert recall["episodes"][0]["metadata"]["kind"] == "graph"
    assert recall["semantic_hits"][0]["name"] == "Semantic Memory"
    assert recall["summary"] == "episodes:1, semantic_hits:1"

    semantic_preview = store.preview_consolidation(semantic_episode_id)
    assert semantic_preview["promotion_type"] == "semantic"
    assert semantic_preview["candidate"]["target_layer"] == "semantic"
    assert semantic_preview["candidate"]["semantic_node"]["properties"]["topic"] == "memory"

    semantic_promote = store.promote_episode(semantic_episode_id)
    assert semantic_promote["ok"] is True
    assert semantic_promote["target_layer"] == "semantic"
    promoted_node = store.get_semantic_node(semantic_promote["created_id"])
    assert promoted_node is not None
    assert promoted_node["properties"]["source_episode_id"] == semantic_episode_id

    procedure_preview = store.preview_consolidation(procedure_episode_id)
    assert procedure_preview["promotion_type"] == "procedure"
    assert procedure_preview["candidate"]["target_layer"] == "procedural"
    assert procedure_preview["candidate"]["procedure"]["steps"][0]["step"] == "init-db"

    procedure_promote = store.promote_episode(procedure_episode_id)
    assert procedure_promote["ok"] is True
    assert procedure_promote["target_layer"] == "procedural"
    promoted_procedure = store.get_procedure(procedure_promote["created_id"])
    assert promoted_procedure is not None
    assert promoted_procedure["steps"][1]["step"] == "load-state"
    store.close()


def test_ledger_verification_detects_tampering(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.set_working_memory("agent_state", {"mode": "ready"})
    store.set_working_memory("agent_state", {"mode": "busy"})

    store.conn.execute("UPDATE ledger SET crypto_hash = 'tampered' WHERE rowid = 1")
    store.conn.commit()

    verification = store.verify_ledger()
    assert verification["ok"] is False
    assert verification["entry_count"] == 2
    assert any(problem["kind"] == "crypto_hash_mismatch" for problem in verification["problems"])
    store.close()


def test_semantic_queries_and_procedures(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()

    store.upsert_semantic_node(node_id="n1", name="SQLite", node_type="Concept", properties={"kind": "db"})
    store.upsert_semantic_node(node_id="n2", name="BrainOS", node_type="Entity", properties={"kind": "system"})
    store.upsert_semantic_node(node_id="n3", name="WAL", node_type="Concept", properties={"kind": "mode"})
    store.upsert_semantic_edge(source_id="n2", target_id="n1", predicate="USES")
    store.upsert_semantic_edge(source_id="n1", target_id="n3", predicate="SUPPORTS")

    node = store.get_semantic_node("n1")
    assert node is not None
    assert node["properties"]["kind"] == "db"

    both_edges = store.list_semantic_edges("n1", direction="both")
    assert len(both_edges) == 2

    out_edges = store.list_semantic_edges("n1", direction="out")
    assert len(out_edges) == 1
    assert out_edges[0]["predicate"] == "SUPPORTS"

    proc_id = store.create_procedure(
        name="bootstrap",
        description="Initialize BrainOS",
        steps=[{"step": "init-db"}, {"step": "load-state"}],
    )
    procedure = store.get_procedure(proc_id)
    assert procedure is not None
    assert procedure["steps"][0]["step"] == "init-db"

    procedures = store.list_procedures(limit=10)
    assert len(procedures) == 1
    assert procedures[0]["name"] == "bootstrap"

    update_event = store.upsert_semantic_node(
        node_id="n1",
        name="SQLite",
        node_type="Concept",
        properties={"kind": "database", "tier": "core"},
    )
    assert isinstance(update_event, str)
    updated_node = store.get_semantic_node("n1")
    assert updated_node["properties"]["tier"] == "core"
    store.close()
