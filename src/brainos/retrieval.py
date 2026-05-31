from __future__ import annotations

import sqlite3
from typing import Protocol, Any

from .errors import BrainOSError
from .retrieval_policy import RETRIEVAL_SCORING_POLICY_V1, RetrievalScoringPolicy


class RetrievalBackend(Protocol):
    def search_episodes_text(self, query: str, *, session_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]: ...
    def sqlite_vec_capability(self) -> dict[str, Any]: ...
    def embed_retrieval_query(self, query: str) -> list[float]: ...
    def vector_search_episodes(
        self, query_vector: list[float], *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]: ...
    def semantic_name_hits(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]: ...
    def vector_search_semantic_nodes(self, query_vector: list[float], *, limit: int = 10) -> list[dict[str, Any]]: ...


class RetrievalService:
    def __init__(self, backend: RetrievalBackend, *, scoring_policy: RetrievalScoringPolicy = RETRIEVAL_SCORING_POLICY_V1):
        self.backend = backend
        self.scoring_policy = scoring_policy

    @staticmethod
    def tokenize_for_overlap(text: str) -> set[str]:
        normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return {token for token in normalized.split() if len(token) >= 3}

    @staticmethod
    def _anchor_terms(query_tokens: set[str]) -> set[str]:
        anchors = {
            'posture', 'ssot', 'restart', 'anchors', 'anchor', 'memory', 'maintenance', 'heartbeat',
            'brainos', 'openclaw', 'gwork', 'google', 'workspace', 'collaboration', 'testing'
        }
        return query_tokens & anchors

    def _rank_episode_hits(
        self,
        *,
        episodes: list[dict[str, Any]],
        vector_episodes: list[dict[str, Any]],
        query_tokens: set[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        ranked_map: dict[str, dict[str, Any]] = {}
        anchor_terms = self._anchor_terms(query_tokens)
        for idx, item in enumerate(episodes):
            merged = dict(item)
            item_tokens = self.tokenize_for_overlap(item.get("content", ""))
            anchor_overlap = len(anchor_terms & item_tokens)
            weak_anchor_penalty = self.scoring_policy.weak_anchor_penalty if anchor_terms and anchor_overlap == 0 else 0.0
            anchor_bonus = float(anchor_overlap) * self.scoring_policy.anchor_term_bonus
            merged["match_sources"] = ["fts"]
            merged["rank_score"] = (1000.0 - float(idx)) + anchor_bonus - weak_anchor_penalty
            merged["lexical_overlap"] = len(query_tokens & item_tokens)
            merged["score_components"] = {
                "fts_rank": 1000.0 - float(idx),
                "anchor_term_bonus": anchor_bonus,
                "weak_anchor_penalty": weak_anchor_penalty,
            }
            ranked_map[item["id"]] = merged

        for idx, item in enumerate(vector_episodes):
            item_id = item["id"]
            distance = float(item.get("distance", 999999.0))
            item_tokens = self.tokenize_for_overlap(item.get("content", ""))
            overlap = len(query_tokens & item_tokens)
            anchor_overlap = len(anchor_terms & item_tokens)
            if distance > self.scoring_policy.vector_distance_cutoff and item_id not in ranked_map:
                continue
            score = max(0.0, self.scoring_policy.episode_vector_base - (distance * 100.0) - (idx * 5.0))
            overlap_bonus = min(float(overlap), 3.0) * self.scoring_policy.lexical_vector_overlap_bonus
            anchor_bonus = float(anchor_overlap) * self.scoring_policy.anchor_term_bonus
            score += overlap_bonus + anchor_bonus
            if item_id in ranked_map:
                ranked_map[item_id]["match_sources"].append("vector")
                ranked_map[item_id]["rank_score"] += score + self.scoring_policy.dual_source_bonus
                ranked_map[item_id]["vector_distance"] = distance
                ranked_map[item_id]["lexical_overlap"] = overlap
                ranked_map[item_id].setdefault("score_components", {})
                ranked_map[item_id]["score_components"].update(
                    {
                        "episode_vector": score,
                        "dual_source_bonus": self.scoring_policy.dual_source_bonus,
                        "lexical_overlap_bonus": overlap_bonus,
                        "anchor_term_bonus": anchor_bonus,
                    }
                )
            else:
                score -= self.scoring_policy.low_overlap_vector_only_penalty if overlap == 0 else 0.0
                score -= self.scoring_policy.weak_anchor_penalty if anchor_terms and anchor_overlap == 0 else 0.0
                if score <= 0.0:
                    continue
                merged = dict(item)
                merged["match_sources"] = ["vector"]
                merged["rank_score"] = score
                merged["vector_distance"] = distance
                merged["lexical_overlap"] = overlap
                merged["score_components"] = {
                    "episode_vector": score,
                    "lexical_overlap_bonus": overlap_bonus,
                    "anchor_term_bonus": anchor_bonus,
                }
                ranked_map[item_id] = merged

        return sorted(
            ranked_map.values(),
            key=lambda item: (-float(item.get("rank_score", 0.0)), str(item.get("id", ""))),
        )[:limit]

    def _semantic_name_hits(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        return self.backend.semantic_name_hits(query, limit=limit)

    def _rank_semantic_hits(
        self,
        *,
        semantic_hits: list[dict[str, Any]],
        vector_semantic_hits: list[dict[str, Any]],
        query_tokens: set[str],
        limit: int,
    ) -> list[dict[str, Any]]:
        ranked_semantic_map: dict[str, dict[str, Any]] = {}
        for idx, item in enumerate(semantic_hits):
            merged = dict(item)
            merged["match_sources"] = ["name_match"]
            merged["rank_score"] = 1000.0 - float(idx) + self.scoring_policy.semantic_name_match_bonus
            merged["score_components"] = {
                "name_match_rank": 1000.0 - float(idx),
                "semantic_name_bonus": self.scoring_policy.semantic_name_match_bonus,
            }
            ranked_semantic_map[item["id"]] = merged

        for idx, item in enumerate(vector_semantic_hits):
            item_id = item["id"]
            distance = float(item.get("distance", 999999.0))
            item_tokens = self.tokenize_for_overlap(item.get("name", ""))
            overlap = len(query_tokens & item_tokens)
            if distance > self.scoring_policy.vector_distance_cutoff and item_id not in ranked_semantic_map:
                continue
            score = max(0.0, self.scoring_policy.semantic_vector_base - (distance * 100.0) - (idx * 5.0))
            overlap_bonus = min(float(overlap), 3.0) * self.scoring_policy.lexical_vector_overlap_bonus
            score += overlap_bonus
            if item_id in ranked_semantic_map:
                ranked_semantic_map[item_id]["match_sources"].append("vector")
                ranked_semantic_map[item_id]["rank_score"] += score + self.scoring_policy.dual_source_bonus
                ranked_semantic_map[item_id]["vector_distance"] = distance
                ranked_semantic_map[item_id]["lexical_overlap"] = overlap
                ranked_semantic_map[item_id].setdefault("score_components", {})
                ranked_semantic_map[item_id]["score_components"].update(
                    {
                        "semantic_vector": score,
                        "dual_source_bonus": self.scoring_policy.dual_source_bonus,
                        "lexical_overlap_bonus": overlap_bonus,
                    }
                )
            else:
                score -= self.scoring_policy.low_overlap_vector_only_penalty if overlap == 0 else 0.0
                if score <= 0.0:
                    continue
                merged = dict(item)
                merged["match_sources"] = ["vector"]
                merged["rank_score"] = score
                merged["vector_distance"] = distance
                merged["lexical_overlap"] = overlap
                merged["score_components"] = {
                    "semantic_vector": score,
                    "lexical_overlap_bonus": overlap_bonus,
                }
                ranked_semantic_map[item_id] = merged

        return sorted(
            ranked_semantic_map.values(),
            key=lambda item: (-float(item.get("rank_score", 0.0)), str(item.get("id", ""))),
        )[:limit]

    @staticmethod
    def _build_summary(
        *,
        episodes: list[dict[str, Any]],
        vector_episodes: list[dict[str, Any]],
        ranked_episodes: list[dict[str, Any]],
        semantic_hits: list[dict[str, Any]],
        vector_semantic_hits: list[dict[str, Any]],
        ranked_semantic_hits: list[dict[str, Any]],
    ) -> str:
        summary_parts = []
        if episodes:
            summary_parts.append(f"episodes:{len(episodes)}")
        if vector_episodes:
            summary_parts.append(f"vector_episodes:{len(vector_episodes)}")
        if ranked_episodes:
            summary_parts.append(f"ranked_episodes:{len(ranked_episodes)}")
        if semantic_hits:
            summary_parts.append(f"semantic_hits:{len(semantic_hits)}")
        if vector_semantic_hits:
            summary_parts.append(f"vector_semantic_hits:{len(vector_semantic_hits)}")
        if ranked_semantic_hits:
            summary_parts.append(f"ranked_semantic_hits:{len(ranked_semantic_hits)}")
        return ", ".join(summary_parts) if summary_parts else "no_hits"

    def recall(self, query: str, *, session_id: str | None = None, limit: int = 10) -> dict[str, Any]:
        episodes = self.backend.search_episodes_text(query, session_id=session_id, limit=limit)
        query_tokens = self.tokenize_for_overlap(query)
        vector_episodes: list[dict[str, Any]] = []
        vector_mode = "disabled"
        vector_error = None
        query_vector: list[float] | None = None

        capabilities = self.backend.sqlite_vec_capability()
        if capabilities.get("sqlite_vec"):
            try:
                query_vector = self.backend.embed_retrieval_query(query)
                vector_episodes = self.backend.vector_search_episodes(query_vector, session_id=session_id, limit=limit)
                vector_mode = "sqlite_vec_episode_similarity"
            except BrainOSError as exc:
                vector_mode = "error"
                vector_error = str(exc)
        else:
            vector_error = capabilities.get("sqlite_vec_error")

        episode_vector_mode = vector_mode
        episode_vector_error = vector_error
        ranked_episodes = self._rank_episode_hits(
            episodes=episodes,
            vector_episodes=vector_episodes,
            query_tokens=query_tokens,
            limit=limit,
        )

        semantic_hits = self._semantic_name_hits(query, limit=limit)
        vector_semantic_hits: list[dict[str, Any]] = []
        semantic_vector_mode = "disabled"
        semantic_vector_error = None

        if query_vector is not None and capabilities.get("sqlite_vec"):
            try:
                vector_semantic_hits = self.backend.vector_search_semantic_nodes(query_vector, limit=limit)
                semantic_vector_mode = "sqlite_vec_semantic_similarity"
            except (BrainOSError, sqlite3.Error) as exc:
                semantic_vector_mode = "error"
                semantic_vector_error = str(exc)
        else:
            semantic_vector_error = capabilities.get("sqlite_vec_error") if not capabilities.get("sqlite_vec") else None

        ranked_semantic_hits = self._rank_semantic_hits(
            semantic_hits=semantic_hits,
            vector_semantic_hits=vector_semantic_hits,
            query_tokens=query_tokens,
            limit=limit,
        )

        return {
            "query": query,
            "session_id": session_id,
            "episodes": episodes,
            "vector_episodes": vector_episodes,
            "ranked_episodes": ranked_episodes,
            "semantic_hits": semantic_hits,
            "vector_semantic_hits": vector_semantic_hits,
            "ranked_semantic_hits": ranked_semantic_hits,
            "count": len(episodes),
            "vector_count": len(vector_episodes),
            "ranked_count": len(ranked_episodes),
            "semantic_count": len(semantic_hits),
            "vector_semantic_count": len(vector_semantic_hits),
            "ranked_semantic_count": len(ranked_semantic_hits),
            "mode": "fts_plus_vector_episode_similarity_plus_semantic_name_match",
            "scoring_policy_version": self.scoring_policy.version,
            "vector_mode": vector_mode,
            "vector_error": vector_error,
            "episode_vector_mode": episode_vector_mode,
            "episode_vector_error": episode_vector_error,
            "semantic_vector_mode": semantic_vector_mode,
            "semantic_vector_error": semantic_vector_error,
            "summary": self._build_summary(
                episodes=episodes,
                vector_episodes=vector_episodes,
                ranked_episodes=ranked_episodes,
                semantic_hits=semantic_hits,
                vector_semantic_hits=vector_semantic_hits,
                ranked_semantic_hits=ranked_semantic_hits,
            ),
        }
