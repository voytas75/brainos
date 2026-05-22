from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .ledger import canonical_json, compute_event_hash
from .schema import initialize_schema


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
            result.append(item)
        return result

    def recall(self, query: str, *, session_id: str | None = None, limit: int = 10) -> dict[str, Any]:
        episodes = self.search_episodes_text(query, session_id=session_id, limit=limit)
        return {
            "query": query,
            "session_id": session_id,
            "episodes": episodes,
            "count": len(episodes),
            "mode": "fts_only",
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
            raise ValueError("direction must be one of: out, in, both")
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
