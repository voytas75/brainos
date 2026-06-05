from __future__ import annotations

from pathlib import Path

from brainos import BrainOSStore


DB_PATH = Path(__file__).resolve().parent / "tmp" / "python_api_quickstart.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    store = BrainOSStore(DB_PATH)
    store.initialize()

    store.set_working_memory("agent_state", {"mode": "ready"})
    store.add_episode(
        session_id="session-1",
        content="Agent initialized successfully",
        metadata={"source": "bootstrap"},
    )
    store.upsert_semantic_node(
        node_id="n1",
        name="SQLite",
        node_type="Concept",
        properties={"role": "storage"},
    )

    print(f"Database: {DB_PATH}")
    print("\nWorking memory:")
    print(store.get_working_memory("agent_state"))

    print("\nEpisode search for 'initialized':")
    for item in store.search_episodes_text("initialized"):
        print(f"- {item['content']}")

    print("\nSemantic node:")
    print(store.get_semantic_node("n1"))

    store.close()


if __name__ == "__main__":
    main()
