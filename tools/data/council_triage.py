#!/usr/bin/env python3
"""Merge multi-model predictions into the review CSV as a triage signal.

Reads per-item prediction dumps (from `run_eval --save-predictions`) for several
models and, per item, counts how many models agreed with our gold answer. Adds two
columns to the review CSV:

  council_correct : "k/N"  (k of N models matched our gold)
  council_flag    : "REVIEW" when models mostly DISAGREE with our gold
                    (likely our gold is wrong OR the item is genuinely hard)

The council is a TRIAGE/prioritization signal only, never the source of truth — a
native reviewer still decides `validated`. Low agreement just means "look here first".

Usage:
    python tools/data/council_triage.py --preds results/preds/ --csv validation/review.csv

ASCII-only console output (Windows cp1251 safe).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

NEW_COLS = ["council_correct", "council_flag"]


def load_predictions(preds_dir: Path) -> dict[str, list[bool]]:
    """id -> list of per-model correctness booleans."""
    by_id: dict[str, list[bool]] = defaultdict(list)
    files = sorted(preds_dir.glob("*.json")) if preds_dir.is_dir() else [preds_dir]
    n_models = 0
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        n_models += 1
        for rec in data.get("predictions", []):
            by_id[rec["id"]].append(bool(rec["correct"]))
    print(f"loaded {n_models} model prediction file(s)")
    return by_id


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preds", type=Path, default=Path("results/preds/"))
    ap.add_argument("--csv", type=Path, default=Path("validation/review.csv"))
    ap.add_argument("--out", type=Path, default=None, help="default: overwrite --csv")
    ap.add_argument("--flag-threshold", type=float, default=0.5,
                    help="flag REVIEW when agreement fraction < this (default 0.5)")
    args = ap.parse_args(argv)
    out_path = args.out or args.csv

    by_id = load_predictions(args.preds)
    if not by_id:
        print("no predictions found - nothing to merge")
        return 1

    with args.csv.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    # insert the two columns right after 'correct_answer' if present, else append
    for col in NEW_COLS:
        if col not in fieldnames:
            anchor = fieldnames.index("correct_answer") + 1 if "correct_answer" in fieldnames else len(fieldnames)
            fieldnames.insert(anchor, col)
            anchor += 1  # keep order council_correct, council_flag

    n_flagged = 0
    for row in rows:
        corr = by_id.get(row.get("id", ""))
        if not corr:
            row["council_correct"] = ""   # tasks without a binary gold (translation/IF)
            row["council_flag"] = ""
            continue
        agree = sum(corr)
        total = len(corr)
        row["council_correct"] = f"{agree}/{total}"
        flag = (agree / total) < args.flag_threshold if total else False
        row["council_flag"] = "REVIEW" if flag else ""
        if flag:
            n_flagged += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    scored = sum(1 for r in rows if r.get("council_correct"))
    print(f"merged: {scored} items scored, {n_flagged} flagged REVIEW -> {out_path}")
    print("Flagged items = models mostly disagree with our gold. Review those FIRST.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
