from __future__ import annotations

import hashlib
import os
import tempfile
from typing import Any

from .errors import BrainOSError
from .store import BrainOSStore


def _benchmark_mode(store: BrainOSStore) -> str:
    capabilities = store.capabilities()
    return "vector-ready" if capabilities.get("sqlite_vec") else "degraded-non-vector"


def _classify_benchmark_failure(*, mode: str, result: dict[str, Any]) -> str:
    if mode != "vector-ready":
        return "likely_runtime_related"
    if result.get("episode_vector_mode") != "sqlite_vec_episode_similarity" or result.get("semantic_vector_mode") != "sqlite_vec_semantic_similarity":
        return "likely_runtime_or_benchmark_seed_path_related"
    return "likely_quality_regression"


def _failed_case_next_debug(*, query: str) -> dict[str, Any]:
    return {
        "tool": "retrieval-explain",
        "query": query,
        "session_id": "bench",
    }


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
    ids["ep_disabled_runtime"] = store.add_episode(
        session_id="bench",
        content="Disabled vector state usually points to sqlite-vec runtime unavailability, not stale data.",
        metadata={"kind": "runtime"},
    )
    ids["ep_policy_version"] = store.add_episode(
        session_id="bench",
        content="Retrieval explain output should show the active scoring policy version.",
        metadata={"kind": "policy"},
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
    store.upsert_semantic_node(
        node_id="sem-disabled-runtime",
        name="Disabled Vector State",
        node_type="Concept",
        properties={"area": "runtime"},
    )
    store.upsert_semantic_node(
        node_id="sem-policy-version",
        name="Scoring Policy Version",
        node_type="Capability",
        properties={"area": "retrieval"},
    )
    return ids


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def benchmark_cases(ids: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "query": "sqlite wal durability",
            "expected_episode_id": ids["ep_sqlite_wal"],
            "expected_episode_hash": _text_hash("SQLite WAL mode helps BrainOS keep local writes safe and concurrent."),
            "expected_semantic_id": "sem-wal",
        },
        {
            "query": "what helps BrainOS keep local writes safe?",
            "expected_episode_id": ids["ep_sqlite_wal"],
            "expected_episode_hash": _text_hash("SQLite WAL mode helps BrainOS keep local writes safe and concurrent."),
            "expected_semantic_id": "sem-wal",
        },
        {
            "query": "azure embedding model",
            "expected_episode_id": ids["ep_embedding_azure"],
            "expected_episode_hash": _text_hash("Azure embeddings are executed through LiteLLM in the current BrainOS path."),
            "expected_semantic_id": "sem-azure-embed",
        },
        {
            "query": "what is the current BrainOS embedding path?",
            "expected_episode_id": ids["ep_embedding_azure"],
            "expected_episode_hash": _text_hash("Azure embeddings are executed through LiteLLM in the current BrainOS path."),
            "expected_semantic_id": "sem-azure-embed",
        },
        {
            "query": "how to repair stale vectors",
            "expected_episode_id": ids["ep_reindex_runtime"],
            "expected_episode_hash": _text_hash("Reindex stale vectors after runtime changes or source text updates."),
            "expected_semantic_id": "sem-reindex",
        },
        {
            "query": "what should I do after runtime changes to vectors?",
            "expected_episode_id": ids["ep_reindex_runtime"],
            "expected_episode_hash": _text_hash("Reindex stale vectors after runtime changes or source text updates."),
            "expected_semantic_id": "sem-reindex",
        },
        {
            "query": "disabled vector runtime",
            "expected_episode_id": ids["ep_disabled_runtime"],
            "expected_episode_hash": _text_hash("Disabled vector state usually points to sqlite-vec runtime unavailability, not stale data."),
            "expected_semantic_id": "sem-disabled-runtime",
        },
        {
            "query": "what does disabled vector state usually point to?",
            "expected_episode_id": ids["ep_disabled_runtime"],
            "expected_episode_hash": _text_hash("Disabled vector state usually points to sqlite-vec runtime unavailability, not stale data."),
            "expected_semantic_id": "sem-disabled-runtime",
        },
        {
            "query": "policy version explain",
            "expected_episode_id": ids["ep_policy_version"],
            "expected_episode_hash": _text_hash("Retrieval explain output should show the active scoring policy version."),
            "expected_semantic_id": "sem-policy-version",
        },
        {
            "query": "what should retrieval explain show?",
            "expected_episode_id": ids["ep_policy_version"],
            "expected_episode_hash": _text_hash("Retrieval explain output should show the active scoring policy version."),
            "expected_semantic_id": "sem-policy-version",
        },
    ]


