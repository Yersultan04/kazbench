#!/usr/bin/env python3
"""Export benchmark items to a human-friendly CSV for native-speaker validation.

Produces one review CSV (UTF-8 with BOM so Excel shows Kazakh correctly) with a
readable rendering of each item plus blank `verdict` / `correction` / `note` columns
for the reviewer to fill. Feed the edited CSV back with import_csv.py.

Usage:
    python tools/data/export_csv.py benchmark/dev/ --out validation/review.csv

ASCII-only console output (Windows cp1251 safe).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

COLUMNS = [
    "id", "task", "source", "validated",
    "content", "correct_answer",
    "verdict", "correction", "note",
]


def render(item: dict) -> tuple[str, str]:
    """Return (human-readable content, correct-answer text) for review."""
    task = item.get("task", "")
    if task in ("knowledge_mc", "reading_comprehension", "grammar_morphology"):
        choices = item.get("choices", [])
        opts = "  ".join(f"{i}){c}" for i, c in enumerate(choices))
        passage = f"[{item.get('passage')}]  " if item.get("passage") else ""
        ans = item.get("answer")
        correct = choices[ans] if isinstance(ans, int) and 0 <= ans < len(choices) else "?"
        return f"{passage}Q: {item.get('question','')}  | {opts}  | answer_idx={ans}", str(correct)
    if task == "sentiment":
        return f"TEXT: {item.get('text','')}", str(item.get("label", ""))
    if task == "translation":
        return (
            f"{item.get('source_lang','')}->{item.get('target_lang','')}: {item.get('source_text','')}",
            str(item.get("reference", "")),
        )
    if task == "instruction_following":
        return f"INSTRUCTION: {item.get('instruction','')}", f"RUBRIC: {item.get('rubric','')}"
    return json.dumps(item, ensure_ascii=False), ""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", type=Path, help="benchmark dir or single .jsonl")
    ap.add_argument("--out", type=Path, default=Path("validation/review.csv"))
    args = ap.parse_args(argv[1:])

    files = sorted(args.src.glob("*.jsonl")) if args.src.is_dir() else [args.src]
    if not files:
        print(f"ERROR: no .jsonl files at '{args.src}'")
        return 2

    rows: list[dict] = []
    for path in files:
        for raw in path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            item = json.loads(raw)
            content, correct = render(item)
            rows.append({
                "id": item.get("id", ""),
                "task": item.get("task", ""),
                "source": item.get("source", ""),
                "validated": item.get("validated", False),
                "content": content,
                "correct_answer": correct,
                "verdict": "",      # reviewer fills: ok | fix | drop
                "correction": "",   # reviewer fills if verdict=fix
                "note": "",
            })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"exported {len(rows)} items -> {args.out}")
    print("Reviewer: fill 'verdict' with ok | fix | drop. For fix, put the corrected")
    print("answer/text in 'correction'. Then run: python tools/data/import_csv.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
