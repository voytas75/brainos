from __future__ import annotations

import os
from pathlib import Path


_LAST_ENV_LOAD_INFO: dict[str, object] = {
    "loaded": False,
    "path": None,
    "keys": [],
    "cwd": None,
    "exists": False,
}


def get_last_env_load_info() -> dict[str, object]:
    return {
        "loaded": bool(_LAST_ENV_LOAD_INFO.get("loaded", False)),
        "path": _LAST_ENV_LOAD_INFO.get("path"),
        "keys": list(_LAST_ENV_LOAD_INFO.get("keys", [])),
        "cwd": _LAST_ENV_LOAD_INFO.get("cwd"),
        "exists": bool(_LAST_ENV_LOAD_INFO.get("exists", False)),
    }


def load_project_env(*, cwd: str | None = None, override: bool = False) -> dict[str, object]:
    base = Path(cwd or os.getcwd())
    env_path = base / ".env"
    loaded: list[str] = []

    _LAST_ENV_LOAD_INFO.update(
        {
            "loaded": False,
            "path": str(env_path),
            "keys": [],
            "cwd": str(base),
            "exists": env_path.exists(),
        }
    )

    if not env_path.exists():
        return {
            "loaded": False,
            "path": str(env_path),
            "keys": loaded,
        }

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value
            loaded.append(key)

    _LAST_ENV_LOAD_INFO.update(
        {
            "loaded": True,
            "path": str(env_path),
            "keys": list(loaded),
            "cwd": str(base),
            "exists": True,
        }
    )

    return {
        "loaded": True,
        "path": str(env_path),
        "keys": loaded,
    }
