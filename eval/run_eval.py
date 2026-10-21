#!/usr/bin/env python3
"""Eval runner for the Wag & Whisker chatbot.

  python3 eval/run_eval.py --questions        # write eval/questions.md from cases.json
  python3 eval/run_eval.py --run c800-o150    # (Task 7) send cases to the chat webhook
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def write_questions() -> None:
    lines = [
        "# Evaluation questions",
        "",
        "Written before any run. Source: `cases.json`.",
        "",
        "| ID | Type | Question(s) | Expected answer | Expected evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in CASES:
        turns = " → ".join(c["turns"])
        lines.append(f"| {c['id']} | {c['type']} | {turns} | {c['expected']} | {c['evidence']} |")
    (HERE / "questions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", HERE / "questions.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", action="store_true")
    args = parser.parse_args()
    if args.questions:
        write_questions()


if __name__ == "__main__":
    main()
