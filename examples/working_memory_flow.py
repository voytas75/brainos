from __future__ import annotations

from pathlib import Path

from brainos.store import BrainOSStore


DB_PATH = Path(__file__).resolve().parent / "tmp" / "working_memory_flow.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    store = BrainOSStore(DB_PATH)
    store.initialize()

    print(f"Database: {DB_PATH}")
    print("\nStep 1: set initial agent state to ready")
    store.set_working_memory("agent_state", {"mode": "ready"})
    print(store.get_working_memory("agent_state"))

    print("\nStep 2: higher-level logic decides to start a task")
    current_state = store.get_working_memory("agent_state")
    if current_state == {"mode": "ready"}:
        store.set_working_memory("agent_state", {"mode": "busy", "task": "index_docs"})
    print(store.get_working_memory("agent_state"))

    print("\nStep 3: higher-level logic marks the task complete")
    store.set_working_memory("agent_state", {"mode": "ready"})
    print(store.get_working_memory("agent_state"))

    print("\nNote: BrainOS stored and returned the state values.")
    print("It did not decide when to start or finish the task; that logic lives above BrainOS.")

    store.close()


if __name__ == "__main__":
    main()
