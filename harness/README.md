# KazBench Eval Harness

Open evaluation harness for the KazBench Kazakh-language benchmark.

## Requirements

- Python 3.11+
- No mandatory third-party dependencies (standard library only for the `dummy` adapter)
- Optional: `anthropic` SDK for `--model claude`
- Optional: `openai` SDK for `--model openai`

## Quick start

```bash
# From the repo root (C:\...\kazbench\)

# Offline smoke-test (no API key needed)
python -m harness.run_eval --model dummy --split dev --out results/dummy.json

# Claude (set ANTHROPIC_API_KEY first)
python -m harness.run_eval --model claude --split dev --out results/claude-haiku.json

# Custom model via OpenAI-compatible endpoint (e.g. local vLLM)
OPENAI_BASE_URL=http://localhost:8000/v1 \
python -m harness.run_eval --model openai --model-id llama3 --split dev --out results/llama3.json
```

## CLI options

| Flag | Default | Description |
|---|---|---|
| `--model` | (required) | `dummy`, `claude`, or `openai` |
| `--model-id` | adapter default | Override model identifier |
| `--split` | `dev` | Dataset split (`dev` or `test`) |
| `--tasks` | all 6 | Space-separated subset of task names |
| `--out` | (required) | Output JSON path |
| `--data-dir` | repo root | Root containing `benchmark/<split>/` |

## Tasks

| Task | File | Metric |
|---|---|---|
| `knowledge_mc` | `benchmark/dev/knowledge_mc.jsonl` | accuracy |
| `reading_comprehension` | `benchmark/dev/reading_comprehension.jsonl` | accuracy |
| `grammar_morphology` | `benchmark/dev/grammar_morphology.jsonl` | accuracy |
| `sentiment` | `benchmark/dev/sentiment.jsonl` | accuracy |
| `translation` | `benchmark/dev/translation.jsonl` | chrF (0-100) |
| `instruction_following` | `benchmark/dev/instruction_following.jsonl` | judge score (0-1 -> x100) |

## Output format

```json
{
  "model": "dummy",
  "adapter": "dummy",
  "kazbench_version": "0.1.0",
  "split": "dev",
  "overall": 42.5,
  "tasks": {
    "knowledge_mc": {"metric": "accuracy", "score": 0.5, "n": 100}
  }
}
```

`overall` is the macro-average across tasks, all normalised to [0, 100].

## Adding a new model adapter

Subclass `harness.models.BaseModel`, implement `generate(prompt: str) -> str`,
and register the name in `build_model()`.

## Metrics

- **accuracy** -- exact-match fraction in [0, 1]
- **chrF** -- character n-gram F-score (n=1..6, beta=2), range [0, 100]; pure Python, no external deps
- **judge** -- LLM-as-judge score normalised to [0, 1]; the same model under evaluation acts as judge unless overridden
