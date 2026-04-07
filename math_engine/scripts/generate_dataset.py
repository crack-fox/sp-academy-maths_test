from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from engine.generator import generate_questions, load_jsonl

DATA_DIR = BASE_DIR / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate maths questions dataset from templates.")
    parser.add_argument("--count", type=int, default=1200, help="Number of questions to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    templates = load_jsonl(DATA_DIR / "templates.jsonl")
    questions = generate_questions(templates, total=args.count, seed=args.seed)

    output_path = DATA_DIR / "questions.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for question in questions:
            handle.write(json.dumps(question, ensure_ascii=False) + "\n")

    print(f"Generated {len(questions)} questions at {output_path}")


if __name__ == "__main__":
    main()
