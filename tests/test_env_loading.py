import os
import subprocess

from brainos.env import load_project_env


def test_load_project_env_reads_dotenv_without_overriding_existing_env(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BRAINOS_EMBEDDING_MODEL=azure/from-dotenv\nAZURE_API_BASE=https://example.openai.azure.com\nAZURE_API_KEY=dotenv-key\nAZURE_API_VERSION=2024-10-21\n",
        encoding="utf-8",
    )
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
        ["uv", "run", "brainos", "--db", str(db), "embedding-readiness"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
        env={k: v for k, v in os.environ.items() if k not in {
            "BRAINOS_EMBEDDING_MODEL",
            "AZURE_API_BASE",
            "AZURE_API_KEY",
            "AZURE_API_VERSION",
            "BRAINOS_SQLITE_VEC_PATH",
        }},
    )
    assert '"missing_env": []' in proc.stdout
    assert '"BRAINOS_EMBEDDING_MODEL"' in proc.stdout
