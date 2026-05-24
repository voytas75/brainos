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
    assert payload["scoring_policy_version"] == "retrieval-scoring-v1"
    assert payload["diagnostic_hint"] in {"inspect_vector_participation", "dual_source_agreement", "lexical_grounded_top_hit", "vector_led_top_hit", "inspect_score_components"}
    assert "top_ranked_episodes" in payload
    assert "top_ranked_semantic_hits" in payload
