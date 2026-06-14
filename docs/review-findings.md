# KazBench — Review findings & disposition

Three parallel reviews after Sprint 0–4: Vex (strategy/red-team), Shield (security), code-reviewer.
Strong convergence: all three flagged the Cyrillic/Latin prompt inconsistency.

## Fixed now (Sprint 5 hardening)

| ID | Severity | Issue | Fix |
|---|---|---|---|
| C1 | CRITICAL | Prompts emitted Latin translit while data is Cyrillic; dummy keyword-sniff never fired | All prompts Cyrillic; `generate(prompt, task=...)` explicit dispatch |
| C2 | CRITICAL | `parse_mc` only read single-digit choice index | Full-integer parse, bounds-checked |
| Sec C-1 | CRITICAL | Prompt injection via `rubric`/`instruction` into LLM judge | Delimited data sections, sentinel, strict score parse |
| Sec C-2/H-4 | HIGH | Path traversal via `--split`/`--out`/`--data-dir` | `--split` allowlist (kept); `--out`/`--data-dir` left caller-controlled by design (CLI), CI vets PR args |
| H1 | HIGH | grammar_morphology all answers index 0; MC skew | Redistributed correct-answer positions evenly + stats skew check (>60% warns) |
| Sec H-2 | HIGH | No file-size limit loading results JSON (DoS) | 1 MB guard before json.load |
| Sec H-3 | HIGH | Gradio 0.0.0.0, unpinned, file exposure | Pin + `allowed_paths`, HF-Spaces-only note |
| Sec H-1/M-6 | HIGH/MED | CI runs PR code; no timeouts | `timeout-minutes`, subprocess timeout, path filters |
| Sec M-1 | MED | Markdown injection via `model` field | Escape `| [ ]` |
| Sec M-5 | MED | No `.dockerignore` | Added |
| M2/M3/M4 | MED | Dead code; broken refresh button; sentinel mismatch | Cleaned; `refresh_table` wired; unified `n/a` |

Verified: 34 tests pass; dummy eval honest (overall 23.22/100; grammar 100%->25% after de-skew).

## Roadmap (NOT fixed now — needs data/native/design work, tracked for v1)

Strategic items from Vex — these are what turn "cool project" into "trusted standard":

1. **Anti-gaming / submission integrity** (Vex #1) — submission ledger (who/when/commit hash), require model+training-data declaration + "did not train on KazBench" attestation, active canary-reproduction monitoring in CI. *Before public submissions open.*
2. **Task justification** (Vex #2) — document per-task rationale ("does this measure Kazakh-specific phenomena vs general ability?"); consider adding linguistically meaningful tasks (NER, code-switching KK-RU, morphology generation). *Before paper submission.*
3. **Judge reliability** (Vex #3) — inter-rater agreement study (2 judge models, Fleiss/Krippendorff), standardized rubrics with concrete score levels, locked judge model version, optional score_std. *Before leaderboard is authoritative.*
4. **Data scale + validation** (Vex #4) — expand to ~200–300 items/task (exam-mined ҰБТ + native authoring), native 2-reviewer validation pass to flip `validated:true`. *The real bottleneck; needs Yersultan (native).* 
5. **chrF comparability** (code H2) — align to sacrebleu or clearly label "KazBench-chrF, not sacrebleu-comparable."
6. **Future scope** (Vex #7) — Latin script, dialects, Russian code-switching as v1.1/v2.0.
7. **Real baselines** — evaluate Claude/GPT/Llama for the paper's results table (needs API budget; cheap).

Single biggest risk (all reviewers agree): a benchmark that is small/unvalidated or whose leaderboard
gets gamed loses trust permanently. Mitigations = items 1 + 4 above.
