# KazBench: An Open Evaluation Benchmark for Large Language Models on the Kazakh Language

**Draft v0.2 — Work in progress. Not for final submission.**

*Submitted to: [TARGET VENUE — e.g., Workshop on Low-Resource Languages at ACL/EMNLP 2026, or similar]*

Authors: [AUTHOR LIST TBD]
Affiliation: [AFFILIATION TBD]
Contact: [EMAIL TBD]

> **Published artifacts (2026-06-16):**
> Code + harness: https://github.com/Yersultan04/kazbench (MIT)
> Dataset (DEV split): https://huggingface.co/datasets/Yersultan03/kazbench (CC-BY-4.0)
> Live leaderboard: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

---

## Abstract

We introduce **KazBench**, an open benchmark for evaluating large language models (LLMs) on the Kazakh language — a Turkic language spoken by approximately 13 million people that remains severely under-represented in LLM evaluation literature. Despite growing community efforts in Kazakh NLP, no standardized, reproducible evaluation suite exists that enables direct, cross-model comparison across a broad set of language capabilities. KazBench fills this gap with six tasks covering factual knowledge, reading comprehension, morphological grammar, sentiment classification, translation (KK→EN and KK→RU), and open-ended instruction following. We release a model-agnostic evaluation harness, a public DEV split, a private TEST split for leaderboard integrity, and a decentralized submission protocol that scales without API costs to the project. A public leaderboard tracks model performance over time. The current DEV split (v0.1.0) contains **296 items** (~49–51 per task), all native-validated by a fluent Kazakh-speaking reviewer. We report baselines on two open-weight models served via Groq: `meta-llama/llama-4-scout-17b-16e-instruct` (overall **87.53/100**) and `llama-3.1-8b-instant` (overall **64.94/100**), plus a dummy floor of **22.97/100** for harness verification. All code, data, and the live leaderboard are publicly available (see artifact links above). We release all artifacts under MIT (code) and CC BY 4.0 (data) licenses.

---

## 1. Introduction

### 1.1 Kazakh as a Low-Resource Language for LLMs

Kazakh (ISO 639-1: `kk`) is a Turkic language with approximately 13 million native speakers, primarily in Kazakhstan, where it holds official state language status alongside Russian [CITE: official Kazakhstan language law]. Kazakh is agglutinative with complex inflectional morphology — nouns decline across seven grammatical cases and verbs encode tense, aspect, mood, person, and number through cascading suffixes — which makes it linguistically distant from the Indo-European languages that dominate LLM pre-training corpora.

The Common Crawl and other large web corpora contain Kazakh data, but its proportion is a small fraction of the total [CITE: Common Crawl language statistics]. Furthermore, Kazakh has historically used three scripts: Arabic (classical), Cyrillic (Soviet-era, still dominant), and a Latin-based script currently being adopted under a state transliteration reform [CITE: Kazakhstan Latin script policy 2017]. This script transition creates data fragmentation: the same word may appear in two or three orthographies in a single corpus, complicating tokenization and evaluation.

Beyond script complexity, Kazakh text in digital contexts is frequently mixed with Russian — a phenomenon often called Russian code-switching — reflecting Kazakhstan's bilingual society. Frontier LLMs trained on mixed Kazakh-Russian web data may conflate the two languages, producing outputs in Russian when prompted in Kazakh or failing to apply the correct grammatical rules for Kazakh morphology.

### 1.2 The Gap: No Standard Measurement

Despite growing interest in Kazakh NLP — evidenced by community datasets, translation corpora, and fine-tuned models — practitioners and researchers face a fundamental problem: **there is no agreed-upon, reproducible benchmark for answering "which LLM is best at Kazakh?"** Evaluations are conducted with ad hoc prompting, model-specific APIs, and non-comparable metrics. The result is that model selection for Kazakh-language applications is based on anecdote rather than evidence.

This gap has real costs. Government agencies exploring Kazakh-language AI tools [CITE: Kazakhstan digital transformation policy], educational technology developers, and language preservation initiatives have no objective basis for choosing between frontier models or fine-tuned alternatives. A standardized benchmark would create a common language for this comparison.

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

The evaluation of LLMs across languages has accelerated significantly since the introduction of multilingual benchmarks. MMLU [CITE: Hendrycks et al. 2021, Measuring Massive Multitask Language Understanding] established a widely used multiple-choice format for English knowledge; its multilingual extension MMLU-M and similar efforts [CITE: multilingual MMLU papers] extended coverage to dozens of languages, though low-resource and Central-Asian languages remain sparse or absent.

BIG-Bench [CITE: Srivastava et al. 2022] and its successors cover a broad set of NLP capabilities but focus predominantly on high-resource languages. HellaSwag [CITE], WinoGrande [CITE], and similar common-sense reasoning benchmarks have been translated into multiple languages [CITE], but Kazakh is not among the covered languages in most efforts.

