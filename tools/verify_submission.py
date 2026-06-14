"""
verify_submission.py — KazBench submission gate (stdlib only, no external deps).

Validates that a submitted results JSON conforms to the KazBench schema v1
(benchmark/schema.md) before it is accepted into the official leaderboard.

Usage:
    python tools/verify_submission.py results/my_model.json
    python tools/verify_submission.py results/my_model.json --strict

Exit codes:
    0  — file passes all checks (may have non-fatal warnings)
    1  — one or more ERRORS found; file must NOT be added to the leaderboard

IMPORTANT: A passing run on public DEV data is PROVISIONAL.
Official leaderboard inclusion requires private TEST verification
by a KazBench maintainer who re-runs eval on the hidden TEST split.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ── Schema constants ──────────────────────────────────────────────────────────

REQUIRED_TOP_KEYS: list[str] = [
    "model",
    "adapter",
    "kazbench_version",
    "split",
    "overall",
    "tasks",
]

ALL_TASKS: list[str] = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]

REQUIRED_TASK_KEYS: list[str] = ["metric", "score", "n"]

# Expected metric for each task (from schema.md)
EXPECTED_METRICS: dict[str, str] = {
    "knowledge_mc": "accuracy",
    "reading_comprehension": "accuracy",
    "grammar_morphology": "accuracy",
    "sentiment": "accuracy",
    "translation": "chrF",
    "instruction_following": "judge",
}

# Score ranges [0,1] for accuracy/judge; [0,100] for chrF
SCALE_X100_METRICS: set[str] = {"accuracy", "judge"}  # raw in [0,1]
CHR_F_RANGE_MAX: float = 100.0


# ── Reporter ──────────────────────────────────────────────────────────────────

class Reporter:
    """Collects errors and warnings during validation."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(f"[ERROR] {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(f"[WARN]  {msg}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_all(self) -> None:
        for line in self.warnings:
            print(line)
        for line in self.errors:
            print(line)


# ── Validators ────────────────────────────────────────────────────────────────

def validate_top_level(data: dict[str, Any], rep: Reporter) -> None:
    """Check required top-level keys exist and have correct types."""
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            rep.error(f"Missing required top-level key: '{key}'")

    # model / adapter / kazbench_version / split -> strings
    for str_key in ("model", "adapter", "kazbench_version", "split"):
        if str_key in data and not isinstance(data[str_key], str):
            rep.error(f"'{str_key}' must be a string, got {type(data[str_key]).__name__}")

    # overall -> number in [0, 100]
    if "overall" in data:
        overall = data["overall"]
        if not isinstance(overall, (int, float)):
            rep.error(f"'overall' must be a number, got {type(overall).__name__}")
        else:
            if overall < 0 or overall > 100:
                rep.error(
                    f"'overall' must be in [0, 100], got {overall:.4f}. "
                    "Reminder: overall = macro-average with accuracy/judge scaled x100."
                )

    # tasks -> dict
    if "tasks" in data and not isinstance(data["tasks"], dict):
        rep.error(f"'tasks' must be an object, got {type(data['tasks']).__name__}")

    # kazbench_version format hint
    if "kazbench_version" in data:
        ver: str = str(data["kazbench_version"])
        parts = ver.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            rep.warn(
                f"'kazbench_version' does not look like semver (e.g. '0.1.0'): '{ver}'"
            )

    # split value
    if "split" in data:
        split_val: str = str(data["split"])
        if split_val not in ("dev", "test"):
            rep.warn(
                f"'split' is '{split_val}'; expected 'dev' or 'test'. "
                "Public submissions should use split='dev'."
            )
        if split_val == "test":
            rep.warn(
                "split='test' submissions are for maintainer use only. "
                "Public submitters must use split='dev'."
            )


def validate_tasks(data: dict[str, Any], rep: Reporter) -> None:
    """Check tasks dict: all 6 present, correct keys, score ranges."""
    tasks: Any = data.get("tasks")
    if not isinstance(tasks, dict):
        # Already reported in validate_top_level
        return

    # All 6 tasks are required for official leaderboard inclusion.
    # run_eval --tasks can produce a subset for local testing, but such
    # partial results will be rejected here and must not be submitted.
    for task in ALL_TASKS:
        if task not in tasks:
            rep.error(f"Missing task: '{task}'. All 6 tasks are required for leaderboard submission.")

    for task_name, task_data in tasks.items():
        prefix = f"tasks.{task_name}"

        if task_name not in ALL_TASKS:
            rep.warn(f"{prefix}: unknown task name (not in schema). Will be ignored by harness.")

        if not isinstance(task_data, dict):
            rep.error(f"{prefix}: must be an object, got {type(task_data).__name__}")
            continue

        # Required keys per task
        for key in REQUIRED_TASK_KEYS:
            if key not in task_data:
                rep.error(f"{prefix}: missing required key '{key}'")

        # metric correctness
        if "metric" in task_data:
            metric: str = str(task_data["metric"])
            if task_name in EXPECTED_METRICS and metric != EXPECTED_METRICS[task_name]:
                rep.error(
                    f"{prefix}: metric mismatch — got '{metric}', "
                    f"expected '{EXPECTED_METRICS[task_name]}'"
                )

        # score range validation
        if "score" in task_data and "metric" in task_data:
            score: Any = task_data["score"]
            metric = str(task_data["metric"])
            if not isinstance(score, (int, float)):
                rep.error(f"{prefix}.score: must be a number, got {type(score).__name__}")
            else:
                if metric in SCALE_X100_METRICS:
                    if score < 0.0 or score > 1.0:
                        rep.error(
                            f"{prefix}.score: {metric} must be in [0, 1], got {score:.4f}"
                        )
                elif metric == "chrF":
                    if score < 0.0 or score > CHR_F_RANGE_MAX:
                        rep.error(
                            f"{prefix}.score: chrF must be in [0, 100], got {score:.4f}"
                        )
                else:
                    # Unknown metric — warn only
                    rep.warn(
                        f"{prefix}: unknown metric '{metric}'. "
                        "Cannot validate score range. Expected: accuracy/judge in [0,1], chrF in [0,100]."
                    )

        # n -> positive integer
        if "n" in task_data:
            n_val: Any = task_data["n"]
            if not isinstance(n_val, int) or n_val < 1:
                rep.error(f"{prefix}.n: must be a positive integer, got {n_val!r}")


def validate_overall_consistency(data: dict[str, Any], rep: Reporter) -> None:
    """
    Soft-check: recompute expected overall from task scores and compare.
    Reports a warning (not error) if it deviates significantly.
    """
    tasks: Any = data.get("tasks")
    if not isinstance(tasks, dict):
        return

    scaled_scores: list[float] = []
    for task_name in ALL_TASKS:
        if task_name not in tasks:
            continue
        task_data = tasks[task_name]
        if not isinstance(task_data, dict):
            continue
        score: Any = task_data.get("score")
        metric: str = str(task_data.get("metric", ""))
        if not isinstance(score, (int, float)):
            continue

        if metric in SCALE_X100_METRICS:
            scaled_scores.append(float(score) * 100.0)
        else:
            # chrF already in [0,100]
            scaled_scores.append(float(score))

    if not scaled_scores:
        return

    recomputed = sum(scaled_scores) / len(scaled_scores)
    reported: Any = data.get("overall")
    if not isinstance(reported, (int, float)):
        return

    delta = abs(float(reported) - recomputed)
    if delta > 0.5:
        rep.warn(
            f"Overall consistency check: reported overall={reported:.4f}, "
            f"recomputed macro-avg={recomputed:.4f} (delta={delta:.4f}). "
            "If more tasks are present (e.g. future versions), this is expected. "
            "Otherwise verify the harness computation."
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a KazBench results JSON before leaderboard submission."
    )
    parser.add_argument("submission", type=Path, help="Path to the results JSON file.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (useful in CI).",
    )
    args = parser.parse_args()

    path: Path = args.submission
    rep = Reporter()

    print(f"KazBench Submission Verifier")
    print(f"File: {path}")
    print("-" * 50)

    # File existence
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return 1

    # Guard against huge/malicious files before parsing (1 MB limit)
    _MAX_BYTES = 1 * 1024 * 1024
    try:
        file_size = path.stat().st_size
        if file_size > _MAX_BYTES:
            print(
                f"[ERROR] File size {file_size} bytes exceeds the {_MAX_BYTES} byte "
                "limit. Submission files must be under 1 MB."
            )
            return 1
    except OSError as exc:
        print(f"[ERROR] Cannot stat file: {exc}")
        return 1

    # JSON parse
    try:
        with path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON: {exc}")
        return 1
    except OSError as exc:
        print(f"[ERROR] Cannot read file: {exc}")
        return 1

    if not isinstance(data, dict):
        print("[ERROR] Top-level JSON must be an object (dict).")
        return 1

    # Run validators
    validate_top_level(data, rep)
    validate_tasks(data, rep)
    validate_overall_consistency(data, rep)

    # Print findings
    rep.print_all()

    if args.strict and rep.warnings:
        print(
            f"\n[STRICT] {len(rep.warnings)} warning(s) treated as error(s) (--strict mode)."
        )
        return 1

    if rep.has_errors():
        print(
            f"\nResult: FAILED — {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)."
        )
        print("Fix all errors before submitting to the leaderboard.")
        return 1

    print(
        f"\nResult: PASSED — {len(rep.warnings)} warning(s), 0 errors."
    )
    print(
        "IMPORTANT: This is a PROVISIONAL pass on the public DEV split."
    )
    print(
        "Official leaderboard inclusion requires a maintainer to run"
    )
    print(
        "verification on the private TEST split. Open a PR with this file"
    )
    print(
        "and the maintainer will handle the private TEST check."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
