from __future__ import annotations

from typing import Any, Dict, List


def generate_funnel_state(student: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    plan_type = student.get("plan_type", "free")

    behind_skills = [
        skill for skill in report.get("skill_breakdown", []) if skill.get("status") == "behind"
    ]
    weak_skills = [skill["skill_name"] for skill in sorted(behind_skills, key=lambda s: s["accuracy"])[:5]]

    if len(behind_skills) >= 3:
        recommended_plan = "premium"
        worksheets_per_week = 5
    elif len(behind_skills) >= 1:
        recommended_plan = "basic"
        worksheets_per_week = 3
    else:
        recommended_plan = "basic" if plan_type == "free" else plan_type
        worksheets_per_week = 2

    if plan_type == "free":
        locked_features = [
            "full diagnostic skill history",
            "weekly intervention sequence",
            "parent progress alerts",
        ]
        cta = "Start personalised plan"
    elif plan_type == "basic":
        locked_features = ["adaptive revision paths", "priority support"]
        cta = "Upgrade to Premium for deeper support"
    else:
        locked_features = []
        cta = "You have full access"

    return {
        "plan_type": plan_type,
        "recommended_plan": {
            "plan": recommended_plan,
            "worksheets_per_week": worksheets_per_week,
            "focus_skills": weak_skills,
        },
        "paywall": {
            "locked_features": locked_features,
            "cta": cta,
        },
    }