For translation specifically, the WMT shared tasks [CITE: WMT annual proceedings] have included Kazakh in limited editions, providing BLEU-scored baselines for KK↔RU translation, but coverage is intermittent and the task format is narrower than a comprehensive language benchmark.

### 2.2 Turkic and Central-Asian NLP

Kazakh belongs to the Turkic language family alongside Turkish, Uzbek, Kyrgyz, Azerbaijani, and others. Turkish has received substantially more NLP attention due to its larger speaker population and digital footprint [CITE: Turkish NLP survey]. Several Turkish benchmarks exist [CITE: Turkish NLP benchmarks], but their design does not transfer directly to Kazakh given morphological differences.

Uzbek [CITE: Uzbek NLP efforts], Kyrgyz [CITE], and other Turkic languages have seen community dataset efforts, but comprehensive, multi-task evaluation benchmarks comparable to MMLU or BIG-Bench remain absent for most members of the family. To our knowledge, KazBench is the first publicly released multi-task evaluation benchmark specifically for Kazakh, though we acknowledge that concurrent or earlier efforts may exist that we are unaware of [CITE: check for KazNLP, KazNLU, or similar workshop proceedings at ACL/EMNLP/COLING].

### 2.3 Benchmark Design Principles

Our design draws on established principles from the benchmark construction literature. We adopt a public DEV / private TEST split strategy following [CITE: NLP benchmark contamination literature] to limit the risk of test data appearing in model training corpora. We use chrF [CITE: Popovic 2015] rather than BLEU for translation evaluation, motivated by its better sensitivity for morphologically rich languages [CITE: chrF comparative studies]. For open-ended generation, we use an LLM-as-judge approach [CITE: LLM-as-judge papers, e.g. Zheng et al. 2023 MT-Bench] with explicit rubric scoring (0/0.5/1.0), acknowledging its limitations (Section 8). The decentralized submission architecture is inspired by community leaderboards such as the Open LLM Leaderboard [CITE: HuggingFace Open LLM Leaderboard].

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

**What it measures.** Whether the model can correctly classify the sentiment of a Kazakh-language text as positive (оң), negative (теріс), or neutral (бейтарап). Sentiment corpora for Kazakh are sparse [CITE: Kazakh sentiment analysis literature], making model-level zero-shot performance informative.

**Format.** A short text (1–2 sentences) in Kazakh; the model must output one of the three sentiment labels.

**Metric.** Accuracy.

**Current size.** 51 items (v0.1.0 DEV split, native-validated); target 100+ items in v1.

**Label encoding.** Gold labels are stored in Cyrillic Kazakh (оң / теріс / бейтарап); the harness normalizes model outputs from both Cyrillic and transliterated forms.

#### Task 5: translation — Translation (KK→EN and KK→RU)

**What it measures.** The quality of the model's translation from Kazakh to English and from Kazakh to Russian, covering both a high-resource (EN) and a regionally important (RU) target language.

**Format.** A Kazakh source sentence and a reference translation in the target language; the model produces a hypothesis translation.

**Metric.** chrF [CITE: Popovic 2015], computed at the sentence level and averaged. chrF is preferred over BLEU for Kazakh because Kazakh's morphological richness causes BLEU's n-gram precision to undercount near-correct translations that differ only in suffix forms.

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
| `exam` | Derived from publicly available Kazakhstani school or UNT/ҰБТ examination materials [CITE: UNT exam source] |
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

We report results for three systems on the fully native-validated DEV split (296 items): two open-weight models served via a Groq-hosted OpenAI-compatible endpoint and an offline dummy baseline for harness verification. Results for `qwen3-32b` and `llama-3.3-70b-versatile` are pending (free-tier token limits); they will be added in a subsequent update.

**DEV leaderboard (v0.1.0):**

| Rank | Model | Overall | KMC (acc%) | RC (acc%) | GM (acc%) | Sent (acc%) | Trans (chrF) | IF (judge%) |
|---|---|---|---|---|---|---|---|---|
| 1 | meta-llama/llama-4-scout-17b-16e-instruct | **87.53** | 96.0 | 87.5 | 87.5 | 100.0 | 92.12 | 62.04 |
| 2 | llama-3.1-8b-instant | **64.94** | 72.0 | 95.83 | 77.08 | 60.78 | 26.41 | 57.55 |
| 3 | dummy (floor) | **22.97** | — | — | — | — | — | — |

*KMC = knowledge_mc, RC = reading_comprehension, GM = grammar_morphology, Sent = sentiment, Trans = translation, IF = instruction_following.*

The benchmark discriminates clearly across capability levels (Scout 87.53 vs. Llama-8B 64.94 vs. dummy floor 22.97). Key observations:

