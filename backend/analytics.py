from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def compute_funnel(events: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    event_list = list(events)
    views = sum(1 for e in event_list if e.get("event_name") == "view_landing")
    starts = sum(1 for e in event_list if e.get("event_name") == "start_assessment")
    completions = sum(
        1 for e in event_list if e.get("event_name") == "complete_assessment"
    )
    upgrades = sum(1 for e in event_list if e.get("event_name") == "click_upgrade")
    purchases = sum(1 for e in event_list if e.get("event_name") == "purchase")

    return {
        "start_rate": _safe_rate(starts, views),
        "completion_rate": _safe_rate(completions, starts),
        "upgrade_rate": _safe_rate(upgrades, completions),
        "conversion_rate": _safe_rate(purchases, upgrades),
    }


def compute_student_stats(events: Iterable[Dict[str, Any]], student_id: str) -> Dict[str, Any]:
    filtered = [e for e in events if e.get("student_id") == student_id]
    answered = [e for e in filtered if e.get("event_name") == "question_answered"]

    total_xp = 0.0
    total_correct = 0.0
    total_questions = 0.0

    for event in answered:
        meta = event.get("metadata", {})
        total_xp += float(meta.get("xp", 0) or 0)
        total_correct += float(meta.get("score", 0) or 0)
        total_questions += float(meta.get("total", 0) or 0)

    accuracy = _safe_rate(int(total_correct), int(total_questions))

    return {
        "student_id": student_id,
        "total_xp": round(total_xp, 2),
        "accuracy": accuracy,
        "total_questions_answered": len(answered),
    }


def segment_funnel(events: Iterable[Dict[str, Any]], key: str) -> Dict[str, Dict[str, float]]:
    segments: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in events:
        metadata = event.get("metadata", {})
        segment_value = metadata.get(key)
        if segment_value is None:
            segment_value = "unknown"
        segments[str(segment_value)].append(event)

    return {segment: compute_funnel(segment_events) for segment, segment_events in segments.items()}
