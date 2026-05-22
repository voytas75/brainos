from __future__ import annotations

from typing import Any

from .store import BrainOSStore


def seed_benchmark_store(store: BrainOSStore) -> dict[str, str]:
    ids = {}
    ids["ep_sqlite_wal"] = store.add_episode(
        session_id="bench",
        content="SQLite WAL mode helps BrainOS keep local writes safe and concurrent.",
        metadata={"kind": "storage"},
    )
    ids["ep_embedding_azure"] = store.add_episode(
        session_id="bench",
        content="Azure embeddings are executed through LiteLLM in the current BrainOS path.",
        metadata={"kind": "embedding"},
    )
    ids["ep_reindex_runtime"] = store.add_episode(
        session_id="bench",
        content="Reindex stale vectors after runtime changes or source text updates.",
        metadata={"kind": "maintenance"},
    )

    store.upsert_semantic_node(
        node_id="sem-wal",
        name="SQLite WAL",
        node_type="Concept",
        properties={"area": "storage"},
    )
    store.upsert_semantic_node(
        node_id="sem-azure-embed",
        name="Azure Embeddings",
        node_type="Capability",
        properties={"area": "embedding"},
    )
    store.upsert_semantic_node(
        node_id="sem-reindex",
        name="Vector Reindex",
        node_type="Procedure",
        properties={"area": "maintenance"},
    )
    return ids


def benchmark_cases(ids: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"query": "sqlite wal durability", "expected_episode_id": ids["ep_sqlite_wal"], "expected_semantic_id": "sem-wal"},
        {"query": "azure embedding model", "expected_episode_id": ids["ep_embedding_azure"], "expected_semantic_id": "sem-azure-embed"},
        {"query": "how to repair stale vectors", "expected_episode_id": ids["ep_reindex_runtime"], "expected_semantic_id": "sem-reindex"},
    ]


def run_retrieval_benchmark(store: BrainOSStore, *, limit: int = 5) -> dict[str, Any]:
    ids = seed_benchmark_store(store)
    cases = benchmark_cases(ids)
    results = []
    passed = 0

    for case in cases:
        recall = store.recall(case["query"], session_id="bench", limit=limit)
        top_episode = recall["ranked_episodes"][0]["id"] if recall["ranked_episodes"] else None
        top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall["ranked_semantic_hits"] else None
        ok = top_episode == case["expected_episode_id"] and top_semantic == case["expected_semantic_id"]
        if ok:
            passed += 1
        results.append(
            {
                "query": case["query"],
                "ok": ok,
                "expected_episode_id": case["expected_episode_id"],
                "top_episode_id": top_episode,
                "expected_semantic_id": case["expected_semantic_id"],
                "top_semantic_id": top_semantic,
                "episode_vector_mode": recall.get("episode_vector_mode"),
                "semantic_vector_mode": recall.get("semantic_vector_mode"),
            }
        )

    return {
        "ok": passed == len(cases),
        "suite": "retrieval-benchmark-v0",
        "case_count": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "results": results,
    }
