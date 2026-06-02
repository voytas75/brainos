from __future__ import annotations

from typing import Any

from .retrieval import RetrievalService


_ACTIVE_STATUSES = {"draft", "active"}
_GENERIC_OPTION_IDS = {chr(code) for code in range(ord("A"), ord("Z") + 1)}


def _tokenize(text: str) -> set[str]:
    return RetrievalService.tokenize_for_overlap(text)


def _option_ids(decision: dict[str, Any]) -> set[str]:
    option_ids = set()
    for option in decision.get("options", []):
        option_id = option.get("option_id")
        if isinstance(option_id, str) and option_id.strip():
            option_ids.add(option_id.strip())
    return option_ids


def _question_overlap_tokens(current: dict[str, Any], other: dict[str, Any]) -> list[str]:
    return sorted(_tokenize(current.get("question", "")) & _tokenize(other.get("question", "")))


def _option_overlap_tokens(current: dict[str, Any], other: dict[str, Any]) -> list[str]:
    current_tokens = set()
    for option in current.get("options", []):
        label = option.get("label")
        if isinstance(label, str):
            current_tokens |= _tokenize(label)

    other_tokens = set()
    for option in other.get("options", []):
        label = option.get("label")
        if isinstance(label, str):
            other_tokens |= _tokenize(label)
    return sorted(current_tokens & other_tokens)


def _active_enough(status: Any) -> bool:
    return status in _ACTIVE_STATUSES


def _meaningful_shared_option_ids(shared_option_ids: list[str]) -> list[str]:
    meaningful: list[str] = []
    for option_id in shared_option_ids:
        normalized = option_id.strip()
        if normalized.upper() in _GENERIC_OPTION_IDS:
            continue
        meaningful.append(option_id)
    return meaningful


def decision_conflict_check(
    current: dict[str, Any],
    others: list[dict[str, Any]],
) -> dict[str, Any]:
    current_entity_id = (current.get("metadata") or {}).get("entity_id")
    current_option_ids = _option_ids(current)
    current_status = current.get("status")
    findings: list[dict[str, Any]] = []
    verdict = "clear"

    for other in others:
        if other.get("decision_id") == current.get("decision_id"):
            continue
        if not _active_enough(other.get("status")):
            continue

        other_entity_id = (other.get("metadata") or {}).get("entity_id")
        other_option_ids = _option_ids(other)
        same_entity = current_entity_id is not None and other_entity_id is not None and current_entity_id == other_entity_id
        active_pair = _active_enough(current_status) and _active_enough(other.get("status"))
        shared_option_ids = sorted(current_option_ids & other_option_ids)
        meaningful_shared_option_ids = _meaningful_shared_option_ids(shared_option_ids)
        current_recommendation = current.get("recommended_option_id")
        other_recommendation = other.get("recommended_option_id")
        comparable_recommendations = (
            current_recommendation in current_option_ids
            and other_recommendation in other_option_ids
            and current_recommendation in shared_option_ids
            and other_recommendation in shared_option_ids
        )
        different_recommendation = comparable_recommendations and current_recommendation != other_recommendation
        question_overlap = _question_overlap_tokens(current, other)
        option_overlap = _option_overlap_tokens(current, other)

        strong_signals: list[str] = []
        medium_signals: list[str] = []
        weak_signals: list[str] = []

        if same_entity:
            strong_signals.append("shared_entity_id")
        if same_entity and active_pair:
            strong_signals.append("active_pair")
        if same_entity and different_recommendation:
            strong_signals.append("different_recommendations")

        if same_entity and meaningful_shared_option_ids:
            medium_signals.append("option_id_overlap")
        if same_entity and current.get("review_after") and other.get("review_after"):
            if current.get("review_after") == other.get("review_after"):
                medium_signals.append("review_after_overlap")

        if question_overlap:
            weak_signals.append("question_text_overlap")
        if option_overlap:
            weak_signals.append("option_text_overlap")

        severity = "clear"
        if {"shared_entity_id", "active_pair", "different_recommendations"}.issubset(set(strong_signals)):
            severity = "conflict"
        elif same_entity and active_pair and medium_signals:
            severity = "caution"

        if severity == "clear":
            continue

        reasons = [*strong_signals, *medium_signals, *weak_signals]
        findings.append(
            {
                "decision_id": other.get("decision_id"),
                "status": other.get("status"),
                "severity": severity,
                "reasons": reasons,
                "strong_signals": strong_signals,
                "medium_signals": medium_signals,
                "weak_signals": weak_signals,
                "question_overlap_tokens": question_overlap,
                "option_overlap_tokens": option_overlap,
                "shared_option_ids": shared_option_ids,
                "meaningful_shared_option_ids": meaningful_shared_option_ids,
                "recommended_option_id": other.get("recommended_option_id"),
                "entity_id": other_entity_id,
            }
        )
        if severity == "conflict":
            verdict = "conflict"
        elif severity == "caution" and verdict == "clear":
            verdict = "caution"

    return {
        "decision_id": current.get("decision_id"),
        "verdict": verdict,
        "finding_count": len(findings),
        "findings": findings,
    }
