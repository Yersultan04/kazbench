#!/usr/bin/env python3
"""Integrate human-sourced sentiment from Darmm/darmm-sentiment-kk (Apache-2.0).

Replaces the unvalidated *synthetic seed* sentiment items with real human
(manual/crowdsourced) reviews mapped to the KazBench 3-class scheme. Keeps the
51 native-validated items untouched and preserves 100 items in DEV.
"""
from __future__ import annotations

import json
import os
import random
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

random.seed(42)
REPO = Path(__file__).resolve().parent.parent

LABEL_MAP = {
    "very_negative": "теріс", "negative": "теріс",
    "neutral": "бейтарап",
    "positive": "оң", "very_positive": "оң",
}
CLASSES = ["оң", "теріс", "бейтарап"]


def norm(t: str) -> str:
    return " ".join(str(t).split()).strip().lower()


def load_existing_texts() -> set[str]:
    texts: set[str] = set()
    for split in ("dev", "test"):
        p = REPO / "benchmark" / split / "sentiment.jsonl"
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    texts.add(norm(json.loads(line)["text"]))
    return texts


def main() -> None:
    tok = os.environ["HF_TOKEN"]
    csv = hf_hub_download(
        "Darmm/darmm-sentiment-kk",
        "data/kazakh_sentiment_10000.cleaned.csv",
        repo_type="dataset", token=tok,
    )
    df = pd.read_csv(csv)
    df = df[df["source"].isin(["manual", "crowdsourced"])].copy()
    df["lab3"] = df["label"].map(LABEL_MAP)
    df = df.dropna(subset=["lab3", "text"])

    existing = load_existing_texts()
    df = df[~df["text"].map(norm).isin(existing)]
    df = df.drop_duplicates(subset="text")

    # balanced pools per class
    pools = {c: df[df["lab3"] == c]["text"].tolist() for c in CLASSES}
    for c in CLASSES:
        random.shuffle(pools[c])
        print(f"  pool {c}: {len(pools[c])}")

    # DEV: 49 community (16/16/17), TEST: 30 community (10/10/10)
    dev_quota = {"оң": 16, "теріс": 16, "бейтарап": 17}
    test_quota = {"оң": 10, "теріс": 10, "бейтарап": 10}

    def take(quota: dict[str, int]) -> list[tuple[str, str]]:
        out = []
        for c in CLASSES:
            for _ in range(quota[c]):
                out.append((pools[c].pop(), c))
        random.shuffle(out)
        return out

    dev_new = take(dev_quota)
    test_new = take(test_quota)

    # --- rebuild DEV sentiment: keep snt_000001..051 (validated), replace 052..100 ---
    dev_path = REPO / "benchmark" / "dev" / "sentiment.jsonl"
    dev_items = [json.loads(l) for l in dev_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    keep = [it for it in dev_items if it.get("validated") is True]
    print(f"  DEV keep validated: {len(keep)}; replacing {len(dev_items) - len(keep)} synthetic with {len(dev_new)} community")
    new_dev = list(keep)
    for i, (text, lab) in enumerate(dev_new, start=52):
        new_dev.append({"id": f"snt_{i:06d}", "task": "sentiment", "source": "community",
                        "validated": False, "text": text, "label": lab})
    dev_path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in new_dev) + "\n", encoding="utf-8")

    # --- rebuild TEST sentiment: all community, 1 canary ---
    test_path = REPO / "benchmark" / "test" / "sentiment.jsonl"
    new_test = []
    for i, (text, lab) in enumerate(test_new, start=200001):
        o = {"id": f"snt_{i:06d}", "task": "sentiment", "source": "community",
             "validated": False, "text": text, "label": lab}
        new_test.append(o)
    new_test[0]["canary"] = "KAZBENCH-CANARY-SNT-test01-do-not-train"
    test_path.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in new_test) + "\n", encoding="utf-8")

    print(f"  DEV sentiment now: {len(new_dev)} (51 validated + {len(dev_new)} community)")
    print(f"  TEST sentiment now: {len(new_test)} community (1 canary)")


if __name__ == "__main__":
    main()
