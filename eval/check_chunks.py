#!/usr/bin/env python3
"""Check the chunks an n8n ingest run stored (from `n8n execute --rawOutput`).

  python3 eval/check_chunks.py <raw-output.json>

Fails unless every chunk names its section, and the facts the eval depends on
sit in the same chunk as the product they belong to.
"""
import json
import sys

FACT_WITH_NAME = [
    ("dogs over 30 kg", "Tug Titan Rope"),
    ("up to 20 kg", "Twisty Rope Ring"),
    ("not for kittens under 12 weeks", "Whisker Wand"),
    ("for dogs 15–45 kg", "Iron Jaw Bone"),
]


def chunks(path: str) -> list[str]:
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw[raw.find("{"):])
    result = data["data"]["resultData"] if "data" in data else data["resultData"]
    items = result["runData"]["Pinecone insert"][-1]["data"]["main"][0]
    return [item["json"]["pageContent"].replace("\n", " ") for item in items]


def main() -> int:
    docs = chunks(sys.argv[1])
    problems = []
    # The cover/introduction comes before Section 1, so it carries an "Introduction" breadcrumb.
    no_section = [i for i, c in enumerate(docs) if not c.startswith(("Section ", "Introduction "))]
    if no_section:
        problems.append(f"{len(no_section)}/{len(docs)} chunks don't start with a section breadcrumb")
    for fact, name in FACT_WITH_NAME:
        holders = [c for c in docs if fact in c]
        if not holders:
            problems.append(f"fact not found: {fact!r}")
        elif not any(name in c for c in holders):
            problems.append(f"{fact!r} is never in the same chunk as {name!r}")
    for p in problems:
        print("FAIL:", p)
    if not problems:
        print(f"OK: {len(docs)} chunks, all with section breadcrumbs; facts stay with their product names")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
