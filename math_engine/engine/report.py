from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from .student_model import calculate_accuracy


STRAND_LABELS = {
    "Number & Algebra": "Number and Algebra",
    "Measurement & Geometry": "Measurement and Geometry",
    "Statistics & Probability": "Statistics and Probability",
}


def _normalise_strand_label(strand: str) -> str:
    return STRAND_LABELS.get(strand, strand)


def generate_student_report(student: Dict[str, Any], skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    student_year = int(student.get("student_year", 0))

    strand_accuracy: Dict[str, List[float]] = defaultdict(list)
    skill_breakdown: List[Dict[str, Any]] = []
    behind_skills: List[Dict[str, Any]] = []

    for skill in skills:
        skill_id = skill["skill_id"]
        expected_year = int(skill["expected_year"])
        accuracy = round(calculate_accuracy(student, skill_id), 3)

        strand_label = _normalise_strand_label(skill.get("strand", "Unknown"))
        strand_accuracy[strand_label].append(accuracy)

        status = "behind" if accuracy < 0.7 and student_year >= expected_year else "on_track"
        breakdown_item = {
            "skill_id": skill_id,
            "skill_name": skill["skill_name"],
            "expected_year": expected_year,
            "accuracy": accuracy,
            "status": status,
        }
        skill_breakdown.append(breakdown_item)

        if status == "behind":
            behind_skills.append(breakdown_item)

    overall_progress = {
        strand: round(sum(scores) / len(scores), 3) for strand, scores in strand_accuracy.items() if scores
    }

    if behind_skills:
        average_expected_year = sum(skill["expected_year"] for skill in behind_skills) / len(behind_skills)
        years_behind = round(max(0.0, student_year - average_expected_year), 2)
    else:
        years_behind = 0.0

    priority_skills = [skill["skill_name"] for skill in sorted(behind_skills, key=lambda s: s["accuracy"])[:3]]

    skill_breakdown.sort(key=lambda s: (s["status"] != "behind", s["accuracy"], s["expected_year"]))

    return {
        "student_id": student.get("student_id", "unknown"),
        "year": student_year,
        "overall_progress": overall_progress,
        "skill_breakdown": skill_breakdown,
        "gap_summary": {
            "years_behind": years_behind,
            "priority_skills": priority_skills,
        },
    }
