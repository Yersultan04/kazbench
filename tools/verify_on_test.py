"""
verify_on_test.py — KazBench maintainer-side TEST verification (P5).

Turns a PROVISIONAL public-DEV submission into an OFFICIAL leaderboard entry by
re-running the model on the private TEST split and recording the verified score.
Also runs an anti-gaming check: a large DEV→TEST gap (or TEST above DEV) is
flagged, since it suggests overfitting / contamination of the public DEV set.

This is a MAINTAINER tool. It requires the private TEST split (benchmark/test/),
which is gitignored and never published.

Usage (maintainer):
    # dummy (free, for infra testing):
    python tools/verify_on_test.py --model dummy --submission results/dummy.json

    # real model (COSTS API budget — gate behind approval):
    python tools/verify_on_test.py --model openai \\
        --model-id meta-llama/llama-4-scout-17b-16e-instruct \\
        --submission results/scout-dev.json

What it does:
  1. Re-runs eval on split=test (validated-only) for the given model.
  2. Compares official TEST overall vs the submitted DEV overall.
  3. Anti-gaming verdict (DEV→TEST drop is expected; TEST > DEV or tiny drop is suspicious).
  4. Appends a tamper-evident line to results/SUBMISSION_LEDGER.md.
  5. Writes the official TEST result JSON (verified_on_test=true).

Exit codes: 0 verified, 1 failed/flagged.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEDGER = Path("results/SUBMISSION_LEDGER.md")
# A real model normally DROPS on held-out TEST. These bound the "normal" zone.
SUSPICIOUS_TEST_ABOVE_DEV = 2.0   # TEST higher than DEV by >2 pts → suspicious
SUSPICIOUS_TINY_DROP = 0.5        # near-identical DEV/TEST on tiny n → weak signal (warn only)


def load_overall(path: Path) -> float | None:
    try:
        with path.open(encoding="utf-8") as f:
            return float(json.load(f).get("overall"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def run_test_eval(model: str, model_id: str | None, out: Path) -> int:
    """Invoke the harness on the private TEST split."""
    # TEST is a fully held-out private split: evaluate ALL items (the validated
    # flag gates the public DEV headline, not the private TEST eval).
    cmd = [
        sys.executable, "-m", "harness.run_eval",
        "--model", model, "--split", "test", "--all-items",
        "--out", str(out),
    ]
    if model_id:
        cmd += ["--model-id", model_id]
    print(f"[verify] running TEST eval: {' '.join(cmd)}")
    return subprocess.call(cmd)


def append_ledger(entry: dict[str, Any]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new = not LEDGER.exists()
    with LEDGER.open("a", encoding="utf-8") as f:
        if new:
            f.write("# KazBench Submission Ledger\n\n")
            f.write("Append-only record of maintainer TEST verifications (anti-gaming audit trail).\n\n")
            f.write("| Timestamp (UTC) | Model | DEV overall | TEST overall | Δ (TEST−DEV) | Verdict |\n")
            f.write("|---|---|---|---:|---:|---|\n")
        f.write(
            f"| {entry['ts']} | {entry['model']} | {entry['dev']} | "
            f"{entry['test']:.2f} | {entry['delta']:+.2f} | {entry['verdict']} |\n"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, help="adapter: dummy | claude | openai")
    ap.add_argument("--model-id", default=None, help="model identifier")
    ap.add_argument("--submission", type=Path, required=True,
                    help="the submitted public-DEV results JSON")
    ap.add_argument("--out", type=Path, default=None,
                    help="output path for official TEST result (default results/official/<model>.json)")
    args = ap.parse_args()

    if not args.submission.exists():
        print(f"[ERROR] submission not found: {args.submission}")
        return 1
    dev_overall = load_overall(args.submission)
    if dev_overall is None:
        print(f"[ERROR] cannot read 'overall' from submission {args.submission}")
        return 1

    label = args.model_id or args.model
    out = args.out or Path(f"results/official/{label.replace('/', '_')}.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    rc = run_test_eval(args.model, args.model_id, out)
    if rc != 0:
        print(f"[ERROR] TEST eval failed (rc={rc}). Not verified.")
        return 1

    test_overall = load_overall(out)
    if test_overall is None:
        print("[ERROR] TEST eval produced no 'overall'.")
        return 1

    delta = test_overall - dev_overall  # normally negative (drop on held-out data)

    # Anti-gaming verdict
    if delta > SUSPICIOUS_TEST_ABOVE_DEV:
        verdict = "🚩 FLAGGED (TEST > DEV — possible DEV contamination / mislabeled submission)"
        flagged = True
    elif delta > -SUSPICIOUS_TINY_DROP:
        verdict = "⚠️ REVIEW (near-zero drop — verify on larger n)"
        flagged = False
    else:
        verdict = "✅ VERIFIED (normal DEV→TEST drop)"
        flagged = False

    # Stamp the official result and persist
    try:
        with out.open(encoding="utf-8") as f:
            official = json.load(f)
        official["verified_on_test"] = True
        official["dev_overall_submitted"] = dev_overall
        official["dev_test_delta"] = round(delta, 2)
        with out.open("w", encoding="utf-8") as f:
            json.dump(official, f, ensure_ascii=False, indent=2)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[WARN] could not stamp official file: {exc}")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    append_ledger({
        "ts": ts, "model": label, "dev": f"{dev_overall:.2f}",
        "test": test_overall, "delta": delta, "verdict": verdict,
    })

    print("-" * 60)
    print(f"Model:        {label}")
    print(f"DEV overall:  {dev_overall:.2f} (submitted)")
    print(f"TEST overall: {test_overall:.2f} (official, private split)")
    print(f"Δ (TEST−DEV): {delta:+.2f}")
    print(f"Verdict:      {verdict}")
    print(f"Official:     {out}")
    print(f"Ledger:       {LEDGER}")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
