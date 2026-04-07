from __future__ import annotations

from typing import Any, Dict, List


StudentRecord = Dict[str, Any]


def _ensure_skill_bucket(student: StudentRecord, skill_id: str) -> None:
    student.setdefault("skill_stats", {})
    student["skill_stats"].setdefault(skill_id, {"correct": 0, "attempted": 0})


def update_skill_score(student: StudentRecord, skill_id: str, correct: bool) -> None:
    _ensure_skill_bucket(student, skill_id)
    bucket = student["skill_stats"][skill_id]
    bucket["attempted"] += 1
    if correct:
        bucket["correct"] += 1


def calculate_accuracy(student: StudentRecord, skill_id: str) -> float:
    _ensure_skill_bucket(student, skill_id)
    bucket = student["skill_stats"][skill_id]
    if bucket["attempted"] == 0:
        return 0.0
    return bucket["correct"] / bucket["attempted"]


def identify_gaps(student: StudentRecord, skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    year = student.get("student_year", 0)
    gaps: List[Dict[str, Any]] = []

    for skill in skills:
        expected_year = int(skill["expected_year"])
        accuracy = calculate_accuracy(student, skill["skill_id"])
        if year >= expected_year and accuracy < 0.7:
            gaps.append(
                {
                    "skill_id": skill["skill_id"],
                    "skill_name": skill["skill_name"],
                    "expected_year": expected_year,
                    "accuracy": round(accuracy, 3),
                }
            )

    gaps.sort(key=lambda s: (s["accuracy"], s["expected_year"]))
    return gaps
