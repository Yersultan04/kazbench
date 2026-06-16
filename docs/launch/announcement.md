---
title: KazBench Launch Announcement
version: v0.1 (296 native-validated items, harness + leaderboard live)
date: 2026-06-16
---

# KazBench — Announcement Copy

## One-paragraph version

(Use for email newsletters, Discord/Slack posts, forum intros, or the top of a blog post.)

---

Kazakh is spoken by 13 million people — but if you build or choose an LLM today, there is no
standard way to measure how well it actually handles the language. KazBench is the open benchmark
that changes that. It covers six Kazakh-language evaluation tasks (factual knowledge, reading
comprehension, agglutinative morphology, sentiment, KK→EN/RU translation, and instruction
following), a model-agnostic eval harness anyone can run locally or in CI, and a live public
leaderboard on Hugging Face. The dataset ships with 296 native-validated items across a public DEV
split and a private TEST split to keep scores honest. First results are in: Llama-4-Scout leads at
87.53 overall; Llama-3.1-8B sits at 64.94; translation is where the biggest gap between models
shows up. Everything is open-source (MIT code, CC BY 4.0 data) and built for community
contributions. If you build or evaluate Kazakh-language AI, KazBench is your measuring stick.

---

## Long-form version

(Use for a blog post, GitHub Discussions announcement, or conference abstract.)

---

### The problem: Kazakh is a blind spot in LLM evaluation

Frontier language models claim multilingual capability, yet for Kazakh — a morphologically complex
Turkic language spoken by 13 million people and the official state language of Kazakhstan — there
has been no standard, reproducible benchmark. Teams building Kazakh-language applications had no
principled way to compare GPT-4o, Gemini, Mistral, or a locally fine-tuned model. Choices got
made on intuition. Progress was invisible.

This is a tractable problem. The NLP community has standardized evaluation for dozens of
low-resource languages through open benchmarks. Kazakh deserves the same infrastructure.

### Introducing KazBench

KazBench is an open benchmark for evaluating LLMs on the Kazakh language. It consists of three
components:

**1. An evaluation suite — six tasks covering the core competencies of Kazakh-language AI:**

| Task | What it tests | Metric |
|---|---|---|
| Knowledge MC | Factual knowledge, multiple-choice | Accuracy |
| Reading Comprehension | Passage understanding, multiple-choice | Accuracy |
| Grammar / Morphology | Agglutinative morphology, case suffixes, MC | Accuracy |
| Sentiment | 3-class sentiment classification (оң / теріс / бейтарап) | Accuracy |
| Translation | KK→EN and KK→RU quality | chrF |
| Instruction Following | Following Kazakh-language instructions | LLM-judge (0–1) |

Overall score = macro-average across all six tasks, all scaled to 0–100.

The dataset ships with 296 native-validated items. The **public DEV split** is available for
running evals; the **private TEST split** is held by maintainers for verifying submitted results.
This prevents benchmark data from leaking into model training and keeps leaderboard rankings honest.

**2. An open-source eval harness:**

Any model plugs in behind a single `generate(prompt)` interface — Claude, OpenAI-compatible APIs,
local/HF models, or the offline dummy baseline. Run evaluation in two commands:

```bash
pip install -r requirements.txt
python -m harness.run_eval --model dummy --split dev --out results/dummy.json
```

Results are saved as versioned JSON, reproducible from fixed prompts.

**3. A live public leaderboard (Hugging Face Space):**

The leaderboard is live at https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard.

Submission is decentralized: you run the eval on your own compute and submit results via pull
request. A maintainer verifies against the private TEST set. No API cost to the project; it scales
with the community.

### First results

| Model | Overall | Notes |
|---|---|---|
| Llama-4-Scout | 87.53 | Current leader |
| Llama-3.1-8B | 64.94 | |
| Dummy baseline | 22.97 | Floor — random-choice model |

Translation (chrF) is the task with the largest spread between models — the gap between the
strongest and weakest submitted result is substantial (chrF 92 vs 26). This is expected for an
agglutinative language where surface-level token overlap is a poor proxy for quality.

### How to run your model

```bash
# Plug in your model:
python -m harness.run_eval \
  --model openai \
  --model-id your-model-id \
  --out results/your-model.json

# Submit: open a PR at github.com/Yersultan04/kazbench
```

### How to contribute

- **Model builders**: run your model on the DEV set, submit results via PR, land on the
  leaderboard at https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard.
- **Native Kazakh speakers**: review existing items, author new ones. Two native reviewers
  must sign off on each item before it earns `validated: true`. This is the highest-leverage
  contribution possible.
- **NLP researchers**: add new task types, improve prompt templates, propose evaluation
  methodology.
- **Everyone**: open issues, fix bugs, improve tooling.

See `CONTRIBUTING.md` for the data contract, PR process, and anti-contamination rules.

### Why this matters beyond the benchmark

KazBench is infrastructure. Every team building a Kazakh-language product — chatbots, search
systems, education tools, government services — benefits from a shared measurement standard. Every
model builder gets a signal they cannot currently get from any other source. And every citation in
a future paper points back to a community that decided Kazakh is worth measuring carefully.

The benchmark is named after the country. The ambition matches.

**GitHub**: https://github.com/Yersultan04/kazbench
**HF Dataset**: https://huggingface.co/datasets/Yersultan03/kazbench
**Live Leaderboard**: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard
**Contact**: open an issue or reach out to [@Yersultan04](https://github.com/Yersultan04)

Рахмет for reading. Run your model and submit a PR.
