---
title: KazBench Launch Announcement
version: v0.1 (seed data, harness complete)
date: 2026-06-14
---

# KazBench — Announcement Copy

## One-paragraph version

(Use for email newsletters, Discord/Slack posts, forum intros, or the top of a blog post.)

---

Kazakh is spoken by 13 million people — but if you build or choose an LLM today, there is no
standard way to measure how well it actually handles the language. KazBench is the open benchmark
that changes that. It ships six Kazakh-language evaluation tasks (factual knowledge, reading
comprehension, agglutinative morphology, sentiment, KK→EN/RU translation, and instruction
following), a model-agnostic eval harness anyone can run locally or in CI, and a public leaderboard
on Hugging Face Space. The dataset is versioned with a public DEV split and a private TEST split to
keep scores honest. Everything is open-source (MIT code, CC BY 4.0 data) and built for community
contributions: if you are a native Kazakh speaker, an NLP researcher, or a team building a
Kazakh-language model, KazBench is your measuring stick — and your way to make an impact on a
language that deserves better coverage in AI.

---

## Long-form version

(Use for a blog post, GitHub Discussions announcement, or conference abstract.)

---

### The problem: Kazakh is a blind spot in LLM evaluation

Frontier language models claim multilingual capability, yet for Kazakh — a morphologically complex
Turkic language spoken by 13 million people and the official state language of Kazakhstan — there is
no standard, reproducible benchmark. Teams building Kazakh-language applications have no principled
way to compare GPT-4o, Gemini, Mistral, or a locally fine-tuned model. Choices get made on
intuition. Progress is invisible.

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

The dataset ships with a **public DEV split** for running evals and a **private TEST split** held
by maintainers for verifying submitted results. This prevents the benchmark from leaking into
model training data and keeps leaderboard rankings honest.

**2. An open-source eval harness:**

Any model plugs in behind a single `generate(prompt)` interface — Claude, OpenAI-compatible APIs,
local/HF models, or the offline dummy baseline. Run evaluation in two commands:

```bash
pip install -r requirements.txt
python -m harness.run_eval --model dummy --split dev --out results/dummy.json
```

Results are saved as versioned JSON, reproducible from fixed prompts.

**3. A public leaderboard (Hugging Face Space):**

Submission is decentralized: you run the eval on your own compute and submit results + a pull
request. A maintainer verifies against the private TEST set. No API cost to the project; it scales
with the community.

### Data status — v0.1, seed only

The harness is complete and runs end-to-end. The dataset ships with approximately 15–20 seed items
per task, all marked `validated: false`. **These seed items make the pipeline functional but are
not yet large enough or native-validated enough to support headline model comparisons.** The core
community contribution we need is expanding each task to 100+ items and putting each through our
two-native-reviewer validation process.

We are being explicit about this because benchmark credibility depends on honest reporting. We
would rather launch early and invite collaboration than wait in private for a perfect v1.

### How to contribute

- **Native Kazakh speakers**: review existing seed items, author new ones. Two native reviewers
  must sign off on each item before it earns `validated: true`. This is the highest-leverage
  contribution possible.
- **NLP researchers**: add new task types, improve prompt templates, propose evaluation
  methodology.
- **Model builders**: run your model on the DEV set, submit results, land on the leaderboard.
- **Everyone**: open issues, fix bugs, improve tooling.

See `CONTRIBUTING.md` for the data contract, PR process, and anti-contamination rules.

### Why this matters beyond the benchmark

KazBench is infrastructure. Every team building a Kazakh-language product — chatbots, search
systems, education tools, government services — benefits from a shared measurement standard. Every
model builder gets a signal they cannot currently get. And every citation in a future paper points
back to a community that decided Kazakh is worth measuring carefully.

The benchmark is named after the country. The ambition matches.

**GitHub**: [github.com/Yersultan04/kazbench](https://github.com/Yersultan04/kazbench)
**HF Leaderboard**: (coming soon — HF Space deploy pending)
**Contact**: open an issue or reach out to [@Yersultan04](https://github.com/Yersultan04)

Рахмет for reading. Contributions welcome.
