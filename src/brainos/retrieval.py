from __future__ import annotations

import sqlite3
from typing import Protocol, Any

from .errors import BrainOSError
from .retrieval_policy import RETRIEVAL_SCORING_POLICY_V1, RetrievalScoringPolicy
from .retrieval_runtime import vector_runtime_preflight


class RetrievalBackend(Protocol):
    def search_episodes_text(self, query: str, *, session_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]: ...
    def sqlite_vec_capability(self) -> dict[str, Any]: ...
    def embed_retrieval_query(self, query: str) -> list[float]: ...
    def vector_search_episodes(
        self, query_vector: list[float], *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]: ...
    def semantic_name_hits(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]: ...
    def vector_search_semantic_nodes(self, query_vector: list[float], *, limit: int = 10) -> list[dict[str, Any]]: ...
    def search_decisions_text(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]: ...


class RetrievalService:
    def __init__(self, backend: RetrievalBackend, *, scoring_policy: RetrievalScoringPolicy = RETRIEVAL_SCORING_POLICY_V1):
        self.backend = backend
        self.scoring_policy = scoring_policy

    @staticmethod
    def tokenize_for_overlap(text: str) -> set[str]:
        normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return {token for token in normalized.split() if len(token) >= 3}

    @staticmethod
    def _query_alias_expansions(query_tokens: set[str]) -> set[str]:
        aliases = {
            "fix": {"repair", "reindex"},
            "repair": {"reindex"},
            "reindex": {"repair"},
            "reindexing": {"reindex", "repair"},
        }
        expanded = set(query_tokens)
        for token in tuple(query_tokens):
            expanded.update(aliases.get(token, set()))
        return expanded

    @staticmethod
    def _anchor_terms(query_tokens: set[str]) -> set[str]:
        anchors = {
            "posture", "ssot", "restart", "anchors", "anchor", "memory", "maintenance", "heartbeat",
            "brainos", "openclaw", "gwork", "google", "workspace", "collaboration", "testing",
        }
        return query_tokens & anchors

    @staticmethod
    def _episode_kind_bonus(kind: str | None) -> float:
        if kind == "decision":
            return 120.0
        if kind == "procedure":
            return 90.0
        if kind == "fact":
            return 40.0
        return 0.0

    @staticmethod
    def _continuation_query_intent(query_tokens: set[str]) -> str | None:
        if {"next", "step"} & query_tokens or "continue" in query_tokens or "continuation" in query_tokens:
            return "next_step"
        if "restart" in query_tokens or "resume" in query_tokens or "leave" in query_tokens:
            return "restart_point"
        if "direction" in query_tokens or "active" in query_tokens or "front" in query_tokens:
            return "current_direction"
        return None

    @staticmethod
    def _procedure_query_intent(query_tokens: set[str]) -> bool:
        procedure_triggers = {"fix", "repair", "reindex", "reindexing", "steps", "step", "how"}
        return bool(query_tokens & procedure_triggers)

    @staticmethod
    def _procedure_intent_bonus(*, procedure_intent: bool, metadata: dict[str, Any], content: str) -> float:
        if not procedure_intent:
            return 0.0
        kind = metadata.get("kind")
        lowered = content.lower()
        if kind == "procedure":
            return 120.0
        if lowered.startswith("to ") and (" run " in lowered or " verify " in lowered):
            return 40.0
        return 0.0

    @staticmethod
    def _continuation_intent_bonus(*, intent: str | None, metadata: dict[str, Any], content: str) -> float:
        lowered = content.lower()
        if intent == "next_step":
            kind = metadata.get("kind")
            if kind == "procedure" or lowered.startswith("next step:"):
                return 140.0
            if lowered.startswith("current restart point:") or lowered.startswith("previous restart point:"):
                return -80.0
            return 0.0
        if intent == "restart_point":
            if lowered.startswith("current restart point:"):
                return 24.0
            return 0.0
        return 0.0

    @staticmethod
    def _authority_bonus(authority: str | None, query_tokens: set[str], configured_bonus: float) -> float:
        if authority != "canonical":
            return 0.0
        authority_triggers = {"ssot", "source", "truth", "canonical", "authoritative"}
        return configured_bonus if query_tokens & authority_triggers else 0.0

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
        continuation_intent = self._continuation_query_intent(query_tokens)
        procedure_intent = self._procedure_query_intent(query_tokens)
        for idx, item in enumerate(episodes):
            merged = dict(item)
            metadata = item.get("metadata") or {}
            content = item.get("content", "")
            item_tokens = self.tokenize_for_overlap(content)
            anchor_overlap = len(anchor_terms & item_tokens)
            weak_anchor_penalty = self.scoring_policy.weak_anchor_penalty if anchor_terms and anchor_overlap == 0 else 0.0
            anchor_bonus = float(anchor_overlap) * self.scoring_policy.anchor_term_bonus
            kind_bonus = self._episode_kind_bonus(metadata.get("kind"))
            authority_bonus = self._authority_bonus(metadata.get("authority"), query_tokens, self.scoring_policy.authority_bonus)
            continuation_bonus = self._continuation_intent_bonus(intent=continuation_intent, metadata=metadata, content=content)
            procedure_bonus = self._procedure_intent_bonus(procedure_intent=procedure_intent, metadata=metadata, content=content)
            merged["match_sources"] = ["fts"]
            merged["rank_score"] = (1000.0 - float(idx)) + anchor_bonus + kind_bonus + authority_bonus + continuation_bonus + procedure_bonus - weak_anchor_penalty
            merged["lexical_overlap"] = len(query_tokens & item_tokens)
            merged["score_components"] = {
                "fts_rank": 1000.0 - float(idx),
                "anchor_term_bonus": anchor_bonus,
                "kind_bonus": kind_bonus,
                "authority_bonus": authority_bonus,
                "continuation_intent_bonus": continuation_bonus,
                "procedure_intent_bonus": procedure_bonus,
                "weak_anchor_penalty": weak_anchor_penalty,
            }
            ranked_map[item["id"]] = merged

        for idx, item in enumerate(vector_episodes):
            item_id = item["id"]
            metadata = item.get("metadata") or {}
            content = item.get("content", "")
            distance = float(item.get("distance", 999999.0))
            item_tokens = self.tokenize_for_overlap(content)
            overlap = len(query_tokens & item_tokens)
            anchor_overlap = len(anchor_terms & item_tokens)
            if distance > self.scoring_policy.vector_distance_cutoff and item_id not in ranked_map:
                continue
            score = max(0.0, self.scoring_policy.episode_vector_base - (distance * 100.0) - (idx * 5.0))
            overlap_bonus = min(float(overlap), 3.0) * self.scoring_policy.lexical_vector_overlap_bonus
            anchor_bonus = float(anchor_overlap) * self.scoring_policy.anchor_term_bonus
            kind_bonus = self._episode_kind_bonus(metadata.get("kind"))
            authority_bonus = self._authority_bonus(metadata.get("authority"), query_tokens, self.scoring_policy.authority_bonus)
            continuation_bonus = self._continuation_intent_bonus(intent=continuation_intent, metadata=metadata, content=content)
            procedure_bonus = self._procedure_intent_bonus(procedure_intent=procedure_intent, metadata=metadata, content=content)
            score += overlap_bonus + anchor_bonus + kind_bonus + authority_bonus + continuation_bonus + procedure_bonus
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
                        "kind_bonus": kind_bonus,
                        "authority_bonus": authority_bonus,
                        "continuation_intent_bonus": continuation_bonus,
                        "procedure_intent_bonus": procedure_bonus,
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
                    "kind_bonus": kind_bonus,
                    "authority_bonus": authority_bonus,
                    "continuation_intent_bonus": continuation_bonus,
                    "procedure_intent_bonus": procedure_bonus,
                }
                ranked_map[item_id] = merged

        return sorted(
            ranked_map.values(),
            key=lambda item: (-float(item.get("rank_score", 0.0)), str(item.get("id", ""))),
        )[:limit]

    @staticmethod
    def _semantic_name_query(query: str) -> str:
        semantic_aliases = {
            "writes": "wal",
            "write": "wal",
            "durability": "wal",
            "safe": "wal",
        }
        stopwords = {
            "brainos", "current", "what", "when", "where", "which", "who", "does",
            "help", "helps", "local", "keep", "the", "is", "are", "should",
        }
        normalized = []
        for token in RetrievalService.tokenize_for_overlap(query):
            mapped = semantic_aliases.get(token, token)
            if mapped in stopwords:
                continue
            normalized.append(mapped)
        deduped = list(dict.fromkeys(normalized))
        return " ".join(deduped) if deduped else " ".join(RetrievalService.tokenize_for_overlap(query))

    def _semantic_name_hits(self, query: str, *, limit: int) -> list[dict[str, Any]]:
        return self.backend.semantic_name_hits(self._semantic_name_query(query), limit=limit)

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
        semantic_hits: list[dict[str, Any]],
        vector_semantic_hits: list[dict[str, Any]],
        decisions: list[dict[str, Any]],
    ) -> str:
        parts = [
            f"episodes:{len(episodes)}",
            f"vector_episodes:{len(vector_episodes)}",
            f"semantic:{len(semantic_hits)}",
            f"vector_semantic:{len(vector_semantic_hits)}",
            f"decisions:{len(decisions)}",
        ]
        return ", ".join(parts)

    def recall(self, query: str, *, session_id: str | None = None, limit: int = 10) -> dict[str, Any]:
        try:
            runtime = vector_runtime_preflight()
        except sqlite3.Error as exc:
            raise BrainOSError(f"retrieval runtime failed: {exc}") from exc

        query_tokens = self._query_alias_expansions(self.tokenize_for_overlap(query))
        episodes = self.backend.search_episodes_text(query, session_id=session_id, limit=limit)
        semantic_hits = self._semantic_name_hits(query, limit=limit)
        decisions = self.backend.search_decisions_text(query, limit=limit)

        vector_episodes: list[dict[str, Any]] = []
        vector_semantic_hits: list[dict[str, Any]] = []
        episode_vector_mode = "disabled"
        semantic_vector_mode = "disabled"
        episode_vector_error = None
        semantic_vector_error = None

        if runtime.get("status") == "ok":
            try:
                query_vector = self.backend.embed_retrieval_query(query)
                vector_episodes = self.backend.vector_search_episodes(query_vector, session_id=session_id, limit=limit)
                vector_semantic_hits = self.backend.vector_search_semantic_nodes(query_vector, limit=limit)
                episode_vector_mode = "sqlite_vec_episode_similarity"
                semantic_vector_mode = "sqlite_vec_semantic_similarity"
            except Exception as exc:  # noqa: BLE001
                episode_vector_error = str(exc)
                semantic_vector_error = str(exc)
                episode_vector_mode = "vector_error"
                semantic_vector_mode = "vector_error"
        elif runtime.get("status") == "misconfigured":
            episode_vector_mode = "misconfigured"
            semantic_vector_mode = "misconfigured"
        elif runtime.get("status") == "runtime_failed":
            episode_vector_mode = "runtime_failed"
            semantic_vector_mode = "runtime_failed"

        ranked_episodes = self._rank_episode_hits(
            episodes=episodes,
            vector_episodes=vector_episodes,
            query_tokens=query_tokens,
            limit=limit,
        )
        ranked_semantic_hits = self._rank_semantic_hits(
            semantic_hits=semantic_hits,
            vector_semantic_hits=vector_semantic_hits,
            query_tokens=query_tokens,
            limit=limit,
        )

        zero_hit_reason = None
        if not ranked_episodes and not ranked_semantic_hits and not decisions:
            if runtime.get("status") == "misconfigured":
                zero_hit_reason = "runtime_misconfigured"
            elif runtime.get("status") == "runtime_failed":
                zero_hit_reason = "runtime_failed"
            else:
                zero_hit_reason = "no_matching_content"

        return {
            "query": query,
            "session_id": session_id,
            "mode": f"fts_plus_{episode_vector_mode}_plus_semantic_name_match_plus_decision_text",
            "scoring_policy_version": self.scoring_policy.version,
            "retrieval_runtime": runtime,
            "summary": self._build_summary(
                episodes=episodes,
                vector_episodes=vector_episodes,
                semantic_hits=semantic_hits,
                vector_semantic_hits=vector_semantic_hits,
                decisions=decisions,
            ),
            "episodes": episodes,
            "vector_episodes": vector_episodes,
            "ranked_episodes": ranked_episodes,
            "semantic_hits": semantic_hits,
            "vector_semantic_hits": vector_semantic_hits,
            "ranked_semantic_hits": ranked_semantic_hits,
            "decisions": decisions,
            "decision_count": len(decisions),
            "ranked_count": len(ranked_episodes),
            "ranked_semantic_count": len(ranked_semantic_hits),
            "episode_vector_mode": episode_vector_mode,
            "episode_vector_error": episode_vector_error,
            "semantic_vector_mode": semantic_vector_mode,
            "semantic_vector_error": semantic_vector_error,
            "zero_hit_reason": zero_hit_reason,
        }
