from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Iterator

from .decision_checks import decision_conflict_check
from .decisions import validate_decision_payload
from .embedding import DEFAULT_EMBEDDING_PROFILE, LiteLLMEmbeddingAdapter
from .errors import (
    BrainOSError,
    EmbeddingProviderNotConfiguredError,
    NotFoundError,
    PromotionError,
    ValidationError,
    VectorIndexContractError,
)
from .ledger import canonical_json, compute_event_hash
from .retrieval import RetrievalService
from .schema import detect_capabilities, get_schema_status, get_vec_table_sql, initialize_schema
from .sqlite_vec import sqlite_vec_readiness


class BrainOSStore:
    DEFAULT_EMBEDDING_PROFILE = DEFAULT_EMBEDDING_PROFILE
    VECTOR_STATUS_MISSING = "missing"
    VECTOR_STATUS_FRESH = "fresh"
    VECTOR_STATUS_STALE = "stale"
    VECTOR_STATUS_ERROR = "error"
    VECTOR_STATUS_DISABLED = "disabled"

    def __init__(self, db_path: str | Path, *, enable_vector: bool = False):
        self.db_path = str(db_path)
        self.enable_vector = enable_vector
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.retrieval = RetrievalService(self)

    def initialize(self) -> None:
        initialize_schema(self.conn, enable_vector=self.enable_vector)

    def schema_status(self) -> dict[str, Any]:
        return get_schema_status(self.conn)

    def capabilities(self) -> dict[str, Any]:
        return detect_capabilities(self.conn)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _decode_json_field(row: dict[str, Any], field: str) -> dict[str, Any] | list[Any] | None:
        value = row.get(field)
        if value is None:
            return None
        return json.loads(value)

    @staticmethod
    def _ensure_dict(value: Any, *, field_name: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be a JSON object")
        return value

    @staticmethod
    def _ensure_list_of_dicts(value: Any, *, field_name: str) -> list[dict[str, Any]]:
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise ValidationError(f"{field_name} must be a JSON array of objects")
        return value

    @staticmethod
    def _text_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def _text_preview(text: str, limit: int = 160) -> str:
        return text if len(text) <= limit else text[:limit]

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).replace(microsecond=0).isoformat()

    def _last_ledger_hash(self) -> str | None:
        row = self.conn.execute(
            "SELECT crypto_hash FROM ledger ORDER BY timestamp DESC, rowid DESC LIMIT 1"
        ).fetchone()
        return None if row is None else row[0]

    def _append_ledger(
        self,
        *,
        layer: str,
        action: str,
        payload: dict[str, Any],
        causal_event_id: str | None = None,
    ) -> str:
        event_id = str(uuid.uuid4())
        payload_json = canonical_json(payload)
        previous_hash = self._last_ledger_hash()
        crypto_hash = compute_event_hash(
            event_id=event_id,
            layer=layer,
            action=action,
            payload_json=payload_json,
            causal_event_id=causal_event_id,
            previous_hash=previous_hash,
        )
        self.conn.execute(
            """
            INSERT INTO ledger(event_id, layer, action, payload, causal_event_id, previous_hash, crypto_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (event_id, layer, action, payload_json, causal_event_id, previous_hash, crypto_hash),
        )
        return event_id

    def _canonical_episode_embedding_text(self, episode: dict[str, Any]) -> str:
        return episode["content"]

    def _canonical_semantic_node_embedding_text(self, node: dict[str, Any]) -> str:
        properties = node.get("properties") or {}
        properties_json = json.dumps(properties, ensure_ascii=False, sort_keys=True)
        return f"{node['name']}\nType: {node['type']}\nProperties: {properties_json}"

    def _set_vector_index_state(
        self,
        *,
        object_type: str,
        object_id: str,
        source_text: str,
        embedding_profile: str,
        vector_status: str,
        embedding_provider: str | None = None,
        embedding_model: str | None = None,
        embedding_dimensions: int | None = None,
        last_embedded_at: str | None = None,
        last_error: str | None = None,
        last_error_at: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO vector_index_state(
                object_type, object_id, source_text_hash, source_text_preview,
                embedding_profile, embedding_provider, embedding_model, embedding_dimensions,
                vector_status, last_embedded_at, last_error, last_error_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(object_type, object_id) DO UPDATE SET
                source_text_hash=excluded.source_text_hash,
                source_text_preview=excluded.source_text_preview,
                embedding_profile=excluded.embedding_profile,
                embedding_provider=excluded.embedding_provider,
                embedding_model=excluded.embedding_model,
                embedding_dimensions=excluded.embedding_dimensions,
                vector_status=excluded.vector_status,
                last_embedded_at=excluded.last_embedded_at,
                last_error=excluded.last_error,
                last_error_at=excluded.last_error_at,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                object_type,
                object_id,
                self._text_hash(source_text),
                self._text_preview(source_text),
                embedding_profile,
                embedding_provider,
                embedding_model,
                embedding_dimensions,
                vector_status,
                last_embedded_at,
                last_error,
                last_error_at,
            ),
        )

    def get_vector_index_state(self, object_type: str, object_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT object_type, object_id, source_text_hash, source_text_preview,
                   embedding_profile, embedding_provider, embedding_model, embedding_dimensions,
                   vector_status, last_embedded_at, last_error, last_error_at, updated_at
            FROM vector_index_state
            WHERE object_type = ? AND object_id = ?
            """,
            (object_type, object_id),
        ).fetchone()
        return None if row is None else dict(row)

    def list_vector_index_states(
        self, *, object_type: str | None = None, vector_status: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        conditions = []
        params: list[Any] = []
        if object_type is not None:
            conditions.append("object_type = ?")
            params.append(object_type)
        if vector_status is not None:
            conditions.append("vector_status = ?")
            params.append(vector_status)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)
        rows = self.conn.execute(
            f"""
            SELECT object_type, object_id, source_text_hash, source_text_preview,
                   embedding_profile, embedding_provider, embedding_model, embedding_dimensions,
                   vector_status, last_embedded_at, last_error, last_error_at, updated_at
            FROM vector_index_state
            {where}
            ORDER BY object_type, object_id
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()
        return [dict(r) for r in rows]

    def sqlite_vec_capability(self) -> dict[str, Any]:
        return self.capabilities()

    def _sqlite_vec_capability(self) -> dict[str, Any]:
        return self.sqlite_vec_capability()

    def embed_retrieval_query(self, query: str) -> list[float]:
        embedding = self.embed_texts([query], profile=self.DEFAULT_EMBEDDING_PROFILE)
        return embedding["vectors"][0]

    def semantic_name_hits(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        semantic_hits = []
        query_lower = query.lower()
        node_rows = self.conn.execute(
            "SELECT id, name, type, properties FROM semantic_nodes ORDER BY name"
        ).fetchall()
        for row in node_rows:
            item = dict(row)
            if query_lower in item["name"].lower():
                item["properties"] = self._decode_json_field(item, "properties") or {}
                item["edges"] = self.list_semantic_edges(item["id"], direction="both")
                semantic_hits.append(item)
                if len(semantic_hits) >= limit:
                    break
        return semantic_hits

    @staticmethod
    def _decision_retrieval_projection(decision: dict[str, Any]) -> str:
        parts: list[str] = []
        if decision.get("question"):
            parts.append(str(decision["question"]))
        if decision.get("recommended_option_id"):
            parts.append(f"recommended option {decision['recommended_option_id']}")
        for option in decision.get("options", []):
            if option.get("option_id"):
                parts.append(f"option {option['option_id']}")
            if option.get("label"):
                parts.append(str(option["label"]))
            if option.get("summary"):
                parts.append(str(option["summary"]))
        for field in (
            "arguments",
            "counterarguments",
            "risks",
            "missing_information",
            "uncertainty_notes",
        ):
            for item in decision.get(field, []):
                if isinstance(item, dict):
                    for key in ("text", "kind", "option_id"):
                        value = item.get(key)
                        if isinstance(value, str) and value.strip():
                            parts.append(value.strip())
                elif isinstance(item, str) and item.strip():
                    parts.append(item.strip())
        metadata = decision.get("metadata") or {}
        for key in ("entity_id", "source_case"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
        return "\n".join(parts)

    def search_decisions_text(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        query_tokens = RetrievalService.tokenize_for_overlap(query)
        query_lower = query.lower()
        rows = self.conn.execute(
            """
            SELECT decision_id, question, status, recommended_option_id, operator_call_required,
                   options_json, arguments_json, counterarguments_json, risks_json,
                   missing_information_json, uncertainty_notes_json, review_after,
                   metadata_json, created_at, updated_at
            FROM decisions
            ORDER BY updated_at DESC, rowid DESC
            """
        ).fetchall()
        ranked: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            item = self._decode_decision_row(row)
            projection = self._decision_retrieval_projection(item)
            projection_lower = projection.lower()
            projection_tokens = RetrievalService.tokenize_for_overlap(projection)
            token_overlap = query_tokens & projection_tokens
            score = float(len(token_overlap))
            if query_lower in projection_lower:
                score += 5.0
            if item.get("question") and query_lower in str(item["question"]).lower():
                score += 2.0
            if score <= 0:
                continue
            enriched = dict(item)
            enriched["match_score"] = score
            enriched["match_terms"] = sorted(token_overlap)
            enriched["retrieval_projection"] = projection
            ranked.append((score, enriched))
        ranked.sort(key=lambda pair: (pair[0], pair[1].get("updated_at", "")), reverse=True)
        return [item for _, item in ranked[:limit]]

    def sqlite_vec_readiness(self) -> dict[str, Any]:
        return sqlite_vec_readiness(self.conn)

    def _vec_table_dimensions(self, table_name: str) -> int | None:
        row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        if row is None or row[0] is None:
            return None
        sql = str(row[0])
        marker = "embedding FLOAT["
        if marker not in sql:
            return None
        tail = sql.split(marker, 1)[1]
        dim_text = tail.split("]", 1)[0].strip()
        return int(dim_text)

    def _ensure_vec_table_contract(self, table_name: str, dimensions: int) -> None:
        current_dimensions = self._vec_table_dimensions(table_name)
        if current_dimensions is None:
            self.conn.execute(get_vec_table_sql(dimensions, table_name=table_name))
            return
        if current_dimensions != dimensions:
            raise VectorIndexContractError(
                f"vector index dimension mismatch: table={table_name}, expected={current_dimensions}, got={dimensions}; rebuild required"
            )

    def _ensure_episode_vec_table(self, dimensions: int) -> None:
        self._ensure_vec_table_contract("episodes_vec", dimensions)

    def _ensure_semantic_node_vec_table(self, dimensions: int) -> None:
        self._ensure_vec_table_contract("semantic_nodes_vec", dimensions)

    def _vec_table_exists(self, table_name: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        return row is not None

    def _upsert_episode_vector(self, episode_id: str, vector: list[float], dimensions: int) -> None:
        self._ensure_episode_vec_table(dimensions)
        vector_json = json.dumps(vector, ensure_ascii=False)
        self.conn.execute("DELETE FROM episodes_vec WHERE id = ?", (episode_id,))
        self.conn.execute(
            "INSERT INTO episodes_vec(id, embedding) VALUES (?, ?)",
            (episode_id, vector_json),
        )

    def _upsert_semantic_node_vector(self, node_id: str, vector: list[float], dimensions: int) -> None:
        self._ensure_semantic_node_vec_table(dimensions)
        vector_json = json.dumps(vector, ensure_ascii=False)
        self.conn.execute("DELETE FROM semantic_nodes_vec WHERE id = ?", (node_id,))
        self.conn.execute(
            "INSERT INTO semantic_nodes_vec(id, embedding) VALUES (?, ?)",
            (node_id, vector_json),
        )

    def vector_search_episodes(
        self, query_vector: list[float], *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        if not self._vec_table_exists("episodes_vec"):
            return []
        vector_json = json.dumps(query_vector, ensure_ascii=False)
        if session_id:
            rows = self.conn.execute(
                """
                SELECT e.id, e.session_id, e.timestamp, e.content, e.metadata, v.distance
                FROM episodes_vec v
                JOIN episodes e ON e.id = v.id
                WHERE v.embedding MATCH ? AND k = ? AND e.session_id = ?
                ORDER BY v.distance ASC
                """,
                (vector_json, limit, session_id),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT e.id, e.session_id, e.timestamp, e.content, e.metadata, v.distance
                FROM episodes_vec v
                JOIN episodes e ON e.id = v.id
                WHERE v.embedding MATCH ? AND k = ?
                ORDER BY v.distance ASC
                """,
                (vector_json, limit),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._decode_json_field(item, "metadata") or {}
            promotion = self.get_episode_promotion(item["id"])
            if promotion is not None:
                item["promotion"] = promotion
            vector_state = self.get_vector_index_state("episode", item["id"])
            if vector_state is not None:
                item["vector_state"] = vector_state
            result.append(item)
        return result

    def _vector_search_episodes(
        self, query_vector: list[float], *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        return self.vector_search_episodes(query_vector, session_id=session_id, limit=limit)

    def vector_search_semantic_nodes(self, query_vector: list[float], *, limit: int = 10) -> list[dict[str, Any]]:
        if not self._vec_table_exists("semantic_nodes_vec"):
            return []
        vector_json = json.dumps(query_vector, ensure_ascii=False)
        rows = self.conn.execute(
            """
            SELECT n.id, n.name, n.type, n.properties, v.distance
            FROM semantic_nodes_vec v
            JOIN semantic_nodes n ON n.id = v.id
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance ASC
            """,
            (vector_json, limit),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["properties"] = self._decode_json_field(item, "properties") or {}
            item["edges"] = self.list_semantic_edges(item["id"], direction="both")
            vector_state = self.get_vector_index_state("semantic_node", item["id"])
            if vector_state is not None:
                item["vector_state"] = vector_state
            result.append(item)
        return result

    def _vector_search_semantic_nodes(self, query_vector: list[float], *, limit: int = 10) -> list[dict[str, Any]]:
        return self.vector_search_semantic_nodes(query_vector, limit=limit)

    def get_embedding_profile_contract(self) -> dict[str, Any]:
        contract = LiteLLMEmbeddingAdapter(profile=self.DEFAULT_EMBEDDING_PROFILE).contract()
        contract["text_object_families"] = ["episode", "semantic_node"]
        contract["vector_storage"] = {
            "kind": "sqlite-vec",
            "status": "capability_gated",
            "object_families": ["episode", "semantic_node"],
        }
        return contract

    def embed_texts(self, texts: list[str], profile: str | None = None) -> dict[str, Any]:
        adapter = LiteLLMEmbeddingAdapter(profile=profile or self.DEFAULT_EMBEDDING_PROFILE)
        return adapter.embed_texts(texts)

    def mark_episode_vector_missing(self, episode_id: str, *, embedding_profile: str | None = None) -> None:
        episode = self.get_episode(episode_id)
        if episode is None:
            raise NotFoundError(f"episode not found: {episode_id}")
        self._set_vector_index_state(
            object_type="episode",
            object_id=episode_id,
            source_text=self._canonical_episode_embedding_text(episode),
            embedding_profile=embedding_profile or self.DEFAULT_EMBEDDING_PROFILE,
            vector_status=self.VECTOR_STATUS_MISSING,
        )

    def mark_semantic_node_vector_missing(self, node_id: str, *, embedding_profile: str | None = None) -> None:
        node = self.get_semantic_node(node_id)
        if node is None:
            raise NotFoundError(f"semantic node not found: {node_id}")
        self._set_vector_index_state(
            object_type="semantic_node",
            object_id=node_id,
            source_text=self._canonical_semantic_node_embedding_text(node),
            embedding_profile=embedding_profile or self.DEFAULT_EMBEDDING_PROFILE,
            vector_status=self.VECTOR_STATUS_MISSING,
        )

    def refresh_vector_freshness_for_episode(self, episode_id: str, *, embedding_profile: str | None = None) -> dict[str, Any]:
        episode = self.get_episode(episode_id)
        if episode is None:
            raise NotFoundError(f"episode not found: {episode_id}")
        source_text = self._canonical_episode_embedding_text(episode)
        state = self.get_vector_index_state("episode", episode_id)
        profile = embedding_profile or self.DEFAULT_EMBEDDING_PROFILE
        if state is None:
            self._set_vector_index_state(
                object_type="episode",
                object_id=episode_id,
                source_text=source_text,
                embedding_profile=profile,
                vector_status=self.VECTOR_STATUS_MISSING,
            )
        elif state["source_text_hash"] != self._text_hash(source_text) or state["embedding_profile"] != profile:
            self._set_vector_index_state(
                object_type="episode",
                object_id=episode_id,
                source_text=source_text,
                embedding_profile=profile,
                vector_status=self.VECTOR_STATUS_STALE,
                embedding_provider=state.get("embedding_provider"),
                embedding_model=state.get("embedding_model"),
                embedding_dimensions=state.get("embedding_dimensions"),
                last_embedded_at=state.get("last_embedded_at"),
                last_error=state.get("last_error"),
                last_error_at=state.get("last_error_at"),
            )
        return self.get_vector_index_state("episode", episode_id) or {}

    def refresh_vector_freshness_for_semantic_node(
        self, node_id: str, *, embedding_profile: str | None = None
    ) -> dict[str, Any]:
        node = self.get_semantic_node(node_id)
        if node is None:
            raise NotFoundError(f"semantic node not found: {node_id}")
        source_text = self._canonical_semantic_node_embedding_text(node)
        state = self.get_vector_index_state("semantic_node", node_id)
        profile = embedding_profile or self.DEFAULT_EMBEDDING_PROFILE
        if state is None:
            self._set_vector_index_state(
                object_type="semantic_node",
                object_id=node_id,
                source_text=source_text,
                embedding_profile=profile,
                vector_status=self.VECTOR_STATUS_MISSING,
            )
        elif state["source_text_hash"] != self._text_hash(source_text) or state["embedding_profile"] != profile:
            self._set_vector_index_state(
                object_type="semantic_node",
                object_id=node_id,
                source_text=source_text,
                embedding_profile=profile,
                vector_status=self.VECTOR_STATUS_STALE,
                embedding_provider=state.get("embedding_provider"),
                embedding_model=state.get("embedding_model"),
                embedding_dimensions=state.get("embedding_dimensions"),
                last_embedded_at=state.get("last_embedded_at"),
                last_error=state.get("last_error"),
                last_error_at=state.get("last_error_at"),
            )
        return self.get_vector_index_state("semantic_node", node_id) or {}

    def generate_episode_embedding(self, episode_id: str, *, embedding_profile: str | None = None) -> dict[str, Any]:
        episode = self.get_episode(episode_id)
        if episode is None:
            raise NotFoundError(f"episode not found: {episode_id}")
        profile = embedding_profile or self.DEFAULT_EMBEDDING_PROFILE
        source_text = self._canonical_episode_embedding_text(episode)
        try:
            result = self.embed_texts([source_text], profile=profile)
            capabilities = self._sqlite_vec_capability()
            with self.transaction():
                if not capabilities.get("sqlite_vec"):
                    self._set_vector_index_state(
                        object_type="episode",
                        object_id=episode_id,
                        source_text=source_text,
                        embedding_profile=profile,
                        vector_status=self.VECTOR_STATUS_DISABLED,
                        embedding_provider=result["provider"],
                        embedding_model=result["model"],
                        embedding_dimensions=result["dimensions"],
                        last_embedded_at=self._now_iso(),
                        last_error=capabilities.get("sqlite_vec_error"),
                        last_error_at=self._now_iso(),
                    )
                    return {
                        "ok": True,
                        "object_type": "episode",
                        "object_id": episode_id,
                        "vector_status": self.VECTOR_STATUS_DISABLED,
                        "embedding_profile": profile,
                        "dimensions": result["dimensions"],
                        "provider": result["provider"],
                        "model": result["model"],
                        "storage": "disabled",
                        "storage_reason": capabilities.get("sqlite_vec_error"),
                    }

                self._upsert_episode_vector(episode_id, result["vectors"][0], result["dimensions"])
                self._set_vector_index_state(
                    object_type="episode",
                    object_id=episode_id,
                    source_text=source_text,
                    embedding_profile=profile,
                    vector_status=self.VECTOR_STATUS_FRESH,
                    embedding_provider=result["provider"],
                    embedding_model=result["model"],
                    embedding_dimensions=result["dimensions"],
                    last_embedded_at=self._now_iso(),
                    last_error=None,
                    last_error_at=None,
                )
            return {
                "ok": True,
                "object_type": "episode",
                "object_id": episode_id,
                "vector_status": self.VECTOR_STATUS_FRESH,
                "embedding_profile": profile,
                "dimensions": result["dimensions"],
                "provider": result["provider"],
                "model": result["model"],
                "storage": "sqlite-vec",
            }
        except (BrainOSError, sqlite3.Error) as exc:
            with self.transaction():
                self._set_vector_index_state(
                    object_type="episode",
                    object_id=episode_id,
                    source_text=source_text,
                    embedding_profile=profile,
                    vector_status=self.VECTOR_STATUS_ERROR,
                    last_error=str(exc),
                    last_error_at=self._now_iso(),
                )
            raise

    def generate_semantic_node_embedding(self, node_id: str, *, embedding_profile: str | None = None) -> dict[str, Any]:
        node = self.get_semantic_node(node_id)
        if node is None:
            raise NotFoundError(f"semantic node not found: {node_id}")
        profile = embedding_profile or self.DEFAULT_EMBEDDING_PROFILE
        source_text = self._canonical_semantic_node_embedding_text(node)
        try:
            result = self.embed_texts([source_text], profile=profile)
            capabilities = self._sqlite_vec_capability()
            with self.transaction():
                if not capabilities.get("sqlite_vec"):
                    self._set_vector_index_state(
                        object_type="semantic_node",
                        object_id=node_id,
                        source_text=source_text,
                        embedding_profile=profile,
                        vector_status=self.VECTOR_STATUS_DISABLED,
                        embedding_provider=result["provider"],
                        embedding_model=result["model"],
                        embedding_dimensions=result["dimensions"],
                        last_embedded_at=self._now_iso(),
                        last_error=capabilities.get("sqlite_vec_error"),
                        last_error_at=self._now_iso(),
                    )
                    return {
                        "ok": True,
                        "object_type": "semantic_node",
                        "object_id": node_id,
                        "vector_status": self.VECTOR_STATUS_DISABLED,
                        "embedding_profile": profile,
                        "dimensions": result["dimensions"],
                        "provider": result["provider"],
                        "model": result["model"],
                        "storage": "disabled",
                        "storage_reason": capabilities.get("sqlite_vec_error"),
                    }

                self._upsert_semantic_node_vector(node_id, result["vectors"][0], result["dimensions"])
                self._set_vector_index_state(
                    object_type="semantic_node",
                    object_id=node_id,
                    source_text=source_text,
                    embedding_profile=profile,
                    vector_status=self.VECTOR_STATUS_FRESH,
                    embedding_provider=result["provider"],
                    embedding_model=result["model"],
                    embedding_dimensions=result["dimensions"],
                    last_embedded_at=self._now_iso(),
                    last_error=None,
                    last_error_at=None,
                )
            return {
                "ok": True,
                "object_type": "semantic_node",
                "object_id": node_id,
                "vector_status": self.VECTOR_STATUS_FRESH,
                "embedding_profile": profile,
                "dimensions": result["dimensions"],
                "provider": result["provider"],
                "model": result["model"],
                "storage": "sqlite-vec",
            }
        except (BrainOSError, sqlite3.Error) as exc:
            with self.transaction():
                self._set_vector_index_state(
                    object_type="semantic_node",
                    object_id=node_id,
                    source_text=source_text,
                    embedding_profile=profile,
                    vector_status=self.VECTOR_STATUS_ERROR,
                    last_error=str(exc),
                    last_error_at=self._now_iso(),
                )
            raise

    def sync_vector_index(
        self,
        *,
        object_type: str,
        object_id: str,
        embedding_profile: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        if object_type == "episode":
            state = self.refresh_vector_freshness_for_episode(object_id, embedding_profile=embedding_profile)
            if force or state.get("vector_status") in {
                self.VECTOR_STATUS_MISSING,
                self.VECTOR_STATUS_STALE,
                self.VECTOR_STATUS_ERROR,
                self.VECTOR_STATUS_DISABLED,
            }:
                result = self.generate_episode_embedding(object_id, embedding_profile=embedding_profile)
                if isinstance(result, dict) and "action_hint" not in result:
                    result["action_hint"] = "reindex"
                return result
            return {"ok": True, "object_type": object_type, "object_id": object_id, "vector_status": state.get("vector_status"), "mode": "noop", "action_hint": "noop", "reason": "already_fresh"}

        if object_type == "semantic_node":
            state = self.refresh_vector_freshness_for_semantic_node(object_id, embedding_profile=embedding_profile)
            if force or state.get("vector_status") in {
                self.VECTOR_STATUS_MISSING,
                self.VECTOR_STATUS_STALE,
                self.VECTOR_STATUS_ERROR,
                self.VECTOR_STATUS_DISABLED,
            }:
                result = self.generate_semantic_node_embedding(object_id, embedding_profile=embedding_profile)
                if isinstance(result, dict) and "action_hint" not in result:
                    result["action_hint"] = "reindex"
                return result
            return {"ok": True, "object_type": object_type, "object_id": object_id, "vector_status": state.get("vector_status"), "mode": "noop", "action_hint": "noop", "reason": "already_fresh"}

        raise ValidationError("object_type must be one of: episode, semantic_node")

    def sync_vector_index_batch(
        self,
        *,
        object_type: str | None = None,
        vector_status: str | None = None,
        limit: int = 100,
        embedding_profile: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        states = self.list_vector_index_states(object_type=object_type, vector_status=vector_status, limit=limit)
        results = []
        errors = []
        seen: set[tuple[str, str]] = set()
        for state in states:
            key = (state["object_type"], state["object_id"])
            if key in seen:
                continue
            seen.add(key)
            try:
                results.append(
                    self.sync_vector_index(
                        object_type=state["object_type"],
                        object_id=state["object_id"],
                        embedding_profile=embedding_profile,
                        force=force,
                    )
                )
            except BrainOSError as exc:
                errors.append(
                    {
                        "object_type": state["object_type"],
                        "object_id": state["object_id"],
                        "error": str(exc),
                    }
                )
        return {
            "ok": len(errors) == 0,
            "requested": len(states),
            "synced": len(results),
            "errors": errors,
            "results": results,
        }

    @staticmethod
    def _decode_decision_row(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        item["operator_call_required"] = bool(item["operator_call_required"])
        for field in (
            "options_json",
            "arguments_json",
            "counterarguments_json",
            "risks_json",
            "missing_information_json",
            "uncertainty_notes_json",
            "metadata_json",
        ):
            value = item.pop(field)
            item[field.removesuffix("_json")] = json.loads(value)
        return item

    def log_decision(
        self,
        *,
        question: str,
        status: str,
        options: list[dict[str, Any]],
        arguments: list[Any],
        counterarguments: list[Any],
        risks: list[Any],
        missing_information: list[Any],
        uncertainty_notes: list[Any],
        metadata: dict[str, Any] | None = None,
        recommended_option_id: str | None = None,
        operator_call_required: bool = True,
        review_after: str | None = None,
        decision_id: str | None = None,
        causal_event_id: str | None = None,
    ) -> dict[str, Any]:
        metadata = metadata or {}
        decision_id = decision_id or str(uuid.uuid4())
        normalized = validate_decision_payload(
            question=question,
            status=status,
            options=options,
            arguments=arguments,
            counterarguments=counterarguments,
            risks=risks,
            missing_information=missing_information,
            uncertainty_notes=uncertainty_notes,
            metadata=metadata,
            recommended_option_id=recommended_option_id,
            operator_call_required=operator_call_required,
        )
        existed = self.get_decision(decision_id) is not None
        with self.transaction():
            self.conn.execute(
                """
                INSERT INTO decisions(
                    decision_id, question, status, recommended_option_id, operator_call_required,
                    options_json, arguments_json, counterarguments_json, risks_json,
                    missing_information_json, uncertainty_notes_json, review_after,
                    metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(decision_id) DO UPDATE SET
                    question=excluded.question,
                    status=excluded.status,
                    recommended_option_id=excluded.recommended_option_id,
                    operator_call_required=excluded.operator_call_required,
                    options_json=excluded.options_json,
                    arguments_json=excluded.arguments_json,
                    counterarguments_json=excluded.counterarguments_json,
                    risks_json=excluded.risks_json,
                    missing_information_json=excluded.missing_information_json,
                    uncertainty_notes_json=excluded.uncertainty_notes_json,
                    review_after=excluded.review_after,
                    metadata_json=excluded.metadata_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    decision_id,
                    normalized["question"],
                    normalized["status"],
                    normalized["recommended_option_id"],
                    1 if normalized["operator_call_required"] else 0,
                    json.dumps(normalized["options"], ensure_ascii=False),
                    json.dumps(normalized["arguments"], ensure_ascii=False),
                    json.dumps(normalized["counterarguments"], ensure_ascii=False),
                    json.dumps(normalized["risks"], ensure_ascii=False),
                    json.dumps(normalized["missing_information"], ensure_ascii=False),
                    json.dumps(normalized["uncertainty_notes"], ensure_ascii=False),
                    review_after,
                    json.dumps(normalized["metadata"], ensure_ascii=False),
                ),
            )
            self._append_ledger(
                layer="decision",
                action="UPDATE" if existed else "CREATE",
                payload={
                    "decision_id": decision_id,
                    "question": normalized["question"],
                    "status": normalized["status"],
                    "recommended_option_id": normalized["recommended_option_id"],
                    "operator_call_required": normalized["operator_call_required"],
                    "options": normalized["options"],
                    "arguments": normalized["arguments"],
                    "counterarguments": normalized["counterarguments"],
                    "risks": normalized["risks"],
                    "missing_information": normalized["missing_information"],
                    "uncertainty_notes": normalized["uncertainty_notes"],
                    "review_after": review_after,
                    "metadata": normalized["metadata"],
                },
                causal_event_id=causal_event_id,
            )
        decision = self.get_decision(decision_id)
        if decision is None:
            raise NotFoundError(f"decision not found after write: {decision_id}")
        return decision

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT decision_id, question, status, recommended_option_id, operator_call_required,
                   options_json, arguments_json, counterarguments_json, risks_json,
                   missing_information_json, uncertainty_notes_json, review_after,
                   metadata_json, created_at, updated_at
            FROM decisions
            WHERE decision_id = ?
            """,
            (decision_id,),
        ).fetchone()
        return None if row is None else self._decode_decision_row(row)

    def list_decisions(self, *, limit: int = 50, status: str | None = None) -> list[dict[str, Any]]:
        if status is not None:
            rows = self.conn.execute(
                """
                SELECT decision_id, question, status, recommended_option_id, operator_call_required,
                       options_json, arguments_json, counterarguments_json, risks_json,
                       missing_information_json, uncertainty_notes_json, review_after,
                       metadata_json, created_at, updated_at
                FROM decisions
                WHERE status = ?
                ORDER BY updated_at DESC, rowid DESC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT decision_id, question, status, recommended_option_id, operator_call_required,
                       options_json, arguments_json, counterarguments_json, risks_json,
                       missing_information_json, uncertainty_notes_json, review_after,
                       metadata_json, created_at, updated_at
                FROM decisions
                ORDER BY updated_at DESC, rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        result = []
        for row in rows:
            item = self._decode_decision_row(row)
            result.append(
                {
                    "decision_id": item["decision_id"],
                    "question": item["question"],
                    "status": item["status"],
                    "recommended_option_id": item["recommended_option_id"],
                    "operator_call_required": item["operator_call_required"],
                    "metadata": item["metadata"],
                    "options": item["options"],
                    "review_after": item["review_after"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                }
            )
        return result

    def set_working_memory(self, key: str, value: dict[str, Any], *, causal_event_id: str | None = None) -> str:
        payload_json = json.dumps(value, ensure_ascii=False)
        with self.transaction():
            self.conn.execute(
                """
                INSERT INTO wm(key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (key, payload_json),
            )
            return self._append_ledger(
                layer="working",
                action="UPDATE",
                payload={"key": key, "value": value},
                causal_event_id=causal_event_id,
            )

    def get_working_memory(self, key: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT value FROM wm WHERE key = ?", (key,)).fetchone()
        return None if row is None else json.loads(row[0])

    def add_episode(
        self,
        *,
        session_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        episode_id: str | None = None,
        causal_event_id: str | None = None,
    ) -> str:
        metadata = metadata or {}
        episode_id = episode_id or str(uuid.uuid4())
        metadata_json = json.dumps(metadata, ensure_ascii=False)
        with self.transaction():
            self.conn.execute(
                "INSERT INTO episodes(id, session_id, content, metadata) VALUES (?, ?, ?, ?)",
                (episode_id, session_id, content, metadata_json),
            )
            self.conn.execute(
                "INSERT INTO episodes_fts(rowid, content, content_id) VALUES (last_insert_rowid(), ?, ?)",
                (content, episode_id),
            )
            self._append_ledger(
                layer="episodic",
                action="CREATE",
                payload={
                    "id": episode_id,
                    "session_id": session_id,
                    "content": content,
                    "metadata": metadata,
                },
                causal_event_id=causal_event_id,
            )
            self._set_vector_index_state(
                object_type="episode",
                object_id=episode_id,
                source_text=content,
                embedding_profile=self.DEFAULT_EMBEDDING_PROFILE,
                vector_status=self.VECTOR_STATUS_MISSING,
            )
        return episode_id

    def get_episode(self, episode_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id, session_id, timestamp, content, metadata FROM episodes WHERE id = ?",
            (episode_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["metadata"] = self._decode_json_field(item, "metadata") or {}
        promotion = self.get_episode_promotion(episode_id)
        if promotion is not None:
            item["promotion"] = promotion
        vector_state = self.get_vector_index_state("episode", episode_id)
        if vector_state is not None:
            item["vector_state"] = vector_state
        return item

    def get_episode_promotion(self, episode_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT episode_id, target_layer, target_id, status, promoted_at, ledger_event_id FROM episode_promotions WHERE episode_id = ?",
            (episode_id,),
        ).fetchone()
        return None if row is None else dict(row)

    def list_episodes(self, *, session_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if session_id:
            rows = self.conn.execute(
                """
                SELECT id, session_id, timestamp, content, metadata
                FROM episodes
                WHERE session_id = ?
                ORDER BY timestamp DESC, rowid DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT id, session_id, timestamp, content, metadata
                FROM episodes
                ORDER BY timestamp DESC, rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._decode_json_field(item, "metadata") or {}
            promotion = self.get_episode_promotion(item["id"])
            if promotion is not None:
                item["promotion"] = promotion
            vector_state = self.get_vector_index_state("episode", item["id"])
            if vector_state is not None:
                item["vector_state"] = vector_state
            result.append(item)
        return result

    def _normalize_fts_query(self, query: str) -> str:
        question_fillers = {
            "what", "is", "the", "current", "how", "do", "does", "can", "should", "could",
            "would", "why", "when", "where", "which", "who", "whats", "please", "tell", "me",
            "about",
        }
        normalized = []
        cleaned_tokens: list[str] = []
        for token in query.split():
            token = token.strip()
            if not token:
                continue
            cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", token, flags=re.UNICODE)
            if not cleaned:
                continue
            cleaned_tokens.append(cleaned)
        filtered_tokens = [token for token in cleaned_tokens if token.lower() not in question_fillers]
        tokens_to_use = filtered_tokens or cleaned_tokens
        for cleaned in tokens_to_use:
            if any(ch in cleaned for ch in ('-', ':', '/')):
                normalized.append(f'"{cleaned}"')
            else:
                normalized.append(cleaned)
        return " ".join(normalized) if normalized else query

    def search_episodes_text(
        self, query: str, *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        normalized_query = self._normalize_fts_query(query)
        sql = """
                SELECT e.id, e.session_id, e.timestamp, e.content, e.metadata
                FROM episodes_fts f
                JOIN episodes e ON e.id = f.content_id
                WHERE episodes_fts MATCH ?
            """
        params: list[Any] = [normalized_query]
        if session_id:
            sql += " AND e.session_id = ?"
            params.append(session_id)
        sql += """
                ORDER BY bm25(episodes_fts)
                LIMIT ?
                """
        params.append(limit)
        try:
            rows = self.conn.execute(sql, tuple(params)).fetchall()
        except sqlite3.OperationalError:
            fallback_query = " ".join(part for part in re.findall(r"[\w]+", query, flags=re.UNICODE) if part)
            if not fallback_query or fallback_query == normalized_query:
                raise
            fallback_params = [fallback_query]
            if session_id:
                fallback_params.append(session_id)
            fallback_params.append(limit)
            rows = self.conn.execute(sql, tuple(fallback_params)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._decode_json_field(item, "metadata") or {}
            promotion = self.get_episode_promotion(item["id"])
            if promotion is not None:
                item["promotion"] = promotion
            vector_state = self.get_vector_index_state("episode", item["id"])
            if vector_state is not None:
                item["vector_state"] = vector_state
            result.append(item)
        return result

    def _validate_promotion_metadata(self, metadata: dict[str, Any]) -> str:
        promotion_type = metadata.get("promotion_type")
        if promotion_type is None:
            return "semantic"
        promotion_type = str(promotion_type).lower()
        if promotion_type not in {"semantic", "procedure"}:
            raise ValidationError("promotion_type must be one of: semantic, procedure")
        return promotion_type

    def _build_procedure_candidate(self, episode: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        procedure_name = metadata.get("procedure_name") or f"procedure_from_{episode['id'][:8]}"
        raw_steps = metadata.get("procedure_steps")
        if raw_steps is None:
            steps = [{"step": episode["content"]}]
        else:
            steps = self._ensure_list_of_dicts(raw_steps, field_name="procedure_steps")
        return {
            "target_layer": "procedural",
            "procedure": {
                "name": procedure_name,
                "description": metadata.get("description") or f"Promoted from episode {episode['id']}",
                "steps": steps,
            },
        }

    def _build_semantic_candidate(self, episode: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        node_id = metadata.get("semantic_node_id") or f"sem_{episode['id'][:8]}"
        node_name = metadata.get("semantic_name") or episode["content"][:80]
        node_type = metadata.get("semantic_type") or "Fact"
        properties = {
            "source_episode_id": episode["id"],
            "source_kind": metadata.get("kind", "episode"),
            "session_id": episode["session_id"],
        }
        raw_properties = metadata.get("semantic_properties")
        if raw_properties is None:
            extra_properties = {}
        else:
            extra_properties = self._ensure_dict(raw_properties, field_name="semantic_properties")
        properties.update(extra_properties)
        return {
            "target_layer": "semantic",
            "semantic_node": {
                "id": node_id,
                "name": node_name,
                "type": node_type,
                "properties": properties,
            },
        }

    def preview_consolidation(self, episode_id: str) -> dict[str, Any]:
        episode = self.get_episode(episode_id)
        if episode is None:
            raise NotFoundError(f"episode not found: {episode_id}")

        existing_promotion = self.get_episode_promotion(episode_id)
        if existing_promotion is not None:
            return {
                "episode_id": episode_id,
                "episode": episode,
                "promotion": existing_promotion,
                "mode": "already_promoted",
                "message": "episode has already been promoted",
            }

        metadata = episode["metadata"] or {}
        promotion_type = self._validate_promotion_metadata(metadata)

        if promotion_type == "procedure":
            candidate = self._build_procedure_candidate(episode, metadata)
        else:
            candidate = self._build_semantic_candidate(episode, metadata)

        return {
            "episode_id": episode_id,
            "episode": episode,
            "promotion_type": promotion_type,
            "candidate": candidate,
            "mode": "preview_only",
        }

    def promote_episode(self, episode_id: str) -> dict[str, Any]:
        existing_promotion = self.get_episode_promotion(episode_id)
        if existing_promotion is not None:
            raise PromotionError("episode has already been promoted")

        preview = self.preview_consolidation(episode_id)
        candidate = preview["candidate"]

        if candidate["target_layer"] == "procedural":
            procedure = candidate["procedure"]
            with self.transaction():
                procedure_id = self.create_procedure(
                    name=procedure["name"],
                    description=procedure["description"],
                    steps=procedure["steps"],
                    causal_event_id=episode_id,
                )
                self.conn.execute(
                    "INSERT INTO episode_promotions(episode_id, target_layer, target_id, status, ledger_event_id) VALUES (?, ?, ?, ?, ?)",
                    (episode_id, "procedural", procedure_id, "promoted", None),
                )
            return {
                "ok": True,
                "episode_id": episode_id,
                "target_layer": "procedural",
                "created_id": procedure_id,
                "mode": "promoted",
            }

        semantic_node = candidate["semantic_node"]
        with self.transaction():
            event_id = self.upsert_semantic_node(
                node_id=semantic_node["id"],
                name=semantic_node["name"],
                node_type=semantic_node["type"],
                properties=semantic_node["properties"],
                causal_event_id=episode_id,
            )
            self.conn.execute(
                "INSERT INTO episode_promotions(episode_id, target_layer, target_id, status, ledger_event_id) VALUES (?, ?, ?, ?, ?)",
                (episode_id, "semantic", semantic_node["id"], "promoted", event_id),
            )
        return {
            "ok": True,
            "episode_id": episode_id,
            "target_layer": "semantic",
            "created_id": semantic_node["id"],
            "ledger_event_id": event_id,
            "mode": "promoted",
        }

    def recall(self, query: str, *, session_id: str | None = None, limit: int = 10) -> dict[str, Any]:
        return self.retrieval.recall(query, session_id=session_id, limit=limit)

    def upsert_semantic_node(
        self,
        *,
        node_id: str,
        name: str,
        node_type: str,
        properties: dict[str, Any] | None = None,
        causal_event_id: str | None = None,
    ) -> str:
        properties = properties or {}
        with self.transaction():
            self.conn.execute(
                """
                INSERT INTO semantic_nodes(id, name, type, properties)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    type=excluded.type,
                    properties=excluded.properties
                """,
                (node_id, name, node_type, json.dumps(properties, ensure_ascii=False)),
            )
            event_id = self._append_ledger(
                layer="semantic",
                action="UPDATE",
                payload={"id": node_id, "name": name, "type": node_type, "properties": properties},
                causal_event_id=causal_event_id,
            )
            node = {"id": node_id, "name": name, "type": node_type, "properties": properties}
            existing_state = self.get_vector_index_state("semantic_node", node_id)
            if existing_state is None:
                self._set_vector_index_state(
                    object_type="semantic_node",
                    object_id=node_id,
                    source_text=self._canonical_semantic_node_embedding_text(node),
                    embedding_profile=self.DEFAULT_EMBEDDING_PROFILE,
                    vector_status=self.VECTOR_STATUS_MISSING,
                )
            else:
                self._set_vector_index_state(
                    object_type="semantic_node",
                    object_id=node_id,
                    source_text=self._canonical_semantic_node_embedding_text(node),
                    embedding_profile=existing_state["embedding_profile"],
                    vector_status=self.VECTOR_STATUS_STALE,
                    embedding_provider=existing_state.get("embedding_provider"),
                    embedding_model=existing_state.get("embedding_model"),
                    embedding_dimensions=existing_state.get("embedding_dimensions"),
                    last_embedded_at=existing_state.get("last_embedded_at"),
                    last_error=existing_state.get("last_error"),
                    last_error_at=existing_state.get("last_error_at"),
                )
            return event_id

    def get_semantic_node(self, node_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id, name, type, properties FROM semantic_nodes WHERE id = ?",
            (node_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["properties"] = self._decode_json_field(item, "properties") or {}
        vector_state = self.get_vector_index_state("semantic_node", node_id)
        if vector_state is not None:
            item["vector_state"] = vector_state
        return item

    def upsert_semantic_edge(
        self,
        *,
        source_id: str,
        target_id: str,
        predicate: str,
        weight: float = 1.0,
        causal_event_id: str | None = None,
    ) -> str:
        with self.transaction():
            self.conn.execute(
                """
                INSERT INTO semantic_edges(source_id, target_id, predicate, weight)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, predicate) DO UPDATE SET
                    weight=excluded.weight
                """,
                (source_id, target_id, predicate, weight),
            )
            return self._append_ledger(
                layer="semantic",
                action="UPDATE",
                payload={
                    "source_id": source_id,
                    "target_id": target_id,
                    "predicate": predicate,
                    "weight": weight,
                },
                causal_event_id=causal_event_id,
            )

    def list_semantic_edges(self, node_id: str, *, direction: str = "both") -> list[dict[str, Any]]:
        if direction == "out":
            rows = self.conn.execute(
                "SELECT source_id, target_id, predicate, weight FROM semantic_edges WHERE source_id = ? ORDER BY target_id, predicate",
                (node_id,),
            ).fetchall()
        elif direction == "in":
            rows = self.conn.execute(
                "SELECT source_id, target_id, predicate, weight FROM semantic_edges WHERE target_id = ? ORDER BY source_id, predicate",
                (node_id,),
            ).fetchall()
        elif direction == "both":
            rows = self.conn.execute(
                """
                SELECT source_id, target_id, predicate, weight
                FROM semantic_edges
                WHERE source_id = ? OR target_id = ?
                ORDER BY source_id, target_id, predicate
                """,
                (node_id, node_id),
            ).fetchall()
        else:
            raise ValidationError("direction must be one of: out, in, both")
        return [dict(r) for r in rows]

    def create_procedure(
        self,
        *,
        name: str,
        steps: list[dict[str, Any]],
        description: str | None = None,
        procedure_id: str | None = None,
        causal_event_id: str | None = None,
    ) -> str:
        self._ensure_list_of_dicts(steps, field_name="steps")
        procedure_id = procedure_id or str(uuid.uuid4())
        with self.transaction():
            self.conn.execute(
                "INSERT INTO procedures(id, name, description, steps_json) VALUES (?, ?, ?, ?)",
                (procedure_id, name, description, json.dumps(steps, ensure_ascii=False)),
            )
            self._append_ledger(
                layer="procedural",
                action="CREATE",
                payload={
                    "id": procedure_id,
                    "name": name,
                    "description": description,
                    "steps": steps,
                },
                causal_event_id=causal_event_id,
            )
        return procedure_id

    def get_procedure(self, procedure_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id, name, description, steps_json, is_active FROM procedures WHERE id = ?",
            (procedure_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["steps"] = self._decode_json_field(item, "steps_json") or []
        del item["steps_json"]
        return item

    def list_procedures(self, *, active_only: bool = True, limit: int = 50) -> list[dict[str, Any]]:
        if active_only:
            rows = self.conn.execute(
                "SELECT id, name, description, steps_json, is_active FROM procedures WHERE is_active = 1 ORDER BY name LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT id, name, description, steps_json, is_active FROM procedures ORDER BY name LIMIT ?",
                (limit,),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["steps"] = self._decode_json_field(item, "steps_json") or []
            del item["steps_json"]
            result.append(item)
        return result

    def list_ledger(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT event_id, timestamp, layer, action, payload, causal_event_id, previous_hash, crypto_hash FROM ledger ORDER BY timestamp, rowid"
        ).fetchall()
        return [dict(r) for r in rows]

    def ledger_events_for_object(self, *, layer: str, object_id_field: str, object_id: str) -> list[dict[str, Any]]:
        events = []
        for entry in self.list_ledger():
            if entry.get("layer") != layer:
                continue
            payload = json.loads(entry["payload"])
            if payload.get(object_id_field) != object_id:
                continue
            enriched = dict(entry)
            enriched["payload"] = payload
            events.append(enriched)
        return events

    @staticmethod
    def _decision_history_changed_fields(current: dict[str, Any], previous: dict[str, Any]) -> list[str]:
        changed = []
        for field in (
            "question",
            "status",
            "recommended_option_id",
            "operator_call_required",
            "options",
            "arguments",
            "counterarguments",
            "risks",
            "missing_information",
            "uncertainty_notes",
            "review_after",
            "metadata",
        ):
            if current.get(field) != previous.get(field):
                changed.append(field)
        return changed

    def decision_history(self, decision_id: str) -> dict[str, Any]:
        current = self.get_decision(decision_id)
        if current is None:
            raise NotFoundError(f"decision not found: {decision_id}")

        events = self.ledger_events_for_object(
            layer="decision",
            object_id_field="decision_id",
            object_id=decision_id,
        )
        revisions = []
        snapshots = []
        for event in events:
            payload = event["payload"]
            snapshot = {
                "decision_id": payload.get("decision_id"),
                "question": payload.get("question"),
                "status": payload.get("status"),
                "recommended_option_id": payload.get("recommended_option_id"),
                "operator_call_required": payload.get("operator_call_required"),
                "options": payload.get("options", []),
                "arguments": payload.get("arguments", []),
                "counterarguments": payload.get("counterarguments", []),
                "risks": payload.get("risks", []),
                "missing_information": payload.get("missing_information", []),
                "uncertainty_notes": payload.get("uncertainty_notes", []),
                "review_after": payload.get("review_after"),
                "metadata": payload.get("metadata", {}),
            }
            snapshots.append(snapshot)
            revisions.append(
                {
                    "event_id": event["event_id"],
                    "timestamp": event["timestamp"],
                    "action": event["action"],
                    "status": snapshot["status"],
                    "recommended_option_id": snapshot["recommended_option_id"],
                }
            )

        previous = snapshots[-2] if len(snapshots) >= 2 else None
        changed_fields = [] if previous is None else self._decision_history_changed_fields(current, previous)

        return {
            "decision_id": decision_id,
            "current": current,
            "previous": previous,
            "changed_fields": changed_fields,
            "revision_count": len(revisions),
            "revisions": revisions,
        }

    def inspect_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        if object_type == "decision":
            decision = self.get_decision(object_id)
            if decision is None:
                raise NotFoundError(f"decision not found: {object_id}")
            return {
                "object_type": "decision",
                "object_id": object_id,
                "record": decision,
                "related_ledger_events": self.ledger_events_for_object(
                    layer="decision",
                    object_id_field="decision_id",
                    object_id=object_id,
                ),
                "related_refs": {
                    "metadata": decision.get("metadata", {}),
                    "recommended_option_id": decision.get("recommended_option_id"),
                    "review_after": decision.get("review_after"),
                },
            }

        if object_type == "episode":
            episode = self.get_episode(object_id)
            if episode is None:
                raise NotFoundError(f"episode not found: {object_id}")
            return {
                "object_type": "episode",
                "object_id": object_id,
                "record": episode,
                "related_ledger_events": self.ledger_events_for_object(
                    layer="episodic",
                    object_id_field="id",
                    object_id=object_id,
                ),
                "related_refs": {
                    "promotion": episode.get("promotion"),
                    "vector_state": episode.get("vector_state"),
                },
            }

        raise ValidationError("object_type must be one of: decision, episode")

    def decision_check(self, decision_id: str) -> dict[str, Any]:
        current = self.get_decision(decision_id)
        if current is None:
            raise NotFoundError(f"decision not found: {decision_id}")
        others = self.list_decisions(limit=1000)
        result = decision_conflict_check(current, others)
        result["checked_at"] = self._now_iso()
        return result

    def verify_ledger(self) -> dict[str, Any]:
        entries = self.list_ledger()
        previous_hash = None
        problems: list[dict[str, Any]] = []

        for index, entry in enumerate(entries):
            expected_hash = compute_event_hash(
                event_id=entry["event_id"],
                layer=entry["layer"],
                action=entry["action"],
                payload_json=entry["payload"],
                causal_event_id=entry["causal_event_id"],
                previous_hash=previous_hash,
            )

            if entry["previous_hash"] != previous_hash:
                problems.append(
                    {
                        "index": index,
                        "event_id": entry["event_id"],
                        "kind": "previous_hash_mismatch",
                        "expected": previous_hash,
                        "actual": entry["previous_hash"],
                    }
                )

            if entry["crypto_hash"] != expected_hash:
                problems.append(
                    {
                        "index": index,
                        "event_id": entry["event_id"],
                        "kind": "crypto_hash_mismatch",
                        "expected": expected_hash,
                        "actual": entry["crypto_hash"],
                    }
                )

            previous_hash = entry["crypto_hash"]

        return {
            "ok": len(problems) == 0,
            "entry_count": len(entries),
            "problems": problems,
        }
