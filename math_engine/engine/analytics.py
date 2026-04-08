from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Set

FUNNEL_STAGES = ("start", "complete", "upgrade", "convert")
EVENT_STORE: List[Dict[str, Any]] = []
# Fast indexes to improve reliability guarantees for duplicate prevention and session linkage.
_EVENT_IDS: Set[str] = set()
_SESSION_STUDENT_INDEX: Dict[str, str] = {}


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    raise ValueError("timestamp must be an ISO-8601 string or datetime object")


def _normalize_identifier(value: Any, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string")
    return normalized


def _event_fingerprint(session_id: str, student_id: str, event_name: str, timestamp: datetime) -> str:
    # Rounds to seconds so caller-side retries with identical payloads remain idempotent.
    rounded_ts = timestamp.replace(microsecond=0).isoformat()
    raw = f"{session_id}|{student_id}|{event_name}|{rounded_ts}"
    return sha256(raw.encode("utf-8")).hexdigest()[:24]


def _normalize_event(event: MutableMapping[str, Any]) -> Dict[str, Any]:
    if "session_id" not in event or "event" not in event:
        raise ValueError("event must include 'session_id' and 'event'")

    metadata = event.get("metadata")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dictionary")

    student_id_value = event.get("student_id")
    if student_id_value is None:
        student_id_value = metadata.get("student_id")
    if student_id_value is None:
        raise ValueError("event must include 'student_id' (top-level or metadata)")

    timestamp = event.get("timestamp")
    parsed_timestamp = _parse_timestamp(timestamp) if timestamp else datetime.now(timezone.utc)

    session_id = _normalize_identifier(event["session_id"], "session_id")
    student_id = _normalize_identifier(student_id_value, "student_id")
    event_name = _normalize_identifier(event["event"], "event")

    event_id = event.get("event_id") or _event_fingerprint(
        session_id=session_id,
        student_id=student_id,
        event_name=event_name,
        timestamp=parsed_timestamp,
    )

    normalized = {
        "event_id": str(event_id),
        "session_id": session_id,
        "student_id": student_id,
        "event": event_name,
        "timestamp": parsed_timestamp,
        "metadata": deepcopy(metadata),
    }
    normalized["metadata"].setdefault("student_id", student_id)
    return normalized


def _validate_session_student_link(session_id: str, student_id: str) -> None:
    previous_student = _SESSION_STUDENT_INDEX.get(session_id)
    if previous_student is not None and previous_student != student_id:
        raise ValueError(
            "session_id is already linked to a different student_id "
            f"({session_id}: {previous_student} != {student_id})"
        )


def track_event(event: MutableMapping[str, Any]) -> Dict[str, Any]:
    """Store and return a normalized analytics event with idempotent dedupe."""
    normalized = _normalize_event(event)
    _validate_session_student_link(normalized["session_id"], normalized["student_id"])

    was_duplicate = normalized["event_id"] in _EVENT_IDS
    if not was_duplicate:
        EVENT_STORE.append(normalized)
        _EVENT_IDS.add(normalized["event_id"])
        _SESSION_STUDENT_INDEX[normalized["session_id"]] = normalized["student_id"]

    out = deepcopy(normalized)
    out["ingested"] = not was_duplicate
    out["duplicate"] = was_duplicate
    return out


def compute_funnel(events: Iterable[MutableMapping[str, Any]]) -> Dict[str, Any]:
    """Compute top-line funnel rates and stage counts by unique session."""
    normalized_events: List[Dict[str, Any]] = []
    invalid_events: List[Dict[str, Any]] = []
    seen_event_ids: Set[str] = set()
    session_student_index: Dict[str, str] = {}

    for raw_event in events:
        try:
            event = _normalize_event(raw_event)
            if event["event_id"] in seen_event_ids:
                continue
            seen_event_ids.add(event["event_id"])

            existing_student = session_student_index.get(event["session_id"])
            if existing_student and existing_student != event["student_id"]:
                invalid_events.append({"reason": "session_student_mismatch", "event": event})
                continue
            session_student_index[event["session_id"]] = event["student_id"]
            normalized_events.append(event)
        except Exception as exc:  # malformed event should not break the whole batch
            invalid_events.append({"reason": "invalid_event", "error": str(exc), "event": deepcopy(dict(raw_event))})

    sessions: Dict[str, set[str]] = defaultdict(set)
    for event in normalized_events:
        sessions[event["session_id"]].add(event["event"])

    total_sessions = len(sessions)
    started = sum(1 for e in sessions.values() if "start" in e)
    completed = sum(1 for e in sessions.values() if "complete" in e)
    upgraded = sum(1 for e in sessions.values() if "upgrade" in e)
    converted = sum(1 for e in sessions.values() if "convert" in e)

    def safe_rate(numerator: int, denominator: int) -> float:
        return round((numerator / denominator), 4) if denominator else 0.0

    return {
        "totals": {
            "sessions": total_sessions,
            "started": started,
            "completed": completed,
            "upgraded": upgraded,
            "converted": converted,
            "events_ingested": len(normalized_events),
            "events_rejected": len(invalid_events),
        },
        "stage_counts": {
            "start": started,
            "complete": completed,
            "upgrade": upgraded,
            "convert": converted,
        },
        "start_rate": safe_rate(started, total_sessions),
        "completion_rate": safe_rate(completed, started),
        "upgrade_rate": safe_rate(upgraded, completed),
        "conversion_rate": safe_rate(converted, started),
        "invalid_events": invalid_events,
    }


def segment_funnel(events: Iterable[MutableMapping[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    """Compute funnel metrics split by a metadata (or top-level) key."""
    buckets: Dict[str, List[MutableMapping[str, Any]]] = defaultdict(list)

    for raw_event in events:
        event = _normalize_event(raw_event)
        value: Optional[Any] = event["metadata"].get(key)
        if value is None and key in event:
            value = event[key]
        segment_name = str(value) if value not in (None, "") else "unknown"
        buckets[segment_name].append(event)

    return {segment: compute_funnel(segment_events) for segment, segment_events in buckets.items()}


def detect_dropoff(funnel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify the largest drop between consecutive funnel stages."""
    stage_counts = funnel_data.get("stage_counts", {})

    biggest: Optional[Dict[str, Any]] = None
    for left, right in zip(FUNNEL_STAGES, FUNNEL_STAGES[1:]):
        left_count = int(stage_counts.get(left, 0))
        right_count = int(stage_counts.get(right, 0))
        drop = max(left_count - right_count, 0)
        drop_rate = round((drop / left_count), 4) if left_count else 0.0
        candidate = {
            "from_stage": left,
            "to_stage": right,
            "drop_count": drop,
            "drop_rate": drop_rate,
        }
        if biggest is None or candidate["drop_rate"] > biggest["drop_rate"]:
            biggest = candidate

    return biggest or {
        "from_stage": None,
        "to_stage": None,
        "drop_count": 0,
        "drop_rate": 0.0,
    }


def generate_daily_summary(events: Iterable[MutableMapping[str, Any]]) -> Dict[str, Any]:
    """Generate daily funnel summary with day-over-day deltas and recommendation."""
    normalized_events = [_normalize_event(event) for event in events]
    if not normalized_events:
        return {
            "date": None,
            "funnel_metrics": compute_funnel([]),
            "deltas_vs_previous_day": {},
            "biggest_issue": "No events received",
            "recommended_action": "Start tracking start/complete/upgrade/convert events.",
        }

    events_by_day: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in normalized_events:
        date_key = event["timestamp"].date().isoformat()
        events_by_day[date_key].append(event)

    sorted_days = sorted(events_by_day)
    current_day = sorted_days[-1]
    prev_day = sorted_days[-2] if len(sorted_days) > 1 else None

    current_funnel = compute_funnel(events_by_day[current_day])
    previous_funnel = compute_funnel(events_by_day[prev_day]) if prev_day else compute_funnel([])

    metric_keys = ("start_rate", "completion_rate", "upgrade_rate", "conversion_rate")
    deltas = {
        metric: round(current_funnel[metric] - previous_funnel[metric], 4)
        for metric in metric_keys
    }

    biggest_dropoff = detect_dropoff(current_funnel)
    stage = biggest_dropoff.get("from_stage")

    action_map = {
        "start": "Improve top-of-funnel entry points: shorten onboarding and clarify the first task.",
        "complete": "Improve task completion: add progress nudges and simplify difficult question flows.",
        "upgrade": "Strengthen value messaging: surface premium outcomes before the paywall.",
        "convert": "Reduce purchase friction: simplify checkout and highlight trust signals.",
        None: "Collect more data to identify the dominant funnel bottleneck.",
    }

    return {
        "date": current_day,
        "funnel_metrics": current_funnel,
        "deltas_vs_previous_day": deltas,
        "biggest_issue": (
            f"Largest drop-off occurs between {biggest_dropoff['from_stage']} and "
            f"{biggest_dropoff['to_stage']} ({biggest_dropoff['drop_rate']:.2%})."
            if biggest_dropoff.get("from_stage")
            else "Insufficient funnel data"
        ),
        "recommended_action": action_map.get(stage, action_map[None]),
        "dropoff": biggest_dropoff,
    }


EXAMPLE_EVENTS: List[Dict[str, Any]] = [
    {"session_id": "s1", "student_id": "st-001", "event": "start", "timestamp": "2026-04-06T09:00:00Z", "metadata": {"device": "mobile", "year": 4}},
    {"session_id": "s1", "student_id": "st-001", "event": "complete", "timestamp": "2026-04-06T09:08:00Z", "metadata": {"device": "mobile", "year": 4}},
    {"session_id": "s2", "student_id": "st-002", "event": "start", "timestamp": "2026-04-06T10:00:00Z", "metadata": {"device": "desktop", "year": 5}},
    {"session_id": "s3", "student_id": "st-003", "event": "start", "timestamp": "2026-04-07T08:20:00Z", "metadata": {"device": "mobile", "year": 4}},
    {"session_id": "s3", "student_id": "st-003", "event": "complete", "timestamp": "2026-04-07T08:40:00Z", "metadata": {"device": "mobile", "year": 4}},
    {"session_id": "s3", "student_id": "st-003", "event": "upgrade", "timestamp": "2026-04-07T08:42:00Z", "metadata": {"device": "mobile", "year": 4}},
    {"session_id": "s4", "student_id": "st-004", "event": "start", "timestamp": "2026-04-07T09:15:00Z", "metadata": {"device": "desktop", "year": 6}},
    {"session_id": "s5", "student_id": "st-005", "event": "start", "timestamp": "2026-04-07T10:00:00Z", "metadata": {"device": "tablet", "year": 5}},
    {"session_id": "s5", "student_id": "st-005", "event": "complete", "timestamp": "2026-04-07T10:10:00Z", "metadata": {"device": "tablet", "year": 5}},
    {"session_id": "s5", "student_id": "st-005", "event": "upgrade", "timestamp": "2026-04-07T10:15:00Z", "metadata": {"device": "tablet", "year": 5}},
    {"session_id": "s5", "student_id": "st-005", "event": "convert", "timestamp": "2026-04-07T10:16:00Z", "metadata": {"device": "tablet", "year": 5}},
]


SAMPLE_DASHBOARD_OUTPUT = {
    "summary": generate_daily_summary(EXAMPLE_EVENTS),
    "segments": {
        "device": segment_funnel(EXAMPLE_EVENTS, "device"),
        "year": segment_funnel(EXAMPLE_EVENTS, "year"),
    },
}
