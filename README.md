# 🇰🇿 KazBench

**An open benchmark for evaluating Large Language Models on the Kazakh language.**

[![Dataset on HF](https://img.shields.io/badge/🤗%20Dataset-KazBench-yellow)](https://huggingface.co/datasets/Yersultan03/kazbench)
[![Leaderboard](https://img.shields.io/badge/🏆%20Leaderboard-live-success)](https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-green)](benchmark/LICENSE-DATA)

Kazakh is spoken by ~13M people but is **low-resource**: frontier LLMs are rarely measured on it,
so nobody knows how well they read, reason, translate, or follow instructions in Kazakh. KazBench
is the measuring stick — a reproducible suite of Kazakh tasks, a model-agnostic evaluation harness,
and a public leaderboard.

> If you build, fine-tune, or choose an LLM for Kazakh, KazBench tells you which one is actually
> good — with numbers, not vibes.

- 📊 **Dataset:** https://huggingface.co/datasets/Yersultan03/kazbench
- 🏆 **Live leaderboard:** https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

---

## ✨ 30-second demo

```bash
pip install -r requirements.txt

# Offline dummy baseline over the whole benchmark (no API key needed)
python -m harness.run_eval --model dummy --split dev --out results/dummy.json
```

Evaluate a real model (any OpenAI-compatible endpoint — OpenAI, OpenRouter, vLLM, Ollama):

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1   # or your endpoint
python -m harness.run_eval --model openai --model-id openai/gpt-4o-mini --out results/gpt-4o-mini.json
```

Or via the Anthropic SDK:

```bash
export ANTHROPIC_API_KEY=...
python -m harness.run_eval --model claude --model-id claude-haiku-4-5-20251001 --out results/claude-haiku.json
```

## 🏆 Leaderboard snapshot (DEV, validated-296)

| Rank | Model | Overall | KMC | RC | GM | Sent | Trans | IF |
|---|---|---|---|---|---|---|---|---|
| 1 | claude-3.5-haiku | **91.50** | 96.0 | 100.0 | 97.9 | 88.2 | 86.1 | 80.7 |
| 2 | gpt-4o-mini | 88.30 | 96.0 | 100.0 | 91.7 | 96.1 | 92.3 | 53.8 |
| 3 | llama-4-scout-17b | 87.53 | 96.0 | 87.5 | 87.5 | 100.0 | 92.1 | 62.0 |
| 4 | gemini-2.5-flash | 84.15 | 90.0 | 100.0 | 91.7 | 100.0 | 88.2 | 35.0 |
| 5 | qwen-2.5-72b | 74.54 | 88.0 | 97.9 | 75.0 | 84.3 | 79.8 | 22.1 |
| 6 | llama-3.1-8b | 64.94 | 72.0 | 95.8 | 77.1 | 60.8 | 26.4 | 57.6 |
| — | dummy (floor) | 22.97 | 26.0 | 25.0 | 25.0 | 33.3 | 8.5 | 20.0 |

*Provisional (public DEV). Live, always-current table: [HF Space leaderboard](https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard). Instruction-following (IF) uses a self-judge — treat as soft.*

## Tasks (v1)

| Task | Measures | Metric |
|---|---|---|
| `knowledge_mc` | factual knowledge (MC) | accuracy |
| `reading_comprehension` | passage understanding (MC) | accuracy |
| `grammar_morphology` | agglutinative morphology / case suffixes (MC) | accuracy |
| `sentiment` | sentiment (оң / теріс / бейтарап) | accuracy |
| `translation` | KK→EN / KK→RU quality | chrF |
| `instruction_following` | following Kazakh instructions | LLM-judge 0–1 |

Overall = macro-average across tasks. Data contract: [`benchmark/schema.md`](benchmark/schema.md).

## Design

- **Model-agnostic** — any model behind `generate(prompt)` plugs in (Claude, OpenAI-compatible,
  local/HF, or the offline dummy).
- **Decentralized submission** — you run the eval on your own budget and submit results + a PR; a
  maintainer verifies on a **private TEST** set. Zero API cost to the project; scales.
- **Public DEV + private TEST** — keeps scores honest and prevents the benchmark leaking into
  model training data (contamination canaries included).
- **Reproducible** — fixed prompts, deterministic parsing, results saved as JSON, leaderboard
  regenerated from results. `chrF` (not BLEU) for translation — better for morphologically rich
  low-resource languages.

## 📦 Data status

Public **DEV split: 600 items (100 per task).** Of these, **296 are native-validated**
(`validated: true`) and **304 are pending native review** (`validated: false`) as the set expands
toward the v1 target. A private **TEST split (180 items)** is held out for contamination-resistant
leaderboard verification. Filter on `validated` for the headline-quality subset. Growing and
validating the data is the core community contribution — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repo layout

```
benchmark/schema.md        # data contract
benchmark/dev/*.jsonl       # public DEV split (600 items, 100/task)
harness/                    # run_eval, models, metrics
tools/data/                 # validate.py, stats.py
leaderboard/                # Gradio app (HF Space)
results/                    # per-model result JSONs
```

## Roadmap

See [`PLAN.md`](PLAN.md). v1 dataset expansion and additional frontier-model baselines are ongoing.

## License

Code: MIT (`LICENSE`). Data: CC BY 4.0 (`benchmark/LICENSE-DATA`). Cite via [`CITATION.cff`](CITATION.cff).
