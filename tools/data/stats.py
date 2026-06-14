#!/usr/bin/env python3
"""KazBench dataset statistics.

Prints per-task item counts, percentage validated, and a source breakdown
for a directory of benchmark JSONL files (or a single file).

Usage:
    python tools/data/stats.py benchmark/dev/
    python tools/data/stats.py benchmark/dev/translation.jsonl

ASCII-only console output (Windows cp1251 safe).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

TASKS: list[str] = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]


def gather_files(target: Path) -> list[Path]:
    if target.is_dir():
        return sorted(target.glob("*.jsonl"))
    if target.is_file():
        return [target]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/data/stats.py <file-or-dir>")
        return 2

    target = Path(argv[1])
    files = gather_files(target)
    if not files:
        print(f"ERROR: no .jsonl files found at '{target}'")
        return 2

    per_task_total: Counter[str] = Counter()
    per_task_validated: Counter[str] = Counter()
    per_task_canary: Counter[str] = Counter()
    per_task_source: dict[str, Counter[str]] = defaultdict(Counter)
    per_task_answer_idx: dict[str, Counter[int]] = defaultdict(Counter)
    source_total: Counter[str] = Counter()
    bad_lines = 0

    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            print(f"ERROR: cannot read {path}: {exc}")
            return 2
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError:
                bad_lines += 1
                continue
            if not isinstance(item, dict):
                bad_lines += 1
                continue
            task = str(item.get("task", "unknown"))
            source = str(item.get("source", "unknown"))
            per_task_total[task] += 1
            if item.get("validated") is True:
                per_task_validated[task] += 1
            if isinstance(item.get("canary"), str):
                per_task_canary[task] += 1
            per_task_source[task][source] += 1
            source_total[source] += 1
            if isinstance(item.get("answer"), int) and not isinstance(item.get("answer"), bool):
                per_task_answer_idx[task][item["answer"]] += 1

    total = sum(per_task_total.values())

    print("=== KazBench dataset stats ===")
    print(f"files: {len(files)}    items: {total}")
    if bad_lines:
        print(f"WARNING: {bad_lines} unparseable line(s) skipped")
    print()

    header = f"{'task':24s} {'items':>6s} {'valid%':>8s} {'canary':>7s}"
    print(header)
    print("-" * len(header))
    # known tasks first (stable order), then any unexpected tasks
    known = [t for t in TASKS if per_task_total.get(t)]
    extra = sorted(t for t in per_task_total if t not in TASKS)
    for task in known + extra:
        n = per_task_total[task]
        v = per_task_validated[task]
        pct = (100.0 * v / n) if n else 0.0
        c = per_task_canary[task]
        print(f"{task:24s} {n:6d} {pct:7.1f}% {c:7d}")
    print("-" * len(header))
    total_valid = sum(per_task_validated.values())
    total_pct = (100.0 * total_valid / total) if total else 0.0
    print(f"{'TOTAL':24s} {total:6d} {total_pct:7.1f}% {sum(per_task_canary.values()):7d}")
    print()

    print("source breakdown (overall):")
    for src, n in source_total.most_common():
        pct = (100.0 * n / total) if total else 0.0
        print(f"  {src:12s} {n:5d}  ({pct:5.1f}%)")
    print()

    print("source breakdown (per task):")
    for task in known + extra:
        parts = ", ".join(
            f"{src}={cnt}" for src, cnt in sorted(per_task_source[task].items())
        )
        print(f"  {task:24s} {parts}")

    # Answer-index distribution for multiple-choice tasks: a heavily skewed
    # correct-answer position is trivially gameable and signals positional bias.
    mc_tasks = [t for t in (known + extra) if per_task_answer_idx.get(t)]
    if mc_tasks:
        print()
        print("answer-index distribution (MC tasks):")
        skew_warnings: list[str] = []
        for task in mc_tasks:
            dist = per_task_answer_idx[task]
            n = sum(dist.values())
            parts = ", ".join(f"{idx}={cnt}" for idx, cnt in sorted(dist.items()))
            print(f"  {task:24s} {parts}")
            top_idx, top_cnt = dist.most_common(1)[0]
            if n and top_cnt / n > 0.60:
                skew_warnings.append(
                    f"  WARNING: {task} is skewed - index {top_idx} holds "
                    f"{100.0 * top_cnt / n:.0f}% of answers (>60%)."
                )
        for w in skew_warnings:
            print(w)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
