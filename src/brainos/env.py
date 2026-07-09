from __future__ import annotations

import os
from pathlib import Path


# Contract:
# 1. Start from the supplied cwd (or process cwd).
# 2. Prefer the nearest .env in that directory.
# 3. If missing, walk upward through parent directories.
# 4. Stop at filesystem root; load the first .env found.
# 5. Never override existing process env unless override=True.
# 6. Report both the original lookup cwd and the resolved env path.
# 7. If nothing is found, report the nearest candidate path (<cwd>/.env).

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
    base = Path(cwd or os.getcwd()).resolve()
    loaded: list[str] = []

    env_path: Path | None = None
    for candidate_base in [base, *base.parents]:
        candidate = candidate_base / ".env"
        if candidate.exists():
            env_path = candidate
            break

    reported_path = env_path if env_path is not None else (base / ".env")

    _LAST_ENV_LOAD_INFO.update(
        {
            "loaded": False,
            "path": str(reported_path.resolve()),
            "keys": [],
            "cwd": str(base),
            "exists": bool(env_path is not None),
        }
    )

    if env_path is None:
        return {
            "loaded": False,
            "path": str(reported_path.resolve()),
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
            "path": str(env_path.resolve()),
            "keys": list(loaded),
            "cwd": str(base),
            "exists": True,
        }
    )

    return {
        "loaded": True,
        "path": str(env_path.resolve()),
        "keys": loaded,
    }
