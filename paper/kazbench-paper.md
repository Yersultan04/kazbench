# KazBench: An Open Evaluation Benchmark for Large Language Models on the Kazakh Language

**Draft v0.2 — Work in progress. Not for final submission.**

*Target venue (candidates, see end of paper): SIGTURK 2026 (Workshop on Turkic Languages and Resources, co-located with ACL/EMNLP) · Workshop on NLP for Low-Resource / Multilingual Languages at ACL or EMNLP 2026 · LoResMT (Workshop on Technologies for MT of Low-Resource Languages). Deadlines [verify deadline].*

Authors: Yersultan Akhmer
Affiliation: [AFFILIATION TBD]
Contact: yerassyl.akhmer@gmail.com

> **Published artifacts (2026-06-16):**
> Code + harness: https://github.com/Yersultan04/kazbench (MIT)
> Dataset (DEV split): https://huggingface.co/datasets/Yersultan03/kazbench (CC-BY-4.0)
> Live leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

---

## Abstract

We introduce **KazBench**, an open benchmark for evaluating large language models (LLMs) on the Kazakh language — a Turkic language spoken by approximately 13 million people that remains severely under-represented in LLM evaluation literature. Despite growing community efforts in Kazakh NLP, no standardized, reproducible evaluation suite exists that enables direct, cross-model comparison across a broad set of language capabilities. KazBench fills this gap with six tasks covering factual knowledge, reading comprehension, morphological grammar, sentiment classification, translation (KK→EN and KK→RU), and open-ended instruction following. We release a model-agnostic evaluation harness, a public DEV split, a private TEST split for leaderboard integrity, and a decentralized submission protocol that scales without API costs to the project. A public leaderboard tracks model performance over time. The current DEV split (v0.1.0) contains **296 items** (~49–51 per task), all native-validated by a fluent Kazakh-speaking reviewer. We report baselines on six models spanning frontier closed-source and open-weight: `anthropic/claude-3.5-haiku` (**91.50/100**), `openai/gpt-4o-mini` (**88.30/100**), `meta-llama/llama-4-scout-17b-16e-instruct` (**87.53/100**), `google/gemini-2.5-flash` (**84.15/100**), `qwen/qwen-2.5-72b-instruct` (**74.54/100**), and `llama-3.1-8b-instant` (**64.94/100**), plus a dummy floor of **22.97/100** for harness verification. All code, data, and the live leaderboard are publicly available (see artifact links above). We release all artifacts under MIT (code) and CC BY 4.0 (data) licenses.

---

## 1. Introduction

### 1.1 Kazakh as a Low-Resource Language for LLMs

Kazakh (ISO 639-1: `kk`) is a Turkic language with approximately 13 million native speakers, primarily in Kazakhstan, where it holds official state language status alongside Russian (Constitution of the Republic of Kazakhstan, Art. 7) [1]. Kazakh is agglutinative with complex inflectional morphology — nouns decline across seven grammatical cases and verbs encode tense, aspect, mood, person, and number through cascading suffixes — which makes it linguistically distant from the Indo-European languages that dominate LLM pre-training corpora.

The Common Crawl and other large web corpora contain Kazakh data, but its proportion is a small fraction of the total [CITE-NEEDED: a citable figure for the Kazakh share of Common Crawl / CC-100 / mC4; verify against Conneau et al. 2020 (CC-100) or Xue et al. 2021 (mC4) per-language statistics before headline use]. Furthermore, Kazakh has historically used three scripts: Arabic (classical), Cyrillic (Soviet-era, still dominant), and a Latin-based script currently being adopted under a state transliteration reform [2]. This script transition creates data fragmentation: the same word may appear in two or three orthographies in a single corpus, complicating tokenization and evaluation.

Beyond script complexity, Kazakh text in digital contexts is frequently mixed with Russian — a phenomenon often called Russian code-switching — reflecting Kazakhstan's bilingual society. Frontier LLMs trained on mixed Kazakh-Russian web data may conflate the two languages, producing outputs in Russian when prompted in Kazakh or failing to apply the correct grammatical rules for Kazakh morphology.

### 1.2 The Gap: No Standard Measurement

Despite growing interest in Kazakh NLP — evidenced by community datasets, translation corpora, and fine-tuned models — practitioners and researchers face a fundamental problem: **there is no agreed-upon, reproducible benchmark for answering "which LLM is best at Kazakh?"** Evaluations are conducted with ad hoc prompting, model-specific APIs, and non-comparable metrics. The result is that model selection for Kazakh-language applications is based on anecdote rather than evidence.

This gap has real costs. Government agencies exploring Kazakh-language AI tools [CITE-NEEDED: a citable Kazakhstan state AI / digital-transformation strategy document, e.g. the national "Digital Kazakhstan" programme or the 2024 AI development concept; locate official decree number before citing], educational technology developers, and language preservation initiatives have no objective basis for choosing between frontier models or fine-tuned alternatives. A standardized benchmark would create a common language for this comparison.

### 1.3 Contributions

This paper introduces KazBench and makes the following contributions:

1. **A benchmark suite** of six tasks covering the core capabilities required for Kazakh-language AI: factual knowledge, reading comprehension, morphological grammar, sentiment, translation, and instruction following (Section 4).

