from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Dict, List

from .generator import generate_question
from .student_model import calculate_accuracy


def _bucket_skills(student: Dict[str, Any], skills: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    year = student.get("student_year", 0)
    weakest = []
    current = []
    stretch = []

    for skill in skills:
        expected_year = int(skill["expected_year"])
        accuracy = calculate_accuracy(student, skill["skill_id"])
        skill_with_accuracy = dict(skill)
        skill_with_accuracy["accuracy"] = accuracy

        if accuracy < 0.7 and expected_year <= year:
            weakest.append(skill_with_accuracy)
        elif expected_year == year:
            current.append(skill_with_accuracy)
        elif expected_year > year:
            stretch.append(skill_with_accuracy)
        else:
            current.append(skill_with_accuracy)

    weakest.sort(key=lambda s: s["accuracy"])
    current.sort(key=lambda s: s["difficulty_level"])
    stretch.sort(key=lambda s: (s["expected_year"], s["difficulty_level"]))
    return {"weakest": weakest, "current": current, "stretch": stretch}


def _choose_templates_for_skill(
    skill_id: str, templates_by_skill: Dict[str, List[Dict[str, Any]]], rng: random.Random
) -> Dict[str, Any]:
    candidates = templates_by_skill.get(skill_id, [])
    if not candidates:
        raise ValueError(f"No templates found for skill {skill_id}")
    return rng.choice(candidates)


def generate_worksheet(
    student: Dict[str, Any],
    skills: List[Dict[str, Any]],
    templates: List[Dict[str, Any]],
    question_count: int = 25,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    if question_count < 20 or question_count > 30:
        raise ValueError("question_count must be between 20 and 30")

    rng = random.Random(seed)
    buckets = _bucket_skills(student, skills)

    targets = {
        "weakest": max(1, round(question_count * 0.6)),
        "current": max(1, round(question_count * 0.3)),
    }
    targets["stretch"] = question_count - targets["weakest"] - targets["current"]

    templates_by_skill: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for template in templates:
        templates_by_skill[template["skill_id"]].append(template)

    worksheet: List[Dict[str, Any]] = []
    for bucket_name in ("weakest", "current", "stretch"):
        skill_pool = buckets[bucket_name] or buckets["current"] or buckets["weakest"] or skills
        for _ in range(targets[bucket_name]):
            skill = rng.choice(skill_pool)
            template = _choose_templates_for_skill(skill["skill_id"], templates_by_skill, rng)
            worksheet.append(generate_question(template, rng=rng))

    rng.shuffle(worksheet)
    return worksheet
