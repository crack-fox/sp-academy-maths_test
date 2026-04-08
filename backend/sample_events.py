from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


def _iso_at(offset_min: int) -> str:
    base = datetime(2026, 4, 8, 12, 0, tzinfo=timezone.utc)
    return (base + timedelta(minutes=offset_min)).isoformat().replace("+00:00", "Z")


def _event(
    session_id: str,
    student_id: str,
    event_name: str,
    offset_min: int,
    device: str,
    stage: str,
    score: int = 0,
    total: int = 0,
    xp: int = 0,
    user_id: str | None = None,
) -> Dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "session_id": session_id,
        "user_id": user_id,
        "student_id": student_id,
        "event_name": event_name,
        "timestamp": _iso_at(offset_min),
        "metadata": {
            "device": device,
            "stage": stage,
            "score": score,
            "total": total,
            "xp": xp,
        },
    }


def generate_sample_events() -> List[Dict[str, Any]]:
    return [
        _event("sess_1", "Raphael", "view_landing", 0, "desktop", "top"),
        _event("sess_1", "Raphael", "start_assessment", 1, "desktop", "diagnostic"),
        _event("sess_1", "Raphael", "question_answered", 2, "desktop", "q1", 1, 1, 10),
        _event("sess_1", "Raphael", "question_answered", 3, "desktop", "q2", 0, 1, 5),
        _event("sess_1", "Raphael", "complete_assessment", 4, "desktop", "done", 8, 10, 50),
        _event("sess_1", "Raphael", "view_report", 5, "desktop", "report", 8, 10, 0),
        _event("sess_1", "Raphael", "click_upgrade", 6, "desktop", "upsell"),
        _event("sess_1", "Raphael", "purchase", 8, "desktop", "checkout"),
        _event("sess_2", "Leo", "view_landing", 0, "mobile", "top"),
        _event("sess_2", "Leo", "start_assessment", 1, "mobile", "diagnostic"),
        _event("sess_2", "Leo", "question_answered", 2, "mobile", "q1", 1, 1, 10),
        _event("sess_2", "Leo", "complete_assessment", 5, "mobile", "done", 6, 10, 35),
        _event("sess_2", "Leo", "view_report", 6, "mobile", "report", 6, 10, 0),
    ]
