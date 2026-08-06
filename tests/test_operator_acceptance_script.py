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
