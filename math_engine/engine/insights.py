from __future__ import annotations

from typing import Any, Dict, List


def _format_skill_list(skills: List[str]) -> str:
    if not skills:
        return "core year-level skills"
    if len(skills) == 1:
        return skills[0]
    if len(skills) == 2:
        return f"{skills[0]} and {skills[1]}"
    return f"{', '.join(skills[:-1])}, and {skills[-1]}"


def generate_insights(report: Dict[str, Any]) -> Dict[str, str]:
    year = report.get("year", 0)
    behind_skills = [
        skill for skill in report.get("skill_breakdown", []) if skill.get("status") == "behind"
    ]
    weak_skill_names = [skill["skill_name"] for skill in sorted(behind_skills, key=lambda s: s["accuracy"])[:3]]
    weak_skills_text = _format_skill_list(weak_skill_names)

    years_behind = float(report.get("gap_summary", {}).get("years_behind", 0.0))

    if weak_skill_names:
        headline = f"Your child is behind in {weak_skills_text}"
        summary = (
            f"In Year {year}, your child is currently below confidence level in {weak_skills_text}. "
            "These skills are showing lower recent accuracy than expected for this stage."
        )
        risk_statement = (
            f"This gap is about {years_behind:.1f} year(s) behind expected level, which can make multi-step "
            "problem solving and new topic learning harder in the next term."
        )
        recommendation = (
            f"Prioritise practice in {weak_skills_text} with short daily sessions and revisit prerequisite skills "
            "before introducing harder mixed questions."
        )
    else:
        headline = "Your child is tracking well across assessed maths skills"
        summary = (
            f"In Year {year}, current responses are at or above the expected confidence threshold across assessed skills."
        )
        risk_statement = (
            "There are no immediate learning-risk signals, but regular mixed revision is still important to maintain fluency."
        )
        recommendation = (
            "Continue with balanced weekly practice across number, geometry, and statistics to keep progress steady."
        )

    return {
        "headline": headline,
        "summary": summary,
        "risk_statement": risk_statement,
        "recommendation": recommendation,
    }
