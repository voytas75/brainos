from __future__ import annotations

from pathlib import Path

from brainos.store import BrainOSStore


DB_PATH = Path(__file__).resolve().parent / "tmp" / "episode_recall_flow.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    store = BrainOSStore(DB_PATH)
    store.initialize()

    print(f"Database: {DB_PATH}")
    print("\nWriting episodes...")
    store.add_episode(
        session_id="demo-session",
        content="Indexed project notes successfully",
        metadata={"kind": "operation", "source": "example"},
    )
    store.add_episode(
        session_id="demo-session",
        content="Observed retrieval drift during test run",
        metadata={"kind": "observation", "source": "example"},
    )
    store.add_episode(
        session_id="demo-session",
        content="Planned a follow-up benchmark for retrieval ranking",
        metadata={"kind": "plan", "source": "example"},
    )

    print("\nRecall query: retrieval")
    results = store.recall("retrieval", session_id="demo-session", limit=5)
    for idx, item in enumerate(results["ranked_episodes"], start=1):
        print(f"{idx}. {item['content']} (sources={','.join(item.get('match_sources', []))})")

    print("\nSummary:")
    print(results["summary"])

    print("\nNote: episodic memory keeps searchable history.")
    print("Use this for events and observations, not for the current one-key runtime state.")

    store.close()


if __name__ == "__main__":
    main()
