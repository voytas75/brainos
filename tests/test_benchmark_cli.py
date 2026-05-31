import json
import os
import subprocess
from pathlib import Path

from brainos.benchmark import run_retrieval_benchmark
from brainos.store import BrainOSStore


_ENV_KEYS = {
    "BRAINOS_EMBEDDING_MODEL",
    "AZURE_API_BASE",
    "AZURE_API_KEY",
    "AZURE_API_VERSION",
    "BRAINOS_SQLITE_VEC_PATH",
}


def _clean_cli_env() -> dict[str, str]:
    prefixes = ("AZURE_", "AZURE_OPENAI_", "OPENAI_", "LITELLM_")
    return {
        key: value
        for key, value in os.environ.items()
        if key not in _ENV_KEYS and not any(key.startswith(prefix) for prefix in prefixes)
    }


def test_retrieval_benchmark_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"), "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    payload = json.loads(proc.stdout)
    assert payload["suite"] == "retrieval-benchmark-v0"
    assert payload["evidence_kind"] == "seeded_fixture"
    assert "truthfulness_note" in payload
    assert payload["mode"] in {"vector-ready", "degraded-non-vector"}
    assert "degraded" in payload
    assert "degraded_reason" in payload
    assert payload["case_count"] == 10
    assert payload["passed"] + payload["failed"] == 10
    assert payload["episode_passed"] + payload["episode_failed"] == 10
    assert payload["semantic_passed"] + payload["semantic_failed"] == 10
    assert "results" in payload
    assert len(payload["results"]) == 10


def test_retrieval_benchmark_cli_exposes_failed_case_drilldown(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"), "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    payload = json.loads(proc.stdout)
    assert "failed_cases" in payload
    assert isinstance(payload["failed_cases"], list)
    for item in payload["failed_cases"]:
        assert "episode_ok" in item
        assert "semantic_ok" in item


def test_retrieval_benchmark_failed_cases_expose_next_debug_handoff(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"), "--db", str(db), "retrieval-benchmark", "--limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    payload = json.loads(proc.stdout)
    assert "failed_cases" in payload
    for item in payload["failed_cases"]:
        assert item["next_debug"]["tool"] == "retrieval-explain"
        assert item["next_debug"]["query"] == item["query"]
        assert item["next_debug"]["session_id"] == "bench"


def test_retrieval_benchmark_nl_semantic_case_is_green(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    payload = run_retrieval_benchmark(store, limit=10)
    target = next(item for item in payload["results"] if item["query"] == "what helps BrainOS keep local writes safe?")
    assert target["episode_ok"] is True
    assert target["semantic_ok"] is True
    assert target["top_semantic_id"] == "sem-wal"
    store.close()


def test_semantic_name_query_reduces_nl_case_to_wal():
    assert run_retrieval_benchmark is not None
    from brainos.retrieval import RetrievalService

    assert RetrievalService._semantic_name_query("what helps BrainOS keep local writes safe?") == "wal"
