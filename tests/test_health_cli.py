import json
import os
import subprocess
from pathlib import Path

from brainos.doctor import doctor_summary, embedding_readiness_summary
from brainos.errors import SqliteVecReadinessError
from brainos.health import retrieval_health_summary
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
        if key not in _ENV_KEYS
        and not any(key.startswith(prefix) for prefix in prefixes)
    }


def _brainos_cli() -> str:
    return os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")


def _test_env() -> dict[str, str]:
    return {
        **_clean_cli_env(),
        "PATH": os.environ.get("PATH", ""),
        "BRAINOS_EMBEDDING_MODEL": "azure/test-embed",
        "AZURE_API_BASE": "https://example.openai.azure.com",
        "AZURE_API_KEY": "test-key",
        "AZURE_API_VERSION": "2024-10-21",
    }


def _test_env_openai() -> dict[str, str]:
    return {
        **_clean_cli_env(),
        "PATH": os.environ.get("PATH", ""),
        "BRAINOS_EMBEDDING_MODEL": "openai/text-embedding-3-small",
        "OPENAI_API_KEY": "test-openai-key",
    }


def _extract_json(stdout: str) -> dict:
    start = stdout.find("{")
    if start == -1:
        raise AssertionError(f"No JSON object in stdout: {stdout!r}")
    return json.loads(stdout[start:])


def test_diagnostics_do_not_run_provider_benchmark(monkeypatch, tmp_path):
    calls: list[object] = []

    def _provider_embedding_forbidden(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))
        raise AssertionError("provider-backed embedding must not run from diagnostics")

    monkeypatch.setattr(
        "brainos.health.run_retrieval_benchmark",
        _provider_embedding_forbidden,
        raising=False,
    )
    monkeypatch.setattr(BrainOSStore, "embed_texts", _provider_embedding_forbidden)
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()
    try:
        health = retrieval_health_summary(store)
        embedding = embedding_readiness_summary(store)
        doctor = doctor_summary(store)
    finally:
        store.close()

    assert calls == []
    assert health["quality"]["benchmark"]["mode"] == "not_evaluated"
    assert embedding["status"] in {"ok", "warn"}
    assert doctor["retrieval_health"]["quality"]["benchmark"]["mode"] == (
        "not_evaluated"
    )


def test_runtime_probe_failure_stays_not_evaluated(monkeypatch, tmp_path):
    store = BrainOSStore(tmp_path / "brain.db")
    store.initialize()

    def _runtime_failure() -> dict[str, object]:
        raise SqliteVecReadinessError(
            "sqlite-vec probe failed", error_kind="readiness_probe_failed"
        )

    monkeypatch.setattr(store, "capabilities", _runtime_failure)
    try:
        summary = retrieval_health_summary(store)
    finally:
        store.close()

    benchmark = summary["quality"]["benchmark"]
    assert benchmark["mode"] == "not_evaluated"
    assert benchmark["runtime_error"] == "sqlite-vec probe failed"
    assert summary["quality"]["status"] == "not_evaluated"


def test_retrieval_health_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert "status" in payload
    assert "summary" in payload
    assert "runtime" in payload
    assert "freshness" in payload
    assert "quality" in payload
    assert "issues" in payload
    assert "capabilities" in payload["runtime"]
    assert "embedding_config" in payload["runtime"]
    assert "sqlite_vec_env" in payload["runtime"]
    assert "dependencies" in payload["runtime"]
    assert "database_runtime" in payload["runtime"]
    assert "vector_index" in payload["freshness"]
    assert "benchmark" in payload["quality"]
    assert "notes" in payload["freshness"]
    assert payload["quality"]["benchmark"]["mode"] == "not_evaluated"
    assert "degraded" in payload["quality"]["benchmark"]
    assert "degraded_reason" in payload["quality"]["benchmark"]
    assert "recommended_fix" in payload["quality"]["benchmark"]
    assert (
        payload["quality"]["benchmark"]["recommended_fix"]["action_hint"]
        == "run_retrieval_benchmark"
    )


