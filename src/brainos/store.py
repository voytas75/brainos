from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .ledger import canonical_json, compute_event_hash
from .schema import detect_capabilities, get_schema_status, initialize_schema


class BrainOSError(Exception):
    pass


class ValidationError(BrainOSError):
    pass


class PromotionError(BrainOSError):
    pass


class NotFoundError(BrainOSError):
    pass


class BrainOSStore:
    def __init__(self, db_path: str | Path, *, enable_vector: bool = False):
        self.db_path = str(db_path)
        self.enable_vector = enable_vector
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.execute("PRAGMA journal_mode=WAL;")

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
            result.append(item)
        return result

    def search_episodes_text(
        self, query: str, *, session_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        if session_id:
            rows = self.conn.execute(
                """
                SELECT e.id, e.session_id, e.timestamp, e.content, e.metadata
                FROM episodes_fts f
                JOIN episodes e ON e.id = f.content_id
                WHERE episodes_fts MATCH ? AND e.session_id = ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, session_id, limit),
            ).fetchall()
        else:
            rows = self.conn.execute(
                """
                SELECT e.id, e.session_id, e.timestamp, e.content, e.metadata
                FROM episodes_fts f
                JOIN episodes e ON e.id = f.content_id
                WHERE episodes_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._decode_json_field(item, "metadata") or {}
            promotion = self.get_episode_promotion(item["id"])
            if promotion is not None:
                item["promotion"] = promotion
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
        episodes = self.search_episodes_text(query, session_id=session_id, limit=limit)

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

        summary_parts = []
        if episodes:
            summary_parts.append(f"episodes:{len(episodes)}")
        if semantic_hits:
            summary_parts.append(f"semantic_hits:{len(semantic_hits)}")

        return {
            "query": query,
            "session_id": session_id,
            "episodes": episodes,
            "semantic_hits": semantic_hits,
            "count": len(episodes),
            "semantic_count": len(semantic_hits),
            "mode": "fts_plus_semantic_name_match",
            "summary": ", ".join(summary_parts) if summary_parts else "no_hits",
        }

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
            return self._append_ledger(
                layer="semantic",
                action="UPDATE",
                payload={"id": node_id, "name": name, "type": node_type, "properties": properties},
                causal_event_id=causal_event_id,
            )

    def get_semantic_node(self, node_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT id, name, type, properties FROM semantic_nodes WHERE id = ?",
            (node_id,),
        ).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["properties"] = self._decode_json_field(item, "properties") or {}
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
