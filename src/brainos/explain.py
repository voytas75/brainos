from __future__ import annotations

from typing import Any

from .store import BrainOSStore


def explain_recall(store: BrainOSStore, query: str, *, session_id: str | None = None, limit: int = 5) -> dict[str, Any]:
    payload = store.recall(query, session_id=session_id, limit=limit)

    def compact_hits(items: list[dict[str, Any]], *, fields: list[str]) -> list[dict[str, Any]]:
        out = []
        for item in items[:limit]:
            row = {field: item.get(field) for field in fields}
            if "score_components" in item:
                row["score_components"] = item.get("score_components")
            if "match_sources" in item:
                row["match_sources"] = item.get("match_sources")
            if "vector_distance" in item:
                row["vector_distance"] = item.get("vector_distance")
            if "lexical_overlap" in item:
                row["lexical_overlap"] = item.get("lexical_overlap")
            out.append(row)
        return out

    return {
        "query": query,
        "session_id": session_id,
        "mode": payload.get("mode"),
        "summary": payload.get("summary"),
        "episode_vector_mode": payload.get("episode_vector_mode"),
        "episode_vector_error": payload.get("episode_vector_error"),
        "semantic_vector_mode": payload.get("semantic_vector_mode"),
        "semantic_vector_error": payload.get("semantic_vector_error"),
        "top_ranked_episodes": compact_hits(
            payload.get("ranked_episodes", []),
            fields=["id", "content", "rank_score"],
        ),
        "top_ranked_semantic_hits": compact_hits(
            payload.get("ranked_semantic_hits", []),
            fields=["id", "name", "type", "rank_score"],
        ),
    }
