# Contributing to KazBench

Thank you for helping build KazBench — an open benchmark for evaluating LLMs on
the **Kazakh language**. The hardest and most valuable part of this project is
**high-quality, native-validated data**. This guide explains how to contribute
benchmark items.

By contributing data you agree it is released under **CC BY 4.0** (see
`benchmark/LICENSE-DATA`).

---

## 1. The data contract (schema)

Every item is **one JSON object per line** (JSONL) in
`benchmark/<split>/<task>.jsonl`. The public split is `dev`; the `test` split is
private and never committed publicly. The authoritative contract is
[`benchmark/schema.md`](benchmark/schema.md) — read it first.

### Common fields (every item)

| Field | Type | Notes |
|---|---|---|
| `id` | string | unique, `<prefix>_<6digits>` (e.g. `kmc_000001`) |
| `task` | string | one of the 6 tasks below |
| `source` | string | `seed` \| `native` \| `exam` \| `community` |
| `validated` | bool | **always `false` for new items** (see rule below) |
| `canary` | string? | optional contamination marker; omit for normal items |

### The 6 tasks and their fields

| Task (prefix) | Extra fields | Metric |
|---|---|---|
| `knowledge_mc` (`kmc`) | `question`, `choices[]`, `answer` (0-based int) | accuracy |
| `reading_comprehension` (`rc`) | `passage`, `question`, `choices[]`, `answer` | accuracy |
| `grammar_morphology` (`gm`) | `question`, `choices[]`, `answer` | accuracy |
| `sentiment` (`snt`) | `text`, `label` in {оң, теріс, бейтарап} | accuracy |
| `translation` (`trn`) | `source_lang` (`kk`), `target_lang` (`en`/`ru`), `source_text`, `reference` | chrF |
| `instruction_following` (`if`) | `instruction`, `rubric` (English judge criteria) | judge 0-1 |

Notes:
- **No answers may leak into prompts.** Keep the gold answer only in `answer` /
  `reference` / `label`.
- For `instruction_following`, write the **rubric in English** with clear,
  testable criteria for an LLM judge (e.g. exact scores for 1.0 / 0.5 / 0.0).
- The item content (questions, passages, sentences) must be in **Kazakh** for
  Kazakh-language tasks.

---

## 2. The golden rule: every new item starts `validated:false`

**`validated` MUST be `false` when you submit.** You do not set it to `true`
yourself — not even for your own items.

An item becomes `validated:true` **only after two native Kazakh speakers** (other
than the author) review it and sign off:

### 2-native-reviewer validation rule

1. Author submits items with `validated:false`, `source` set correctly.
2. **Reviewer #1** (native Kazakh speaker) checks correctness: language is
   natural, the gold answer is right, choices are unambiguous, no contamination.
3. **Reviewer #2** (a different native Kazakh speaker) independently confirms.
4. Only when **both** approve does a maintainer flip `validated` to `true` in a
   follow-up commit. A single reviewer is never enough.

This keeps the benchmark honest: unvalidated items can ship in `dev` but are not
counted as "headline" quality until two natives confirm them.

---

## 3. Anti-contamination

- Do **not** copy items verbatim from public websites, model outputs, or other
  benchmarks — this risks the data already being in training sets.
- A few items per task carry a unique `canary` string. Never remove or alter
  existing canaries.
- Prefer freshly authored, simple, verifiable content over scraped text.

---

## 4. Pull request process

1. **Fork** and create a branch: `git checkout -b data/<task>-<short-desc>`.
2. Add or edit items in `benchmark/dev/<task>.jsonl`. Use sequential ids that do
   not collide with existing ones.
3. **Run the validator and stats locally before opening the PR:**
   ```
   python tools/data/validate.py benchmark/dev/
   python tools/data/stats.py benchmark/dev/
   ```
   The validator must exit `0` (no schema, duplicate-id, or duplicate-content
   errors). Fix anything it reports.
4. Open a PR and fill in the PR template checklist
   (`.github/PULL_REQUEST_TEMPLATE.md`):
   - schema valid (validator passes)?
   - native-reviewed by 2 (or flagged as needing review)?
   - no contamination?
   - `source` labeled correctly?
5. A maintainer assigns two native reviewers. After both approve, a maintainer
   merges and (separately) marks items `validated:true`.

---

## 4b. Model submissions → official leaderboard (TEST verification)

Leaderboard scores you submit on the public DEV split are **provisional**. To become
**official**, a maintainer re-runs your model on the private TEST split:

1. Submitter: run eval on DEV, then `python tools/verify_submission.py results/<model>.json`
   (schema gate) and open a PR with the result JSON.
2. Maintainer: `python tools/verify_on_test.py --model <adapter> --model-id <id> --submission results/<model>.json`
   — re-runs on the private TEST split, compares DEV→TEST, and appends a row to
   `results/SUBMISSION_LEDGER.md` (append-only anti-gaming audit trail).
3. Anti-gaming verdict: a normal model **drops** from DEV to held-out TEST. TEST > DEV
   (or a near-zero drop) is **flagged** as possible DEV contamination / overfitting.
4. Only `✅ VERIFIED` entries are added to the official leaderboard with `verified_on_test:true`.

---

## 5. Quick checklist before you submit

- [ ] One JSON object per line, valid JSONL.
- [ ] All required fields present, correct types.
- [ ] `validated:false` on every new item.
- [ ] `source` set (`native`, `exam`, or `community` — not `seed`, which is
      reserved for the project's bootstrap data).
- [ ] Ids unique, follow `<prefix>_<6digits>`.
- [ ] `python tools/data/validate.py benchmark/dev/` exits 0.
- [ ] No answers leak into prompts; canaries untouched.

Questions? Open an issue. Рахмет for contributing!
