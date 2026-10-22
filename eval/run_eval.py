#!/usr/bin/env python3
"""Eval runner for the Wag & Whisker chatbot.

  python3 eval/run_eval.py --questions        # write eval/questions.md from cases.json
  python3 eval/run_eval.py --run <config>     # send cases to the chat webhook; saves eval/runs/<config>.json
"""
import argparse
import json
import os
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


CHAT_URL = os.environ.get(
    "CHAT_URL", "http://localhost:5678/webhook/3b6f8f2e-7c1a-4d55-9a3e-2f0c9b7d4a11/chat"
)


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


def run(config: str, ids: set[str] | None = None, force: bool = False) -> None:
    out = HERE / "runs" / (f"{config}.json" if not ids else f"{config}-{'-'.join(sorted(ids))}.json")
    if out.exists() and not force:
        raise SystemExit(f"{out} already exists (committed evidence). Use a new config name, or --force to overwrite.")
    out.parent.mkdir(exist_ok=True)
    results = []
    for case in CASES:
        if ids and case["id"] not in ids:
            continue
        session = f"eval-{config}-{case['id']}-{int(time.time())}"
        turns = []
        for text in case["turns"]:
            try:
                response = ask(session, text)
                error = None
            except Exception as exc:  # keep going: one failed call shouldn't lose the answers already paid for
                response, error = {}, f"{type(exc).__name__}: {exc}"
            steps = response.get("intermediateSteps") or []
            turns.append({
                "question": text,
                "answer": response.get("output", ""),
                "tool_called": bool(steps),
                "tool_queries": [s["action"].get("toolInput") for s in steps],
                "retrieved": [c.get("pageContent", "") for c in retrieved(response)],
                "error": error,
            })
            if error:
                break
        last = turns[-1]
        results.append({"id": case["id"], "type": case["type"], **last, "turns": turns})
        print(f"{case['id']}: tool_called={last['tool_called']} chunks={len(last['retrieved'])}"
              + (f" ERROR {last['error']}" if last["error"] else ""))
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", action="store_true")
    parser.add_argument("--run", metavar="CONFIG")
    parser.add_argument("--ids", help="comma-separated case ids to run (default: all)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing results file")
    args = parser.parse_args()
    if args.questions:
        write_questions()
    if args.run:
        run(args.run, set(args.ids.split(",")) if args.ids else None, args.force)


if __name__ == "__main__":
    main()
