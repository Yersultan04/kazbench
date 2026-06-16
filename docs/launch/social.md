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

So I built one — and it is live with real results.

Introducing KazBench: 6 tasks, model-agnostic harness, live leaderboard on HF Space.

Thread.

---

**Tweet 2 — The problem in one line**

Kazakh is agglutinative, morphologically rich, and low-resource. Frontier models claim multilingual
support. Nobody has measured whether that claim holds for Kazakh — with a reproducible evaluation
suite, not vibes.

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

Overall = macro-avg across all 6, scaled 0–100. 296 native-validated items.

---

**Tweet 4 — First leaderboard results**

Current standings (live at huggingface.co/spaces/Yersultan03/kazbench-leaderboard):

Llama-4-Scout: 87.53
Llama-3.1-8B:  64.94
Dummy floor:   22.97

Translation is where the biggest gap opens up — chrF 92 vs 26 between best and worst.
That is the task that exposes whether a model actually handles agglutinative morphology.

---

**Tweet 5 — Design choices that make it trustworthy**

- Public DEV + private TEST split (prevents contamination)
- Decentralized submission: you run eval on your own budget, submit results + PR
- chrF for translation (better for morphologically rich surface forms than BLEU)
- 296 items, all native-validated by two independent Kazakh speakers

---

**Tweet 6 — How to run it (2 commands)**

```bash
pip install -r requirements.txt
python -m harness.run_eval --model dummy --split dev --out results/dummy.json

# Real model:
python -m harness.run_eval --model openai --model-id your-model-id \
  --out results/your-model.json
```

Plug in any OpenAI-compatible API or local HF model behind generate(prompt). Then open a PR.

---

**Tweet 7 — CTA**

GitHub: https://github.com/Yersultan04/kazbench
HF Dataset: https://huggingface.co/datasets/Yersultan03/kazbench
Live Leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

Run your model. Submit a PR. Get on the board.

Рахмет.

---

## LinkedIn Post

(Professional framing. Doubles as a personal-brand signal for an ML/NLP engineer.)

---

**Headline:** I built an open benchmark for Kazakh-language LLMs — here are the first real results.

---

Kazakh is spoken by 13 million people. It is the official state language of Kazakhstan. It is
morphologically complex — agglutinative, with rich case suffixes that break naive tokenizers.

Until now, there was no standard, reproducible benchmark for measuring how well LLMs actually
handle it.

KazBench is live to fix that. Here is what we know so far.

**What KazBench is:**

An open evaluation suite (6 tasks), a model-agnostic eval harness, and a live public leaderboard
on Hugging Face Space. Anyone can run a model evaluation locally in under two minutes and submit
results via pull request. The private TEST split is held by maintainers to prevent data
contamination and keep scores honest.

**The 6 tasks:**
Knowledge MC, Reading Comprehension, Grammar/Morphology, Sentiment, KK→EN+RU Translation (chrF),
and Instruction Following (LLM-judge rubric). 296 native-validated items across all tasks.

**First leaderboard results:**

Llama-4-Scout leads at 87.53 overall. Llama-3.1-8B sits at 64.94. The dummy floor is 22.97.
Translation is the most discriminating task — the gap between top and bottom is chrF 92 vs 26.
That spread makes sense: agglutinative morphology punishes models that rely on surface-level
token matching.

**What I built it with:**
Python, the Hugging Face ecosystem, Gradio for the leaderboard UI, and a CI pipeline with GitHub
Actions for schema validation and smoke tests. The evaluation harness is model-agnostic — Claude,
OpenAI-compatible APIs, and local models all plug in via a single generate(prompt) interface.

**Why I built it:**
Partly because Kazakh deserves better AI coverage. Partly because benchmark design, evaluation
methodology, and low-resource NLP are exactly the intersection I want to work in — and building
real infrastructure is better evidence of that than writing about it.

If you work in NLP, low-resource languages, or LLM evaluation, I would welcome feedback on the
methodology — especially the instruction-following rubric design and the anti-contamination
approach.

GitHub: https://github.com/Yersultan04/kazbench
Live Leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