2. **A model-agnostic evaluation harness** that plugs any model (commercial API or local/HF model) into the same evaluation pipeline via a minimal `generate(prompt)` interface, with deterministic parsing and JSON-serialized results (Section 6).

3. **A public DEV + private TEST split design** with anti-contamination canaries that preserves leaderboard integrity while allowing open community participation (Section 5).

4. **A decentralized submission protocol** that scales to many models without per-submission API costs to the project maintainers (Section 6).

5. **A public leaderboard** hosted as a Hugging Face Space, regenerated from community-submitted results files verified on the private TEST set (Section 6).

6. **An open contribution pipeline** with a PR-based native-speaker review process for growing and validating the dataset over time (Section 5).

All artifacts — code, data, harness, leaderboard app — are released publicly. The repository is at https://github.com/Yersultan04/kazbench; the dataset is published on Hugging Face Datasets at https://huggingface.co/datasets/Yersultan03/kazbench; and the live leaderboard is at https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard.

---

## 2. Related Work

### 2.1 Multilingual and Low-Resource NLP Benchmarks

The evaluation of LLMs across languages has accelerated significantly since the introduction of multilingual benchmarks. MMLU [3] established a widely used multiple-choice format for English knowledge; multilingual extensions and translated variants [CITE-NEEDED: a specific multilingual-MMLU paper — e.g. OpenAI's MMMLU or a translated-MMLU effort at ACL/EMNLP; confirm exact title and venue before citing] extended coverage to dozens of languages, though low-resource and Central-Asian languages remain sparse or absent.

BIG-Bench [4] and its successors cover a broad set of NLP capabilities but focus predominantly on high-resource languages. Common-sense reasoning benchmarks such as HellaSwag [5] and WinoGrande [6] have been translated into multiple languages, and the multilingual reading-comprehension benchmark Belebele [7] covers Kazakh (kaz_Cyrl) among 122 languages — but Kazakh is absent from most such efforts.

For translation specifically, the WMT shared tasks [CITE-NEEDED: a specific WMT proceedings/findings paper for the year(s) that included the Kazakh-Russian or Kazakh-English news-translation pair, e.g. WMT19 findings; confirm exact edition before citing] have included Kazakh in limited editions, providing BLEU-scored baselines for KK↔RU translation, but coverage is intermittent and the task format is narrower than a comprehensive language benchmark.

### 2.2 Turkic and Central-Asian NLP

Kazakh belongs to the Turkic language family alongside Turkish, Uzbek, Kyrgyz, Azerbaijani, and others. Turkish has received substantially more NLP attention due to its larger speaker population and digital footprint [CITE-NEEDED: a Turkish NLP survey paper; confirm a canonical reference, e.g. a recent ACL Anthology survey, before citing]. Several Turkish benchmarks exist [CITE-NEEDED: a specific Turkish benchmark paper such as a Turkish MMLU/GLUE-style suite; verify title/venue before citing], but their design does not transfer directly to Kazakh given morphological differences.

Uzbek, Kyrgyz, and other Turkic languages have seen community dataset efforts [CITE-NEEDED: specific Uzbek and Kyrgyz NLP dataset/benchmark papers; locate in ACL Anthology before citing], but comprehensive, multi-task evaluation benchmarks comparable to MMLU or BIG-Bench remain absent for most members of the family. For Kazakh specifically, prior resources include KazMMLU, an MMLU-style multiple-choice benchmark over Kazakh and Russian state-exam content [8], KazQAD, an open-domain question-answering dataset built from real UNT/ЕНТ exams [9], the KazSAnDRA sentiment corpus [10], and the KazParC parallel corpus [11]. These are largely single-task; to our knowledge KazBench is the first publicly released *multi-task* evaluation benchmark specifically for Kazakh that ships a unified harness and live leaderboard, though we acknowledge that concurrent or earlier efforts may exist that we are unaware of.

### 2.3 Benchmark Design Principles

Our design draws on established principles from the benchmark construction literature. We adopt a public DEV / private TEST split strategy to limit the risk of test data appearing in model training corpora, a concern documented in the benchmark-contamination literature [CITE-NEEDED: a specific data-contamination paper, e.g. Magar & Schwartz 2022 or a 2023-2024 ACL contamination study; confirm exact reference before citing]. We use chrF [12] rather than BLEU [13] for translation evaluation, motivated by its better sensitivity for morphologically rich languages [CITE-NEEDED: a study comparing chrF vs BLEU on morphologically rich languages; verify a citable MT-evaluation paper before headline use]. For open-ended generation, we use an LLM-as-judge approach (MT-Bench / Chatbot Arena) [14] with explicit rubric scoring (0/0.5/1.0), acknowledging its limitations (Section 8). The decentralized submission architecture is inspired by community leaderboards such as the Hugging Face Open LLM Leaderboard [15].

---

## 3. The KazBench Benchmark

### 3.1 Design Principles

KazBench was designed around four principles:

**Breadth over depth (v1).** Rather than a deep single-capability evaluation, we prioritize coverage of the major language competencies needed for real applications: factual recall, text comprehension, grammatical knowledge, sentiment understanding, cross-lingual communication, and instruction following. Depth — larger item counts, harder difficulty tiers, domain specialization — is deferred to future versions.

**Native-language items.** Questions, passages, and instructions are written or validated in Kazakh. We do not translate English benchmark items, which can introduce cultural artifacts and unnatural language patterns. Items sourced from translated or exam materials are explicitly labeled with their provenance (see Section 4.2).

**Reproducibility above all.** Fixed prompts, deterministic answer parsers, versioned data, and JSON-serialized results ensure that any two runs of the same model on the same split produce identical scores. Randomness is explicitly excluded from the evaluation pipeline.

**Honest reporting.** The v0.1.0 DEV split is native-validated (all 296 items `validated: true`) but still modest in size (~49–51 items per task, target 100+). We report this explicitly throughout: scores on a set this size carry wide confidence intervals, and the private TEST split is not yet populated, so current numbers are indicative rather than definitive. Every item carries a `validated` flag so consumers can filter on review status.

### 3.2 Task Descriptions

KazBench v1 comprises six tasks, described below.

#### Task 1: knowledge_mc — Factual Knowledge (Multiple Choice)

**What it measures.** Whether the model has retained factual knowledge about Kazakhstan (geography, culture, history, language) and can apply it when prompted in Kazakh. This is a direct measure of Kazakh-language encyclopedic knowledge as stored in model weights.

**Format.** A question in Kazakh followed by four answer choices; the model must output the index (0–3) of the correct answer. Items range from elementary (national symbols, capital city) to moderately difficult (historical figures, geographic features).

**Metric.** Accuracy (fraction of items correctly answered).

**Current size.** 50 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Example (translated for readability):**
> Question: What is the national instrument of Kazakhstan?
> Choices: [Balalaika, Dombra, Sitar, Accordion]
> Answer: 1 (Dombra)

#### Task 2: reading_comprehension — Reading Comprehension (Multiple Choice)

**What it measures.** Whether the model can read a short Kazakh passage and answer a factual question about its content, requiring comprehension rather than world knowledge retrieval.

**Format.** A passage (1–3 sentences) followed by a question and four answer choices. All information needed to answer the question is contained in the passage.

**Metric.** Accuracy.

**Current size.** 48 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Note.** At v0.1, passages are short. Longer, more complex passages are planned for v1.1.

#### Task 3: grammar_morphology — Grammatical and Morphological Knowledge (Multiple Choice)

**What it measures.** Whether the model understands Kazakh agglutinative morphology: case suffixes (nominative, genitive, dative, accusative, locative, ablative), plural formation, part-of-speech identification, and verb tense conjugation. This is the task most specific to Kazakh's linguistic structure and most diagnostic of genuine Kazakh capability versus Russian fallback behavior.

**Format.** A grammatical question in Kazakh with four answer choices, testing suffix selection, word form identification, or syntactic category labeling.

**Metric.** Accuracy.

**Current size.** 48 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Why this task matters.** A model that generates fluent Russian when prompted in Kazakh will fail this task systematically, making it a strong discriminator between "understands Kazakh" and "understands a Kazakh-Russian mix."

#### Task 4: sentiment — Sentiment Classification

**What it measures.** Whether the model can correctly classify the sentiment of a Kazakh-language text as positive (оң), negative (теріс), or neutral (бейтарап). Sentiment corpora for Kazakh are sparse; the largest public resource is KazSAnDRA [10], making model-level zero-shot performance informative.

**Format.** A short text (1–2 sentences) in Kazakh; the model must output one of the three sentiment labels.

**Metric.** Accuracy.

**Current size.** 51 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Label encoding.** Gold labels are stored in Cyrillic Kazakh (оң / теріс / бейтарап); the harness normalizes model outputs from both Cyrillic and transliterated forms.

#### Task 5: translation — Translation (KK→EN and KK→RU)

**What it measures.** The quality of the model's translation from Kazakh to English and from Kazakh to Russian, covering both a high-resource (EN) and a regionally important (RU) target language.

**Format.** A Kazakh source sentence and a reference translation in the target language; the model produces a hypothesis translation.

**Metric.** chrF [12], computed at the sentence level and averaged. chrF is preferred over BLEU for Kazakh because Kazakh's morphological richness causes BLEU's n-gram precision to undercount near-correct translations that differ only in suffix forms.

**Current size.** 50 items (v0.1.0 DEV split, native-validated), split approximately equally between KK→EN and KK→RU; target 50+ items per direction in v1.

#### Task 6: instruction_following — Instruction Following

**What it measures.** Whether the model can follow explicit instructions written in Kazakh — e.g., "Write two sentences about your favorite fruit" or "List the days of the week in order." This tests output format compliance, language compliance (response must be in Kazakh unless instructed otherwise), and instruction comprehension simultaneously.

**Format.** An instruction string in Kazakh. The model generates a free-form response. An LLM judge evaluates the response against a rubric on a three-point scale: 1.0 (fully compliant), 0.5 (partially compliant), 0.0 (non-compliant or wrong language).

**Metric.** Mean judge score (0–1), normalized to 0–100 for the overall aggregate.

**Current size.** 49 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Judge reliability caveat.** LLM-as-judge evaluation introduces its own reliability concerns; see Section 8.

### 3.3 Overall Score

The KazBench overall score is a **macro-average** across all six tasks on a 0–100 scale. Accuracy and judge scores (native range [0,1]) are multiplied by 100. chrF (native range [0,100]) is used as-is. This puts all tasks on a common scale before averaging.

---

## 4. Data Collection and Validation

### 4.1 Provenance Taxonomy

Every item in KazBench carries a `source` field indicating its provenance:

| Source label | Description |
|---|---|
| `seed` | AI-assisted generation (v0.1 bootstrap); requires native-speaker validation before counting as official |
| `native` | Written directly by a fluent native Kazakh speaker |
| `exam` | Derived from publicly available Kazakhstani school or UNT/ҰБТ examination materials (e.g. the open kz-transformers Kazakh Unified National Testing MC dataset) [16] |
| `community` | Contributed via community PR, reviewed by two native speakers |

In v0.1.0, items were generated with AI assistance and then reviewed by a native Kazakh speaker via Google Sheet. All 296 items now carry `validated: true`. The native reviewer confirmed the correctness of all gold answers across all six tasks. Community contributors can continue expanding the item set via PR.

### 4.2 Native-Speaker Validation Protocol

Each item must pass a two-reviewer native-speaker validation gate before its `validated` field is set to `true`. The review checklist covers:

1. **Linguistic correctness** — Is the Kazakh grammatically correct and natural?
2. **Answer correctness** — Is the gold answer unambiguously correct?
3. **Cultural appropriateness** — Does the item avoid stereotypes or culturally insensitive framing?
4. **Difficulty calibration** — Is the item neither trivially easy nor unanswerable without external resources?
5. **Script consistency** — Is the item consistently in Cyrillic Kazakh (the current standard)?

Reviewers submit their assessments via GitHub PR review; items receiving two approvals are merged with `validated: true`. Disagreements are resolved by a third reviewer or a maintainer.

### 4.3 DEV / TEST Split Design

KazBench uses a public DEV split and a private TEST split:

- **Public DEV** — Released openly on Hugging Face Datasets. Used for local development, prompt engineering, and community evaluation. Scores on DEV are for development purposes only; they are not listed on the leaderboard.

- **Private TEST** — Held by project maintainers; never committed to the public repository. Leaderboard scores are official only when verified on TEST by a maintainer. The TEST split follows the identical schema as DEV.

The DEV/TEST ratio target for v1 is approximately 50/50 after validation. In v0.1, only the DEV split exists (the seed data).

This split design is motivated by contamination risk: benchmark data that appears in model training corpora inflates measured performance. By withholding the TEST split, we ensure that even if DEV items appear in future training runs, the leaderboard score remains informative.

### 4.4 Anti-Contamination Canaries

Each task file includes one canary item: a benchmark item with a unique `canary` string that a model trained on the benchmark data would reproduce verbatim. The canary strings follow the pattern `KAZBENCH-CANARY-<TASK>-<UUID>-do-not-train`. If a submission's generated outputs contain a canary string verbatim, the submission is flagged for contamination review and excluded from the leaderboard pending investigation.

Canary check is enforced in the CI pipeline via `tools/data/validate.py` and in the submission verification script `tools/verify_submission.py`.

### 4.5 Validation Status at Time of Writing (v0.1.0)

Native-speaker validation is complete for the full DEV split. A fluent Kazakh speaker reviewed all items via Google Sheet and confirmed the correctness of every gold answer across all six tasks.

| Task | Items in DEV | Validated | Canary present |
|---|---|---|---|
| knowledge_mc | 50 | 50 (100%) | Yes |
| reading_comprehension | 48 | 48 (100%) | Yes |
| grammar_morphology | 48 | 48 (100%) | Yes |
| sentiment | 51 | 51 (100%) | Yes |
| translation | 50 | 50 (100%) | Yes |
| instruction_following | 49 | 49 (100%) | Yes |
| **Total** | **296** | **296 (100%)** | — |

The primary open task for KazBench v1 is expanding each task to 100+ items and populating the private TEST split.

---

## 5. Evaluation Methodology

### 5.1 Model-Agnostic Harness

The KazBench harness (`harness/run_eval.py`) implements a single `generate(prompt: str) -> str` interface that any model adapter must satisfy. Three adapters ship with v0.1:

- **`dummy`** — Returns deterministic, empty-ish responses for each task type (offline, no API key required). Used to verify harness correctness and CI smoke tests.
- **`claude`** — Calls the Anthropic Messages API via `anthropic` Python client.
- **`openai`** — Calls any OpenAI-compatible endpoint (including local models via LM Studio, Ollama, or vLLM).

Adding a new model requires implementing a four-line subclass of `BaseModel`; no changes to the task runners, prompt builders, or scorers are required.

### 5.2 Prompt Design

Prompts are minimal and instruction-free beyond the task requirements. We deliberately avoid elaborate system prompts or chain-of-thought scaffolding in v1, so that scores reflect the model's native Kazakh capability rather than prompt engineering. Prompts are written in a phonemic Latin transliteration of Kazakh rather than pure Cyrillic in the current seed implementation — this is a known limitation to be corrected in v1 (see Section 8.2).

### 5.3 Decentralized Submission

The submission workflow is:

1. A submitter clones the repository, sets their API credentials, and runs: `python -m harness.run_eval --model <adapter> --model-id <id> --split dev --out results/<model>.json`
2. The submitter opens a PR adding their `results/<model>.json` to the repository.
3. A project maintainer runs `tools/verify_submission.py` using the private TEST split to verify the reported scores.
4. If verification passes within tolerance, the PR is merged and the leaderboard (Hugging Face Space) regenerates automatically.

This architecture means the project incurs zero inference cost per submission. It scales to arbitrarily many models and adapters. The trust model relies on the private TEST verification step to prevent score fabrication.

### 5.4 Leaderboard

The leaderboard is a Gradio app (`leaderboard/app.py`) hosted on Hugging Face Spaces. It reads all `results/*.json` files, computes per-task breakdowns, and renders a sorted table by overall score. The leaderboard marks each entry with the split used (`dev`/`test`) and a `verified` boolean, so users can distinguish self-reported DEV scores from maintainer-verified TEST scores.

---

## 6. Baseline Results

### 6.1 Baseline Results (DEV split, v0.1.0, native-validated)

We report results for seven systems on the fully native-validated DEV split (296 items): six real models spanning frontier closed-source and open-weight, plus an offline dummy baseline for harness verification. Models were served via OpenRouter (frontier) and Groq (open-weight) OpenAI-compatible endpoints. A Llama-70B-class baseline (e.g., `llama-3.3-70b-versatile`) remains pending due to free-tier token limits and will be added in a subsequent update.

**DEV leaderboard (v0.1.0):**

| Rank | Model | Overall | KMC (acc%) | RC (acc%) | GM (acc%) | Sent (acc%) | Trans (chrF) | IF (judge%) |
|---|---|---|---|---|---|---|---|---|
| 1 | anthropic/claude-3.5-haiku | **91.50** | 96.0 | 100.0 | 97.9 | 88.2 | 86.12 | 80.71 |
| 2 | openai/gpt-4o-mini | **88.30** | 96.0 | 100.0 | 91.7 | 96.1 | 92.27 | 53.78 |
| 3 | meta-llama/llama-4-scout-17b-16e-instruct | **87.53** | 96.0 | 87.5 | 87.5 | 100.0 | 92.12 | 62.04 |
| 4 | google/gemini-2.5-flash | **84.15** | 90.0 | 100.0 | 91.7 | 100.0 | 88.23 | 35.00 |
| 5 | qwen/qwen-2.5-72b-instruct | **74.54** | 88.0 | 97.9 | 75.0 | 84.3 | 79.84 | 22.14 |
| 6 | llama-3.1-8b-instant | **64.94** | 72.0 | 95.8 | 77.1 | 60.8 | 26.41 | 57.55 |
| — | dummy (floor) | **22.97** | 26.0 | 25.0 | 25.0 | 33.3 | 8.50 | 20.00 |

*KMC = knowledge_mc, RC = reading_comprehension, GM = grammar_morphology, Sent = sentiment, Trans = translation, IF = instruction_following.*

The benchmark discriminates clearly across the full range of evaluated models (claude-3.5-haiku 91.50 → llama-3.1-8b 64.94 → dummy floor 22.97). Key observations:

- **Frontier models lead overall.** claude-3.5-haiku (91.50) and gpt-4o-mini (88.30) top the leaderboard, with llama-4-scout (87.53) and gemini-2.5-flash (84.15) close behind. qwen-2.5-72b (74.54) and llama-3.1-8b (64.94) form a second tier.
- **Reading comprehension is saturated at the top.** Three of six models score 100.0% on RC (claude-3.5-haiku, gpt-4o-mini, gemini-2.5-flash), suggesting the current item set is too easy for frontier models; harder items are needed for v1.
- **Instruction-following has the widest spread.** IF scores range from 22.14 (qwen-2.5-72b) to 80.71 (claude-3.5-haiku), making it the most discriminative task at the top end. The earlier "cluster around 57–62%" observation was an artifact of evaluating only two open-weight models.
- **Translation (chrF) correlates with overall rank except for gpt-4o-mini.** The chrF range is 26.41 (llama-3.1-8b) to 92.27 (gpt-4o-mini); notably gpt-4o-mini achieves the highest chrF (92.27) despite ranking second overall, dragged down by its IF score (53.78).
- **Sentiment is easy for most frontier models.** gemini-2.5-flash and llama-4-scout both reach 100.0%; claude-3.5-haiku scores 88.2% and llama-3.1-8b 60.8%, the widest gap after IF.

### 6.1b Methodology validation: the evaluation caught its own bug

A multi-model **triage** pass (each model's per-item correctness compared against the gold answer) flagged a cluster of obviously-positive sentiment items that *every* model failed. Investigation traced this to a corrupted prompt template instructing models to answer the positive class with a nonsense token instead of "оң", which the parser then scored as wrong — silently depressing every model's sentiment score. After the one-line fix, the stronger model's sentiment rose from 66.7% to 100% and triage-flagged items fell from 22 to 1 (the remaining one a genuinely hard accusative-case morphology question, not a data error). We report this not as an embarrassment but as evidence that the protocol — adversarial cross-model triage with a native-speaker authority backstop — detects scoring errors *before* numbers are published.

Native-speaker validation of the seed (in progress) remains required before these numbers are treated as authoritative.

### 6.2 Dummy Baseline (Harness Verification Only)

The dummy adapter returns a fixed deterministic response per task type (index `"1"` for MC tasks, an empty string for generation tasks). This produces a harness-verification score, not a meaningful capability score. The overall dummy score on the v0.1.0 validated DEV split is **22.97/100**.

> Note: an earlier seed run produced a `grammar_morphology` dummy score of 100% — a data artifact caused by all correct answers sitting at index 0. Answer positions were subsequently randomized evenly across choices, eliminating the artifact. The dummy overall dropped from 25.79 (initial seed) to 22.97 (v0.1.0). Sentiment/translation near-zero reflects the dummy producing no real generation, not a model property.

**These scores should not appear in any comparison table or marketing material.** They exist solely to confirm that the harness runs without errors.

### 6.3 Planned Additional Baselines

The current baseline set covers frontier closed-source (claude-3.5-haiku, gpt-4o-mini, gemini-2.5-flash) and open-weight (llama-4-scout-17b, qwen-2.5-72b, llama-3.1-8b) models. Planned additions include:

- A Llama-70B-class model (e.g., `llama-3.3-70b-versatile`) pending free-tier token availability [CITE-NEEDED: technical report / model card for the specific Llama-70B-class model once it is run, e.g. the Llama 3 herd-of-models report; add when the baseline is added]
- Kazakh-specific fine-tuned models, if available [17]
- Re-runs on the expanded DEV split (100 validated items/task) once v1 data is complete

Results will be added to the public leaderboard (https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard) as they become available and reported in a subsequent version of this paper.

---

## 7. Limitations

### 7.1 Dataset Size

The v0.1.0 DEV split contains 48–51 items per task (50/48/48/51/50/49 for KMC/RC/GM/Sent/Trans/IF respectively; 296 total), all native-validated. This is sufficient to discriminate strong from weak models (§6.1) but still too small for statistically tight per-task estimates: a few items can swing a 50-item accuracy by several percentage points, and we do not yet report confidence intervals. The target for v1 is 100 items per task. The private TEST split has not yet been populated; leaderboard scores are currently DEV-only and should be treated as indicative rather than definitive until TEST verification is in place.

### 7.2 Coverage of Additional Models

Six real models have been evaluated to date, including frontier closed-source models (claude-3.5-haiku, gpt-4o-mini, gemini-2.5-flash) and open-weight models (llama-4-scout-17b, qwen-2.5-72b, llama-3.1-8b). The leaderboard now spans a meaningful range of capability. The primary gap remaining is a Llama-70B-class baseline (e.g., `llama-3.3-70b-versatile`) and a full re-run once the DEV split is expanded to 100 items per task.

### 7.3 Prompt Script (resolved)

Early v0.1 harness prompts mixed Latin transliteration with Cyrillic, which was inconsistent with the Cyrillic DEV data. Prompts have since been rewritten to standard Cyrillic Kazakh, and an explicit per-task dispatch replaced fragile script-based keyword detection. The sentiment-prompt corruption described in §6.1b was a regression introduced during this rewrite and has been fixed.

### 7.4 Script Transition and Orthographic Variation

Kazakhstan is in the process of transitioning from Cyrillic to a Latin-based Kazakh script [2]. KazBench v1 uses Cyrillic throughout. Models trained after significant adoption of Latin Kazakh may show degraded performance on Cyrillic inputs, or vice versa. Future versions should evaluate both scripts explicitly. The benchmark does not currently test cross-script robustness.

### 7.5 Russian Code-Switching

A model that generates Russian when prompted in Kazakh will score near zero on `grammar_morphology` and `instruction_following` but may score artificially high on `knowledge_mc` if Russian knowledge overlaps with Kazakh factual knowledge. The benchmark currently does not explicitly penalize Russian outputs except via the rubric in `instruction_following`. A language-detection check on model outputs is planned as a diagnostic field in future result schemas.

### 7.6 LLM-Judge Reliability for instruction_following

The judge-based evaluation for `instruction_following` uses the same model adapter that is being evaluated, or an external LLM. This introduces at least two reliability concerns: (1) a judge model may exhibit in-group bias toward its own output style or training distribution; (2) rubric scoring (0/0.5/1.0) compresses the output space and may not capture nuanced partial compliance. We plan to add inter-rater reliability measurements between human evaluators and the LLM judge before treating instruction-following scores as definitive.

### 7.7 Domain Coverage

The v0.1 items are predominantly simple and general-domain. They do not cover legal, medical, technical, or formal administrative Kazakh — domains highly relevant to practical AI deployment in Kazakhstan. Domain-specific tasks are planned for v2.

### 7.8 Absence of Cross-Task Correlation Analysis

Due to the small seed size, we cannot yet analyze whether the six tasks measure independent dimensions of Kazakh competency or whether they collapse onto a single "overall Kazakh proficiency" factor. Confirmatory factor analysis is planned once validated data is available.

---

## 8. Ethics Statement

### 8.1 Language Preservation Framing

We frame KazBench explicitly as a **language preservation and development tool**. Standardized evaluation creates incentive for model developers to invest in Kazakh-language capability, which benefits the approximately 13 million Kazakh speakers globally. By making the benchmark fully open (CC BY 4.0 data, MIT code), we ensure that Kazakhstani institutions, universities, and independent developers can participate in improving AI for their language without gatekeeping by commercial entities.

### 8.2 No Personal Data

The KazBench dataset contains no personal information. Items are constructed from fictional scenarios, public-domain factual knowledge, and general linguistic structures. No individual is named, identified, or described in the benchmark data. No data was collected from human subjects.

### 8.3 Honest Reporting Commitment

We commit to:

- Marking any unvalidated data explicitly with `validated: false`; all current DEV items are `validated: true`.
- Disclosing all known harness artifacts and data biases in benchmark documentation (see §6.1b for the scoring bug we caught and fixed before publication).
- Maintaining the private TEST split's confidentiality even if data requests are received, to preserve leaderboard integrity.
- Updating this paper when additional model results are available, without cherry-picking favorable results.

### 8.4 Potential for Misuse

A benchmark can be "gamed" by fine-tuning directly on the DEV split. We mitigate this with the private TEST split and canary mechanism, but cannot prevent motivated contamination. We ask community members to adhere to fair-evaluation norms and to disclose any training on KazBench-adjacent data in their submissions.

### 8.5 Representativeness

The benchmark was designed by a non-native Kazakh speaker with AI-assisted generation and subsequently reviewed by a native Kazakh speaker who confirmed the correctness of all gold answers across all 296 items. Risks of grammatically unusual phrasing or subtle cultural misrepresentation remain; we consider the current validation a necessary first pass rather than a comprehensive two-reviewer audit. We invite additional native speakers to review and contribute items via the GitHub PR pipeline.

---

## 9. Conclusion

KazBench provides the first publicly available, multi-task, reproducible evaluation suite for assessing LLM performance on the Kazakh language. By releasing a model-agnostic harness, a native-validated DEV split, a live public leaderboard, and an open contribution pipeline, we aim to make KazBench community-maintained infrastructure rather than a one-time research artifact.

As of v0.1.0, the benchmark is fully operational: 296 native-validated items across six tasks, six model baselines spanning frontier and open-weight (claude-3.5-haiku 91.50 → llama-3.1-8b 64.94), and all artifacts publicly available at https://github.com/Yersultan04/kazbench and https://huggingface.co/datasets/Yersultan03/kazbench. The most critical near-term work is expanding each task to 100 validated items, populating the private TEST split, and adding a Llama-70B-class baseline. We invite the Kazakh NLP community to contribute items and submit model results via GitHub.

---

## References

> Citation style: ACL (numbered). Entries marked **[verify]** are believed correct from
> project research notes but should be confirmed against the canonical source before
> camera-ready. Entries still missing a reliable source appear as **[CITE-NEEDED]** in the
> text and are listed in Section 10.

[1] Constitution of the Republic of Kazakhstan. 1995 (with amendments). Article 7 (state and official languages). Official text: https://www.akorda.kz/en/official_documents/constitution **[verify exact article/clause and stable URL]**

[2] President of the Republic of Kazakhstan. 2017. Decree on the transition of the Kazakh alphabet from Cyrillic to Latin script (Presidential Decree No. 569, 26 October 2017), and subsequent revisions of the Latin alphabet (2018, 2021). **[verify decree number and dates]**

[3] Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt. 2021. Measuring Massive Multitask Language Understanding. In *International Conference on Learning Representations (ICLR)*. arXiv:2009.03300.

[4] Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao, et al. 2022. Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-Bench). *Transactions on Machine Learning Research (TMLR)*. arXiv:2206.04615.

[5] Rowan Zellers, Ari Holtzman, Yonatan Bisk, Ali Farhadi, and Yejin Choi. 2019. HellaSwag: Can a Machine Really Finish Your Sentence? In *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics (ACL)*. https://aclanthology.org/P19-1472/

[6] Keisuke Sakaguchi, Ronan Le Bras, Chandra Bhagavatula, and Yejin Choi. 2020. WinoGrande: An Adversarial Winograd Schema Challenge at Scale. In *Proceedings of the AAAI Conference on Artificial Intelligence*. arXiv:1907.10641.

[7] Lucas Bandarkar, Davis Liang, Benjamin Muller, Mikel Artetxe, Satya Narayan Shukla, Donald Husa, Naman Goyal, Abhinandan Krishnan, Luke Zettlemoyer, and Madian Khabsa. 2024. The Belebele Benchmark: A Parallel Reading Comprehension Dataset in 122 Language Variants. In *Proceedings of ACL 2024*. https://github.com/facebookresearch/belebele

[8] Mukhammed Togmanov, Nurdaulet Mukhituly, Diana Turmakhan, et al. 2025. KazMMLU: Measuring Massive Multitask Language Understanding in Kazakh and Russian. In *Proceedings of ACL 2025 (Long Papers)*. https://aclanthology.org/2025.acl-long.701/ · Dataset: https://huggingface.co/datasets/MBZUAI/KazMMLU **[verify full author list]**

[9] Rustem Yeshpanov, Pavel Efimov, Leonid Boytsov, Ardak Shalkarbayuli, and Pavel Braslavski. 2024. KazQAD: Kazakh Open-Domain Question Answering Dataset. In *Proceedings of the First Workshop on NLP for Turkic Languages (SIGTURK 2024)*. https://aclanthology.org/2024.sigturk-1.8.pdf · Data: https://huggingface.co/datasets/issai/kazqad **[verify author list / page]**

[10] Rustem Yeshpanov and Huseyin Atakan Varol. 2024. KazSAnDRA: Kazakh Sentiment Analysis Dataset of Reviews and Attitudes. Institute of Smart Systems and Artificial Intelligence (ISSAI), Nazarbayev University. Data: https://huggingface.co/datasets/issai/kazsandra · https://github.com/IS2AI/KazSAnDRA **[verify author list, venue/year]**

[11] Rustem Yeshpanov, Alina Polonskaya, and Huseyin Atakan Varol. 2024. KazParC: Kazakh Parallel Corpus for Machine Translation. Data: https://huggingface.co/datasets/issai/kazparc · https://github.com/IS2AI/KazParC **[verify author list, venue/year]**

[12] Maja Popović. 2015. chrF: Character n-gram F-score for Automatic MT Evaluation. In *Proceedings of the Tenth Workshop on Statistical Machine Translation (WMT)*, pages 392–395. https://aclanthology.org/W15-3049/

[13] Kishore Papineni, Salim Roukos, Todd Ward, and Wei-Jing Zhu. 2002. BLEU: a Method for Automatic Evaluation of Machine Translation. In *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL)*, pages 311–318. https://aclanthology.org/P02-1040/

