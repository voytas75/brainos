import os
import subprocess
from pathlib import Path

from brainos.env import load_project_env


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


def test_load_project_env_reads_dotenv_without_overriding_existing_env(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-dotenv\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AZURE_API_KEY", "already-set")
    result = load_project_env(cwd=str(tmp_path))
    assert result["loaded"] is True
    assert os.environ["BRAINOS_EMBEDDING_MODEL"] == "azure/from-dotenv"
    assert os.environ["AZURE_API_BASE"] == "https://example.openai.azure.com"
    assert os.environ["AZURE_API_KEY"] == "already-set"
    assert os.environ["AZURE_API_VERSION"] == "2024-10-21"


def test_cli_honors_project_dotenv_for_embedding_readiness(tmp_path):
    db = tmp_path / "brain.db"
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-dotenv\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos"), "--db", str(db), "embedding-readiness"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    assert '"missing_env": []' in proc.stdout
    assert '"BRAINOS_EMBEDDING_MODEL"' in proc.stdout


def test_load_project_env_falls_back_to_parent_dotenv(tmp_path, monkeypatch):
    project_root = tmp_path / "project"
    nested = project_root / "artifacts" / "runtime"
    nested.mkdir(parents=True)
    (project_root / ".env").write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-parent\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    result = load_project_env(cwd=str(nested))
    assert result["loaded"] is True
    assert result["path"] == str((project_root / ".env").resolve())
    assert os.environ["BRAINOS_EMBEDDING_MODEL"] == "azure/from-parent"



def test_cli_uses_parent_dotenv_when_db_lives_in_nested_directory(tmp_path):
    project_root = tmp_path / "project"
    nested = project_root / "artifacts" / "runtime"
    nested.mkdir(parents=True)
    db = nested / "brain.db"
    (project_root / ".env").write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-parent\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
    cli = os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")

    init_proc = subprocess.run(
        [cli, "--db", str(db), "init"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    assert f"Initialized {db}" in init_proc.stdout
    assert db.exists()

    explain_proc = subprocess.run(
        [cli, "--db", str(db), "retrieval-explain", "runtime drift"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        check=True,
        env={**_clean_cli_env(), "PATH": os.environ.get("PATH", "")},
    )
    assert f'"effective_db_path": "{db.resolve()}"' in explain_proc.stdout
    assert f'"cwd": "{db.resolve().parent}"' in explain_proc.stdout
    assert f'"path": "{(project_root / ".env").resolve()}"' in explain_proc.stdout



def test_cli_uses_brainos_db_path_env_for_db_selection(tmp_path):
    db = tmp_path / "via-env.db"
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-dotenv\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
    cli = os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")
    env = {**_clean_cli_env(), "PATH": os.environ.get("PATH", ""), "BRAINOS_DB_PATH": str(db)}

    init_proc = subprocess.run(
        [cli, "init"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert f"Initialized {db}" in init_proc.stdout
    assert db.exists()

    explain_proc = subprocess.run(
        [cli, "retrieval-explain", "runtime drift"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    assert f'"effective_db_path": "{db.resolve()}"' in explain_proc.stdout
    assert f'"cwd": "{db.resolve().parent}"' in explain_proc.stdout
