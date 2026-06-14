"""
build_leaderboard.py — KazBench leaderboard builder (stdlib only, no external deps).

Reads all results/*.json files, sorts by overall score descending, and writes
a Markdown leaderboard table to the specified output file (default: leaderboard.md).

Usage:
    python tools/build_leaderboard.py --results results/ --out leaderboard.md
    python tools/build_leaderboard.py --results results/ --out leaderboard.md --date 2026-06-14
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Canonical task order for leaderboard columns
TASK_ORDER: list[str] = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]

# Human-readable short column headers (ASCII-safe)
TASK_LABELS: dict[str, str] = {
    "knowledge_mc": "KMC",
    "reading_comprehension": "RC",
    "grammar_morphology": "GM",
    "sentiment": "Sent",
    "translation": "Trans",
    "instruction_following": "IF",
}

# Metrics whose raw scores are [0,1] and must be scaled *100 for display
SCALE_X100: set[str] = {"accuracy", "judge"}
# chrF is already [0,100]


def load_result(path: Path) -> dict[str, Any] | None:
    """Load and lightly validate a single results JSON. Returns None on error."""
    try:
        with path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[WARN] Could not load {path}: {exc}", file=sys.stderr)
        return None

    required = {"model", "overall", "tasks"}
    missing = required - data.keys()
    if missing:
        print(
            f"[WARN] Skipping {path} — missing required keys: {missing}",
            file=sys.stderr,
        )
        return None

    return data


def task_display_score(task_data: dict[str, Any]) -> str:
    """
    Return a display string for a single task entry.

    Schema:
      - accuracy / judge -> raw score in [0,1], display as x*100 rounded to 1 dp
      - chrF -> raw score in [0,100], display rounded to 1 dp
    """
    metric: str = task_data.get("metric", "")
    raw: float | None = task_data.get("score")
    if raw is None:
        return "n/a"

    if metric in SCALE_X100:
        return f"{raw * 100:.1f}"
    # chrF (and any unknown metric) — display as-is
    return f"{raw:.1f}"


def build_row(data: dict[str, Any]) -> dict[str, str]:
    """Extract display values from a result dict."""
    model: str = data.get("model", "unknown")
    adapter: str = data.get("adapter", "")
    split: str = data.get("split", "dev")
    overall: float = float(data.get("overall", 0.0))
    version: str = data.get("kazbench_version", "?")
    tasks: dict[str, Any] = data.get("tasks", {})

    task_scores: dict[str, str] = {}
    for task in TASK_ORDER:
        if task in tasks:
            task_scores[task] = task_display_score(tasks[task])
        else:
            task_scores[task] = "—"

    return {
        "model": model,
        "adapter": adapter,
        "split": split,
        "overall": overall,
        "overall_str": f"{overall:.2f}",
        "version": version,
        "task_scores": task_scores,  # type: ignore[dict-item]
    }


def md_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def build_leaderboard_md(rows: list[dict[str, Any]], date_str: str) -> str:
    """Render the full leaderboard Markdown string."""
    lines: list[str] = []

    lines.append("# KazBench Leaderboard")
    lines.append("")
    lines.append(
        "Ranks models on Kazakh-language AI tasks. "
        "Overall = macro-average across all 6 tasks (accuracy/judge scaled x100, "
        "chrF already in [0-100])."
    )
    lines.append("")
    lines.append(
        "> **Provisional (DEV split)** — scores below are from the public DEV set. "
        "Official rankings require private TEST verification by a KazBench maintainer. "
        "See CONTRIBUTING.md for the submission process."
    )
    lines.append("")

    # Table header
    task_cols = [TASK_LABELS[t] for t in TASK_ORDER]
    header = ["Rank", "Model", "Split", "Overall"] + task_cols + ["Version"]
    separator = ["----", "-----", "-----", "-------"] + ["----"] * len(task_cols) + ["-------"]
    lines.append(md_table_row(header))
    lines.append(md_table_row(separator))

    for rank, row in enumerate(rows, start=1):
        task_scores: dict[str, str] = row["task_scores"]
        cells = (
            [str(rank), row["model"], row["split"], row["overall_str"]]
            + [task_scores[t] for t in TASK_ORDER]
            + [row["version"]]
        )
        lines.append(md_table_row(cells))

    lines.append("")
    lines.append(f"*Generated: {date_str}*")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build KazBench leaderboard.md from results/*.json"
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("results"),
        help="Directory containing results JSON files (default: results/)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("leaderboard.md"),
        help="Output Markdown file path (default: leaderboard.md)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default="(date not set)",
        help="Date string for the 'Generated' note (default: '(date not set)')",
    )
    args = parser.parse_args()

    results_dir: Path = args.results
    out_path: Path = args.out
    date_str: str = args.date

    if not results_dir.is_dir():
        print(f"[ERROR] Results directory not found: {results_dir}", file=sys.stderr)
        return 1

    json_files = sorted(results_dir.glob("*.json"))
    if not json_files:
        print(f"[WARN] No JSON files found in {results_dir}", file=sys.stderr)

    rows: list[dict[str, Any]] = []
    for path in json_files:
        data = load_result(path)
        if data is not None:
            rows.append(build_row(data))

    if not rows:
        print("[ERROR] No valid result files to build leaderboard from.", file=sys.stderr)
        return 1

    # Sort descending by overall score
    rows.sort(key=lambda r: r["overall"], reverse=True)

    md_content = build_leaderboard_md(rows, date_str)

    try:
        out_path.write_text(md_content, encoding="utf-8")
    except OSError as exc:
        print(f"[ERROR] Could not write {out_path}: {exc}", file=sys.stderr)
        return 1

    print(f"[OK] Leaderboard written -> {out_path}  ({len(rows)} model(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
