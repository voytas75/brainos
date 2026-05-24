from __future__ import annotations

from typing import Any

from .store import BrainOSStore


def _available_probe_session_ids(store: BrainOSStore, *, limit: int = 10) -> list[str]:
    rows = store.conn.execute(
        "SELECT session_id, COUNT(*) AS n FROM episodes GROUP BY session_id ORDER BY n DESC, session_id ASC LIMIT ?",
        (limit,),
    ).fetchall()
    return [row[0] for row in rows if row[0]]


def real_corpus_probe_cases(*, session_id: str) -> list[dict[str, str]]:
    return [
        {"query": "brainos initialized with wal", "session_id": session_id},
        {"query": "store semantic fact", "session_id": session_id},
    ]


def run_real_corpus_probe(store: BrainOSStore, *, limit: int = 5) -> dict[str, Any]:
    available_session_ids = _available_probe_session_ids(store)
    if not available_session_ids:
        return {
            "probe": "real-corpus-retrieval-quality-v1",
            "evidence_kind": "small_real_sample",
            "truthfulness_note": "This probe is a small read-only real-sample check and is not a broad corpus-quality guarantee.",
            "target_status": "no_session_sample_available",
            "available_session_ids": [],
            "case_count": 0,
            "results": [],
        }

    target_session_id = available_session_ids[0]
    cases = real_corpus_probe_cases(session_id=target_session_id)
    results = []
    for case in cases:
        recall = store.recall(case["query"], session_id=case["session_id"], limit=limit)
        top_episode = recall["ranked_episodes"][0]["id"] if recall.get("ranked_episodes") else None
        top_semantic = recall["ranked_semantic_hits"][0]["id"] if recall.get("ranked_semantic_hits") else None
        results.append(
            {
                "query": case["query"],
                "session_id": case["session_id"],
                "top_episode_id": top_episode,
                "top_semantic_id": top_semantic,
                "episode_vector_mode": recall.get("episode_vector_mode"),
                "semantic_vector_mode": recall.get("semantic_vector_mode"),
                "ranked_count": recall.get("ranked_count"),
                "ranked_semantic_count": recall.get("ranked_semantic_count"),
            }
        )
    return {
        "probe": "real-corpus-retrieval-quality-v1",
        "evidence_kind": "small_real_sample",
        "truthfulness_note": "This probe is a small read-only real-sample check and is not a broad corpus-quality guarantee.",
        "target_status": "aligned_to_available_session_sample",
        "target_session_id": target_session_id,
        "available_session_ids": available_session_ids,
        "case_count": len(cases),
        "results": results,
    }