[14] Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, and Ion Stoica. 2023. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. In *Advances in Neural Information Processing Systems (NeurIPS), Datasets and Benchmarks Track*. arXiv:2306.05685.

[15] Edward Beeching, Clémentine Fourrier, Nathan Habib, Sheon Han, Nathan Lambert, Nazneen Rajani, Omar Sanseviero, Lewis Tunstall, and Thomas Wolf. 2023. Open LLM Leaderboard. Hugging Face. https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard **[verify citation form / authorship]**

[16] kz-transformers. 2024. Kazakh Unified National Testing — Multiple Choice (real ЕНТ/ҰБТ exam questions, 7 subjects). Hugging Face Datasets (Apache-2.0). https://huggingface.co/datasets/kz-transformers/kazakh-unified-national-testing-mc **[verify maintainer/author attribution]**

[17] Community Kazakh model and dataset efforts on Hugging Face, including the kz-transformers and TilQazyna collections (e.g. kz-transformers/kk-socio-cultural-bench-mc, kazakh-dastur-mc, kazakh-constitution-mc; TilQazyna/til-kk-sentiment-v1). **[CITE-NEEDED: select and cite the specific fine-tuned Kazakh model(s) actually evaluated, with model card, once such baselines are added]**

---

## 10. Citation Gap Summary (for Authors)

