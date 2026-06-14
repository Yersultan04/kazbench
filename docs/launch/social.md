---
title: KazBench — Social Media Copy
note: All copy calibrated for a technical audience. No hype; lead with the gap and the solution.
---

# Social Media Copy

---

## Twitter / X Thread (7 tweets)

Post these as a thread. Tweet 1 is the hook; the rest are depth.

---

**Tweet 1 — Hook (the gap)**

There is no standard benchmark for evaluating LLMs on Kazakh. 13 million speakers. No numbers.

So I built one.

Introducing KazBench: 6 tasks, model-agnostic harness, public leaderboard on HF Space.

Thread.

---

**Tweet 2 — The problem in one line**

Kazakh is agglutinative, morphologically rich, and low-resource. Frontier models claim multilingual
support. Nobody has ever measured whether that claim holds for Kazakh — with a reproducible
evaluation suite, not vibes.

KazBench is the measuring stick.

---

**Tweet 3 — What's in the benchmark**

6 tasks covering Kazakh-language AI competency:

- Knowledge MC (factual)
- Reading comprehension
- Grammar / morphology (agglutinative suffixes)
- Sentiment (оң / теріс / бейтарап)
- KK→EN + KK→RU translation (chrF, not BLEU)
- Instruction following (LLM-judge rubric)

Overall = macro-avg across all 6, scaled 0–100.

---

**Tweet 4 — The design choices**

Design decisions that make it trustworthy:

- Public DEV + private TEST split (prevents contamination)
- Decentralized submission: you run eval on your own budget, submit results + PR
- Deterministic prompts, chrF for translation (better for morphologically rich languages)
- 2-native-speaker review required before any item is marked validated

---

**Tweet 5 — How to run it (30 seconds)**

```bash
pip install -r requirements.txt
python -m harness.run_eval --model dummy --split dev --out results/dummy.json

# Real model:
export ANTHROPIC_API_KEY=...
python -m harness.run_eval --model claude --model-id claude-haiku-4-5-20251001 \
  --out results/claude-haiku.json
```

Plug in any OpenAI-compatible API or local HF model behind generate(prompt).

---

**Tweet 6 — Honest data status**

Honest caveat: v0.1 ships with ~15–20 seed items per task. The harness runs end-to-end. But the
data is NOT yet native-validated or large enough for headline rankings.

The benchmark is infrastructure. Expanding to 100+ items/task with native validation is the job.

Contributions wanted — especially native Kazakh speakers.

---

**Tweet 7 — CTA**

GitHub: github.com/Yersultan04/kazbench
HF Leaderboard: [link when live]
CONTRIBUTING.md: how to add items, run validation, submit model results

If you build KZ-language products, research low-resource NLP, or just want a side project with
real-world impact — this is a good place to start.

Рахмет.

---

## LinkedIn Post

(Professional framing. Doubles as a personal-brand signal for an ML/NLP engineer.)

---

**Headline:** I built an open benchmark for Kazakh-language LLMs — here's why it matters and what I learned.

---

Kazakh is spoken by 13 million people. It is the official state language of Kazakhstan. It is
morphologically complex — agglutinative, with rich case suffixes that break naive tokenizers.

And until now, there was no standard, reproducible benchmark for measuring how well LLMs actually
handle it.

I spent the past several weeks building KazBench to fix that.

**What KazBench is:**

An open evaluation suite (6 tasks), a model-agnostic eval harness, and a public leaderboard
(Hugging Face Space). Anyone can run a model evaluation locally in under two minutes and submit
results via pull request. The private TEST split is held by maintainers to prevent data contamination
and keep scores honest.

**The 6 tasks:**
Knowledge MC, Reading Comprehension, Grammar/Morphology, Sentiment, KK→EN+RU Translation (chrF),
and Instruction Following (LLM-judge rubric).

**What I built it with:**
Python, the Hugging Face ecosystem, Gradio for the leaderboard UI, and a CI pipeline with GitHub
Actions for schema validation and smoke tests. The evaluation harness is model-agnostic — Claude,
OpenAI-compatible APIs, and local models all plug in via a single generate(prompt) interface.

**Honest status:**
v0.1 ships with seed data (~15–20 items/task, unvalidated). The pipeline works end-to-end. The
hard work — expanding to 100+ items/task with two-native-reviewer validation — is the community
contribution phase we are entering now.

