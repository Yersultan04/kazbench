# 🇰🇿 KazBench

**An open benchmark for evaluating Large Language Models on the Kazakh language.**

Kazakh is spoken by ~13M people but is **low-resource**: frontier LLMs are rarely measured on it,
so nobody knows how well they read, reason, translate, or follow instructions in Kazakh. KazBench
is the measuring stick — a reproducible suite of Kazakh tasks, a model-agnostic evaluation harness,
and a public leaderboard.

> If you build, fine-tune, or choose an LLM for Kazakh, KazBench tells you which one is actually
> good — with numbers, not vibes.

---

## ✨ 30-second demo

```bash
pip install -r requirements.txt

# Offline dummy baseline over the whole benchmark
python -m harness.run_eval --model dummy --split dev --out results/dummy.json
```

Evaluate a real model:

```bash
export ANTHROPIC_API_KEY=...
python -m harness.run_eval --model claude --model-id claude-haiku-4-5-20251001 --out results/claude-haiku.json
```

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

## ⚠️ Data status

Ships with a **seed set (v0.1)**: ~15–20 items/task, all marked `validated:false`. It makes the
harness runnable end-to-end but is **not yet validated or large enough for headline claims**.
Expanding and **native-speaker validating** each task (target 100+ items/task) is the core community
contribution — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repo layout

```
benchmark/schema.md       # data contract
benchmark/dev/*.jsonl      # public DEV split (seed v0.1)
harness/                   # run_eval, models, metrics
tools/data/                # validate.py, stats.py
results/                   # per-model result JSONs
```

## Roadmap

See [`PLAN.md`](PLAN.md). Leaderboard (HF Space), CI, and the v1 dataset expansion are in progress.

## License

Code: MIT (`LICENSE`). Data: CC BY 4.0 (`benchmark/LICENSE-DATA`). Cite via [`CITATION.cff`](CITATION.cff).
