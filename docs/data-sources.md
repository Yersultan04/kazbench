# KazBench — External Data Sources (research 2026-06-16)

Prioritized, license-checked sources for expanding KazBench with **human-authored**
items (closing the synthetic-data and ceiling risks). Compiled from a deep-research
pass (15 primary sources, 74 claims; 7 verified 3-0/2-1, rest source-backed but
verification cut short by a session limit — re-verify before headline use).

## TL;DR — what to take first

1. **KazSAnDRA** → `sentiment` (license CC-BY-4.0, drop-in compatible)
2. **KazNERD** → source text for `grammar_morphology` / item grounding (CC-BY-4.0)
3. **KazParC** → `translation` KK→EN/RU (largest parallel corpus; confirm license)
4. **ЕНТ/oltest.kz raw exams** → author fresh `knowledge_mc` items grounded in real
   exams (facts aren't copyrightable; sidesteps KazMMLU's NC license)
5. **Belebele (kaz_Cyrl)** / **KazQAD** → `reading_comprehension` (ShareAlike — cite or
   dual-license the derived subset)
6. **KazMMLU** → cite & compare in paper (NC license blocks redistribution)

## License compatibility map

| License | Sources | Can redistribute items in CC-BY-4.0 KazBench? |
|---|---|---|
| **CC-BY-4.0** (compatible) | KazNERD, KazSAnDRA*, Leipzig (CC-BY) | ✅ yes, attribution only |
| **CC-BY-SA-4.0** (ShareAlike) | KazQAD, Belebele* | ⚠️ only if derived subset is released CC-BY-SA, or cite + author fresh |
| **CC-BY-NC-4.0** (NonCommercial) | KazMMLU | ❌ cannot redistribute; cite/compare only, or use underlying public exams |

\* license reported by source page; re-confirm on the HF card before merging.

Three ways to "use" a source — pick by license:
- **Redistribute** items → needs CC-BY or more permissive.
- **Ground new items** → the underlying *facts / public exam questions* aren't
  copyrightable; we author fresh items grounded in them (works even for NC sources).
- **Cite / compare** in the paper → all sources, freely.

---

## 1. Exam materials (highest priority — human-authored, hard)

### KazMMLU — VERIFIED (3-0)
- **What:** MMLU-style MC benchmark in Kazakh + Russian, sourced from state exams
  (ЕНТ/ҰБТ) and professional certification via oltest.kz. 37 subjects (high school →
  university → professional). ACL 2025 paper reports ~23,000 MC (10,969 kk + 12,031 ru);
  frontier models (Llama3.1, Qwen-2.5, GPT-4, DeepSeek V3) **struggle** → ceiling problem is real.
