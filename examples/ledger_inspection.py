from __future__ import annotations

from pathlib import Path

from brainos.store import BrainOSStore


DB_PATH = Path(__file__).resolve().parent / "tmp" / "ledger_inspection.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    store = BrainOSStore(DB_PATH)
    store.initialize()

    store.set_working_memory("agent_state", {"mode": "ready"})
    store.add_episode(
        session_id="demo-session",
        content="BrainOS example wrote working memory and an episode",
        metadata={"source": "example"},
    )

    ledger = store.list_ledger()

    print(f"Database: {DB_PATH}")
    print("\nLedger entries:")
    for idx, entry in enumerate(ledger, start=1):
        print(
            f"{idx}. layer={entry['layer']} action={entry['action']} "
            f"event_id={entry['event_id']} causal_event_id={entry['causal_event_id']}"
        )

    print("\nNote: ledger inspection shows that BrainOS keeps an auditable write trail.")
    store.close()


if __name__ == "__main__":
    main()
