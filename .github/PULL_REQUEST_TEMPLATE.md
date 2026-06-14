<!--
KazBench data PR. Please fill in this checklist. PRs that add/edit benchmark
items must pass the validator and follow the 2-native-reviewer rule.
See CONTRIBUTING.md for full details.
-->

## What does this PR change?

<!-- e.g. "Adds 20 new sentiment items (community)" -->

- Task(s):
- Number of items added / edited:
- Source label used (`native` / `exam` / `community`):

## Data PR checklist

### Schema & validation
- [ ] Each item is valid JSONL (one JSON object per line).
- [ ] All required fields present with correct types (see `benchmark/schema.md`).
- [ ] `answer` indices are in range; `sentiment` labels are in {оң, теріс, бейтарап}.
- [ ] Ids are unique and follow `<prefix>_<6digits>`.
- [ ] I ran `python tools/data/validate.py benchmark/dev/` and it **exits 0** (paste output below).
- [ ] I ran `python tools/data/stats.py benchmark/dev/` and the counts look right.

### Validation status (2-native-reviewer rule)
- [ ] Every new item has `validated: false` (I did NOT set it to `true`).
- [ ] I understand items become `validated:true` only after **2 native Kazakh
      reviewers** sign off in a separate maintainer commit.
- [ ] Reviewer #1 (native): <!-- @handle, leave blank if pending -->
- [ ] Reviewer #2 (native): <!-- @handle, leave blank if pending -->

### Contamination
- [ ] Items are freshly authored, not copied verbatim from public web pages,
      other benchmarks, or model outputs.
- [ ] I did not remove or alter any existing `canary` markers.
- [ ] No gold answers leak into prompts/passages/questions.

### Provenance
- [ ] `source` is labeled correctly on every item (`native` / `exam` / `community`).
- [ ] Content is in Kazakh for Kazakh-language tasks; translation `reference`
      is in the correct target language.

## Validator output

```
<!-- paste the output of: python tools/data/validate.py benchmark/dev/ -->
```

## Notes for reviewers

<!-- Anything the native reviewers should pay attention to. -->
