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

## Attribution

`knowledge_mc_real.jsonl` derived from
[`kz-transformers/kazakh-unified-national-testing-mc`](https://huggingface.co/datasets/kz-transformers/kazakh-unified-national-testing-mc)
(Apache-2.0) — real Unified National Testing (ЕНТ/ҰБТ) multiple-choice questions.
Subjects sampled: history_of_kazakhstan, kazakh_and_literature, geography,
human_society_rights, biology, world_history. Per-item provenance recorded in the
`provenance` field. PII scan: clean (aidefence `hasPII: false`).

## Regenerate

```bash
python tools/data/integrate_real_sources.py --limit 60
```

## Validation checklist (for Yersultan — before DEV merge)

- [ ] Spot-check question text renders correctly (Cyrillic, no mojibake)
- [ ] `answer` index points to the correct option
- [ ] Question is genuine exam content (not malformed/truncated)
- [ ] On approval: set `validated: true`, move into `benchmark/dev/knowledge_mc.jsonl`,
      and decide whether to route a portion into the private TEST split
      (real exams are public → contamination risk → prefer TEST per data-sources.md)
