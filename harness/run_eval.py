"""
KazBench evaluation runner.

Usage:
    python -m harness.run_eval --model dummy --split dev --out results/dummy.json
    python -m harness.run_eval --model claude --split dev --out results/claude.json
    python -m harness.run_eval --model openai --model-id llama3 --split dev --out results/llama3.json

Reproducibility flags:
    --validated-only      Evaluate only items with validated=true (default: True).
    --all-items           Override --validated-only; evaluate all items regardless.
    --temperature FLOAT   Sampling temperature logged in run metadata (default: 0.0).
    --seed INT            Random seed logged in run metadata (default: 42).

All console output uses ASCII-safe characters only (Windows cp1251 safe).
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Any

from harness import __version__
from harness.metrics import accuracy, chrf_sentence, judge_score
from harness.models import BaseModel, build_model

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Security constants
# ---------------------------------------------------------------------------

_ALLOWED_SPLITS: set[str] = {"dev", "test", "staging_eval"}

# Maximum size (bytes) for a single results JSON loaded by tooling
MAX_RESULT_FILE_BYTES: int = 1 * 1024 * 1024  # 1 MB

# ---------------------------------------------------------------------------
# Task names (must match schema.md)
# ---------------------------------------------------------------------------

ALL_TASKS = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]

# Tasks scored with accuracy (MC or classification)
ACCURACY_TASKS = {"knowledge_mc", "reading_comprehension", "grammar_morphology", "sentiment"}
# Tasks scored with chrF
CHRF_TASKS = {"translation"}
# Tasks scored with LLM judge
JUDGE_TASKS = {"instruction_following"}

# ---------------------------------------------------------------------------
# Prompt builders -- ALL prompts are Cyrillic Kazakh
# ---------------------------------------------------------------------------

def _choices_block(choices: list[str]) -> str:
    """Format a choices list as '0. ...\n1. ...'"""
    return "\n".join(f"{i}. {c}" for i, c in enumerate(choices))


def build_prompt_knowledge_mc(item: dict) -> str:
    return (
        f"Сұрақ: {item['question']}\n\n"
        f"{_choices_block(item['choices'])}\n\n"
        "Жауап нөмірін "
        "жазыңыз (0, 1, 2, ...): "
    )


def build_prompt_reading_comprehension(item: dict) -> str:
    return (
        f"Мәтін:\n{item['passage']}\n\n"
        f"Сұрақ: {item['question']}\n\n"
        f"{_choices_block(item['choices'])}\n\n"
        "Жауап нөмірін "
        "жазыңыз (0, 1, 2, ...): "
    )


def build_prompt_grammar_morphology(item: dict) -> str:
    return (
        f"Грамматика "
        f"сұрақы: {item['question']}\n\n"
        f"{_choices_block(item['choices'])}\n\n"
        "Жауап нөмірін "
        "жазыңыз (0, 1, 2, ...): "
    )


def build_prompt_sentiment(item: dict) -> str:
    return (
        f"Келесі мәтіннің көңіл-күйін анықта: '{item['text']}'\n\n"
        "Тек бір сөзбен жауап бер: оң, теріс немесе бейтарап."
    )


def build_prompt_translation(item: dict) -> str:
    src = item["source_lang"]
    tgt = item["target_lang"]
    text = item["source_text"]
    return (
        f"Келесі мәтінді "
        f"{src} тілінен {tgt} "
        f"тіліне аудар:\n\n"
        f"{text}\n\n"
        "Тек аударманы "
        "жазыңыз, басқа "
        "нәрсесін қоспа."
    )


def build_prompt_instruction_following(item: dict) -> str:
    return item["instruction"]


# ---------------------------------------------------------------------------
# Answer parsers
# ---------------------------------------------------------------------------

# Match full integers (including multi-digit) at a word boundary
_INT_RE = re.compile(r"\b(\d+)\b")


def parse_mc(response: str, num_choices: int) -> int:
    """
    Parse a multiple-choice answer from the model response.

    Tries to find the first standalone integer in [0, num_choices-1].
    Handles 2-digit+ choice indices (e.g. index 10, 11, ...).
    Falls back to -1 (no valid answer) if nothing matches.
    """
    for m in _INT_RE.finditer(response.strip()):
        digit = int(m.group(1))
        if 0 <= digit < num_choices:
            return digit
    return -1  # unparseable -> wrong


_SENTIMENT_MAP = {
    # Positive forms
    "on":          "on",
    "ijobaly":     "on",
    "positive":    "on",
    # Negative forms
    "teris":       "teris",
    "terisshi":    "teris",
    "negative":    "teris",
    # Neutral forms
    "beitarap":    "beitarap",
    "beyjaiy":     "beitarap",
    "neutral":     "beitarap",
}

# Map Cyrillic Kazakh labels to our ASCII internal keys
_CYRILLIC_SENTIMENT = {
    "ң":           "on",        # оң (short form)
    "оң":     "on",        # оң
    "теріс": "teris",    # теріс
    "бейтарап": "beitarap",  # бейтарап
}

# The gold labels in schema.md are Cyrillic: оң / теріс / бейтарап
_GOLD_LABEL_TO_INTERNAL = {
    "оң":     "on",        # оң
    "теріс": "teris",
    "бейтарап": "beitarap",
}


def parse_sentiment(response: str) -> str:
    """
    Map a sentiment response string to one of: on / teris / beitarap.

    Returns "unknown" if no label found.
    """
    clean = response.strip().lower()

    # Try Cyrillic label first (model may output in Kazakh script)
    for cyr, internal in _CYRILLIC_SENTIMENT.items():
        if cyr in clean:
            return internal

    # Try transliterated / English labels
    for token, internal in _SENTIMENT_MAP.items():
        if token in clean:
            return internal

    # Substring scan on first word
    first_word = clean.split()[0] if clean.split() else ""
    for token, internal in _SENTIMENT_MAP.items():
        if first_word.startswith(token):
            return internal

    return "unknown"


def gold_sentiment(label: str) -> str:
    """Convert a gold Cyrillic sentiment label to internal ASCII key."""
    return _GOLD_LABEL_TO_INTERNAL.get(label, label.lower())


# ---------------------------------------------------------------------------
# Per-task evaluator
# ---------------------------------------------------------------------------

def evaluate_task(
    task_name: str,
    items: list[dict],
    model: BaseModel,
    predictions: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Run evaluation for a single task.

    Returns:
        {"metric": str, "score": float, "n": int}
        score is in [0,1] for accuracy/judge, [0,100] for chrF.

    If `predictions` is given, per-item records {id, task, pred, gold, correct}
    are appended for accuracy tasks (used by the council triage tool).
    """
    n = len(items)
    if n == 0:
        return {"metric": "accuracy", "score": 0.0, "n": 0}

    if task_name in ACCURACY_TASKS:
        preds: list[int | str] = []
        golds: list[int | str] = []

        for item in items:
            if task_name == "sentiment":
                prompt = build_prompt_sentiment(item)
                response = model.generate(prompt, task=task_name)
                pred = parse_sentiment(response)
                gold = gold_sentiment(item["label"])
            else:
                if task_name == "knowledge_mc":
                    prompt = build_prompt_knowledge_mc(item)
                elif task_name == "reading_comprehension":
                    prompt = build_prompt_reading_comprehension(item)
                else:  # grammar_morphology
                    prompt = build_prompt_grammar_morphology(item)
                response = model.generate(prompt, task=task_name)
                pred = parse_mc(response, len(item["choices"]))
                gold = item["answer"]
            preds.append(pred)
            golds.append(gold)
            if predictions is not None:
                predictions.append({
                    "id": item.get("id", ""),
                    "task": task_name,
                    "pred": pred,
                    "gold": gold,
                    "correct": pred == gold,
                })

        score = accuracy(preds, golds)
        return {"metric": "accuracy", "score": score, "n": n}

    elif task_name in CHRF_TASKS:
        scores: list[float] = []
        for item in items:
            prompt = build_prompt_translation(item)
            hypothesis = model.generate(prompt, task=task_name)
            s = chrf_sentence(hypothesis, item["reference"])
            scores.append(s)
        avg = sum(scores) / len(scores) if scores else 0.0
        return {"metric": "chrF", "score": avg, "n": n}

    elif task_name in JUDGE_TASKS:
        raw_scores: list[float] = []
        for item in items:
            prompt = build_prompt_instruction_following(item)
            response = model.generate(prompt, task=task_name)
            s = judge_score(response, item["rubric"], model)
            raw_scores.append(s)
        avg = sum(raw_scores) / len(raw_scores) if raw_scores else 0.0
        return {"metric": "judge", "score": avg, "n": n}

    else:
        warnings.warn(f"Unknown task '{task_name}'; skipping.")
        return {"metric": "unknown", "score": 0.0, "n": n}


