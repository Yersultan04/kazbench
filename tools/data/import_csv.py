#!/usr/bin/env python3
"""Apply a reviewed CSV (from export_csv.py) back to the benchmark JSONL files.

Reads the reviewer's `verdict` per item id and updates the dataset in place:
  - verdict "ok"   -> set validated:true        (approved by native reviewer)
  - verdict "drop" -> remove the item
  - verdict "fix"  -> keep validated:false, attach the reviewer note/correction
                      for a follow-up edit (content is NOT auto-rewritten to avoid
                      mangling structured fields; surfaced for manual application)
  - blank verdict  -> leave unchanged

Usage:
    python tools/data/import_csv.py validation/review.csv --data benchmark/dev/

ASCII-only console output (Windows cp1251 safe).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

OK = {"ok", "approve", "approved", "yes", "y", "true", "valid"}
DROP = {"drop", "remove", "delete", "no", "reject"}
FIX = {"fix", "edit", "change"}


def load_verdicts(csv_path: Path) -> dict[str, dict]:
    verdicts: dict[str, dict] = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            vid = (row.get("id") or "").strip()
            if vid:
                verdicts[vid] = {
                    "verdict": (row.get("verdict") or "").strip().lower(),
                    "correction": (row.get("correction") or "").strip(),
                    "note": (row.get("note") or "").strip(),
                }
    return verdicts


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", type=Path, help="reviewed review.csv")
    ap.add_argument("--data", type=Path, default=Path("benchmark/dev/"))
    args = ap.parse_args(argv[1:])

    if not args.csv.exists():
        print(f"ERROR: CSV not found: {args.csv}")
        return 2
    verdicts = load_verdicts(args.csv)

    files = sorted(args.data.glob("*.jsonl")) if args.data.is_dir() else [args.data]
    n_ok = n_drop = n_fix = n_skip = 0
    fix_report: list[str] = []

    for path in files:
        items = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        out: list[dict] = []
        for item in items:
            v = verdicts.get(item.get("id", ""))
            verdict = v["verdict"] if v else ""
            if verdict in OK:
                item["validated"] = True
                n_ok += 1
                out.append(item)
            elif verdict in DROP:
                n_drop += 1  # skip (remove)
            elif verdict in FIX:
                item["validated"] = False
                n_fix += 1
                fix_report.append(f"  {item['id']}: {v['correction'] or v['note'] or '(see note)'}")
                out.append(item)
            else:
                n_skip += 1
                out.append(item)
        path.write_text(
            "\n".join(json.dumps(it, ensure_ascii=False) for it in out) + "\n",
            encoding="utf-8",
        )

    print(f"applied: {n_ok} validated, {n_drop} dropped, {n_fix} flagged-for-fix, {n_skip} unchanged")
    if fix_report:
        print("items needing manual correction:")
        print("\n".join(fix_report))
    print("Tip: re-run tools/data/validate.py after import.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
