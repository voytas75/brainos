import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_operator_acceptance_ignores_inherited_sqlite_vec_path(tmp_path):
    db = tmp_path / "operator-acceptance.db"
    out_dir = tmp_path / "operator-acceptance"
    env = os.environ.copy()
    env["BRAINOS_SQLITE_VEC_PATH"] = "/nonexistent/vec0.so"

    subprocess.run(
        ["bash", "scripts/operator_acceptance.sh", str(db), str(out_dir)],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
        env=env,
    )

    summary = json.loads((out_dir / "summary.json").read_text())
    assert summary["status"] == "PASS"
    assert summary["failed_scenarios"] == []


def test_canonical_demo_default_strips_provider_env(tmp_path):
    db = tmp_path / "canonical.db"
    out_dir = tmp_path / "canonical"
    env = os.environ.copy()
    for key in (
        "BRAINOS_CLI",
        "BRAINOS_CANONICAL_E2E_ENABLE_VECTOR_SYNC",
        "BRAINOS_SQLITE_VEC_PATH",
    ):
        env.pop(key, None)
    env.update(
        {
            "BRAINOS_EMBEDDING_MODEL": "azure/should-not-call",
            "BRAINOS_EMBEDDING_API_KEY": "test-generic-key",
            "AZURE_API_BASE": "http://127.0.0.1:9",
            "AZURE_API_KEY": "test-key",
            "AZURE_API_VERSION": "2024-10-21",
            "OPENAI_API_KEY": "test-openai-key",
        }
    )
    (tmp_path / ".env").write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-dotenv\n"
        "BRAINOS_EMBEDDING_API_KEY=dotenv-generic-key\n"
        "AZURE_API_BASE=http://127.0.0.1:9\n"
        "AZURE_API_KEY=dotenv-key\n"
        "AZURE_API_VERSION=2024-10-21\n"
        "OPENAI_API_KEY=dotenv-openai-key\n"
    )

    subprocess.run(
        ["bash", "scripts/canonical_e2e_demo.sh", str(db), str(out_dir)],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
        env=env,
    )

    summary = json.loads((out_dir / "summary.json").read_text())
    embedding = json.loads((out_dir / "embedding-readiness.json").read_text())
    explain = json.loads((out_dir / "explain.json").read_text())
    assert summary["overall_status"] == "DEGRADED"
    assert embedding["profile_contract"]["operational_provider"] == "unknown"
    assert embedding["embedding_config"]["missing_env"] == ["BRAINOS_EMBEDDING_MODEL"]
    env_presence = explain["startup_runtime_context"]["env_presence"]
    for name in (
        "BRAINOS_EMBEDDING_MODEL",
        "AZURE_API_BASE",
        "AZURE_API_KEY",
        "AZURE_API_VERSION",
    ):
        assert env_presence[name] == {"present": False, "source": "missing"}
