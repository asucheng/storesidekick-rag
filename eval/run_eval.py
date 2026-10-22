#!/usr/bin/env python3
"""Eval runner for the Wag & Whisker chatbot.

  python3 eval/run_eval.py --questions        # write eval/questions.md from cases.json
  python3 eval/run_eval.py --run c800-o150    # (Task 7) send cases to the chat webhook
"""
import argparse
import json
import time
import urllib.request
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


CHAT_URL = "http://localhost:5678/webhook/3b6f8f2e-7c1a-4d55-9a3e-2f0c9b7d4a11/chat"


def ask(session: str, text: str) -> dict:
    body = json.dumps({"action": "sendMessage", "sessionId": session, "chatInput": text}).encode()
    req = urllib.request.Request(CHAT_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def retrieved(response: dict) -> list[dict]:
    """Return the chunks the search_handbook tool sent back to the agent.

    n8n shapes each tool observation as [{"response": [{"type": "text", "text": "<chunk JSON>"}]}].
    """
    chunks = []
    for step in response.get("intermediateSteps") or []:
        observation = step.get("observation") or []
        if isinstance(observation, str):  # sometimes the whole observation arrives as JSON text
            try:
                observation = json.loads(observation)
            except json.JSONDecodeError:
                chunks.append({"pageContent": observation})
                continue
        for block in observation if isinstance(observation, list) else [observation]:
            parts = block.get("response", [block]) if isinstance(block, dict) else [{"text": str(block)}]
            for part in parts:
                text = part.get("text", "") if isinstance(part, dict) else str(part)
                try:
                    doc = json.loads(text)
                except json.JSONDecodeError:
                    doc = {"pageContent": text}
                chunks.append(doc if isinstance(doc, dict) else {"pageContent": str(doc)})
    return chunks


def run(config: str, ids: set[str] | None = None) -> None:
    results = []
    for case in CASES:
        if ids and case["id"] not in ids:
            continue
        session = f"eval-{config}-{case['id']}-{int(time.time())}"
        response = {}
        for turn in case["turns"]:
            response = ask(session, turn)
        steps = response.get("intermediateSteps") or []
        chunks = retrieved(response)
        results.append({
            "id": case["id"],
            "type": case["type"],
            "question": case["turns"][-1],
            "answer": response.get("output", ""),
            "tool_called": bool(steps),
            "tool_queries": [s["action"].get("toolInput") for s in steps],
            "retrieved": [c.get("pageContent", "") for c in chunks],
        })
        print(f"{case['id']}: tool_called={bool(steps)} chunks={len(chunks)}")
    out = HERE / "runs" / (f"{config}.json" if not ids else f"{config}-{'-'.join(sorted(ids))}.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", action="store_true")
    parser.add_argument("--run", metavar="CONFIG")
    parser.add_argument("--ids", help="comma-separated case ids to run (default: all)")
    args = parser.parse_args()
    if args.questions:
        write_questions()
    if args.run:
        run(args.run, set(args.ids.split(",")) if args.ids else None)


if __name__ == "__main__":
    main()
