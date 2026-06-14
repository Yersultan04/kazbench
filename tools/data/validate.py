#!/usr/bin/env python3
"""KazBench data validator.

Schema-lints benchmark JSONL files (one item per line) against the KazBench
data contract (benchmark/schema.md), detects duplicate ids and duplicate
content, and reports canary coverage per task.

Usage:
    python tools/data/validate.py benchmark/dev/
    python tools/data/validate.py benchmark/dev/sentiment.jsonl

Exit code 0 = clean, non-zero = one or more violations found.

Console output is ASCII-only (Windows cp1251 safe): use '->' not arrows.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- Data contract --------------------------------------------------------

TASKS: set[str] = {
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
}

SOURCES: set[str] = {"seed", "native", "exam", "community"}

SENTIMENT_LABELS: set[str] = {"оң", "теріс", "бейтарап"}
# i.e. {"on", "teris", "beitarap"} written with the real Kazakh letters above.

# Task prefixes for the id convention <prefix>_<6digits>.
TASK_PREFIX: dict[str, str] = {
    "knowledge_mc": "kmc",
    "reading_comprehension": "rc",
    "grammar_morphology": "gm",
    "sentiment": "snt",
    "translation": "trn",
    "instruction_following": "if",
}

MC_TASKS: set[str] = {"knowledge_mc", "reading_comprehension", "grammar_morphology"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # task -> total item count
    counts: dict[str, int] = field(default_factory=dict)
    # task -> canary count
    canaries: dict[str, int] = field(default_factory=dict)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _is_str(v: object) -> bool:
    return isinstance(v, str)


def _is_list_of_str(v: object) -> bool:
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, str) for x in v)


def validate_item(item: dict, where: str, rep: Report) -> str | None:
    """Validate a single item dict. Returns the item id if usable, else None."""
    # --- common required fields ---
    for fld in ("id", "task", "source", "validated"):
        if fld not in item:
            rep.error(f"{where}: missing required field '{fld}'")

    item_id = item.get("id")
    task = item.get("task")
    source = item.get("source")
    validated = item.get("validated")

    if item_id is not None and not _is_str(item_id):
        rep.error(f"{where}: 'id' must be a string")
        item_id = None
    if task is not None and not _is_str(task):
        rep.error(f"{where}: 'task' must be a string")
    if source is not None and not _is_str(source):
        rep.error(f"{where}: 'source' must be a string")
    if validated is not None and not isinstance(validated, bool):
        rep.error(f"{where}: 'validated' must be a bool")

    if task is not None and task not in TASKS:
        rep.error(f"{where}: unknown task '{task}'")
    if source is not None and source not in SOURCES:
        rep.error(f"{where}: unknown source '{source}' (allowed: {sorted(SOURCES)})")

    # id convention check (warn only - non-fatal naming hint)
    if _is_str(item_id) and task in TASK_PREFIX:
        prefix = TASK_PREFIX[task]
        if not item_id.startswith(prefix + "_"):
            rep.warn(f"{where}: id '{item_id}' does not match prefix '{prefix}_' for task '{task}'")

    # canary field, when present, must be a string
    if "canary" in item:
        if not _is_str(item["canary"]):
            rep.error(f"{where}: 'canary' must be a string when present")
        elif task in rep.canaries:
            rep.canaries[task] += 1

    # --- per-task fields ---
    if task in MC_TASKS:
        _validate_mc(item, task, where, rep)
    elif task == "sentiment":
        _validate_sentiment(item, where, rep)
    elif task == "translation":
        _validate_translation(item, where, rep)
    elif task == "instruction_following":
        _validate_instruction(item, where, rep)

    return item_id if _is_str(item_id) else None


def _validate_mc(item: dict, task: str, where: str, rep: Report) -> None:
    # reading_comprehension additionally requires a passage
    if task == "reading_comprehension":
        if not _is_str(item.get("passage")):
            rep.error(f"{where}: 'passage' must be a non-empty string")
    if not _is_str(item.get("question")):
        rep.error(f"{where}: 'question' must be a non-empty string")

    choices = item.get("choices")
    if not _is_list_of_str(choices):
        rep.error(f"{where}: 'choices' must be a non-empty list of strings")
        choices = None

    answer = item.get("answer")
    if not isinstance(answer, int) or isinstance(answer, bool):
        rep.error(f"{where}: 'answer' must be an int (0-based index)")
    elif choices is not None and not (0 <= answer < len(choices)):
        rep.error(
            f"{where}: 'answer' index {answer} out of range "
            f"(choices length {len(choices)})"
        )


def _validate_sentiment(item: dict, where: str, rep: Report) -> None:
    if not _is_str(item.get("text")):
        rep.error(f"{where}: 'text' must be a non-empty string")
    label = item.get("label")
    if not _is_str(label):
        rep.error(f"{where}: 'label' must be a string")
    elif label not in SENTIMENT_LABELS:
        # show labels in a cp1251-safe way using unicode escapes count
        rep.error(
            f"{where}: 'label' must be one of the 3 allowed Kazakh sentiment "
            f"labels (on/teris/beitarap)"
        )


def _validate_translation(item: dict, where: str, rep: Report) -> None:
    for fld in ("source_lang", "target_lang", "source_text", "reference"):
        if not _is_str(item.get(fld)):
            rep.error(f"{where}: '{fld}' must be a non-empty string")
    src = item.get("source_lang")
    if _is_str(src) and src != "kk":
        rep.warn(f"{where}: source_lang '{src}' is not 'kk' (KazBench source is Kazakh)")
    tgt = item.get("target_lang")
    if _is_str(tgt) and tgt not in {"en", "ru"}:
        rep.warn(f"{where}: target_lang '{tgt}' is not in expected set (en, ru)")


def _validate_instruction(item: dict, where: str, rep: Report) -> None:
    if not _is_str(item.get("instruction")):
        rep.error(f"{where}: 'instruction' must be a non-empty string")
    if not _is_str(item.get("rubric")):
        rep.error(f"{where}: 'rubric' must be a non-empty string")


def gather_files(target: Path) -> list[Path]:
    if target.is_dir():
        return sorted(target.glob("*.jsonl"))
    if target.is_file():
        return [target]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/data/validate.py <file-or-dir>")
        return 2

    target = Path(argv[1])
    files = gather_files(target)
    if not files:
        print(f"ERROR: no .jsonl files found at '{target}'")
        return 2

    rep = Report()
    # initialize counters for all tasks so report is complete
    for t in sorted(TASKS):
        rep.counts.setdefault(t, 0)
        rep.canaries.setdefault(t, 0)

    seen_ids: dict[str, str] = {}        # id -> first location
    seen_content: dict[str, str] = {}    # content-key -> first location

    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            rep.error(f"{path}: cannot read file: {exc}")
            continue

        for lineno, raw in enumerate(lines, start=1):
            raw = raw.strip()
            if not raw:
                continue
            where = f"{path.name}:{lineno}"
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                rep.error(f"{where}: invalid JSON: {exc}")
                continue
            if not isinstance(item, dict):
                rep.error(f"{where}: top-level item must be a JSON object")
                continue

            task = item.get("task")
            if task in rep.counts:
                rep.counts[task] += 1

            item_id = validate_item(item, where, rep)

            # duplicate id detection
            if item_id is not None:
                if item_id in seen_ids:
                    rep.error(
                        f"{where}: duplicate id '{item_id}' "
                        f"(first seen at {seen_ids[item_id]})"
                    )
                else:
                    seen_ids[item_id] = where

            # duplicate content detection (task + primary text payload)
            ckey = _content_key(item)
            if ckey is not None:
                if ckey in seen_content:
                    rep.error(
                        f"{where}: duplicate content "
                        f"(first seen at {seen_content[ckey]})"
                    )
                else:
                    seen_content[ckey] = where

    return _emit(rep)


def _content_key(item: dict) -> str | None:
    """Build a normalized content key for duplicate detection."""
    task = item.get("task")
    parts: list[str] = [str(task)]
    if task in MC_TASKS:
        parts.append(str(item.get("passage", "")))
        parts.append(str(item.get("question", "")))
    elif task == "sentiment":
        parts.append(str(item.get("text", "")))
    elif task == "translation":
        # same source text into a different target language is a distinct item
        parts.append(str(item.get("target_lang", "")))
        parts.append(str(item.get("source_text", "")))
    elif task == "instruction_following":
        parts.append(str(item.get("instruction", "")))
    else:
        return None
    key = "||".join(p.strip().lower() for p in parts)
    # if there is no actual content beyond the task name, skip
    if key == str(task) or key.endswith("||"):
        return None
    return key


def _emit(rep: Report) -> int:
    print("=== KazBench data validation ===")
    total = sum(rep.counts.values())
    print(f"items scanned: {total}")
    print()
    print("per-task counts (canary in parentheses):")
    for t in sorted(TASKS):
        print(f"  {t:24s} {rep.counts.get(t, 0):4d}  (canary: {rep.canaries.get(t, 0)})")
    print()

    # canary coverage report
    missing_canary = [t for t in sorted(TASKS) if rep.counts.get(t, 0) > 0 and rep.canaries.get(t, 0) == 0]
    if missing_canary:
        for t in missing_canary:
            rep.warn(f"task '{t}' has items but no canary marker")

    if rep.warnings:
        print(f"WARNINGS ({len(rep.warnings)}):")
        for w in rep.warnings:
            print(f"  [warn] {w}")
        print()

    if rep.errors:
        print(f"ERRORS ({len(rep.errors)}):")
        for e in rep.errors:
            print(f"  [error] {e}")
        print()
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
