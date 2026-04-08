from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

ALLOWED_EVENTS = {
    "view_landing",
    "start_assessment",
    "question_answered",
    "complete_assessment",
    "view_report",
    "click_upgrade",
    "purchase",
}


def _is_iso_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _validate_metadata(metadata: Any, errors: List[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
        return

    expected_types = {
        "device": str,
        "stage": str,
        "score": (int, float),
        "total": (int, float),
        "xp": (int, float),
    }

    for key, expected_type in expected_types.items():
        if key not in metadata:
            continue
        if not isinstance(metadata[key], expected_type):
            errors.append(f"metadata.{key} has invalid type")


def validate_event(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return False, ["event payload must be an object"]

    required = [
        "event_id",
        "session_id",
        "student_id",
        "event_name",
        "timestamp",
        "metadata",
    ]
    for field in required:
        if field not in payload:
            errors.append(f"{field} is required")

    event_id = payload.get("event_id")
    if event_id is not None:
        try:
            uuid.UUID(str(event_id))
        except (ValueError, TypeError):
            errors.append("event_id must be a valid UUID")

    session_id = payload.get("session_id")
    if session_id is not None and not isinstance(session_id, str):
        errors.append("session_id must be a string")

    user_id = payload.get("user_id")
    if user_id is not None and not isinstance(user_id, str):
        errors.append("user_id must be null or string")

    student_id = payload.get("student_id")
    if student_id is not None and not isinstance(student_id, str):
        errors.append("student_id must be a string")

    event_name = payload.get("event_name")
    if event_name is not None:
        if not isinstance(event_name, str):
            errors.append("event_name must be a string")
        elif event_name not in ALLOWED_EVENTS:
            errors.append("event_name is not supported")

    timestamp = payload.get("timestamp")
    if timestamp is not None:
        if not isinstance(timestamp, str) or not _is_iso_timestamp(timestamp):
            errors.append("timestamp must be a valid ISO-8601 string")

    _validate_metadata(payload.get("metadata"), errors)

    return len(errors) == 0, errors
