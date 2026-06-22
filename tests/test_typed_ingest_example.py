import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_typed_ingest_example_runs() -> None:
    proc = subprocess.run(
        ["uv", "run", "python", "examples/typed_ingest_flow.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = proc.stdout
    assert "Writing small typed-ingest corpus" in stdout
    assert "Recall query: retrieval smoke check" in stdout
    assert "typed ingest is a small corpus hygiene lever" in stdout
    assert "kind=decision" in stdout or "kind=procedure" in stdout
