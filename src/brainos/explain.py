from __future__ import annotations

from typing import Any


def _top_hit_evidence(*, payload: dict[str, Any]) -> dict[str, Any] | None:
    ranked = payload.get("ranked_episodes", [])
    if not ranked:
        return None
    top = ranked[0]
    return {
        "id": top.get("id"),
        "kind": (top.get("metadata") or {}).get("kind"),
        "match_sources": top.get("match_sources") or [],
        "lexical_overlap": top.get("lexical_overlap") or 0,
        "vector_distance": top.get("vector_distance"),
        "score_components": top.get("score_components") or {},
    }


def _comparison_hint(*, payload: dict[str, Any]) -> dict[str, Any] | None:
    ranked = payload.get("ranked_episodes", [])
    if len(ranked) < 2:
        return None
    top = ranked[0]
    second = ranked[1]
    top_score = float(top.get("rank_score") or 0.0)
    second_score = float(second.get("rank_score") or 0.0)
    return {
        "top_id": top.get("id"),
        "runner_up_id": second.get("id"),
        "score_gap": round(top_score - second_score, 3),
        "top_kind": (top.get("metadata") or {}).get("kind"),
        "runner_up_kind": (second.get("metadata") or {}).get("kind"),
    }


def _confidence_hint(*, payload: dict[str, Any]) -> str | None:
    ranked = payload.get("ranked_episodes", [])
    if len(ranked) < 2:
        return None
    top = ranked[0]
    second = ranked[1]
    top_score = float(top.get("rank_score") or 0.0)
    second_score = float(second.get("rank_score") or 0.0)
    if abs(top_score - second_score) <= 40.0:
        return "tight_ranking"
    return None


def _operator_summary(*, payload: dict[str, Any]) -> str:
    runtime = payload.get("retrieval_runtime") or {}
    ranked = payload.get("ranked_episodes", [])
    if runtime.get("status") == "misconfigured" and not ranked:
        return "retrieval degraded: vector runtime is not configured; lexical retrieval may still work; check BRAINOS_SQLITE_VEC_PATH"
    if runtime.get("status") == "runtime_failed" and not ranked:
        return "retrieval degraded: sqlite-vec runtime preflight failed; lexical retrieval may still work"
    if ranked:
        top = ranked[0]
        sources = set(top.get("match_sources") or [])
        kind = (top.get("metadata") or {}).get("kind")
        kind_suffix = f"; kind={kind}" if kind else ""
        prefix = ""
        if runtime.get("status") == "misconfigured":
            prefix = "retrieval degraded: vector runtime is not configured; lexical retrieval may still work and did participate here; "
        elif runtime.get("status") == "runtime_failed":
            prefix = "retrieval degraded: sqlite-vec runtime preflight failed; lexical retrieval may still work and did participate here; "
        if len(sources) >= 2:
            return f"{prefix}top hit supported by lexical and vector evidence{kind_suffix}"
        if "vector" in sources:
            return f"{prefix}top hit is primarily vector-led{kind_suffix}"
        if "fts" in sources:
            return f"{prefix}top hit is primarily lexical{kind_suffix}"
    if payload.get("ranked_semantic_hits"):
        return "semantic hits returned without ranked episodic support"
    if payload.get("decisions"):
        return "decision hits returned without ranked episodic support"
    return "no ranked hits returned"

from .store import BrainOSStore


def _diagnostic_hint(*, payload: dict[str, Any]) -> str:
    runtime = payload.get("retrieval_runtime") or {}
    has_any_hits = bool(payload.get("ranked_episodes") or payload.get("ranked_semantic_hits") or payload.get("decisions"))
    if runtime.get("status") == "misconfigured" and not has_any_hits:
        return "configure_sqlite_vec_path_before_quality_debug"
    if runtime.get("status") == "runtime_failed" and not has_any_hits:
        return "inspect_sqlite_vec_runtime_failure_before_quality_debug"
    ranked = payload.get("ranked_episodes", [])
    if ranked:
        top = ranked[0]
        sources = set(top.get("match_sources") or [])
        overlap = top.get("lexical_overlap") or 0
        has_vector_distance = top.get("vector_distance") is not None
        if len(sources) >= 2:
            return "dual_source_agreement"
        if has_vector_distance and overlap > 0:
            return "vector_primary_with_lexical_support"
        if has_vector_distance:
            return "vector_led_top_hit"
        if overlap > 0:
            return "lexical_grounded_top_hit"
    if payload.get("episode_vector_mode") != "sqlite_vec_episode_similarity" or payload.get("semantic_vector_mode") != "sqlite_vec_semantic_similarity":
        return "inspect_vector_participation"
    return "inspect_score_components"


def explain_recall(store: BrainOSStore, query: str, *, session_id: str | None = None, limit: int = 5) -> dict[str, Any]:
    payload = store.recall(query, session_id=session_id, limit=limit)

    def compact_hits(items: list[dict[str, Any]], *, fields: list[str]) -> list[dict[str, Any]]:
        out = []
        for item in items[:limit]:
            row = {field: item.get(field) for field in fields}
            if "metadata" in item:
                row["metadata"] = item.get("metadata")
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
        "scoring_policy_version": payload.get("scoring_policy_version"),
        "summary": payload.get("summary"),
        "retrieval_runtime": payload.get("retrieval_runtime"),
        "zero_hit_reason": payload.get("zero_hit_reason"),
        "episode_vector_mode": payload.get("episode_vector_mode"),
        "episode_vector_error": payload.get("episode_vector_error"),
        "semantic_vector_mode": payload.get("semantic_vector_mode"),
        "semantic_vector_error": payload.get("semantic_vector_error"),
        "diagnostic_hint": _diagnostic_hint(payload=payload),
        "operator_summary": _operator_summary(payload=payload),
        "confidence_hint": _confidence_hint(payload=payload),
        "top_hit_evidence": _top_hit_evidence(payload=payload),
        "comparison_hint": _comparison_hint(payload=payload),
        "top_ranked_episodes": compact_hits(
            payload.get("ranked_episodes", []),
            fields=["id", "content", "rank_score"],
        ),
        "top_ranked_semantic_hits": compact_hits(
            payload.get("ranked_semantic_hits", []),
            fields=["id", "name", "type", "rank_score"],
        ),
        "top_decisions": compact_hits(
            payload.get("decisions", []),
            fields=["decision_id", "question", "status", "recommended_option_id", "operator_call_required"],
        ),
    }
