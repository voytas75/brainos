from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_event_hash(
    *,
    event_id: str,
    layer: str,
    action: str,
    payload_json: str,
    causal_event_id: str | None,
    previous_hash: str | None,
) -> str:
    basis = "|".join(
        [
            event_id,
            layer,
            action,
            payload_json,
            causal_event_id or "",
            previous_hash or "",
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()