- **Link:** https://huggingface.co/datasets/MBZUAI/KazMMLU · paper https://aclanthology.org/2025.acl-long.701/
- **License:** CC-BY-**NC**-4.0 → ❌ cannot redistribute in KazBench.
- **Use:** cite & compare in paper; author our own `knowledge_mc` from the same public
  ЕНТ/oltest.kz sources (not from KazMMLU's curated file).
- **Contamination:** public + on HF → likely in frontier training. Put any derived items in private TEST.

### KazQAD — VERIFIED (3-0)
- **What:** Kazakh open-domain QA; dev/test questions from the real UNT/ЕНТ exam.
  ~6,000 unique questions, ~12,000 passage relevance judgements, 800k+ kk Wikipedia passages.
  (Test split ~1,927–2,713 original exam questions across 6 subjects.)
- **Link:** https://github.com/IS2AI/KazQAD · https://huggingface.co/datasets/issai/kazqad · paper https://aclanthology.org/2024.sigturk-1.8.pdf
- **License:** CC-BY-**SA**-4.0 → ⚠️ ShareAlike.
- **Best for:** `reading_comprehension` (passage+Q) and `knowledge_mc`.
- **Contamination:** kk Wikipedia passages are in training corpora → private TEST.

### NIS Math (method) — source-backed
- **What:** SIGTURK'24 authors built a 100-item kk math MC set by parsing Nazarbayev
  Intellectual Schools entrance-test PDFs. A concrete, replicable recipe for harder items.
- **Link:** https://aclanthology.org/2024.sigturk-1.8.pdf
- **Use:** replicate the method on exam PDFs Yersultan can supply.

---

## 2. Open Kazakh NLP datasets

### KazSAnDRA — source-backed (best sentiment source)
- **What:** Largest Kazakh sentiment dataset — 180,064 real reviews across 4 domains
  (Appstore 135,073; Market 30,289; Mapping 8,897; Bookstore 5,805). Naturally occurring, non-synthetic.
- **Link:** https://github.com/IS2AI/KazSAnDRA · https://huggingface.co/datasets/issai/kazsandra
- **License:** reported CC-BY-4.0 → ✅ compatible (re-confirm on HF card).
- **Best for:** `sentiment`. Note: reviews are star-rated (polarity); map to оң/теріс/бейтарап.
- **Contamination:** low-moderate; sample recent/long-tail items for TEST.

### KazNERD — source-backed (CC-BY-4.0!)
- **What:** Kazakh NER — 112,702 sentences, 136,333 annotations, 25 entity classes.
- **Link:** https://github.com/IS2AI/KazNERD
- **License:** CC-BY-4.0 → ✅ directly compatible.
- **Best for:** real source sentences to ground `grammar_morphology` / reading items; or a future NER task.

### KazParC — VERIFIED (3-0)
- **What:** First & largest public parallel corpus KK/EN/RU/TR. ~371,902 human-translated
  lines (5 domains: mass media, general, legal, education/science, fiction) + ~1.8M synthetic.
- **Link:** https://huggingface.co/datasets/issai/kazparc · https://github.com/IS2AI/KazParC
- **License:** confirm on HF (issai datasets are often CC-BY-4.0).
- **Best for:** `translation` KK→EN and KK→RU — use the human-translated lines only.
- **Contamination:** large public corpus → sample for private TEST; prefer fiction/legal (less memorized).

---

## 3. Open-licensed text corpora (raw source text)

### Leipzig Corpora — Kazakh — source-backed
- **Link:** https://wortschatz.uni-leipzig.de/en/download/Kazakh
- **License:** CC-BY (attribution) → ✅ usable.
- **Use:** raw sentences to ground reading/grammar items.

### Kazakh Wikipedia
- **License:** CC-BY-SA → ⚠️ ShareAlike. Heavy contamination (in every web corpus).
- **Use:** grounding only; never as held-out TEST.

---

## 4. Benchmarks to cite (avoid duplication, borrow methodology)

- **Belebele (kaz_Cyrl)** — 900 human-translated kk MC reading-comprehension items,
  test-only, passages from FLORES-200. GPT-3.5 ~35% kk vs 87.7% en → genuinely hard.
  https://github.com/facebookresearch/belebele · license CC-BY-SA-4.0.
- **KazMMLU** (above) — the kk MMLU reference point.
- **FLORES-200 / KazParC** — translation reference.

---

## Action plan (when picking up data expansion)

1. **Sentiment:** pull KazSAnDRA, map ratings → 3 labels, sample balanced + native spot-check. (CC-BY-4.0)
2. **Translation:** sample human lines from KazParC (fiction/legal first for low contamination). (confirm license)
3. **Knowledge MC:** author fresh items grounded in ЕНТ/oltest.kz public exams (avoids KazMMLU NC). Hard by design.
4. **Reading:** ground passages in KazNERD/Leipzig sentences (CC-BY); or adapt Belebele/KazQAD with SA handling.
5. Route any item built from a public/web source into the **private TEST** split (contamination).
6. Re-run the verify pass after 18:50 (session-limit reset) to confirm the source-backed licenses before headline use.

---

## ADDENDUM — crowd-sourced from other LLMs, license-VERIFIED via HF API (2026-06-16)

All entries below confirmed to **exist** (HTTP 200) and license/size pulled directly
from the HuggingFace API — not model claims.

### 🥇 JACKPOT — real exams, permissive license, large

| Dataset | License (verified) | Rows | Task | Note |
|---|---|---|---|---|
| **kz-transformers/kazakh-unified-national-testing-mc** | **apache-2.0** ✅ | 14,850 | knowledge_mc, reading | **Real ЕНТ/ҰБТ MC, 7 subjects. Permissive → directly usable. The #1 find.** |
| **issai/KazCulture** | **cc-by-4.0** ✅ | 16,137 | reading, knowledge_mc | PQA on deep KZ culture/history/traditions. Compatible. |
| **issai/kazsandra** | **cc-by-4.0** ✅ | 523,183 | sentiment | Confirmed CC-BY-4.0. Map ratings → оң/теріс/бейтарап. |
| **kz-transformers/kk-socio-cultural-bench-mc** | **cc-by-4.0** ✅ | 7,111 | knowledge_mc | Socio-cultural MC, 18 categories. Compatible. |
| **kz-transformers/kazakh-dastur-mc** | **apache-2.0** ✅ | 1,005 | knowledge_mc | Traditions («Дәстүр»). |
| **kz-transformers/kazakh-constitution-mc** | **apache-2.0** ✅ | 414 | knowledge_mc | Constitution of RK. |
| **TilQazyna/til-kk-sentiment-v1** | **apache-2.0** ✅ | n/a | sentiment | Fresh release; labels оң/теріс/бейтарап. |
| **TilQazyna/til-kk-normalize-v1** | **apache-2.0** ✅ | n/a | grammar_morphology | Normalization pairs — raw material. |

### Usable with caveats
| Dataset | License (verified) | Rows | Task | Caveat |
|---|---|---|---|---|
| **kz-transformers/law-mc-codex** | **none specified** ⚠️ | 43,857 | knowledge_mc | License unset on HF — confirm in repo before reuse. |
| **AmanMussa/kazakh-instruction-v2** | **mit** ✅ | n/a | instruction_following | Alpaca-derived → high contamination + it's *training* data, weak for eval. |
| **shyngys879/Kazakh-Wiki-RAG-Dataset** | **cc-by-sa-4.0** ⚠️ | n/a | reading | ShareAlike + Wikipedia (heavy contamination → TEST only). |
| **issai/kazparc** | **none on HF** ⚠️ | 15.1M | translation | License unset on HF card (paper/repo may state CC-BY); huge (incl. synthetic) — use human lines. |

### Source pointers (not HF datasets — verify license/scrape terms)
- **Mendeley Kazakhstani news corpus** `data.mendeley.com/datasets/2vz7vtbhn2/1` — CC-BY, 6.2M docs → sentiment/reading.
- **adilet.zan.kz** — official RK legislation (kk+ru), open gov access → knowledge/translation.
- **a-toleu/KazSim** (GitHub) — 9,200 text-simplification pairs → instruction_following.
- **zloy-zhake/kaz-parallel-corpora** (GitHub) — kk-en gov news pairs → translation.
- Exam/olympiad PDF sites (buki-kz, ziatker, megamozg, kko, goo.kz) — **unknown license, "for study" terms → use only to author fresh items, not redistribute.**

### Revised "take first" order (post-verification)
1. **kz-transformers/kazakh-unified-national-testing-mc** (Apache, real ЕНТ) → knowledge_mc. Solves ceiling + license clean.
2. **issai/KazCulture** (CC-BY-4.0) → reading_comprehension (hard cultural passages).
3. **issai/kazsandra** (CC-BY-4.0) → sentiment.
4. **kz-transformers/kk-socio-cultural-bench-mc + dastur + constitution** → knowledge_mc.
5. **TilQazyna/til-kk-sentiment-v1** → sentiment (fresh, low contamination).
6. Author fresh items from exam PDFs (Yersultan-supplied) for the private TEST split.

---

## ADDENDUM 2 — third deep-research pass, license-VERIFIED via HF API (2026-06-17)

New sources (not in the lists above); existence + license confirmed via HF API.

### ✅ CC-BY-4.0 / permissive — directly usable
| Dataset | License (verified) | Size | Task | Note |
|---|---|---|---|---|
| **yeshpanovrustem/100k_movie_reviews_from_kz** | **cc-by-4.0** ✅ | 100,502 | sentiment | Manual 3-class sentiment + language labels (kk/ru/code-switch). Strong sentiment source. |
| **Kundyzka/informatics_kaz** | **apache-2.0** ✅ | 7.7k | reading_comprehension | QA with context/answer spans, niche domain (low contamination). |
| **stukenov/ekitil-parallel-kkru-v2** | **mit** ✅ | 5.1M kk-ru / 126k kk-en | translation | Hub corpus, but mixes WMT19/OPUS/KazParC → vet sub-sources before reuse. |
| **Darmm/darmm-sentiment-kk** | **apache-2.0** ✅ | 3,309 | sentiment | 5-class; use only `manual`/`crowdsourced` rows (has synthetic tag). |

### ✅ grammar — manual annotation (ShareAlike)
| **UD Kazakh-KTB** (universaldependencies.org/treebanks/kk_ktb) | CC-BY-**SA**-4.0 ⚠️ | small treebank | grammar_morphology | Manual morphology/POS/deps. Best for heavily-transformed items, not raw copy. |

### ❌ NonCommercial — cite/ground only, NOT redistributable
| **raphaelmerx/openwho** | cc-by-**nc**-4.0 | 936 kk sentences | translation | Expert-translated, **shielded from web crawl** (low contamination) — ideal but NC. Use for a *private* validation set only. |
| **farabi-lab/Retrieval-Augmented-Question-Answering** | cc-by-**nc**-4.0 | 10,002 | reading/instruction | Human-curated; NC blocks public reuse. |
| **farabi-lab/Translation** | cc-by-**nc**-4.0 | 1,000 | translation/instruction | NC. |
| **mrlbenchmarks/global-piqa-nonparallel** (kaz_cyrl) | CC-BY-SA + **no-training clause** | ~100 | knowledge_mc | Cite/compare only. |

### Exam PDFs & raw archives (unknown license → author fresh items, never copy raw)
- **Daryn олимпиада PDFs** — `daryn.kz/pol514/ro5-6kz.pdf` (30 closed MCQ, 5–6 класс), `daryn.kz/ro/2022/ts2/kz10_2.pdf` + `..._sol.pdf` (10 класс + rubric/answers). Best exam-format source with answer keys.
- **ҚАЗТЕСТ** (testcenter.kz) — official KZ-language proficiency exam structure/spec (no public answer keys → format template).
- **QazCorpus** (qazcorpus.kz) — Main 31M words + **Historical subcorpus** (XII–XX cc., Arabic/**Latin** script) → best lead for hard **kk-Latn** items.
- **Almaty Corpus** (web-corpora.net/KazakhCorpus), **makazhan/kazcorpus-news** (CC-BY-SA, 55k docs), **eGov / Adilet / Akorda** (official texts, unknown license) → grounding only.

### Papers to cite
- KazCulture (ISSAI, 2026) · OpenWHO (WMT 2025, aclanthology.org/2025.wmt-1.8) · 100k Movie Reviews (arXiv 2605.08600) · Assembling the KLC (D13-1104) · UD Kazakh-KTB.

### kk-Latn gap (important finding)
Almost **no open, clean, human-made, labeled kk-Latn datasets exist.** Best path: hand-build hard kk-Latn reading/morphology items from the **QazCorpus historical subcorpus** (originals in Latin script). A real differentiator if we add a Latin-script track.

### Final consolidated "first wave" (all three research passes merged)
1. **kz-transformers/kazakh-unified-national-testing-mc** (Apache, real ЕНТ) → knowledge_mc — *needs provenance spot-check*.
2. **issai/KazCulture** (CC-BY-4.0) → reading_comprehension.
3. **yeshpanovrustem/100k_movie_reviews_from_kz** + **issai/kazsandra** (CC-BY-4.0) → sentiment.
4. **kk-socio-cultural-bench-mc / dastur / constitution** (CC-BY/Apache) → knowledge_mc.
5. **Kundyzka/informatics_kaz** (Apache) → reading_comprehension.
6. **UD Kazakh-KTB** (SA, transformed) + **TilQazyna normalize** → grammar_morphology.
7. **Daryn PDFs** → author fresh hard items into the **private TEST** split.
