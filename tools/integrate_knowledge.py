#!/usr/bin/env python3
"""Integrate real ЕНТ/ҰБТ questions from kz-transformers/kazakh-unified-national-testing-mc
(Apache-2.0) into KazBench knowledge_mc.

Replaces unvalidated synthetic seed knowledge items with real exam questions.
Filters to clean 4-choice items, drops image/table-dependent questions, and
de-skews the answer-index distribution.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd

random.seed(42)
REPO = Path(__file__).resolve().parent.parent

# Kazakh-language subjects (skip 'english')
SUBJECTS = [
    "biology", "geography", "history_of_kazakhstan",
    "human_society_rights", "kazakh_and_literature", "world_history",
]
BASE = "https://huggingface.co/datasets/kz-transformers/kazakh-unified-national-testing-mc/resolve/main/data"
COLS = ["A", "B", "C", "D", "E", "F", "G", "H"]
# question references an image/table we don't have -> unanswerable, drop
BAD = ("сурет", "кесте", "график", "сызба", "диаграмма", "төмендегі кесте")


def norm(t: str) -> str:
    return " ".join(str(t).split()).strip().lower()


def existing_questions() -> set[str]:
    qs: set[str] = set()
    for split in ("dev", "test"):
        p = REPO / "benchmark" / split / "knowledge_mc.jsonl"
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    qs.add(norm(json.loads(line)["question"]))
    return qs


def main() -> None:
    frames = []
    for s in SUBJECTS:
        df = pd.read_parquet(f"{BASE}/{s}-00000-of-00001.parquet")
        df["subject_file"] = s
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)
    print(f"  raw rows: {len(raw)}")

    seen = existing_questions()
    cand: list[dict] = []
    seen_local: set[str] = set()
    for _, r in raw.iterrows():
        ca = str(r["correct_answer"]).strip()
        if ca not in COLS:
            continue
        # gather all real options (5-choice ЕНТ is common; downsample to 4)
        JUNK = {"none", "<missing>", "missing", "", "-", "—", "n/a", "null"}
        opts = {c: str(r[c]).strip() for c in COLS}
        valid = {c: v for c, v in opts.items() if v and v.lower() not in JUNK}
        if ca not in valid:
            continue
        correct = valid.pop(ca)
        distractors = [v for v in valid.values() if v and v != correct]
        if len(set(distractors)) < 3:
            continue
        q = str(r["question"]).strip()
        if not q or len(q) < 8:
            continue
        ql = q.lower()
        if any(b in ql for b in BAD):              # drop image/table-dependent
            continue
        nq = norm(q)
        if nq in seen or nq in seen_local:
            continue
        # build a 4-choice item: correct + 3 random distractors, shuffled
        picks = random.sample(list(dict.fromkeys(distractors)), 3)
        choices = [correct] + picks
        random.shuffle(choices)
        ans = choices.index(correct)
        seen_local.add(nq)
        cand.append({"question": q, "choices": choices, "answer": ans,
                     "subject": str(r["subject_file"])})
    print(f"  clean 4-choice candidates: {len(cand)}")

    # de-skew: bucket by answer index, draw evenly
    random.shuffle(cand)
    buckets: dict[int, list[dict]] = {0: [], 1: [], 2: [], 3: []}
    for c in cand:
        buckets[c["answer"]].append(c)
    for i in range(4):
        print(f"    answer={i}: {len(buckets[i])}")

    def draw(n: int) -> list[dict]:
        per = [n // 4] * 4
        for i in range(n % 4):
            per[i] += 1
        out = []
        for i in range(4):
            for _ in range(per[i]):
                out.append(buckets[i].pop())
        random.shuffle(out)
        return out

    dev_new = draw(50)   # replace kmc_000051..100
    test_new = draw(30)  # replace kmc_200001..200030

    # --- DEV: keep validated kmc_000001..050, replace synthetic with exam items ---
    dev_path = REPO / "benchmark" / "dev" / "knowledge_mc.jsonl"
    dev_items = [json.loads(l) for l in dev_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    keep = [it for it in dev_items if it.get("validated") is True]
    print(f"  DEV keep validated: {len(keep)}; replacing {len(dev_items)-len(keep)} synthetic with {len(dev_new)} exam")
    new_dev = list(keep)
    for i, c in enumerate(dev_new, start=51):
        new_dev.append({"id": f"kmc_{i:06d}", "task": "knowledge_mc", "source": "exam",
                        "validated": False, "question": c["question"],
                        "choices": c["choices"], "answer": c["answer"]})
    dev_path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in new_dev) + "\n", encoding="utf-8")

    # --- TEST: all exam, 1 canary ---
    test_path = REPO / "benchmark" / "test" / "knowledge_mc.jsonl"
    new_test = []
    for i, c in enumerate(test_new, start=200001):
        new_test.append({"id": f"kmc_{i:06d}", "task": "knowledge_mc", "source": "exam",
                         "validated": False, "question": c["question"],
                         "choices": c["choices"], "answer": c["answer"]})
    new_test[0]["canary"] = "KAZBENCH-CANARY-KMC-test01-do-not-train"
    test_path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in new_test) + "\n", encoding="utf-8")

    from collections import Counter
    print(f"  DEV knowledge now: {len(new_dev)} (50 validated + {len(dev_new)} exam)")
    print(f"  DEV exam answer dist: {dict(Counter(o['answer'] for o in new_dev if o['source']=='exam'))}")
    print(f"  TEST knowledge now: {len(new_test)} exam (1 canary)")
    print(f"  subjects used (dev): {dict(Counter(c['subject'] for c in dev_new))}")


if __name__ == "__main__":
    main()