**Why I built it:**
Partly because Kazakh deserves better AI coverage. Partly because benchmark design, evaluation
methodology, and low-resource NLP are exactly the intersection I want to work in — and building
real infrastructure is better than writing about it.

If you work in NLP, low-resource languages, or LLM evaluation, I would welcome feedback on the
methodology — especially task selection, the instruction-following rubric design, and the
anti-contamination approach.

GitHub: github.com/Yersultan04/kazbench

#NLP #LLM #MachineLearning #KazakhAI #OpenSource #LowResourceNLP #BenchmarkEvaluation

---

## Show HN

**Title:**
Show HN: KazBench – open benchmark for evaluating LLMs on Kazakh (6 tasks, HF leaderboard)

**Blurb:**

There is no standard way to measure LLM performance on Kazakh (13M speakers, agglutinative Turkic
language). KazBench is the open benchmark I built to fix that.

It has three parts:

1. An evaluation suite: 6 tasks (knowledge MC, reading comprehension, grammar/morphology,
   sentiment, KK→EN/RU translation with chrF, and instruction following with an LLM-judge rubric).

2. A model-agnostic harness: plug any model behind generate(prompt) — Claude, OpenAI-compatible,
   or local HF. Run end-to-end in two commands.

3. A public leaderboard (Hugging Face Space): decentralized submission — you run eval on your
   own compute, submit results + PR, maintainers verify on a private TEST split.

Data status: v0.1 ships ~15–20 seed items/task. The harness is complete. Expanding to 100+
validated items/task is the next phase — especially looking for native Kazakh speakers to review
and author items.

MIT (code) / CC BY 4.0 (data). All design decisions (public DEV + private TEST split, chrF
over BLEU, LLM-judge for instruction following) are documented in CONTRIBUTING.md.

Feedback welcome, especially on evaluation methodology and task design.

---

## r/MachineLearning Post

**Title:**
[Project] KazBench: an open evaluation benchmark for LLMs on Kazakh (low-resource, agglutinative Turkic language)

**Body:**

**tl;dr:** I built KazBench — 6-task evaluation suite + model-agnostic harness + public HF
leaderboard for measuring LLM performance on Kazakh. v0.1 is live; looking for collaborators,
especially native Kazakh speakers for data validation.

---

**Motivation**

Kazakh is a morphologically rich agglutinative Turkic language (~13M speakers, SOV word order,
14 grammatical cases). Frontier LLMs claim multilingual support, but there is no standard
reproducible benchmark to verify this for Kazakh. Teams building KZ-language applications
currently cannot compare models with numbers.

**What I built**

Six tasks:

| Task | Metric | Why |
|---|---|---|
| Knowledge MC | Accuracy | Factual probe, MC format |
| Reading Comprehension | Accuracy | Passage understanding |
| Grammar / Morphology | Accuracy | Specifically targets agglutinative morphology and case system |
| Sentiment | Accuracy | 3-class: оң / теріс / бейтарап |
| Translation (KK→EN, KK→RU) | chrF | Better than BLEU for morphologically rich languages |
| Instruction Following | LLM-judge (0–1) | Rubric-based; judge runs in the same harness |

Overall = macro-average across all 6 tasks, all normalized to 0–100.

**Design decisions worth discussing:**

- **Public DEV + private TEST**: prevents data contamination. Submitters run on DEV; maintainers
  re-verify on the private TEST set before official leaderboard placement.
- **Decentralized submission**: submitters pay their own API costs. This scales without budget.
- **chrF for translation**: handles character n-gram overlap better than BLEU for agglutinative
  surface forms.
- **LLM-judge for instruction following**: rubrics are written in English with explicit 0/0.5/1
  scoring criteria, reducing ambiguity.
- **2-native-reviewer validation**: no item is marked validated:true until two native Kazakh
  speakers (independent) approve it.

**Data status**

v0.1 ships ~15–20 seed items per task. All are `validated: false`. The harness runs end-to-end
on this seed set, but the data is not yet suitable for headline model comparisons. The benchmark
is infrastructure; the data expansion phase is now.

**Looking for:**

- Native Kazakh speakers willing to review or author items
- Feedback on task selection (anything obviously missing?)
- Feedback on the instruction-following rubric format
- Anyone who has evaluated LLMs on other Turkic languages (UZ, KG, TR) — interested in
  cross-language evaluation design comparison

GitHub: https://github.com/Yersultan04/kazbench
