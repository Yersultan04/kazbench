# Dataset Card for KazBench

**Draft v0.1 — Not yet published on Hugging Face. Placeholder for HF Dataset repository.**

---

## Dataset Summary

KazBench is an open, multi-task evaluation benchmark for assessing large language models (LLMs) on the Kazakh language. It covers six task categories: factual knowledge (multiple choice), reading comprehension (multiple choice), grammatical and morphological knowledge (multiple choice), sentiment classification, translation (KK→EN and KK→RU), and open-ended instruction following. The benchmark is designed for zero-shot and few-shot evaluation; it is not intended for fine-tuning.

KazBench provides a public DEV split for local development and a private TEST split whose scores constitute the official leaderboard entries. See the [GitHub repository](https://github.com/[ORG]/kazbench) for the evaluation harness and submission protocol.

**Current status: v0.1 seed data — small, unvalidated, not suitable for headline capability claims.**

---

## Dataset Details

### Dataset Description

- **Languages:** Kazakh (`kk`) — Cyrillic script (primary); target languages for translation task: English (`en`), Russian (`ru`)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Version:** 0.1.0 (seed)
- **Created:** June 2026
- **Curated by:** [AUTHOR/ORG TBD]
- **Funded by:** [FUNDING SOURCE TBD — or "self-funded / community effort"]
- **Repository:** https://github.com/[ORG]/kazbench
- **Leaderboard:** https://huggingface.co/spaces/[ORG]/kazbench-leaderboard

### Dataset Sources

The v0.1 seed data was generated with AI assistance to bootstrap the harness infrastructure. It has not been reviewed by native Kazakh speakers. Future data will be sourced from:

- Native-authored items written by fluent Kazakh speakers
- Publicly available Kazakhstani standardized exam materials (ҰБТ/UNT) with provenance labeling
- Community contributions via GitHub PR with two-native-reviewer validation

All items include a `source` field (`seed` | `native` | `exam` | `community`) and a `validated` boolean.

---

## Uses

### Direct Use

KazBench is intended for **evaluating LLMs on Kazakh-language understanding and generation**. Canonical use:

```bash
python -m harness.run_eval --model claude --model-id claude-haiku-4-5-20251001 --split dev --out results/claude-haiku.json
```

### Out-of-Scope Use

- **Fine-tuning on the test set** — the TEST split is private and must not be used for training. Fine-tuning on the DEV split and then reporting DEV scores as a model capability claim is considered dishonest practice and violates the spirit of the benchmark.
- **As a gold-standard capability measure (v0.1 only)** — the seed data is too small and unvalidated for reliable model ranking. Do not cite v0.1 seed scores in papers or product comparisons.
- **Content generation for production systems** — KazBench items are evaluation items, not templates for downstream text generation.

---

## Dataset Structure

### Data Fields (all tasks)

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique item identifier, format `<taskprefix>_<6digits>` (e.g., `kmc_000001`) |
| `task` | string | Task name — one of the six canonical task names |
| `source` | string | Provenance label: `seed`, `native`, `exam`, or `community` |
| `validated` | boolean | `true` if reviewed and approved by two native speakers; `false` otherwise |
| `canary` | string (optional) | Anti-contamination marker string; present on one item per task file |

### Per-Task Fields

#### knowledge_mc
| Field | Type |
|---|---|
| `question` | string — question text in Kazakh |
| `choices` | list[string] — four answer options in Kazakh |
| `answer` | int — 0-based index of the correct choice |

#### reading_comprehension
| Field | Type |
|---|---|
| `passage` | string — short text in Kazakh |
| `question` | string — comprehension question in Kazakh |
| `choices` | list[string] — four answer options in Kazakh |
| `answer` | int — 0-based index of the correct choice |

#### grammar_morphology
| Field | Type |
|---|---|
| `question` | string — grammatical question in Kazakh |
| `choices` | list[string] — four answer options |
| `answer` | int — 0-based index of the correct choice |

#### sentiment
| Field | Type |
|---|---|
| `text` | string — short Kazakh text to classify |
| `label` | string — one of `оң` (positive), `теріс` (negative), `бейтарап` (neutral) |

#### translation
| Field | Type |
|---|---|
| `source_lang` | string — always `kk` |
| `target_lang` | string — `en` or `ru` |
| `source_text` | string — Kazakh source sentence |
| `reference` | string — human reference translation in target language |

#### instruction_following
| Field | Type |
|---|---|
| `instruction` | string — instruction in Kazakh |
| `rubric` | string — scoring rubric for the LLM judge (1.0 / 0.5 / 0.0 scale) |

### Data Splits

| Split | Access | Purpose |
|---|---|---|
| `dev` | Public (HF Datasets + GitHub) | Development, local evaluation, prompt tuning |
| `test` | Private (maintainers only) | Official leaderboard verification |

The TEST split follows the identical schema as DEV. It is never committed to the public repository.

### Dataset Size (v0.1 seed)

| Task | DEV items | Validated | Split balance |
|---|---|---|---|
| knowledge_mc | 18 | 0 (0%) | 1 canary item |
| reading_comprehension | 16 | 0 (0%) | 1 canary item |
| grammar_morphology | 16 | 0 (0%) | 1 canary item |
| sentiment | 18 | 0 (0%) | 1 canary item |
| translation | 18 | 0 (0%) | ~9 KK→EN, ~9 KK→RU; 1 canary item |
| instruction_following | 16 | 0 (0%) | 1 canary item |
| **Total** | **102** | **0** | — |

**Target after v1 validation:** 100+ validated items per task, split approximately 50/50 between DEV and TEST.

---

## Dataset Creation

### Curation Rationale

Kazakh is a low-resource language for LLMs despite having approximately 13 million native speakers. No standardized, multi-task evaluation benchmark existed at the time of KazBench's creation. KazBench fills this gap to enable reproducible, comparable evaluation of LLMs on Kazakh across multiple capability dimensions.

### Source Data

**v0.1 seed:** AI-generated items designed to represent the intended task formats and difficulty levels. Language: Cyrillic Kazakh. Content domain: general knowledge, cultural facts, simple everyday scenarios.

**Future sources planned:**
- Native-authored items from fluent Kazakh speakers (recruited via community outreach)
- Kazakh standardized exam materials (ҰБТ/UNT) — publicly available items covering factual knowledge and reading comprehension; items derived from exams will be labeled `source: exam`
- Community contributions via the GitHub PR pipeline with two-reviewer validation

#### Who are the source data producers?

v0.1: AI system with human oversight (not reviewed by native speakers — acknowledged limitation).
Future: Native Kazakh speakers recruited from the community.

### Annotations

**Annotation process:**

For MC tasks (`knowledge_mc`, `reading_comprehension`, `grammar_morphology`): a single correct answer index is defined at item creation time.

For `sentiment`: a single gold label (оң / теріс / бейтарап) is assigned at item creation.

For `translation`: a single reference translation is provided. chrF allows partial credit via character n-gram overlap; a single reference is a known limitation.

For `instruction_following`: a natural-language rubric string specifies the scoring criteria (full/partial/zero compliance) for an LLM judge.

**Validation annotation:** Each item gets a binary `validated` flag set to `true` after two native-speaker reviewers approve it via the GitHub PR review process.

#### Who are the annotators?

v0.1: No human annotators — items are unvalidated seed data.
Target: Recruited native Kazakh speakers serving as reviewers.

### Personal and Sensitive Information

None. The dataset contains no personal information, no individually identifiable data, and no sensitive demographic information. All items use fictional names or generic scenarios.

---

## Bias, Risks, and Limitations

### Bias

- **Generator bias (v0.1):** Items were AI-generated and may reflect biases in the generating model's understanding of Kazakh language and culture, including potential inaccuracies in morphology or cultural references.
- **Script bias:** All items use Cyrillic Kazakh. Models trained predominantly on Latin-script Kazakh (post-reform) may be disadvantaged.
- **Domain imbalance:** v0.1 items are general-domain. Specialized domains (legal, medical, technical, administrative) are absent.
- **Answer-index skew (grammar_morphology):** In the v0.1 seed, the correct answer is at index 0 for all grammar items. This will be corrected during validation. This makes grammar_morphology dummy-baseline scores misleading.

### Risks

- **Contamination:** The DEV split is public and may appear in future model training corpora. The private TEST split mitigates this for leaderboard scores, but DEV scores are subject to contamination risk as the benchmark matures.
- **Score inflation from gaming:** A model fine-tuned on KazBench DEV items would achieve inflated scores. Submissions are expected to disclose training data usage.
- **Misrepresentation:** the dummy-baseline score (overall 22.97/100 on the v0.1.0 DEV split) must not be presented as a model capability estimate. It reflects harness plumbing and random guessing, not Kazakh language understanding.

### Limitations

- **Size:** 16–18 items per task is insufficient for reliable model differentiation. Statistical significance between models requires substantially more items.
- **Single reference translation:** Single-reference chrF underestimates translation quality when multiple valid translations exist.
- **LLM judge reliability:** The `instruction_following` scorer uses an LLM judge whose scores have not been validated against human judgments.
- **No difficulty tiers:** All v0.1 items are at approximately A1–B1 difficulty. Harder items for native-speaker-level capability are absent.
- **No spoken language evaluation:** KazBench evaluates text only; no audio/ASR tasks are included.
- **Code-switching not modeled:** Items are monolingual Kazakh; the Russian code-switching common in everyday Kazakh text is not explicitly tested.

---

## License

**Data license:** Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

Full license text: https://creativecommons.org/licenses/by/4.0/

**Code license (evaluation harness):** MIT License. See `LICENSE` in the GitHub repository.

---

## Citation

If you use KazBench in your research, please cite:

```bibtex
@misc{kazbench2026,
  title        = {{KazBench}: An Open Evaluation Benchmark for Large Language Models on the Kazakh Language},
  author       = {[AUTHOR LIST TBD]},
  year         = {2026},
  howpublished = {GitHub / Hugging Face Datasets},
  url          = {https://github.com/[ORG]/kazbench},
  note         = {v0.1 seed dataset — pending native-speaker validation}
}
```

*Note: citation details will be finalized upon paper publication.*

---

## Contact

For questions about the benchmark, data contributions, or leaderboard submissions, open an issue on the GitHub repository at https://github.com/[ORG]/kazbench.

For native-speaker validation contributions, see `CONTRIBUTING.md` in the repository.

---

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | June 2026 | Initial seed release — AI-generated items, harness functional, all items unvalidated |
| 1.0.0 | TBD | First validated release — 100+ items/task, native-speaker reviewed, real model baselines |
