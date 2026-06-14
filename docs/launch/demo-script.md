---
title: KazBench — Demo Script / Storyboard
format: 30–60 second terminal recording (GIF or MP4)
tool-recommendation: asciinema (Linux/macOS) or PowerShell + ttyrec / Terminalizer (Windows)
---

# Demo Script — 30–60 Second Terminal Recording

## Goal

Show in one continuous take: install dependencies, run an offline eval, inspect results, preview
the leaderboard. No API key required. Viewer understands what KazBench does without reading a word.

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
[kazbench] Task=knowledge_mc        n=18  ...  accuracy=22.2%
[kazbench] Task=reading_comprehension  n=16  ...  accuracy=12.5%
[kazbench] Task=grammar_morphology  n=16  ...  accuracy=100.0%
[kazbench] Task=sentiment           n=18  ...  accuracy=0.0%
[kazbench] Task=translation         n=18  ...  chrF=0.00
[kazbench] Task=instruction_following  n=16  ...  judge=20.0%
[kazbench] Done. Tasks run: 6  Overall: 25.79/100
[kazbench] Results -> .../results/dummy.json
```

Let this run at normal speed — it takes 1–2 seconds total (no API calls). The per-task lines
appear sequentially, giving a sense of the pipeline in motion.

**Voice-over / caption:**
"Run any model. Here: the offline dummy baseline."

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
  "overall": 25.79,
  "tasks": {
    "knowledge_mc":         { "metric": "accuracy", "score": 0.2222, "n": 18 },
    "reading_comprehension": { "metric": "accuracy", "score": 0.1250, "n": 16 },
    "grammar_morphology":   { "metric": "accuracy", "score": 1.0000, "n": 16 },
    "sentiment":            { "metric": "accuracy", "score": 0.0000, "n": 18 },
    "translation":          { "metric": "chrF",     "score": 0.0000, "n": 18 },
    "instruction_following":{ "metric": "judge",    "score": 0.2000, "n": 16 }
  }
}
```

Pause 1–2 seconds on this. It communicates: structured output, every task scored, versioned.

**Voice-over / caption:**
"Structured JSON output. Drop it in results/ to update the leaderboard."

---

### SHOT 4 — Swap to real model (5 seconds)

**What appears on screen (just the command, do not actually run it in the recording — it costs money):**

```
(kazbench) $ python -m harness.run_eval \
    --model claude \
    --model-id claude-haiku-4-5-20251001 \
    --out results/claude-haiku.json
```

Show the command, then cut before it executes. This communicates "it works with real models too"
without requiring an API call on screen.

**Voice-over / caption:**
"Swap --model claude. Or --model openai. Same interface."

---

### SHOT 5 — Build the leaderboard locally (8–10 seconds)

**What appears on screen:**

```
(kazbench) $ python tools/build_leaderboard.py
[leaderboard] Found 1 result(s) in results/
[leaderboard] Written leaderboard.md

(kazbench) $ head -30 leaderboard.md
```

The head command shows the markdown table. A leaderboard row appears with the dummy model scores.
This is the moment the viewer understands the full pipeline: eval → JSON → leaderboard.

**Voice-over / caption:**
"Auto-builds the leaderboard from result files."

---

### SHOT 6 — Open the HF Space (3–5 seconds)

**Switch to browser (not terminal).**

Cut to a browser tab showing the Gradio leaderboard (HF Space URL). The ranked table is visible.
The Refresh button is visible. At minimum one row is populated (even with dummy data).

If the HF Space is not yet live at recording time, use a locally running instance:

```
(kazbench) $ python leaderboard/app.py
Running on local URL: http://127.0.0.1:7860
```

Then switch to browser showing http://127.0.0.1:7860.

**Voice-over / caption:**
"Public leaderboard on Hugging Face Space. Submit a PR to add your model."

---

### SHOT 7 — End card (3 seconds)

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

# 4. (Optional: show real model command, do not execute)
# python -m harness.run_eval --model claude --model-id claude-haiku-4-5-20251001 --out results/claude-haiku.json

# 5. Build leaderboard markdown
python tools/build_leaderboard.py
head -30 leaderboard.md

# 6. Launch leaderboard UI (then switch to browser)
python leaderboard/app.py
```

---

## Recording notes

- Total runtime target: 40–50 seconds. Under 60 seconds keeps GIF file sizes manageable.
- If using asciinema: `asciinema rec demo.cast --overwrite` then `agg demo.cast demo.gif`
- If using Terminalizer (Windows): `terminalizer record demo -d "zsh"` then `terminalizer render demo`
- Add 1.0s pause after each command completes before typing the next (looks deliberate, not rushed).
- The grammar_morphology line showing `accuracy=100.0%` is from the dummy model — the dummy always
  picks choice 0, and the seed data happens to have answer=0 for all grammar items. Fine to show;
  it is a property of the seed data, not a real model result. Do not frame it as a real score.
