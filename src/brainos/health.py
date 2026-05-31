from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

from .benchmark import run_retrieval_benchmark
from .embedding import LiteLLMEmbeddingAdapter
from .errors import SqliteVecReadinessError
from .sqlite_vec import configured_sqlite_vec_path
from .store import BrainOSStore


SQLITE_WAL_REQUIRED_VALUE = "wal"


def _health_action_hint(*, runtime_issues: list[str], freshness_issues: list[str], freshness_notes: list[str], benchmark: dict[str, Any], low_evidence: bool) -> str:
    if runtime_issues:
        return "runtime_fix"
    if low_evidence:
        return "seed_or_ingest_more_data"
    if freshness_issues:
        return "reindex_or_repair"
    if benchmark.get("degraded"):
        return "runtime_fix_or_accept_degraded"
    if freshness_notes:
        return "inspect_notes"
    return "noop"


def _health_summary_text(*, runtime_issues: list[str], freshness_issues: list[str], benchmark: dict[str, Any], low_evidence: bool) -> str:
    if runtime_issues:
        return "runtime fix needed before vector-quality interpretation"
    if low_evidence:
        return "low evidence: retrieval quality not yet meaningful on this database"
    if freshness_issues:
        return "freshness issues likely affecting retrieval quality"
    if benchmark.get("degraded"):
        return "benchmark running in degraded non-vector mode"
    if benchmark.get("ok"):
        return "benchmark green in vector-ready mode"
    return "benchmark failure needs explain-side inspection"


_AZURE_API_VERSION_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}(?:-preview)?$")
_AZURE_API_VERSION_KEYWORDS = {"v1", "latest", "preview"}


