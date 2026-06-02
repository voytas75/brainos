from __future__ import annotations

from typing import Any

from .errors import ValidationError


ALLOWED_DECISION_STATUSES = {"draft", "active", "superseded", "closed"}


def _ensure_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _ensure_list(value: Any, *, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be a JSON array")
    return value


def _ensure_dict(value: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be a JSON object")
    return value


def _normalize_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    raise ValidationError(f"{field_name} must be a boolean")


def validate_decision_payload(
    *,
    question: str,
    status: str,
    options: Any,
    arguments: Any,
    counterarguments: Any,
    risks: Any,
    missing_information: Any,
    uncertainty_notes: Any,
    metadata: Any,
    recommended_option_id: str | None,
    operator_call_required: Any,
) -> dict[str, Any]:
    normalized_question = _ensure_non_empty_text(question, field_name="question")
    normalized_status = _ensure_non_empty_text(status, field_name="status")
    if normalized_status not in ALLOWED_DECISION_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_DECISION_STATUSES))
        raise ValidationError(f"status must be one of: {allowed}")

    normalized_options = _ensure_list(options, field_name="options_json")
    if not normalized_options:
        raise ValidationError("options_json must be a non-empty JSON array")

    option_ids: set[str] = set()
    validated_options: list[dict[str, Any]] = []
    for index, item in enumerate(normalized_options):
        option = _ensure_dict(item, field_name=f"options_json[{index}]")
        option_id = _ensure_non_empty_text(option.get("option_id"), field_name=f"options_json[{index}].option_id")
        label = _ensure_non_empty_text(option.get("label"), field_name=f"options_json[{index}].label")
        summary = option.get("summary")
        if summary is not None and not isinstance(summary, str):
            raise ValidationError(f"options_json[{index}].summary must be a string when present")
        if option_id in option_ids:
            raise ValidationError(f"duplicate option_id not allowed: {option_id}")
        option_ids.add(option_id)
        cleaned = {"option_id": option_id, "label": label}
        if summary is not None:
            cleaned["summary"] = summary
        validated_options.append(cleaned)

    normalized_arguments = _ensure_list(arguments, field_name="arguments_json")
    normalized_counterarguments = _ensure_list(counterarguments, field_name="counterarguments_json")
    normalized_risks = _ensure_list(risks, field_name="risks_json")
    normalized_missing_information = _ensure_list(missing_information, field_name="missing_information_json")
    normalized_uncertainty_notes = _ensure_list(uncertainty_notes, field_name="uncertainty_notes_json")
    normalized_metadata = _ensure_dict(metadata, field_name="metadata_json")
    normalized_operator_call_required = _normalize_bool(
        operator_call_required,
        field_name="operator_call_required",
    )

    if recommended_option_id is not None:
        recommended_option_id = _ensure_non_empty_text(
            recommended_option_id,
            field_name="recommended_option_id",
        )
        if recommended_option_id not in option_ids:
            raise ValidationError("recommended_option_id must match one declared option_id")

    return {
        "question": normalized_question,
        "status": normalized_status,
        "recommended_option_id": recommended_option_id,
        "operator_call_required": normalized_operator_call_required,
        "options": validated_options,
        "arguments": normalized_arguments,
        "counterarguments": normalized_counterarguments,
        "risks": normalized_risks,
        "missing_information": normalized_missing_information,
        "uncertainty_notes": normalized_uncertainty_notes,
        "metadata": normalized_metadata,
    }
