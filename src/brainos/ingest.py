from __future__ import annotations

import re
from typing import Any

CANONICAL_EPISODE_KINDS = {"fact", "decision", "procedure", "note", "observation"}
LEGACY_KIND_MAP = {
    "other": "note",
}
PRESERVE_KINDS = {"graph", "storage", "embedding", "maintenance", "browser", "policy", "ops", "ui", "runtime", "lesson"}


def normalize_episode_content(content: str) -> str:
    text = (content or "").strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def normalize_episode_metadata(metadata: dict[str, Any] | None = None, *, kind: str | None = None, topic: str | None = None, source: str | None = None) -> dict[str, Any]:
    data = dict(metadata or {})

    raw_kind = (kind or data.get("kind") or "").strip().lower()
    if raw_kind in LEGACY_KIND_MAP:
        raw_kind = LEGACY_KIND_MAP[raw_kind]
    if raw_kind not in CANONICAL_EPISODE_KINDS and raw_kind not in PRESERVE_KINDS:
        if raw_kind:
            data.setdefault("original_kind", raw_kind)
        raw_kind = "note"
    data["kind"] = raw_kind or "note"

    normalized_source = (source or data.get("source") or "").strip().lower()
    data["source"] = normalized_source or "manual"

    normalized_topic = (topic or data.get("topic") or "").strip()
    if normalized_topic:
        data["topic"] = normalized_topic
    else:
        data.pop("topic", None)

    return data


def prepare_episode_ingest(content: str, metadata: dict[str, Any] | None = None, *, kind: str | None = None, topic: str | None = None, source: str | None = None) -> tuple[str, dict[str, Any]]:
    return normalize_episode_content(content), normalize_episode_metadata(metadata, kind=kind, topic=topic, source=source)
