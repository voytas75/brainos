import json
import os
import subprocess
from pathlib import Path

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


def _brainos_cli() -> str:
    return os.fspath(Path(__file__).resolve().parents[1] / ".venv" / "bin" / "brainos")


def _test_env() -> dict[str, str]:
    return {**_clean_cli_env(), "PATH": os.environ.get("PATH", "")}


def test_recall_marks_runtime_misconfigured_when_sqlite_vec_missing(tmp_path):
    db = tmp_path / "brain.db"
    store = BrainOSStore(db)
    store.initialize()
    store.add_episode(session_id="s1", content="BrainOS retrieval should detect runtime drift.", metadata={})

    payload = store.recall("runtime drift", session_id="s1", limit=5)

    assert payload["retrieval_runtime"]["status"] == "misconfigured"
    assert payload["retrieval_runtime"]["degraded"] is True
    assert payload["vector_mode"] == "disabled"
    assert payload["semantic_vector_mode"] == "disabled"
    assert payload["retrieval_runtime"]["action_hint"] == "configure_sqlite_vec_path"


def test_retrieval_explain_cli_surfaces_runtime_misconfiguration(tmp_path):
    db = tmp_path / "brain.db"
    subprocess.run([_brainos_cli(), "--db", str(db), "init"], check=True, capture_output=True, text=True, env=_test_env())
    subprocess.run(
        [
            _brainos_cli(),
            "--db",
            str(db),
            "episode-add",
            "s1",
            "BrainOS retrieval should detect runtime drift.",
            "--metadata-json",
            "{}",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=_test_env(),
    )
    proc = subprocess.run(
        [_brainos_cli(), "--db", str(db), "retrieval-explain", "runtime drift", "--session-id", "s1"],
        capture_output=True,
        text=True,
        check=True,
        env=_test_env(),
    )
    payload = json.loads(proc.stdout)
    assert payload["retrieval_runtime"]["status"] == "misconfigured"
    assert payload["diagnostic_hint"] in {"inspect_vector_participation", "lexical_grounded_top_hit"}
    assert payload["retrieval_runtime"]["action_hint"] == "configure_sqlite_vec_path"
    assert payload["zero_hit_reason"] in {"misconfigured", None}


def test_bounded_smoke_green_path_with_real_env(tmp_path):
    vec_path = os.environ.get("BRAINOS_SQLITE_VEC_PATH")
    model = os.environ.get("BRAINOS_EMBEDDING_MODEL")
    api_base = os.environ.get("AZURE_API_BASE")
    api_key = os.environ.get("AZURE_API_KEY")
    api_version = os.environ.get("AZURE_API_VERSION")
    if not all([vec_path, model, api_base, api_key, api_version]):
        return

    db = tmp_path / "brain.db"
    env = {
        **_test_env(),
        "BRAINOS_SQLITE_VEC_PATH": vec_path,
        "BRAINOS_EMBEDDING_MODEL": model,
        "AZURE_API_BASE": api_base,
        "AZURE_API_KEY": api_key,
        "AZURE_API_VERSION": api_version,
    }

    subprocess.run([_brainos_cli(), "--db", str(db), "init"], check=True, capture_output=True, text=True, env=env)
    corpus = [
        "W Polsce wdrożenie AI Act obejmuje projekt ustawy tworzącej organ nadzoru i piaskownice regulacyjne.",
        "Polskie firmy mają wysoki poziom zainteresowania AI, ale wdrożenia blokują koszty, kompetencje i dostęp do mocy obliczeniowej.",
        "Państwo deklaruje rozwój krajowej infrastruktury AI i wsparcie dla polskich modeli językowych.",
    ]
    for text in corpus:
        subprocess.run([_brainos_cli(), "--db", str(db), "episode-add", "s1", text, "--metadata-json", "{}"], check=True, capture_output=True, text=True, env=env)
    subprocess.run([_brainos_cli(), "--db", str(db), "vector-index-sync-batch", "--object-type", "episode", "--vector-status", "missing"], check=True, capture_output=True, text=True, env=env)
    proc = subprocess.run([_brainos_cli(), "--db", str(db), "retrieval-explain", "AI Act w Polsce nadzor i piaskownice", "--session-id", "s1"], check=True, capture_output=True, text=True, env=env)
    payload = json.loads(proc.stdout)
    assert payload["retrieval_runtime"]["status"] == "ok"
    assert len(payload["top_ranked_episodes"]) >= 1
