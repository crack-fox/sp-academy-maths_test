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

## Student Diagnostics, Insights, and Funnel

### 1) Generate Student Report

Use `engine/report.py` to compute strand progress, per-skill status, and gap summary.

```python
from pathlib import Path
from math_engine.engine.generator import load_jsonl
from math_engine.engine.report import generate_student_report

base = Path("math_engine/data")
skills = load_jsonl(base / "skills.jsonl")

student = {
    "student_id": "st-101",
    "student_year": 4,
    "plan_type": "free",
    "skill_stats": {
        "SK-NA-S2-02": {"correct": 4, "attempted": 10},
        "SK-NA-S2-03": {"correct": 8, "attempted": 10},
    },
}

report = generate_student_report(student, skills)
```

How report logic works:
- Aggregates progress by syllabus strand.
- Marks a skill as `behind` when `accuracy < 0.7` and student year is at/above the expected year level.
- Computes `years_behind` from the average expected year of behind skills.
- Prioritises lowest-accuracy skills in `gap_summary.priority_skills`.

### 2) Compute Parent-Friendly Insights

Use `engine/insights.py` to turn diagnostics into concise, dynamic parent messaging.

```python
from math_engine.engine.insights import generate_insights

insights = generate_insights(report)
```

Insight logic:
- Headline and recommendations are generated from actual weak skills in the report.
- No generic placeholders: the weakest skills are explicitly named.
- If no skills are behind, insight content shifts to maintenance guidance.

### 3) Generate Monetisation Funnel State

Use `engine/funnel.py` to produce plan recommendations and paywall details.

```python
from math_engine.engine.funnel import generate_funnel_state

funnel = generate_funnel_state(student, report)
```

Funnel logic:
- `premium` is recommended when there are multiple (3+) skill gaps.
- `basic` is recommended for minor gaps.
- Free plans include locked features and CTA messaging.
- `recommended_plan.focus_skills` can be passed directly to worksheet generation.

### 4) Generate Focused Worksheets

`engine/worksheet.py` now accepts `focus_skills` to target intervention areas.

```python
from math_engine.engine.worksheet import generate_worksheet
from math_engine.engine.generator import load_jsonl

templates = load_jsonl(base / "templates.jsonl")
worksheet = generate_worksheet(
    student,
    skills,
    templates,
    question_count=25,
    seed=99,
    focus_skills=funnel["recommended_plan"]["focus_skills"],
)
```

When `focus_skills` is supplied, worksheet composition prioritises those skills before weakest/current/stretch balancing.
