---
title: KazBench — Demo Script / Storyboard
format: 30–60 second terminal recording (GIF or MP4)
tool-recommendation: asciinema (Linux/macOS) or PowerShell + ttyrec / Terminalizer (Windows)
---

# Demo Script — 30–60 Second Terminal Recording

## Goal

Show in one continuous take: install dependencies, run an offline eval, inspect results, open the
live leaderboard. No API key required. Viewer understands what KazBench does without reading a word.

## Prerequisites for recording

- Terminal: 120 columns wide, dark background (black or #1e1e2e)
- Font: monospace, 14–16pt
- Working directory: repo root
- Python 3.11+ with a fresh venv already activated (do not show `pip install` scrolling — use
  a pre-warmed venv and run pip install in advance, or use a requirements cache)
- Dummy results file already deleted before recording starts:
  `rm results/dummy.json` (or rename it)

---

## Shot-by-shot storyboard

---

### SHOT 1 — Install (3–5 seconds)

**What appears on screen:**

```
(kazbench) $ pip install -r requirements.txt -q
```

Type this live. The `-q` flag suppresses the download noise. It completes almost instantly
because the venv is pre-warmed. The line just clears cleanly.

**Voice-over / caption (optional):**
"Install: one command."

---

### SHOT 2 — Run the offline dummy eval (10–15 seconds)

**What appears on screen:**

```
(kazbench) $ python -m harness.run_eval --model dummy --split dev --out results/dummy.json
[kazbench] Building model adapter: dummy
[kazbench] Task=knowledge_mc           n=...  accuracy=...%
[kazbench] Task=reading_comprehension  n=...  accuracy=...%
[kazbench] Task=grammar_morphology     n=...  accuracy=...%
[kazbench] Task=sentiment              n=...  accuracy=...%
[kazbench] Task=translation            n=...  chrF=...
[kazbench] Task=instruction_following  n=...  judge=...%
[kazbench] Done. Tasks run: 6  Overall: 22.97/100
[kazbench] Results -> .../results/dummy.json
```

Let this run at normal speed — it takes 1–2 seconds total (no API calls). The per-task lines
appear sequentially, giving a sense of the pipeline in motion.

**Voice-over / caption:**
"Run any model. Here: the offline dummy baseline. Floor is 22.97."

---

### SHOT 3 — Show the results JSON (5–7 seconds)

**What appears on screen:**

```
(kazbench) $ cat results/dummy.json
{
  "model": "dummy",
  "adapter": "dummy",
  "kazbench_version": "0.1.0",
  "split": "dev",
  "overall": 22.97,
  "tasks": {
    "knowledge_mc":          { "metric": "accuracy", "score": ..., "n": ... },
    "reading_comprehension":  { "metric": "accuracy", "score": ..., "n": ... },
    "grammar_morphology":    { "metric": "accuracy", "score": ..., "n": ... },
    "sentiment":             { "metric": "accuracy", "score": ..., "n": ... },
    "translation":           { "metric": "chrF",     "score": ..., "n": ... },
    "instruction_following": { "metric": "judge",    "score": ..., "n": ... }
  }
}
```

Pause 1–2 seconds on this. It communicates: structured output, every task scored, versioned.

**Voice-over / caption:**
"Structured JSON output. Open a PR to submit and land on the leaderboard."

---

### SHOT 4 — Swap to real model (5 seconds)

**What appears on screen (just the command — do not actually run it in the recording):**

```
(kazbench) $ python -m harness.run_eval \
    --model openai \
    --model-id your-model-id \
    --out results/your-model.json
```

Show the command, then cut before it executes. This communicates "it works with real models too"
without requiring an API call on screen.

**Voice-over / caption:**
"Swap --model openai. Or --model claude. Same interface."

---

### SHOT 5 — Open the live leaderboard (5–8 seconds)

**Switch to browser.**

Cut to a browser tab showing the live Gradio leaderboard at:
https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard

The ranked table is visible with real results:

| Model | Overall | ... |
|---|---|---|
| Llama-4-Scout | 87.53 | |
| Llama-3.1-8B | 64.94 | |
| dummy | 22.97 | |

Pause 2 seconds so the viewer can read the scores.

**Voice-over / caption:**
"Live leaderboard on Hugging Face. Submit a PR to add your model."

---

### SHOT 6 — End card (3 seconds)

Terminal or static frame. Show:

```
github.com/Yersultan04/kazbench
The standard benchmark for Kazakh-language AI.
```

---

## Full command sequence (copy-paste for recording)

```bash
# 1. Install
pip install -r requirements.txt -q

# 2. Run offline eval
python -m harness.run_eval --model dummy --split dev --out results/dummy.json

# 3. Inspect results
cat results/dummy.json

# 4. (Show real model command, do not execute)
# python -m harness.run_eval --model openai --model-id your-model-id --out results/your-model.json

# 5. Switch to browser: https://huggingface.co/spaces/Yersultan03/kazbench-leaderboard
```

---

## Recording notes

- Total runtime target: 40–50 seconds. Under 60 seconds keeps GIF file sizes manageable.
- If using asciinema: `asciinema rec demo.cast --overwrite` then `agg demo.cast demo.gif`
- If using Terminalizer (Windows): `terminalizer record demo -d "zsh"` then `terminalizer render demo`
- Add 1.0s pause after each command completes before typing the next (looks deliberate, not rushed).
- The dummy overall is 22.97 — use that as the floor reference in any caption or voice-over.
- For Shot 5, the leaderboard is live: no need to run locally. Just open the HF Space URL directly.