def run_retrieval_benchmark(store: BrainOSStore, *, limit: int = 5) -> dict[str, Any]:
    mode = _benchmark_mode(store)
    fd, temp_db = tempfile.mkstemp(prefix="brainos-bench-", suffix=".db")
    os.close(fd)
    try:
        bench_store = BrainOSStore(temp_db, enable_vector=False)
        bench_store.initialize()
        ids = seed_benchmark_store(bench_store)
        for object_type, vector_status in (("episode", "missing"), ("semantic_node", "missing")):
            bench_store.sync_vector_index_batch(
                object_type=object_type,
                vector_status=vector_status,
                limit=100,
            )
        cases = benchmark_cases(ids)
        results = []
        overall_passed = 0
        episode_passed = 0
        semantic_passed = 0

        benchmark_runtime_error = None
        for case in cases:
            try:
                recall = bench_store.recall(case["query"], session_id="bench", limit=limit)
                top_episode_row = recall["ranked_episodes"][0] if recall["ranked_episodes"] else None
                top_episode = top_episode_row["id"] if top_episode_row else None
                top_episode_hash = _text_hash(top_episode_row["content"]) if top_episode_row else None
                top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall["ranked_semantic_hits"] else None
                episode_ok = (
                    top_episode == case["expected_episode_id"]
                    or top_episode_hash == case["expected_episode_hash"]
                )
                semantic_ok = top_semantic == case["expected_semantic_id"]
                ok = episode_ok and semantic_ok
                if episode_ok:
                    episode_passed += 1
                if semantic_ok:
                    semantic_passed += 1
                if ok:
                    overall_passed += 1
                results.append(
                    {
                        "query": case["query"],
                        "ok": ok,
                        "episode_ok": episode_ok,
                        "semantic_ok": semantic_ok,
                        "expected_episode_id": case["expected_episode_id"],
                        "top_episode_id": top_episode,
                        "expected_semantic_id": case["expected_semantic_id"],
                        "expected_episode_hash": case["expected_episode_hash"],
                        "top_episode_hash": top_episode_hash,
                        "top_semantic_id": top_semantic,
                        "episode_vector_mode": recall.get("episode_vector_mode"),
                        "semantic_vector_mode": recall.get("semantic_vector_mode"),
                        "runtime_error": None,
                    }
                )
            except Exception as exc:
                benchmark_runtime_error = str(exc)
                results.append(
                    {
                        "query": case["query"],
                        "ok": False,
                        "episode_ok": False,
                        "semantic_ok": False,
                        "expected_episode_id": case["expected_episode_id"],
                        "top_episode_id": None,
                        "expected_semantic_id": case["expected_semantic_id"],
                        "expected_episode_hash": case["expected_episode_hash"],
                        "top_episode_hash": None,
                        "top_semantic_id": None,
                        "episode_vector_mode": None,
                        "semantic_vector_mode": None,
                        "runtime_error": str(exc),
                    }
                )

        degraded = mode != "vector-ready"
        degraded_reason = None if not degraded else "sqlite_vec_unavailable"
        failed_cases = []
        for result in results:
            if not result["ok"]:
                failed_cases.append(
                    {
                        "query": result["query"],
                        "failure_hint": _classify_benchmark_failure(mode=mode, result=result),
                        "episode_ok": result["episode_ok"],
                        "semantic_ok": result["semantic_ok"],
                        "expected_episode_id": result["expected_episode_id"],
                        "top_episode_id": result["top_episode_id"],
                        "expected_semantic_id": result["expected_semantic_id"],
                        "expected_episode_hash": result.get("expected_episode_hash"),
                        "top_episode_hash": result.get("top_episode_hash"),
                        "top_semantic_id": result["top_semantic_id"],
                        "next_debug": _failed_case_next_debug(query=result["query"]),
                        "recommended_fix": {
                            "action_hint": "configure_sqlite_vec_path" if result.get("runtime_error") else "inspect_retrieval_explain",
                            "target": "BRAINOS_SQLITE_VEC_PATH" if result.get("runtime_error") else "retrieval-explain",
                        },
                        "runtime_error": result.get("runtime_error"),
                    }
                )

        return {
            "ok": overall_passed == len(cases),
            "suite": "retrieval-benchmark-v0",
            "evidence_kind": "seeded_fixture",
            "truthfulness_note": "This benchmark uses an internal seeded fixture corpus and should be read as implementation-level evidence, not direct evidence about the current live database corpus.",
            "mode": mode,
            "degraded": degraded,
            "degraded_reason": degraded_reason,
            "case_count": len(cases),
            "passed": overall_passed,
            "failed": len(cases) - overall_passed,
            "episode_passed": episode_passed,
            "episode_failed": len(cases) - episode_passed,
            "semantic_passed": semantic_passed,
            "semantic_failed": len(cases) - semantic_passed,
            "failed_cases": failed_cases,
            "results": results,
            "runtime_error": benchmark_runtime_error,
        }
    finally:
        try:
            bench_store.close()
        except Exception:
            pass
        for path in (temp_db, f"{temp_db}-wal", f"{temp_db}-shm"):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
