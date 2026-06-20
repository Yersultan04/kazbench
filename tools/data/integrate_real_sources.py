#!/usr/bin/env python3
"""Integrate real human-sourced Kazakh data into KazBench staging (P2).

Pulls real ЕНТ (Unified National Testing) multiple-choice questions from
kz-transformers/kazakh-unified-national-testing-mc (Apache-2.0) and converts
them to the KazBench knowledge_mc JSONL format.

Output goes to benchmark/staging/ with validated=false, source="exam" — these
items are NOT part of the live DEV split until native validation (HITL gate).

Usage:
    python tools/data/integrate_real_sources.py --limit 50
    python tools/data/integrate_real_sources.py --limit 100 --subjects history_of_kazakhstan kazakh_and_literature
"""
import argparse
import json
import os
import sys

REPO = "kz-transformers/kazakh-unified-national-testing-mc"
LICENSE = "Apache-2.0"
OPTION_COLS = ["A", "B", "C", "D", "E", "F", "G", "H"]
# Subjects most relevant to Kazakh-language knowledge (avoid english/world subjects first)
DEFAULT_SUBJECTS = [
    "history_of_kazakhstan",
    "kazakh_and_literature",
    "geography",
    "human_society_rights",
    "biology",
    "world_history",
]
DEV_FILE = "benchmark/dev/knowledge_mc.jsonl"
OUT_FILE = "benchmark/staging/knowledge_mc_real.jsonl"


def load_existing_questions(path):
    """Return set of normalized existing question texts for dedup."""
    seen = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    q = (obj.get("question") or "").strip().lower()
                    if q:
                        seen.add(q)
                except json.JSONDecodeError:
                    continue
    return seen


def convert_row(row, idx, subject):
    """Convert one source row to KazBench knowledge_mc item. Returns None if invalid."""
    question = (row.get("question") or "").strip()
    if not question:
        return None
    # collect non-empty options in A..H order
    choices = []
    letter_to_index = {}
    for col in OPTION_COLS:
        val = row.get(col)
        if val is not None and str(val).strip():
            letter_to_index[col] = len(choices)
            choices.append(str(val).strip())
    if len(choices) < 2:
        return None
    correct = (row.get("correct_answer") or "").strip().upper()
    if correct not in letter_to_index:
        return None  # answer letter not among options -> skip
    answer = letter_to_index[correct]
    return {
        "id": f"kmc_real_{idx:06d}",
        "task": "knowledge_mc",
        "source": "exam",
        "validated": False,
        "question": question,
        "choices": choices,
        "answer": answer,
        "provenance": {
            "dataset": REPO,
            "license": LICENSE,
            "subject": subject,
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=50, help="max items to emit (total)")
    ap.add_argument("--subjects", nargs="*", default=DEFAULT_SUBJECTS,
                    help="subject files to pull from")
    ap.add_argument("--out", default=OUT_FILE)
    args = ap.parse_args()

    try:
        from huggingface_hub import hf_hub_download
        import pyarrow.parquet as pq
    except ImportError as e:
        print(f"[ERROR] missing dependency: {e}. Install: pip install huggingface_hub pyarrow",
              file=sys.stderr)
        sys.exit(1)

    seen = load_existing_questions(DEV_FILE)
    print(f"[info] dedup against {len(seen)} existing DEV questions")

    emitted = []
    per_subject = max(1, args.limit // max(1, len(args.subjects)))
    idx = 0
    for subject in args.subjects:
        if len(emitted) >= args.limit:
            break
        try:
            fpath = hf_hub_download(
                REPO, f"data/{subject}-00000-of-00001.parquet", repo_type="dataset")
        except Exception as e:
            print(f"[warn] cannot download {subject}: {e}", file=sys.stderr)
            continue
        table = pq.read_table(fpath)
        rows = table.to_pylist()
        taken = 0
        for row in rows:
            if len(emitted) >= args.limit or taken >= per_subject:
                break
            item = convert_row(row, idx, subject)
            if item is None:
                continue
            qnorm = item["question"].strip().lower()
            if qnorm in seen:
                continue
            seen.add(qnorm)
            emitted.append(item)
            idx += 1
            taken += 1
        print(f"[info] {subject}: +{taken} items")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for item in emitted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"[done] wrote {len(emitted)} real ЕНТ items -> {args.out}")
    print(f"[note] validated=false, source=exam. Awaiting native validation (HITL gate) before DEV merge.")


if __name__ == "__main__":
    main()
