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

# --- sentiment source (Darmm, Apache-2.0) ---
SENT_REPO = "Darmm/darmm-sentiment-kk"
SENT_LICENSE = "Apache-2.0"
SENT_FILE = "data/test.jsonl"
# Darmm 5-class -> KazBench 3-class
SENT_LABEL_MAP = {
    "positive": "оң", "very_positive": "оң",
    "negative": "теріс", "very_negative": "теріс",
    "neutral": "бейтарап",
}
# Only human-authored rows (data-sources.md: skip synthetic)
SENT_ALLOWED_SOURCES = {"manual", "crowdsourced"}
SENT_DEV_FILE = "benchmark/dev/sentiment.jsonl"
SENT_OUT_FILE = "benchmark/staging/sentiment_real.jsonl"
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


def load_existing_texts(path):
    """Return set of normalized existing review texts for dedup."""
    seen = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    t = (json.loads(line).get("text") or "").strip().lower()
                    if t:
                        seen.add(t)
                except json.JSONDecodeError:
                    continue
    return seen


def integrate_sentiment(limit, out_path):
    """Pull real human-authored Kazakh sentiment reviews (Darmm) into staging."""
    from huggingface_hub import hf_hub_download
    fpath = hf_hub_download(SENT_REPO, SENT_FILE, repo_type="dataset")
    rows = [json.loads(l) for l in open(fpath, encoding="utf-8") if l.strip()]
    seen = load_existing_texts(SENT_DEV_FILE)
    print(f"[info] sentiment: dedup against {len(seen)} existing DEV texts")
    emitted, idx = [], 0
    # balance across the 3 target labels
    from collections import Counter
    per_label = max(1, limit // 3)
    counts = Counter()
    for row in rows:
        if len(emitted) >= limit:
            break
        src = (row.get("source") or "").strip().lower()
        if src not in SENT_ALLOWED_SOURCES:  # skip synthetic
            continue
        raw_label = (row.get("label") or "").strip().lower()
        label = SENT_LABEL_MAP.get(raw_label)
        if label is None:
            continue
        text = (row.get("text") or "").strip()
        if not text or text.lower() in seen:
            continue
        if counts[label] >= per_label and len(emitted) < limit - 1:
            continue  # keep balance until near the end
        seen.add(text.lower())
        counts[label] += 1
        emitted.append({
            "id": f"sent_real_{idx:06d}",
            "task": "sentiment",
            "source": "community",
            "validated": False,
            "text": text,
            "label": label,
            "provenance": {
                "dataset": SENT_REPO,
                "license": SENT_LICENSE,
                "origin_label": raw_label,
                "origin_source": src,
                "domain": row.get("domain"),
            },
        })
        idx += 1
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for it in emitted:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"[info] sentiment label balance: {dict(counts)}")
    print(f"[done] wrote {len(emitted)} real sentiment items -> {out_path}")
    return emitted


def integrate_knowledge(limit, subjects, out_path):
    """Original knowledge_mc integration (real ЕНТ exams)."""
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download

    seen = load_existing_questions(DEV_FILE)
    print(f"[info] knowledge_mc: dedup against {len(seen)} existing DEV questions")

    emitted = []
    per_subject = max(1, limit // max(1, len(subjects)))
    idx = 0
    for subject in subjects:
        if len(emitted) >= limit:
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
            if len(emitted) >= limit or taken >= per_subject:
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

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for item in emitted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"[done] wrote {len(emitted)} real ЕНТ items -> {out_path}")
    return emitted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", choices=["knowledge_mc", "sentiment", "both"],
                    default="knowledge_mc", help="which task to integrate")
    ap.add_argument("--limit", type=int, default=50, help="max items per task")
    ap.add_argument("--subjects", nargs="*", default=DEFAULT_SUBJECTS,
                    help="knowledge_mc subject files to pull from")
    ap.add_argument("--out", default=None, help="override output path (single-task only)")
    args = ap.parse_args()

    try:
        from huggingface_hub import hf_hub_download  # noqa: F401
        import pyarrow.parquet as pq  # noqa: F401
    except ImportError as e:
        print(f"[ERROR] missing dependency: {e}. Install: pip install huggingface_hub pyarrow",
              file=sys.stderr)
        sys.exit(1)

    if args.task in ("knowledge_mc", "both"):
        integrate_knowledge(args.limit, args.subjects,
                            args.out if (args.out and args.task != "both") else OUT_FILE)
    if args.task in ("sentiment", "both"):
        integrate_sentiment(args.limit,
                            args.out if (args.out and args.task != "both") else SENT_OUT_FILE)

    print("[note] validated=false. Awaiting native validation (HITL gate) before DEV merge.")


if __name__ == "__main__":
    main()