def _is_valid_azure_api_version(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in _AZURE_API_VERSION_KEYWORDS or bool(_AZURE_API_VERSION_PATTERN.fullmatch(normalized))


def _embedding_config_health() -> dict[str, Any]:
    contract = LiteLLMEmbeddingAdapter().contract()
    missing: list[str] = []
    invalid: list[str] = []
    present: list[str] = []
    values: dict[str, str] = {}

    for name in contract["required_env"]:
        import os

        value = os.getenv(name, "").strip()
        if not value:
            missing.append(name)
            continue
        present.append(name)
        values[name] = value

    api_base = values.get("AZURE_API_BASE")
    if api_base and not api_base.startswith(("https://", "http://")):
        invalid.append("AZURE_API_BASE")

    api_version = values.get("AZURE_API_VERSION")
    if api_version and not _is_valid_azure_api_version(api_version):
        invalid.append("AZURE_API_VERSION")

    model = values.get("BRAINOS_EMBEDDING_MODEL")
    if model and "/" not in model:
        invalid.append("BRAINOS_EMBEDDING_MODEL")

    status = "ok" if not missing and not invalid else "warn"
    issues = [f"missing:{name}" for name in missing] + [f"invalid:{name}" for name in invalid]
    return {
        "status": status,
        "issues": issues,
        "action_hint": "set_required_env" if missing else ("fix_invalid_env" if invalid else "noop"),
        "contract": contract,
        "required_env": contract["required_env"],
        "present_env": present,
        "missing_env": missing,
        "invalid_env": invalid,
    }


def _sqlite_vec_env_health() -> dict[str, Any]:
    path = configured_sqlite_vec_path()
    issues: list[str] = []
    notes: list[str] = []
    source = "explicit_configured" if path else "not_configured"

    if not path:
        issues.append("missing:BRAINOS_SQLITE_VEC_PATH")
        status = "warn"
    else:
        p = Path(path)
        try:
            if not p.exists():
                issues.append("path_missing")
            elif not p.is_file():
                issues.append("path_not_file")
            else:
                notes.append("path_exists")
                if "/home/openclaw/" in path:
                    source = "ambient_detected"
                    notes.append("path_looks_ambient")
        except PermissionError:
            issues.append("path_permission_denied")
            if "/home/openclaw/" in path:
                source = "ambient_detected"
                notes.append("path_looks_ambient")
        status = "ok" if not issues else "warn"

    return {
        "status": status,
        "issues": issues,
        "notes": notes,
        "action_hint": "configure_sqlite_vec_path" if issues else "noop",
        "configured": bool(path) and source == "explicit_configured",
        "runtime_origin": source,
        "path": path,
    }


def _dependency_health() -> dict[str, Any]:
    checks = {
        "litellm": importlib.util.find_spec("litellm") is not None,
    }
    missing = [name for name, ok in checks.items() if not ok]
    return {
        "status": "ok" if not missing else "warn",
        "issues": [f"missing_dependency:{name}" for name in missing],
        "action_hint": "install_dependencies" if missing else "noop",
        "checks": checks,
    }


def _database_runtime_health(store: BrainOSStore) -> dict[str, Any]:
    journal_mode = str(store.conn.execute("PRAGMA journal_mode;").fetchone()[0]).lower()
    wal_ok = journal_mode == SQLITE_WAL_REQUIRED_VALUE
    issues = [] if wal_ok else [f"journal_mode_not_{SQLITE_WAL_REQUIRED_VALUE}"]
    return {
        "status": "ok" if wal_ok else "warn",
        "issues": issues,
        "action_hint": "fix_sqlite_runtime" if issues else "noop",
        "journal_mode": journal_mode,
        "expected_journal_mode": SQLITE_WAL_REQUIRED_VALUE,
        "db_path": store.db_path,
    }


def _runtime_failure_summary(*, store: BrainOSStore, error_kind: str, detail: str) -> dict[str, Any]:
    sqlite_vec_env = _sqlite_vec_env_health()
    sqlite_vec_env = {
        **sqlite_vec_env,
        "issues": list(dict.fromkeys([*sqlite_vec_env["issues"], error_kind])),
        "action_hint": "configure_sqlite_vec_path",
    }
    runtime_issue = f"sqlite_vec_runtime:{error_kind}"
    benchmark = {
        "suite": "retrieval-benchmark-v0",
        "evidence_kind": "seeded_fixture",
        "truthfulness_note": "This benchmark could not complete because sqlite-vec runtime failed before execution.",
        "ok": False,
        "mode": "runtime_error",
        "degraded": True,
        "degraded_reason": error_kind,
        "case_count": 0,
        "passed": 0,
        "failed": 0,
        "failed_cases": [],
        "runtime_error": detail,
    }
    return {
        "status": "warn",
        "summary": "runtime fix needed before vector-quality interpretation",
        "action_hint": "runtime_fix",
        "runtime": {
            "status": "warn",
            "issues": [runtime_issue],
            "action_hint": "runtime_fix",
            "capabilities": {"sqlite_vec": False},
            "embedding_config": _embedding_config_health(),
            "sqlite_vec_env": sqlite_vec_env,
            "dependencies": _dependency_health(),
            "database_runtime": {
                "status": "warn",
                "issues": [runtime_issue],
                "action_hint": "runtime_fix",
                "journal_mode": None,
                "expected_journal_mode": SQLITE_WAL_REQUIRED_VALUE,
                "db_path": store.db_path,
            },
        },
        "freshness": {
            "status": "warn",
            "issues": [],
            "notes": ["runtime_probe_incomplete"],
            "action_hint": "inspect_notes",
            "vector_index": {"total": 0, "by_status": {}, "by_type": {}},
        },
        "quality": {
            "status": "degraded",
            "issues": ["benchmark_runtime_error"],
            "notes": [],
            "action_hint": "accept_degraded_or_fix_runtime",
            "benchmark": benchmark,
        },
        "issues": [runtime_issue, "benchmark_runtime_error"],
    }


def retrieval_health_summary(store: BrainOSStore, *, benchmark_limit: int = 5) -> dict[str, Any]:
    try:
        capabilities = store.capabilities()
        states = store.list_vector_index_states(limit=1000)
    except SqliteVecReadinessError as exc:
        return _runtime_failure_summary(store=store, error_kind=exc.error_kind, detail=exc.detail or str(exc))

    counts_by_status: dict[str, int] = {}
    counts_by_type: dict[str, int] = {}
    for item in states:
        counts_by_status[item["vector_status"]] = counts_by_status.get(item["vector_status"], 0) + 1
        counts_by_type[item["object_type"]] = counts_by_type.get(item["object_type"], 0) + 1

    benchmark = run_retrieval_benchmark(store, limit=benchmark_limit)
    low_evidence = len(states) == 0

    embedding_config = _embedding_config_health()
    sqlite_vec_env = _sqlite_vec_env_health()
    dependency_health = _dependency_health()
    database_runtime = _database_runtime_health(store)

    runtime_issues = []
    if not capabilities.get("sqlite_vec"):
        runtime_issues.append("sqlite_vec_unavailable")
    runtime_issues.extend(embedding_config["issues"])
    runtime_issues.extend(sqlite_vec_env["issues"])
    runtime_issues.extend(dependency_health["issues"])
    runtime_issues.extend(database_runtime["issues"])

    freshness_issues = []
    if counts_by_status.get("stale", 0) > 0:
        freshness_issues.append("stale_vectors_present")
    if counts_by_status.get("error", 0) > 0:
        freshness_issues.append("vector_errors_present")

    freshness_notes = []
    if counts_by_status.get("missing", 0) > 0:
        freshness_notes.append("missing_vectors_present")
    if counts_by_status.get("disabled", 0) > 0:
        freshness_notes.append("disabled_vectors_present")

    quality_issues = []
    quality_notes = []
    if low_evidence:
        quality_notes.append("low_evidence_database")
    elif not benchmark.get("ok"):
        if benchmark.get("degraded"):
            quality_issues.append("benchmark_not_green_in_degraded_mode")
        else:
            quality_issues.append("benchmark_not_green")

    issues = runtime_issues + freshness_issues + quality_issues
    status = "ok" if not issues else "warn"

    runtime_status = "ok" if not runtime_issues else "warn"
    freshness_status = "ok" if not freshness_issues else "warn"
    quality_status = "low_evidence" if low_evidence else ("ok" if not quality_issues else ("degraded" if benchmark.get("degraded") else "warn"))

    action_hint = _health_action_hint(
        runtime_issues=runtime_issues,
        freshness_issues=freshness_issues,
        freshness_notes=freshness_notes,
        benchmark=benchmark,
        low_evidence=low_evidence,
    )
    summary = _health_summary_text(
        runtime_issues=runtime_issues,
        freshness_issues=freshness_issues,
        benchmark=benchmark,
        low_evidence=low_evidence,
    )

    return {
        "status": status,
        "summary": summary,
        "action_hint": action_hint,
        "runtime": {
            "status": runtime_status,
            "issues": runtime_issues,
            "action_hint": "runtime_fix" if runtime_issues else "noop",
            "capabilities": capabilities,
            "embedding_config": embedding_config,
            "sqlite_vec_env": sqlite_vec_env,
            "dependencies": dependency_health,
            "database_runtime": database_runtime,
        },
        "freshness": {
            "status": freshness_status,
            "issues": freshness_issues,
            "notes": freshness_notes,
            "action_hint": "reindex_or_repair" if freshness_issues else ("inspect_notes" if freshness_notes else "noop"),
            "vector_index": {
                "total": len(states),
                "by_status": counts_by_status,
                "by_type": counts_by_type,
            },
        },
        "quality": {
            "status": quality_status,
            "issues": quality_issues,
            "notes": quality_notes,
            "action_hint": "seed_or_ingest_more_data" if low_evidence else ("inspect_benchmark_failure" if quality_issues else ("accept_degraded_or_fix_runtime" if benchmark.get("degraded") else "noop")),
            "benchmark": {
                "suite": benchmark.get("suite"),
                "evidence_kind": benchmark.get("evidence_kind"),
                "truthfulness_note": benchmark.get("truthfulness_note"),
                "ok": benchmark.get("ok"),
                "mode": benchmark.get("mode"),
                "degraded": benchmark.get("degraded"),
                "degraded_reason": benchmark.get("degraded_reason"),
                "case_count": benchmark.get("case_count"),
                "passed": benchmark.get("passed"),
                "failed": benchmark.get("failed"),
                "failed_cases": benchmark.get("failed_cases", []),
                "runtime_error": benchmark.get("runtime_error"),
            },
        },
        "issues": issues,
    }
