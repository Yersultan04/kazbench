"""
KazBench Leaderboard — Gradio App (Hugging Face Space)

Deploy as a Hugging Face Space:
  - Runtime: Gradio (select "Gradio" when creating the Space)
  - Python 3.11+
  - requirements.txt should contain: gradio>=4.0

The app reads results/*.json relative to the repo root (one directory up from
this file), builds a ranked table, and renders it with per-task breakdown.

Locally:
    pip install gradio
    python leaderboard/app.py

HF Space deploy:
    Push this repo to a Hugging Face Space (Gradio SDK). The Space must have
    the results/ directory available (either committed or fetched at startup).

File ownership layout expected:
    kazbench/
      results/          <- result JSONs
      leaderboard/
        app.py          <- this file
        README.md
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Maximum result file size (bytes) — guard against malicious/corrupt large files
MAX_RESULT_FILE_BYTES: int = 1 * 1024 * 1024  # 1 MB

# ── Resolve paths ──────────────────────────────────────────────────────────────

# Resolve the results directory robustly: works whether app.py runs from
# leaderboard/ (repo layout) or sits at the root of an HF Space alongside results/.
_HERE = Path(__file__).parent
_RESULT_CANDIDATES = (_HERE / "results", _HERE.parent / "results")
RESULTS_DIR = next((p for p in _RESULT_CANDIDATES if p.is_dir()), _RESULT_CANDIDATES[0])
REPO_ROOT = RESULTS_DIR.parent

# ── Task definitions ───────────────────────────────────────────────────────────

TASK_ORDER: list[str] = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]

TASK_LABELS: dict[str, str] = {
    "knowledge_mc": "Knowledge MC",
    "reading_comprehension": "Reading Comp.",
    "grammar_morphology": "Grammar/Morph.",
    "sentiment": "Sentiment",
    "translation": "Translation (chrF)",
    "instruction_following": "Instruction Following",
}

SCALE_X100_METRICS: set[str] = {"accuracy", "judge"}


# ── Data loading ───────────────────────────────────────────────────────────────

def task_score_display(task_data: dict[str, Any]) -> float | None:
    """Return the display score (scaled consistently to [0-100]) or None."""
    metric: str = task_data.get("metric", "")
    raw = task_data.get("score")
    if raw is None:
        return None
    if metric in SCALE_X100_METRICS:
        return round(float(raw) * 100.0, 2)
    return round(float(raw), 2)


def load_results() -> list[dict[str, Any]]:
    """
    Scan RESULTS_DIR for *.json files, parse, and return a list of row dicts
    sorted by overall score descending.
    """
    rows: list[dict[str, Any]] = []

    if not RESULTS_DIR.is_dir():
        return rows

    for path in sorted(RESULTS_DIR.glob("*.json")):
        # Guard against huge/malicious files before parsing
        try:
            if path.stat().st_size > MAX_RESULT_FILE_BYTES:
                print(
                    f"[WARN] Skipping {path} — exceeds {MAX_RESULT_FILE_BYTES} byte limit.",
                    file=sys.stderr,
                )
                continue
        except OSError:
            pass
        try:
            with path.open(encoding="utf-8") as fh:
                data: dict[str, Any] = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue

        if not all(k in data for k in ("model", "overall", "tasks")):
            continue

        tasks: dict[str, Any] = data.get("tasks", {})
        row: dict[str, Any] = {
            "model": data.get("model", "unknown"),
            "adapter": data.get("adapter", ""),
            "split": data.get("split", "dev"),
            "version": data.get("kazbench_version", "?"),
            "overall": float(data.get("overall", 0.0)),
        }

        for task in TASK_ORDER:
            if task in tasks:
                score = task_score_display(tasks[task])
                row[task] = score if score is not None else "n/a"
            else:
                row[task] = "n/a"

        rows.append(row)

    rows.sort(key=lambda r: r["overall"], reverse=True)
    return rows


def build_table_data(rows: list[dict[str, Any]]) -> tuple[list[list[Any]], list[str]]:
    """Return (table_data, column_names) for Gradio Dataframe."""
    columns = (
        ["Rank", "Model", "Split", "Overall"]
        + [TASK_LABELS[t] for t in TASK_ORDER]
        + ["Version"]
    )
    table: list[list[Any]] = []
    for rank, row in enumerate(rows, start=1):
        task_scores = [row.get(t, "n/a") for t in TASK_ORDER]
        table.append(
            [rank, row["model"], row["split"], f"{row['overall']:.2f}"]
            + task_scores
            + [row["version"]]
        )
    return table, columns


# ── Gradio UI (lazy import) ────────────────────────────────────────────────────

def make_app():  # type: ignore[return]
    """Build and return the Gradio Blocks app. Import gradio lazily."""
    try:
        import gradio as gr  # type: ignore[import-untyped]
    except ImportError as exc:
        print(
            f"[ERROR] failed to import gradio: {exc!r}. "
            "Install with: pip install gradio",
            file=sys.stderr,
        )
        raise

    def refresh_table() -> Any:
        rows = load_results()
        table_data, columns = build_table_data(rows)
        return gr.Dataframe(
            value=table_data,
            headers=columns,
            datatype=["number"] + ["str"] * (len(columns) - 1),
            interactive=False,
        )

    with gr.Blocks(title="KazBench Leaderboard") as app:
        gr.Markdown(
            """
# KazBench Leaderboard

Ranks LLM models on **Kazakh-language** AI tasks.

| Column | Metric | Notes |
|--------|--------|-------|
| Knowledge MC | Accuracy (0-100) | Multiple-choice knowledge |
| Reading Comp. | Accuracy (0-100) | Reading comprehension MC |
| Grammar/Morph. | Accuracy (0-100) | Grammar & morphology MC |
| Sentiment | Accuracy (0-100) | 3-class sentiment |
| Translation (chrF) | chrF (0-100) | Kaz <-> other lang |
| Instruction Following | Judge score (0-100) | LLM-judge rubric eval |

**Overall** = macro-average of all 6 task scores (all on 0-100 scale).

> **Provisional (DEV split):** Scores come from the public DEV set.
> Official rankings require private TEST verification by a maintainer.
> See [CONTRIBUTING.md](https://github.com/Yersultan04/kazbench) to submit.
            """
        )

        rows = load_results()
        table_data, columns = build_table_data(rows)

        lb_table = gr.Dataframe(
            value=table_data,
            headers=columns,
            interactive=False,
            wrap=False,
        )

        refresh_btn = gr.Button("Refresh")
        refresh_btn.click(fn=refresh_table, outputs=lb_table)

        gr.Markdown(
            "*KazBench — the standard benchmark for Kazakh-language AI. "
            "[GitHub](https://github.com/Yersultan04/kazbench) | "
            "[HF Datasets](https://huggingface.co/datasets/Yersultan03/kazbench)*"
        )

    return app


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = make_app()
    # NOTE: 0.0.0.0 binding is intentional for Hugging Face Spaces only.
    # Do NOT expose this publicly without authentication in other environments.
    # Pin gradio to a specific version in requirements: gradio==4.44.1
    port = int(os.environ.get("PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        # Restrict file serving to the results directory only
        allowed_paths=[str(RESULTS_DIR)],
    )