#NLP #LLM #MachineLearning #KazakhAI #OpenSource #LowResourceNLP #BenchmarkEvaluation

---

## Русский пост (KZ-аудитория — Telegram, LinkedIn KZ)

Запустил KazBench — первый открытый бенчмарк для оценки языковых моделей на казахском.

6 задач: фактические знания, понимание текста, морфология, тональность, перевод KK→EN/RU,
следование инструкциям. 296 пунктов с нативной валидацией.

Первые результаты уже на лидерборде:
- Llama-4-Scout — 87.53 (лидер)
- Llama-3.1-8B — 64.94
- Перевод — самый показательный таск: разрыв chrF 92 против 26

Хочешь проверить свою модель — два клика и PR.

GitHub: https://github.com/Yersultan04/kazbench
Лидерборд: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

---

## Show HN

**Title:**
Show HN: KazBench – open benchmark for evaluating LLMs on Kazakh (296 items, live leaderboard)

**Blurb:**

There is no standard way to measure LLM performance on Kazakh (13M speakers, agglutinative Turkic
language). KazBench is the open benchmark I built to fix that.

It has three parts:

1. An evaluation suite: 6 tasks (knowledge MC, reading comprehension, grammar/morphology,
   sentiment, KK→EN/RU translation with chrF, and instruction following with an LLM-judge rubric).
   296 native-validated items.

2. A model-agnostic harness: plug any model behind generate(prompt) — Claude, OpenAI-compatible,
   or local HF. Run end-to-end in two commands.

3. A live public leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard
   Decentralized submission — you run eval on your own compute, submit results + PR, maintainers
   verify on a private TEST split.

First results: Llama-4-Scout 87.53, Llama-3.1-8B 64.94, dummy floor 22.97. Translation shows the
largest inter-model variance (chrF 92 vs 26).

MIT (code) / CC BY 4.0 (data). All design decisions (public DEV + private TEST split, chrF
over BLEU, LLM-judge for instruction following) are documented in CONTRIBUTING.md.

Dataset: https://huggingface.co/datasets/Yersultan03/kazbench
GitHub: https://github.com/Yersultan04/kazbench

Feedback welcome, especially on evaluation methodology and task design.

---

## r/MachineLearning Post

**Title:**
[Project] KazBench: open evaluation benchmark for LLMs on Kazakh — first results in (Llama-4-Scout 87.53, Llama-3.1-8B 64.94)

**Body:**

**tl;dr:** KazBench is a 6-task evaluation suite + model-agnostic harness + live public HF
leaderboard for Kazakh. 296 native-validated items. First real model results are on the board.
Run your model and submit a PR.

---

**Motivation**

Kazakh is a morphologically rich agglutinative Turkic language (~13M speakers, SOV word order,
14 grammatical cases). Frontier LLMs claim multilingual support, but there has been no standard
reproducible benchmark to verify this for Kazakh.

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

Overall = macro-average across all 6 tasks, all normalized to 0–100. 296 native-validated items
(DEV split public, TEST split private for anti-contamination).

**First leaderboard results**

| Model | Overall |
|---|---|
| Llama-4-Scout | 87.53 |
| Llama-3.1-8B | 64.94 |
| Dummy baseline | 22.97 |

Translation is the most discriminating task — chrF spread of 92 vs 26 between best and worst.
This is where agglutinative morphology bites hardest.

Live leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

**Design decisions worth discussing:**

- **Public DEV + private TEST**: prevents data contamination. Submitters run on DEV; maintainers
  re-verify on the private TEST set before official leaderboard placement.
- **Decentralized submission**: submitters pay their own API costs. Scales without project budget.
- **chrF for translation**: handles character n-gram overlap better than BLEU for agglutinative
  surface forms.
- **LLM-judge for instruction following**: rubrics are written in English with explicit 0/0.5/1
  scoring criteria, reducing ambiguity.
- **2-native-reviewer validation**: no item is marked validated:true until two independent native
  Kazakh speakers approve it.

**Links**

GitHub: https://github.com/Yersultan04/kazbench
HF Dataset: https://huggingface.co/datasets/Yersultan03/kazbench
Live Leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard
