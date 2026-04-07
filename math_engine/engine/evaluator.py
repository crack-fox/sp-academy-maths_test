from __future__ import annotations

from typing import Any, Dict


def evaluate_response(question: Dict[str, Any], response: Any) -> bool:
    answer = question["answer"]
    if isinstance(answer, float):
        try:
            return abs(float(response) - answer) < 1e-9
        except (TypeError, ValueError):
            return False
    return str(response).strip() == str(answer)
