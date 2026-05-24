from __future__ import annotations

from typing import Any

from .health import retrieval_health_summary
from .store import BrainOSStore


def embedding_readiness_summary(store: BrainOSStore) -> dict[str, Any]:
    contract = store.get_embedding_profile_contract()
    runtime = retrieval_health_summary(store, benchmark_limit=1)["runtime"]
    embedding_config = runtime["embedding_config"]
    sqlite_vec_env = runtime["sqlite_vec_env"]
    dependencies = runtime["dependencies"]
    capabilities = runtime["capabilities"]

    issues: list[str] = []
    issues.extend(embedding_config.get("issues", []))
    issues.extend(sqlite_vec_env.get("issues", []))
    issues.extend(dependencies.get("issues", []))
    if not capabilities.get("sqlite_vec"):
        issues.append("sqlite_vec_unavailable")

    status = "ok" if not issues else "warn"
    action_hint = "noop" if status == "ok" else "fix_embedding_runtime"
    return {
        "status": status,
        "action_hint": action_hint,
        "profile_contract": contract,
        "embedding_config": embedding_config,
        "sqlite_vec_env": sqlite_vec_env,
        "dependencies": dependencies,
        "capabilities": capabilities,
        "issues": issues,
    }


def doctor_summary(store: BrainOSStore, *, benchmark_limit: int = 5) -> dict[str, Any]:
    health = retrieval_health_summary(store, benchmark_limit=benchmark_limit)
    embedding = embedding_readiness_summary(store)

    checks = {
        "retrieval_health": health["status"] == "ok",
        "embedding_runtime": embedding["status"] == "ok",
        "sqlite_vec_capability": health["runtime"]["capabilities"].get("sqlite_vec", False),
        "sqlite_wal": health["runtime"]["database_runtime"]["status"] == "ok",
        "dependencies": health["runtime"]["dependencies"]["status"] == "ok",
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "ok" if not failed_checks else "warn"

    return {
        "status": status,
        "action_hint": "noop" if status == "ok" else "fix_failed_checks",
        "checks": checks,
        "failed_checks": failed_checks,
        "embedding": embedding,
        "retrieval_health": health,
    }