- **Translation is the sharpest discriminator.** chrF 92.12 vs. 26.41 — a ~3.5× gap — shows that translation quality scales strongly with model size and multilingual training.
- **Instruction-following is hard for both.** Both models cluster around 57–62%, reflecting genuine difficulty in understanding and complying with instructions written in Kazakh.
- **Sentiment is a strength for Scout.** 100% accuracy on 51 items, compared to 60.78% for the smaller model.
- **Reading comprehension is a relative strength for Llama-8B** (95.83%), narrowly outperforming Scout (87.5%) — likely a prompt-sensitivity artifact at this item count.

### 6.1b Methodology validation: the evaluation caught its own bug

A multi-model **triage** pass (each model's per-item correctness compared against the gold answer) flagged a cluster of obviously-positive sentiment items that *every* model failed. Investigation traced this to a corrupted prompt template instructing models to answer the positive class with a nonsense token instead of "оң", which the parser then scored as wrong — silently depressing every model's sentiment score. After the one-line fix, the stronger model's sentiment rose from 66.7% to 100% and triage-flagged items fell from 22 to 1 (the remaining one a genuinely hard accusative-case morphology question, not a data error). We report this not as an embarrassment but as evidence that the protocol — adversarial cross-model triage with a native-speaker authority backstop — detects scoring errors *before* numbers are published.

Native-speaker validation of the seed (in progress) remains required before these numbers are treated as authoritative.

### 6.2 Dummy Baseline (Harness Verification Only)

The dummy adapter returns a fixed deterministic response per task type (index `"1"` for MC tasks, an empty string for generation tasks). This produces a harness-verification score, not a meaningful capability score. The overall dummy score on the v0.1.0 validated DEV split is **22.97/100**.

> Note: an earlier seed run produced a `grammar_morphology` dummy score of 100% — a data artifact caused by all correct answers sitting at index 0. Answer positions were subsequently randomized evenly across choices, eliminating the artifact. The dummy overall dropped from 25.79 (initial seed) to 22.97 (v0.1.0). Sentiment/translation near-zero reflects the dummy producing no real generation, not a model property.

**These scores should not appear in any comparison table or marketing material.** They exist solely to confirm that the harness runs without errors.

### 6.3 Planned Additional Baselines

We plan to run and report results for a broader set of models including:

- Frontier closed-source models with known multilingual support (GPT-4o, Claude, Gemini variants) [CITE: model technical reports]
- Open-source multilingual models with Turkic or Central-Asian language coverage [CITE: relevant model papers]
- Kazakh-specific fine-tuned models, if available [CITE: community Kazakh model efforts]

Results will be added to the public leaderboard (https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard) as they become available and reported in a subsequent version of this paper.

---

## 7. Limitations

### 7.1 Dataset Size

The v0.1.0 DEV split contains ~49–51 items per task (296 total), all native-validated. This is sufficient to discriminate strong from weak models (§6.1) but still too small for statistically tight per-task estimates: a few items can swing a 50-item accuracy by several percentage points, and we do not yet report confidence intervals. The target for v1 is 100 items per task. The private TEST split has not yet been populated; leaderboard scores are currently DEV-only and should be treated as indicative rather than definitive until TEST verification is in place.

### 7.2 Coverage of Additional Models

Only two real models have been evaluated to date. Frontier closed-source models (GPT-4o, Claude, Gemini) and larger open-weight models have not yet been run. The current leaderboard therefore does not represent the full range of model capability on Kazakh.

### 7.3 Prompt Script (resolved)

Early v0.1 harness prompts mixed Latin transliteration with Cyrillic, which was inconsistent with the Cyrillic DEV data. Prompts have since been rewritten to standard Cyrillic Kazakh, and an explicit per-task dispatch replaced fragile script-based keyword detection. The sentiment-prompt corruption described in §6.1b was a regression introduced during this rewrite and has been fixed.

### 7.4 Script Transition and Orthographic Variation

Kazakhstan is in the process of transitioning from Cyrillic to a Latin-based Kazakh script [CITE: Kazakhstan Latin reform]. KazBench v1 uses Cyrillic throughout. Models trained after significant adoption of Latin Kazakh may show degraded performance on Cyrillic inputs, or vice versa. Future versions should evaluate both scripts explicitly. The benchmark does not currently test cross-script robustness.

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

As of v0.1.0, the benchmark is fully operational: 296 native-validated items across six tasks, two open-weight model baselines (Scout 87.53, Llama-8B 64.94), and all artifacts publicly available at https://github.com/Yersultan04/kazbench and https://huggingface.co/datasets/Yersultan03/kazbench. The most critical near-term work is expanding each task to 100+ items, populating the private TEST split, and broadening model coverage to include frontier closed-source models. We invite the Kazakh NLP community to contribute items and submit model results via GitHub.

---

## References

> **Note to authors:** The references below are placeholder markers. Each [CITE] in the text must be replaced with a real citation before submission. Locations of [CITE] markers are documented in Section 10 (Citation Gap Summary) below.

[CITE-1] Kazakhstan official language law / Constitution of the Republic of Kazakhstan, language provisions.

[CITE-2] Common Crawl language distribution statistics — see Common Crawl Foundation reports or analysis papers such as [analysis of CC-100 or mC4 language fractions].

[CITE-3] Kazakhstan Latin script transition policy — Presidential Decree on Latin alphabet adoption, 2017, and subsequent updates.

[CITE-4] Hendrycks, D. et al. (2021). Measuring Massive Multitask Language Understanding. ICLR 2021.

[CITE-5] Multilingual MMLU variants — e.g. MMMLU, or multilingual reasoning benchmarks at ACL/EMNLP.

[CITE-6] Srivastava, A. et al. (2022). Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-Bench). Transactions on Machine Learning Research.

