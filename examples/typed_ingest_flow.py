from __future__ import annotations

from pathlib import Path

from brainos.store import BrainOSStore


DB_PATH = Path(__file__).resolve().parent / "tmp" / "typed_ingest_flow.db"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    store = BrainOSStore(DB_PATH)
    store.initialize()

    print(f"Database: {DB_PATH}")
    print("\nWriting small typed-ingest corpus...")

    entries = [
        {
            "content": "BrainOS should keep sqlite-vec runtime checks explicit and operator-facing.",
            "metadata": {"kind": "fact", "topic": "runtime", "source": "manual"},
        },
        {
            "content": "Decision: typed ingest is a small corpus hygiene lever for retrieval smoke checks.",
            "metadata": {"kind": "decision", "topic": "retrieval", "source": "manual"},
        },
        {
            "content": "Procedure: run init, add episodes, sync vectors, then run retrieval-explain.",
            "metadata": {"kind": "procedure", "topic": "smoke", "source": "manual"},
        },
        {
            "content": "Observation: typed ingest is a small corpus hygiene lever.",
            "metadata": {"kind": "observation", "topic": "corpus", "source": "manual"},
        },
    ]

    for entry in entries:
        store.add_episode(session_id="typed-demo", content=entry["content"], metadata=entry["metadata"])

    print("\nStored episodes:")
    for item in store.list_episodes(session_id="typed-demo", limit=10):
        meta = item.get("metadata") or {}
        print(f"- kind={meta.get('kind')} topic={meta.get('topic')} source={meta.get('source')} :: {item['content']}")

    print("\nRecall query: retrieval smoke check")
    recall_rows = store.search_episodes_text("retrieval")
    for idx, item in enumerate(recall_rows, start=1):
        metadata = item.get("metadata") or {}
        kind = metadata.get("kind", "note")
        topic = metadata.get("topic")
        print(f"{idx}. {item['content']} (kind={kind}, topic={topic})")

    print("\nWhy this example exists:")
    print("- typed ingest is a small corpus hygiene lever")
    print("- it helps new entries carry useful retrieval context")
    print("- it is not a heavy schema system and does not require backfilling old data")

    print("\nSummary:")
    if recall_rows:
        print("typed-ingest retrieval example returned lexical matches")
    else:
        print("no_hits")

    store.close()


if __name__ == "__main__":
    main()
