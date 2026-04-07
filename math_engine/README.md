# NSW Primary Maths Engine

Backend-ready maths generation engine aligned to NSW primary stages (Early Stage 1 to Stage 3).

## Structure

```text
math_engine/
  data/
    skills.jsonl
    templates.jsonl
    questions.jsonl
  engine/
    generator.py
    evaluator.py
    worksheet.py
    student_model.py
  scripts/
    generate_dataset.py
```

## Generate Dataset

From repository root:

```bash
python math_engine/scripts/generate_dataset.py --count 1200 --seed 42
```

Output file:
- `math_engine/data/questions.jsonl`

## Generate Adaptive Worksheets

Example usage:

```python
import json
from pathlib import Path
from math_engine.engine.generator import load_jsonl
from math_engine.engine.worksheet import generate_worksheet

base = Path("math_engine/data")
skills = load_jsonl(base / "skills.jsonl")
templates = load_jsonl(base / "templates.jsonl")

student = {
    "student_id": "st-001",
    "student_year": 4,
    "skill_stats": {
        "SK-NA-S2-02": {"correct": 4, "attempted": 10},
        "SK-NA-S2-03": {"correct": 8, "attempted": 10}
    }
}

worksheet = generate_worksheet(student, skills, templates, question_count=25, seed=99)
print(json.dumps(worksheet[:3], indent=2))
```

Distribution logic:
- 60% questions from weakest skills
- 30% from current-level skills
- 10% stretch skills

## Extend Templates

Add new JSONL records to `data/templates.jsonl` with:
- `template_id`
- `skill_id`
- `question_format` (e.g. `"What is {a} + {b}?"`)
- `variables` with min/max ranges
- `constraints` (e.g. `no_carry`, `no_borrow`, `divides_evenly`)
- `answer_formula` (safe arithmetic expression)
- `distractor_rules`
- `difficulty`

Then regenerate questions:

```bash
python math_engine/scripts/generate_dataset.py --count 1500 --seed 123
```

## Notes

- `engine/generator.py` uses an AST-based safe evaluator for arithmetic formulas.
- Constraint enforcement retries variable generation until a valid sample is found.
- The code is deterministic when a seed is provided.