[CITE-7] HellaSwag multilingual extensions — [relevant papers].

[CITE-8] WMT proceedings — Annual proceedings of the Conference on Machine Translation; relevant Kazakh-Russian language pair editions.

[CITE-9] Turkish NLP survey and benchmarks — [relevant papers on Turkish NLP, e.g. from ACL Anthology].

[CITE-10] Uzbek / Kyrgyz NLP efforts — [community datasets or workshop papers].

[CITE-11] Central Asian or Kazakh NLP workshop papers — KazNLP, KazNLU, or similar; search ACL Anthology for "Kazakh NLP".

[CITE-12] Benchmark contamination literature — papers on data contamination in LLM evaluation; e.g. Magar & Schwartz (2022), papers from ACL 2023–2024.

[CITE-13] Popovic, M. (2015). chrF: Character n-gram F-score for Automatic MT Evaluation. WMT 2015.

[CITE-14] chrF comparative studies for morphologically rich languages — [relevant MT evaluation papers].

[CITE-15] Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023.

[CITE-16] Hugging Face Open LLM Leaderboard — https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

[CITE-17] Kazakhstan digital transformation / AI policy — government digital strategy documents.

[CITE-18] UNT / ҰБТ exam materials — national standardized testing materials from National Testing Centre of Kazakhstan.

[CITE-19] Kazakh sentiment analysis prior work — [search for Kazakh sentiment datasets or classification papers].

[CITE-20] Frontier model technical reports — GPT-4 technical report (OpenAI 2023), Claude model cards (Anthropic), Gemini technical report (Google DeepMind 2023/2024).

[CITE-21] Kazakh-specific fine-tuned models — [community Hugging Face models for Kazakh; search kz-transformers or similar].

---

## 10. Citation Gap Summary (for Authors)

The following [CITE] markers require real citations before submission. Markers are grouped by section.

**Section 1 — Introduction:**
- Language status, speaker count, official recognition: [CITE-1]
- Common Crawl Kazakh data fraction: [CITE-2]
- Latin script reform policy: [CITE-3]
- Kazakhstan AI/digital transformation policy: [CITE-17]

**Section 2 — Related Work:**
- MMLU and multilingual MMLU: [CITE-4], [CITE-5]
- BIG-Bench: [CITE-6]
- HellaSwag multilingual: [CITE-7]
- WMT Kazakh-Russian: [CITE-8]
- Turkish NLP: [CITE-9]
- Uzbek/Kyrgyz NLP: [CITE-10]
- Concurrent Kazakh NLP benchmarks (check ACL Anthology): [CITE-11]
- Contamination literature: [CITE-12]
- chrF paper: [CITE-13]
- chrF vs BLEU for morphologically rich languages: [CITE-14]
- LLM-as-judge (MT-Bench): [CITE-15]
- HF Open LLM Leaderboard: [CITE-16]

**Section 4 — Data:**
- UNT/ҰБТ exam source (if exam-mined items added): [CITE-18]
- Kazakh sentiment analysis prior work: [CITE-19]

**Section 6 — Baselines:**
- Frontier model technical reports (when real runs added): [CITE-20]
- Kazakh fine-tuned model citations (when relevant models added): [CITE-21]

**Action items before submission:**
1. Conduct a thorough ACL Anthology search for "Kazakh" + "benchmark", "Kazakh" + "evaluation", "Kazakh" + "NLP dataset" to check for concurrent or prior work and cite appropriately.
2. Verify that no Kazakh-specific multi-task benchmark was published between 2023 and submission date that would weaken the novelty claim.
3. Confirm the correct citation for chrF (Popovic 2015 is standard but check for the most-cited version).
4. Add HF dataset card URL and GitHub repository URL once published.
5. Replace all [AUTHOR LIST TBD] and [AFFILIATION TBD] fields.
