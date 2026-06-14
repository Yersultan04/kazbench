# KazBench — Build Plan (sprints & tasks)

*Autonomous build. Owner: Chelsea (orchestrator) + agent team. See VISION.md for goal/architecture.*

## v1 scope (locked decisions)
- **Name:** KazBench
- **Tasks (6):** knowledge_mc, reading_comprehension, sentiment, translation, grammar_morphology, instruction_following
- **Target size:** 100 items/task for credible v1 (seed generated now → expanded → native-validated)
- **Splits:** public DEV + private TEST (anti-contamination)
- **Stack:** GitHub (code) · HF Datasets (data) · HF Space/Gradio (leaderboard) · decentralized submission

## Human-in-the-loop gates (only two)
1. **Native data validation** — Yersultan reviews generated Kazakh items before "headline" status.
2. **Public publish** — actual push to public GitHub/HF (needs credentials). Everything built to ready-state first.

---

## Sprint 0 — Foundation  *(Chelsea, in progress)*
- [x] VISION.md
- [x] PLAN.md
- [ ] benchmark/schema.md — data contract (item + results JSON formats, splits, canaries)
- [ ] README, CONTRIBUTING, LICENSE (MIT code + CC-BY-4.0 data), CITATION, .gitignore, repo skeleton

## Sprint 1 — Eval engine  *(Maya — owns `harness/`)*
- [ ] Model adapters: dummy (offline), Claude, OpenAI-compatible, HF/local
- [ ] Task runners + prompt builders + answer parsers (per task type)
- [ ] Scorers: accuracy, chrF (translation), LLM-judge for instruction_following
- [ ] `run_eval` CLI → results JSON (versioned schema)
- [ ] Deterministic, model-agnostic, runs end-to-end on dummy

## Sprint 2 — Data layer & tooling  *(Data agent — owns `benchmark/`, `tools/data/`)*
- [ ] Final per-task JSONL schema + validators (schema lint, dedup, canary check)
- [ ] DEV/TEST split logic; private-test handling
- [ ] Seed-generation tooling + generate ~20 items/task (marked `seed`, pending native validation)
- [ ] Native-validation workflow: PR template + 2-reviewer checklist

## Sprint 3 — Leaderboard & submission  *(Maya/FE agent — owns `leaderboard/`)*
- [ ] HF Space (Gradio) reading results → ranked table, per-task breakdown
- [ ] Submission flow (results JSON + PR) + verification script on private TEST
- [ ] Leaderboard build from `results/`

## Sprint 4 — Infra / CI / reproducibility  *(Kai — owns `.github/`, `Dockerfile`)*
- [ ] GitHub Actions: schema lint, dummy-eval sanity, leaderboard build, PR validation
- [ ] Dockerfile + reproducible run
- [ ] Contamination/canary CI check

## Sprint 5 — Paper & launch  *(Leo + Nova; Chelsea gates publish)*
- [ ] Paper/preprint draft (methods, dataset card, baseline results)
- [ ] Launch assets: README polish, demo GIF, announcement copy
- [ ] **Publish gate** → present for approval → push public

## Review (continuous)
- Vex (critique) + Shield (security) + code-reviewer after each sprint's code lands.
