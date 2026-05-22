from __future__ import annotations

from typing import Any

from .benchmark import run_retrieval_benchmark
from .store import BrainOSStore


def retrieval_health_summary(store: BrainOSStore, *, benchmark_limit: int = 5) -> dict[str, Any]:
    capabilities = store.capabilities()
    states = store.list_vector_index_states(limit=1000)

    counts_by_status: dict[str, int] = {}
    counts_by_type: dict[str, int] = {}
    for item in states:
        counts_by_status[item["vector_status"]] = counts_by_status.get(item["vector_status"], 0) + 1
        counts_by_type[item["object_type"]] = counts_by_type.get(item["object_type"], 0) + 1

    benchmark = run_retrieval_benchmark(store, limit=benchmark_limit)

    issues = []
    if not capabilities.get("sqlite_vec"):
        issues.append("sqlite_vec_unavailable")
    if counts_by_status.get("stale", 0) > 0:
        issues.append("stale_vectors_present")
    if counts_by_status.get("error", 0) > 0:
        issues.append("vector_errors_present")
    if not benchmark.get("ok"):
        issues.append("benchmark_not_green")

    status = "ok" if not issues else "warn"

    return {
        "status": status,
        "capabilities": capabilities,
        "vector_index": {
            "total": len(states),
            "by_status": counts_by_status,
            "by_type": counts_by_type,
        },
        "benchmark": {
            "suite": benchmark.get("suite"),
            "ok": benchmark.get("ok"),
            "case_count": benchmark.get("case_count"),
            "passed": benchmark.get("passed"),
            "failed": benchmark.get("failed"),
        },
        "issues": issues,
    }