Status: 13 of 21 original markers resolved with a real reference (canonical or
verified project source); 8 remain **[CITE-NEEDED]** in the text and must be filled
before submission. The list below tracks the outstanding ones.

**Remaining [CITE-NEEDED] (must resolve before camera-ready):**

1. **Common Crawl / web-corpus Kazakh fraction** (§1.1) — find a citable per-language statistic; candidates: Conneau et al. 2020 (CC-100) or Xue et al. 2021 (mC4) appendix tables.
2. **Kazakhstan AI / digital-transformation policy** (§1.2) — locate the official "Digital Kazakhstan" programme or the 2024 national AI development concept with decree number.
3. **Multilingual-MMLU variant** (§2.1) — pick one concrete paper (e.g. OpenAI MMMLU or a translated-MMLU effort) and confirm title/venue.
4. **WMT Kazakh edition** (§2.1) — cite the specific WMT findings paper for the year(s) that included KK↔RU/EN (likely WMT19).
5. **Turkish NLP survey** (§2.2) — confirm a canonical survey reference.
6. **Turkish benchmark suite** (§2.2) — confirm a specific Turkish MMLU/GLUE-style benchmark paper.
7. **Uzbek / Kyrgyz NLP datasets** (§2.2) — locate specific dataset/benchmark papers in ACL Anthology.
8. **Benchmark-contamination paper** (§2.3) — confirm Magar & Schwartz 2022 or an equivalent ACL 2023–2024 study.
9. **chrF vs BLEU for morphologically rich languages** (§2.3) — find a citable comparative MT-evaluation study.
10. **Llama-70B-class technical report** (§6.3) — add the model card/report when the baseline is actually run.
11. **Specific fine-tuned Kazakh model** ([17], §6.3) — cite the exact model evaluated, once added.

**Notes on verify-before-camera-ready items already given a reference:**
- Author lists for the ISSAI/MBZUAI Kazakh datasets ([8]–[11]) are reconstructed from project research notes — confirm against each paper/HF card.
- Legal/policy references ([1], [2]) need exact article numbers, decree numbers, and stable official URLs.
- Open LLM Leaderboard ([15]) — confirm the project's preferred citation form.

**Action items before submission:**
1. Resolve the 11 items above; replace each [CITE-NEEDED] inline.
2. Conduct a thorough ACL Anthology search for "Kazakh" + "benchmark"/"evaluation"/"dataset" to confirm the multi-task novelty claim and catch any concurrent work.
3. Confirm all **[verify]** author lists, venues, and URLs against canonical sources.
4. Fill `[AFFILIATION TBD]` in the header.
