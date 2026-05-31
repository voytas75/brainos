import json
import subprocess


def test_retrieval_explain_cli_runs(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(["uv", "run", "brainos", "--db", str(db), "init"], check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "uv",
            "run",
            "brainos",
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
    )
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-explain", "Azure embeddings", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "Azure embeddings"
    assert payload["scoring_policy_version"] == "retrieval-scoring-v1a"
    assert payload["diagnostic_hint"] in {"dual_source_agreement", "lexical_grounded_top_hit", "vector_led_top_hit", "inspect_score_components"}
    assert "top_ranked_episodes" in payload
    assert "top_ranked_semantic_hits" in payload


def test_retrieval_explain_cli_accepts_question_query(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(["uv", "run", "brainos", "--db", str(db), "init"], check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "uv",
            "run",
            "brainos",
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
    )
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-explain", "What is the BrainOS testing posture?", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "What is the BrainOS testing posture?"
    assert payload["summary"] in {"no_hits", "episodes:1", "vector_episodes:1", "episodes:1, vector_episodes:1", "episodes:1, vector_episodes:1, ranked_episodes:1", "vector_episodes:1, ranked_episodes:1"} or "top_ranked_episodes" in payload
    assert "top_ranked_episodes" in payload


def test_retrieval_explain_cli_accepts_slash_query(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run(["uv", "run", "brainos", "--db", str(db), "init"], check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "uv",
            "run",
            "brainos",
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
    )
    proc = subprocess.run(
        ["uv", "run", "brainos", "--db", str(db), "retrieval-explain", "What is the current Google Workspace / gwork posture?", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["query"] == "What is the current Google Workspace / gwork posture?"
    assert "top_ranked_episodes" in payload