def test_retrieval_health_cli_exposes_action_hints(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert "action_hint" in payload
    assert payload["runtime"]["action_hint"] in {"runtime_fix", "noop"}
    assert payload["freshness"]["action_hint"] in {
        "reindex_or_repair",
        "inspect_notes",
        "noop",
    }
    assert payload["quality"]["action_hint"] in {
        "seed_or_ingest_more_data",
        "run_retrieval_benchmark",
        "inspect_benchmark_failure",
        "accept_degraded_or_fix_runtime",
        "noop",
    }
    assert payload["runtime"]["embedding_config"]["action_hint"] in {
        "set_required_env",
        "fix_invalid_env",
        "noop",
    }
    assert payload["runtime"]["sqlite_vec_env"]["action_hint"] in {
        "configure_sqlite_vec_path",
        "noop",
    }
    assert payload["runtime"]["dependencies"]["action_hint"] in {
        "install_dependencies",
        "noop",
    }
    assert payload["runtime"]["database_runtime"]["action_hint"] in {
        "fix_sqlite_runtime",
        "noop",
    }


def test_retrieval_health_cli_summary_is_compact_string(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert isinstance(payload["summary"], str)
    assert payload["summary"]


def test_retrieval_health_cli_degraded_benchmark_summary_is_explicit_not_generic_failure(
    tmp_path,
):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert payload["quality"]["benchmark"]["degraded"] is False
    assert payload["quality"]["benchmark"]["mode"] == "not_evaluated"
    assert "low_evidence_database" in payload["quality"]["notes"]
    assert payload["action_hint"] == "runtime_fix"


def test_retrieval_health_cli_marks_empty_db_as_low_evidence(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert payload["quality"]["status"] == "low_evidence"
    assert "low_evidence_database" in payload["quality"]["notes"]
    assert payload["quality"]["action_hint"] == "seed_or_ingest_more_data"
    assert payload["runtime"]["status"] == "warn"
    assert (
        payload["summary"]
        == "runtime fix needed before vector-quality interpretation; quality evidence is also still low"
    )


def test_retrieval_health_cli_surfaces_benchmark_truthfulness_metadata(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert payload["quality"]["benchmark"]["evidence_kind"] == "seeded_fixture"
    assert "truthfulness_note" in payload["quality"]["benchmark"]


def test_retrieval_health_cli_surfaces_runtime_prereq_details(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = _extract_json(proc.stdout)
    assert (
        payload["summary"]
        == "runtime fix needed before vector-quality interpretation; quality evidence is also still low"
    )
    embedding = payload["runtime"]["embedding_config"]
    assert embedding["required_env"] == [
        "BRAINOS_EMBEDDING_MODEL",
        "AZURE_API_BASE",
        "AZURE_API_KEY",
        "AZURE_API_VERSION",
    ]
    assert embedding["contract"]["operational_provider"] == "azure"
    assert "missing_env" in embedding
    assert "invalid_env" in embedding
    sqlite_vec = payload["runtime"]["sqlite_vec_env"]
    assert "configured" in sqlite_vec
    assert "runtime_origin" in sqlite_vec
    assert sqlite_vec["runtime_origin"] in {"explicit_configured", "not_configured"}
    assert "path" in sqlite_vec
    deps = payload["runtime"]["dependencies"]
    assert deps["checks"]["litellm"] is True
    db_runtime = payload["runtime"]["database_runtime"]
    assert db_runtime["expected_journal_mode"] == "wal"
    assert db_runtime["journal_mode"] == "wal"


def test_retrieval_health_cli_openai_path_reports_openai_contract(tmp_path):
    db = tmp_path / "brain.db"
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-health", "--benchmark-limit", "5"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env_openai(),
    )
    payload = _extract_json(proc.stdout)
    assert (
        payload["summary"]
        == "runtime fix needed before vector-quality interpretation; quality evidence is also still low"
    )
    embedding = payload["runtime"]["embedding_config"]
    assert embedding["contract"]["operational_provider"] == "openai"
    assert embedding["required_env"] == ["BRAINOS_EMBEDDING_MODEL", "OPENAI_API_KEY"]
    assert embedding["missing_env"] == []
    assert embedding["invalid_env"] == []