# ---------------------------------------------------------------------------
# Results writer
# ---------------------------------------------------------------------------

def _overall_score(task_results: dict[str, dict]) -> float:
    """
    Compute macro-average across tasks.

    Accuracy and judge scores are already in [0,1] -> multiply by 100.
    chrF is in [0,100] -> use as-is.
    Returns the macro-average in [0, 100].
    """
    if not task_results:
        return 0.0
    values: list[float] = []
    for info in task_results.values():
        if info["n"] == 0:
            continue
        metric = info["metric"]
        score = info["score"]
        if metric in ("accuracy", "judge"):
            values.append(score * 100.0)
        else:  # chrF already in [0,100]
            values.append(score)
    return sum(values) / len(values) if values else 0.0


def write_results(
    out_path: Path,
    model_label: str,
    adapter_name: str,
    split: str,
    task_results: dict[str, dict],
    *,
    validated_only: bool = True,
    temperature: float = 0.0,
    seed: int = 42,
) -> None:
    """Write results JSON in the schema.md format."""
    # Create only the immediate parent directory (no deep auto-create)
    out_path.parent.mkdir(exist_ok=True)

    # Aggregate reproducibility metadata across tasks
    n_total_all = sum(info.get("n_total", info["n"]) for info in task_results.values())
    n_validated_all = sum(info.get("n_validated", info["n"]) for info in task_results.values())

    payload = {
        "model": model_label,
        "adapter": adapter_name,
        "kazbench_version": __version__,
        "split": split,
        "overall": round(_overall_score(task_results), 4),
        # --- run metadata for reproducibility ---
        "run_metadata": {
            "validated_only": validated_only,
            "n_total": n_total_all,
            "n_validated": n_validated_all,
            "temperature": temperature,
            "seed": seed,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "tasks": {
            task: {
                "metric": info["metric"],
                "score": round(info["score"], 6),
                "n": info["n"],
            }
            for task, info in task_results.items()
        },
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m harness.run_eval",
        description="KazBench evaluation harness",
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=["dummy", "claude", "openai"],
        help="Model adapter to use.",
    )
    parser.add_argument(
        "--model-id",
        default=None,
        help="Model identifier (e.g. claude-haiku-4-5-20251001, gpt-4o-mini).",
    )
    parser.add_argument(
        "--split",
        default="dev",
        help="Dataset split to evaluate (default: dev). Must be 'dev' or 'test'.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=None,
        help="Subset of tasks to run. Defaults to all 6.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output JSON path, e.g. results/dummy.json.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Root directory containing benchmark/<split>/ folders. "
             "Defaults to the parent of the harness/ package.",
    )
    parser.add_argument(
        "--save-predictions",
        default=None,
        help="Optional path to dump per-item predictions JSON (for council triage).",
    )

    # --- Reproducibility flags ---
    validated_group = parser.add_mutually_exclusive_group()
    validated_group.add_argument(
        "--validated-only",
        dest="validated_only",
        action="store_true",
        default=True,
        help="Evaluate only items with validated=true (default behaviour).",
    )
    validated_group.add_argument(
        "--all-items",
        dest="validated_only",
        action="store_false",
        help="Evaluate all items regardless of validated flag.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (logged in run metadata, default: 0.0).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (logged in run metadata, default: 42).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # --- Security: validate --split against allowlist ---
    if args.split not in _ALLOWED_SPLITS:
        print(
            f"[kazbench] ERROR: --split must be one of {sorted(_ALLOWED_SPLITS)}, "
            f"got '{args.split}'."
        )
        return 1

    # The --split allowlist above already blocks path-traversal via the split name.
    # --out / --data-dir are caller-controlled by design (this is a CLI the user runs
    # themselves); restricting them to the repo root breaks legitimate use such as writing
    # results to a temp dir. CI pipelines, not the CLI, vet PR-supplied arguments.
    harness_pkg_dir = Path(__file__).parent
    repo_root = harness_pkg_dir.parent.resolve()

    data_root = Path(args.data_dir).resolve() if args.data_dir else repo_root
    out_path = Path(args.out).resolve()

    split_dir = data_root / "benchmark" / args.split

    # Build model
    print(f"[kazbench] Building model adapter: {args.model}")
    model = build_model(args.model, args.model_id)
    model_label = args.model_id or args.model

    # Determine tasks and whether they were explicitly requested
    explicitly_requested = args.tasks is not None
    tasks_to_run = args.tasks if args.tasks else ALL_TASKS

    task_results: dict[str, dict] = {}
    all_predictions: list[dict] | None = [] if args.save_predictions else None

    for task_name in tasks_to_run:
        task_file = split_dir / f"{task_name}.jsonl"
        if not task_file.exists():
            if explicitly_requested:
                # Hard-fail: user explicitly asked for this task
                print(
                    f"[kazbench] ERROR: requested task '{task_name}' data file not found: "
                    f"{task_file}"
                )
                return 1
            else:
                # Warn-only when running the default full set
                print(
                    f"[kazbench] WARNING: {task_file} not found -- skipping "
                    f"(data agent may not have written it yet)."
                )
                continue

        # Load items
        all_items: list[dict] = []
        with task_file.open(encoding="utf-8-sig") as f:  # utf-8-sig strips BOM if present
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    all_items.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    print(
                        f"[kazbench] WARNING: {task_file}:{lineno} -- "
                        f"invalid JSON ({exc}), skipping line."
                    )

        n_total = len(all_items)
        if args.validated_only:
            items = [it for it in all_items if it.get("validated") is True]
        else:
            items = all_items
        n_validated = sum(1 for it in all_items if it.get("validated") is True)

        print(
            f"[kazbench] Task={task_name}  "
            f"total={n_total}  validated={n_validated}  "
            f"evaluating={len(items)}  ...",
            end="",
            flush=True,
        )
        result = evaluate_task(task_name, items, model, predictions=all_predictions)
        # Attach per-task reproducibility counts for write_results aggregation
        result["n_total"] = n_total
        result["n_validated"] = n_validated
        metric = result["metric"]
        score = result["score"]
        if metric in ("accuracy", "judge"):
            display = f"{score * 100:.1f}%"
        else:
            display = f"{score:.2f}"
        print(f"  {metric}={display}")
        task_results[task_name] = result

    # Write output
    write_results(
        out_path,
        model_label,
        args.model,
        args.split,
        task_results,
        validated_only=args.validated_only,
        temperature=args.temperature,
        seed=args.seed,
    )

    if all_predictions is not None:
        pred_path = Path(args.save_predictions).resolve()
        pred_path.parent.mkdir(exist_ok=True)
        pred_path.write_text(
            json.dumps(
                {"model": model_label, "split": args.split, "predictions": all_predictions},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )
        print(f"[kazbench] Predictions -> {pred_path}")

    overall = _overall_score(task_results)
    tasks_ran = sum(1 for r in task_results.values() if r["n"] > 0)
    print(f"[kazbench] Done. Tasks run: {tasks_ran}  Overall: {overall:.2f}/100")
    print(f"[kazbench] Results -> {out_path.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
