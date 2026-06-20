# Staging — real human-sourced items (pending native validation)

Items here are **prepared but NOT yet part of the live DEV split**. They are
`validated: false` and await native-speaker validation (Yersultan, HITL gate)
before any merge into `benchmark/dev/`.

This is the P2 (real-data expansion) staging area — the core of the
synthetic-ceiling fix (synthetic items saturated at 96%, real ЕНТ exposes ~50%).

## Contents

| File | Task | Source | Count | License |
|------|------|--------|-------|---------|
| `knowledge_mc_real.jsonl` | knowledge_mc | real ЕНТ/ҰБТ exams | 60 | Apache-2.0 |
| `sentiment_real.jsonl` | sentiment | real KZ reviews (Darmm) | 60 | Apache-2.0 |

## Attribution

`knowledge_mc_real.jsonl` derived from
[`kz-transformers/kazakh-unified-national-testing-mc`](https://huggingface.co/datasets/kz-transformers/kazakh-unified-national-testing-mc)
(Apache-2.0) — real Unified National Testing (ЕНТ/ҰБТ) multiple-choice questions.
Subjects sampled: history_of_kazakhstan, kazakh_and_literature, geography,
human_society_rights, biology, world_history.

`sentiment_real.jsonl` derived from
[`Darmm/darmm-sentiment-kk`](https://huggingface.co/datasets/Darmm/darmm-sentiment-kk)
(Apache-2.0) — real Kazakh reviews. Only `manual` + `crowdsourced` rows used (synthetic
rows skipped). 5-class origin mapped to KazBench 3-class: positive/very_positive→оң,
negative/very_negative→теріс, neutral→бейтарап. Label-balanced (~20 each).

Per-item provenance recorded in the `provenance` field. PII scan: clean (aidefence
`hasPII: false`) for both files.

## Regenerate

```bash
python tools/data/integrate_real_sources.py --task knowledge_mc --limit 60
python tools/data/integrate_real_sources.py --task sentiment   --limit 60
# or both at once:
python tools/data/integrate_real_sources.py --task both --limit 60
```

## Validation checklist (for Yersultan — before DEV merge)

**knowledge_mc_real.jsonl:**
- [ ] Question text renders correctly (Cyrillic, no mojibake)
- [ ] `answer` index points to the correct option
- [ ] Genuine exam content (not malformed/truncated)

**sentiment_real.jsonl:**
- [ ] Review text renders correctly
- [ ] 3-class `label` (оң/теріс/бейтарап) matches the review's actual sentiment
- [ ] 5→3 mapping is sensible for borderline cases (e.g. mild reviews)

**On approval (both):** set `validated: true`, move into `benchmark/dev/<task>.jsonl`,
and route a portion into the private TEST split (real public data → contamination risk
→ prefer TEST per `docs/data-sources.md`).
