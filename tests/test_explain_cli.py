import json
import os
import subprocess
from pathlib import Path


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


def _brainos_cli() -> str:
    return os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")


def _test_env() -> dict[str, str]:
    return {**_clean_cli_env(), "PATH": os.environ.get("PATH", "")}


def test_retrieval_explain_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run([_brainos_cli(), "--db", str(db), "init"], check=True, capture_output=True, text=True, env=_test_env())
    subprocess.run(
        [
            _brainos_cli(),
            "--db",
            str(db),
            "episode-add",
            "s1",
            "Azure embeddings through LiteLLM help retrieval quality.",
            "--metadata-json",
            "{}",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-explain", "Azure embeddings", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "Azure embeddings"
    assert payload["scoring_policy_version"] == "retrieval-scoring-v1a"
    assert payload["diagnostic_hint"] in {"dual_source_agreement", "lexical_grounded_top_hit", "vector_led_top_hit", "inspect_score_components", "inspect_vector_participation"}
    assert "top_ranked_episodes" in payload
    assert "top_ranked_semantic_hits" in payload
    assert "top_decisions" in payload


def test_retrieval_explain_cli_accepts_question_query(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run([_brainos_cli(), "--db", str(db), "init"], check=True, capture_output=True, text=True, env=_test_env())
    subprocess.run(
        [
            _brainos_cli(),
            "--db",
            str(db),
            "episode-add",
            "s1",
            "BrainOS testing posture should prefer bounded usage validation before deeper consistency work.",
            "--metadata-json",
            "{}",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-explain", "What is the BrainOS testing posture?", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "What is the BrainOS testing posture?"
    assert payload["summary"] in {"episodes:1", "vector_episodes:1", "episodes:1, ranked_episodes:1", "episodes:1, vector_episodes:1", "episodes:1, vector_episodes:1, ranked_episodes:1", "vector_episodes:1, ranked_episodes:1"}
    assert len(payload["top_ranked_episodes"]) >= 1


def test_retrieval_explain_cli_accepts_slash_query(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run([_brainos_cli(), "--db", str(db), "init"], check=True, capture_output=True, text=True, env=_test_env())
    subprocess.run(
        [
            _brainos_cli(),
            "--db",
            str(db),
            "episode-add",
            "s1",
            "Google Workspace via gwork is the operational path; Gmail and Calendar writes require explicit confirm.",
            "--metadata-json",
            "{}",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-explain", "What is the current Google Workspace / gwork posture?", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "What is the current Google Workspace / gwork posture?"
    assert "top_ranked_episodes" in payload
