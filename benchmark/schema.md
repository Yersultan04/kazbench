# KazBench — Data Contract (schema v1)

Every benchmark item is one JSON object per line (JSONL), in `benchmark/<split>/<task>.jsonl`
where `<split>` ∈ {`dev`} publicly (the `test` split is private, same schema).

## Common fields (all tasks)
| Field | Type | Notes |
|---|---|---|
| `id` | string | unique, `<taskprefix>_<6digits>` (e.g. `kmc_000001`) |
| `task` | string | one of the 6 task names below |
| `source` | string | `seed` \| `native` \| `exam` \| `community` — provenance |
| `validated` | bool | `true` once a native reviewer signs off (default `false`) |
| `canary` | string? | optional contamination canary marker; omit for normal items |

## Per-task fields & metric
| Task | Extra fields | Metric |
|---|---|---|
| `knowledge_mc` | `question:str`, `choices:[str]`, `answer:int` (0-based) | accuracy |
| `reading_comprehension` | `passage:str`, `question:str`, `choices:[str]`, `answer:int` | accuracy |
| `grammar_morphology` | `question:str`, `choices:[str]`, `answer:int` | accuracy |
| `sentiment` | `text:str`, `label:str` ∈ {`оң`,`теріс`,`бейтарап`} | accuracy |
| `translation` | `source_lang:str`, `target_lang:str`, `source_text:str`, `reference:str` | chrF |
| `instruction_following` | `instruction:str`, `rubric:str` (criteria for an LLM-judge) | judge score 0–1 |

## Results JSON (harness output) — `results/<model-label>.json`
```json
{
  "model": "claude-haiku-4-5",
  "adapter": "claude",
  "kazbench_version": "0.1.0",
  "split": "dev",
  "overall": 0.0,
  "tasks": {
    "knowledge_mc": {"metric": "accuracy", "score": 0.0, "n": 100}
  }
}
```
- Accuracy/judge scores in [0,1]; chrF in [0,100].
- `overall` = macro-average across tasks, accuracy/judge scaled ×100 so all are on 0–100.

## Integrity rules
- **Private TEST** mirrors this schema but is never committed publicly; scores are official only
  when verified on TEST by a maintainer.
- **Canary items**: a few items carry a unique `canary` string; if a model reproduces it verbatim,
  contamination is flagged.
- **No answers in DEV prompts**; parsers must not leak gold.
- Every item must pass `tools/data/validate.py` (schema lint + dedup) before merge.
