from __future__ import annotations

import ast
import json
import random
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


class SafeExpressionEvaluator(ast.NodeVisitor):
    """Safely evaluates arithmetic expressions with named variables."""

    ALLOWED_BINOPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
    }
    ALLOWED_UNARYOPS = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    def __init__(self, variables: Dict[str, Any]):
        self.variables = variables

    def evaluate(self, expression: str) -> Any:
        tree = ast.parse(expression, mode="eval")
        return self.visit(tree.body)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.ALLOWED_BINOPS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.ALLOWED_BINOPS[op_type](left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.ALLOWED_UNARYOPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = self.visit(node.operand)
        return self.ALLOWED_UNARYOPS[op_type](operand)

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.variables:
            raise ValueError(f"Unknown variable in expression: {node.id}")
        return self.variables[node.id]

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def generate_variables(template: Dict[str, Any], rng: random.Random | None = None) -> Dict[str, int]:
    rng = rng or random.Random()
    variables: Dict[str, int] = {}
    for name, bounds in template["variables"].items():
        low = int(bounds["min"])
        high = int(bounds["max"])
        variables[name] = rng.randint(low, high)
    return variables


def _digits(number: int) -> List[int]:
    return [int(ch) for ch in str(abs(number))]


def _has_carry_addition(a: int, b: int) -> bool:
    carry = 0
    da = list(reversed(_digits(a)))
    db = list(reversed(_digits(b)))
    for i in range(max(len(da), len(db))):
        x = da[i] if i < len(da) else 0
        y = db[i] if i < len(db) else 0
        if x + y + carry >= 10:
            return True
        carry = 0
    return False


def _has_borrow_subtraction(a: int, b: int) -> bool:
    da = list(reversed(_digits(a)))
    db = list(reversed(_digits(b)))
    borrow = 0
    for i in range(max(len(da), len(db))):
        x = da[i] if i < len(da) else 0
        y = db[i] if i < len(db) else 0
        x -= borrow
        if x < y:
            return True
        borrow = 0
    return False


def apply_constraints(
    variables: Dict[str, int],
    template: Dict[str, Any],
    rng: random.Random | None = None,
    max_attempts: int = 250,
) -> Dict[str, int]:
    rng = rng or random.Random()
    constraints = template.get("constraints", {})
    for _ in range(max_attempts):
        valid = True
        working = dict(variables)

        if constraints.get("a_gte_b") and working.get("a", 0) < working.get("b", 0):
            valid = False

        if constraints.get("multiple_of"):
            for key, multiple in constraints["multiple_of"].items():
                if working[key] % multiple != 0:
                    valid = False

        if constraints.get("divides_evenly"):
            numerator = working[constraints["divides_evenly"]["numerator"]]
            denominator = working[constraints["divides_evenly"]["denominator"]]
            if denominator == 0 or numerator % denominator != 0:
                valid = False

        if constraints.get("no_carry") and {"a", "b"}.issubset(working):
            if _has_carry_addition(working["a"], working["b"]):
                valid = False

        if constraints.get("no_borrow") and {"a", "b"}.issubset(working):
            if working["a"] < working["b"] or _has_borrow_subtraction(working["a"], working["b"]):
                valid = False

        if constraints.get("proper_fraction") and {"numerator", "denominator"}.issubset(working):
            if not (0 < working["numerator"] < working["denominator"]):
                valid = False

        if constraints.get("non_zero"):
            for key in constraints["non_zero"]:
                if working.get(key, 0) == 0:
                    valid = False

        if constraints.get("sum_to"):
            left = sum(working[key] for key in constraints["sum_to"]["vars"])
            if left != constraints["sum_to"]["value"]:
                valid = False

        if valid:
            return working

        variables = generate_variables(template, rng=rng)

    raise ValueError(f"Unable to satisfy constraints for template {template['template_id']}")


def build_question(template: Dict[str, Any], variables: Dict[str, int]) -> str:
    return template["question_format"].format(**variables)


def compute_answer(variables: Dict[str, int], template: Dict[str, Any]) -> Any:
    expression = template["answer_formula"]
    evaluator = SafeExpressionEvaluator(variables)
    result = evaluator.evaluate(expression)
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return round(result, 2) if isinstance(result, float) else result


def _generate_distractors(answer: Any, template: Dict[str, Any], rng: random.Random) -> List[Any]:
    rules = template.get("distractor_rules", {})
    distractors: set[Any] = set()

    if isinstance(answer, float) and not float(answer).is_integer():
        step = rules.get("step", 0.1)
        offsets = rules.get("offsets", [-2, -1, 1, 2])
        for offset in offsets:
            distractors.add(round(answer + offset * step, 2))
    else:
        answer_int = int(answer)
        offsets = rules.get("offsets", [-10, -1, 1, 10])
        for offset in offsets:
            distractors.add(answer_int + int(offset))

    distractors.discard(answer)
    ordered = list(distractors)
    rng.shuffle(ordered)
    return ordered[:3]


def generate_question(template: Dict[str, Any], rng: random.Random | None = None) -> Dict[str, Any]:
    rng = rng or random.Random()
    variables = generate_variables(template, rng=rng)
    variables = apply_constraints(variables, template, rng=rng)
    question_text = build_question(template, variables)
    answer = compute_answer(variables, template)
    return {
        "question_id": str(uuid.uuid4()),
        "template_id": template["template_id"],
        "skill_id": template["skill_id"],
        "question_text": question_text,
        "answer": answer,
        "distractors": _generate_distractors(answer, template, rng=rng),
        "difficulty": template["difficulty"],
    }


def generate_questions(templates: Iterable[Dict[str, Any]], total: int, seed: int = 42) -> List[Dict[str, Any]]:
    template_list = list(templates)
    if not template_list:
        return []
    rng = random.Random(seed)
    questions: List[Dict[str, Any]] = []
    for i in range(total):
        template = template_list[i % len(template_list)]
        questions.append(generate_question(template, rng=rng))
    return questions


if __name__ == "__main__":
    templates = load_jsonl(DATA_DIR / "templates.jsonl")
    sample = generate_questions(templates, total=5, seed=7)
    for record in sample:
        print(json.dumps(record, ensure_ascii=False))
