import json
import subprocess
import sys


def run_cli(tmp_path, *args):
    db = tmp_path / "brain.db"
    cmd = [sys.executable, "-m", "brainos.cli", "--db", str(db), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def log_decision(
    tmp_path,
    decision_id,
    question,
    recommended_option_id,
    options,
    metadata=None,
    status="draft",
    review_after=None,
):
    args = [
        "decision-log",
        question,
        "--decision-id",
        decision_id,
        "--status",
        status,
        "--recommended-option-id",
        recommended_option_id,
        "--options-json",
        json.dumps(options),
        "--metadata-json",
        json.dumps(metadata or {}),
    ]
    if review_after:
        args.extend(["--review-after", review_after])
    result = run_cli(tmp_path, *args)
    assert result.returncode == 0, result.stderr


def test_decision_check_clear_when_no_related_active_decisions(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "Which next slice should we choose?",
        "A",
        [{"option_id": "A", "label": "Fix retrieval first"}],
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "clear"
    assert payload["finding_count"] == 0


def test_decision_check_conflict_for_shared_entity_and_different_recommendation(tmp_path):
    log_decision(
        tmp_path,
        "dec-a",
        "Should we improve retrieval credibility before UI work?",
        "A",
        [
            {"option_id": "A", "label": "Fix retrieval credibility first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-b",
        "Should we improve retrieval credibility before UI work this week?",
        "B",
        [
            {"option_id": "A", "label": "Fix retrieval credibility first"},
            {"option_id": "B", "label": "Build dashboard first"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-a")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "conflict"
    assert payload["finding_count"] == 1
    finding = payload["findings"][0]
    assert finding["decision_id"] == "dec-b"
    assert finding["severity"] == "conflict"
    assert "shared_entity_id" in finding["strong_signals"]
    assert "active_pair" in finding["strong_signals"]
    assert "different_recommendations" in finding["strong_signals"]


def test_decision_check_caution_for_same_scope_and_meaningful_option_overlap(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "Should we stabilize retrieval credibility before polishing the dashboard?",
        "retrieval_first",
        [
            {"option_id": "retrieval_first", "label": "Fix retrieval credibility first"},
            {"option_id": "ui_first", "label": "Polish dashboard first"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "Should we revisit the retrieval roadmap before UI work?",
        "retrieval_first",
        [
            {"option_id": "retrieval_first", "label": "Fix retrieval ranking first"},
            {"option_id": "pause_ui", "label": "Pause UI work"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "caution"
    assert payload["finding_count"] == 1
    finding = payload["findings"][0]
    assert finding["severity"] == "caution"
    assert "shared_entity_id" in finding["strong_signals"]
    assert "option_id_overlap" in finding["medium_signals"]
    assert finding["meaningful_shared_option_ids"] == ["retrieval_first"]


def test_decision_check_clear_for_same_scope_without_divergence_or_medium_signals(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "Should BrainOS prioritize retrieval credibility?",
        "A",
        [
            {"option_id": "A", "label": "Improve retrieval credibility"},
            {"option_id": "B", "label": "Delay UI polish"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "Should BrainOS improve operator documentation?",
        "C",
        [
            {"option_id": "C", "label": "Improve operator docs"},
            {"option_id": "D", "label": "Postpone template cleanup"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "clear"
    assert payload["finding_count"] == 0


def test_decision_check_ignores_weak_lexical_overlap_without_shared_scope(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "What should we do next this week?",
        "A",
        [{"option_id": "A", "label": "Fix retrieval credibility first"}],
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "What should we choose next this week?",
        "A",
        [{"option_id": "A", "label": "Build dashboard first"}],
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "clear"
    assert payload["finding_count"] == 0


def test_decision_check_ignores_weak_lexical_overlap_with_shared_scope(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "What should we do next this week for BrainOS?",
        "A",
        [
            {"option_id": "A", "label": "Fix retrieval credibility first"},
            {"option_id": "B", "label": "Delay dashboard polish"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "What should we choose next this week for BrainOS?",
        "C",
        [
            {"option_id": "C", "label": "Document operator workflow first"},
            {"option_id": "D", "label": "Pause analytics cleanup"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "clear"
    assert payload["finding_count"] == 0


def test_decision_check_ignores_generic_option_id_overlap_for_caution(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "What should we do next this week for BrainOS?",
        "A",
        [
            {"option_id": "A", "label": "Fix retrieval credibility first"},
            {"option_id": "B", "label": "Delay dashboard polish"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "What should we choose next this week for BrainOS?",
        "A",
        [
            {"option_id": "A", "label": "Document operator workflow first"},
            {"option_id": "C", "label": "Pause analytics cleanup"},
        ],
        metadata={"entity_id": "brainos"},
        status="active",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "clear"
    assert payload["finding_count"] == 0



def test_decision_check_uses_review_after_as_medium_signal_with_shared_scope(tmp_path):
    log_decision(
        tmp_path,
        "dec-1",
        "Should we revisit BrainOS decision support next week?",
        "A",
        [{"option_id": "A", "label": "Keep current direction"}],
        metadata={"entity_id": "brainos"},
        status="active",
        review_after="2026-06-09T09:00:00Z",
    )
    log_decision(
        tmp_path,
        "dec-2",
        "Should we check BrainOS posture again next week?",
        "A",
        [{"option_id": "A", "label": "Delay changes for now"}],
        metadata={"entity_id": "brainos"},
        status="active",
        review_after="2026-06-09T09:00:00Z",
    )

    result = run_cli(tmp_path, "decision-check", "dec-1")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "caution"
    finding = payload["findings"][0]
    assert "shared_entity_id" in finding["strong_signals"]
    assert "review_after_overlap" in finding["medium_signals"]
