# KazBench Leaderboard

Gradio app that renders the KazBench model rankings. Designed to deploy as a
Hugging Face Space, but also runnable locally.

## Run locally

```bash
# From repo root
pip install gradio
python leaderboard/app.py
# Open http://localhost:7860
```

The app reads `results/*.json` relative to the repo root automatically.

## Deploy to Hugging Face Spaces

1. Create a new Space at https://huggingface.co/new-space
   - SDK: **Gradio**
   - Python 3.11
2. Push this repository (or just `leaderboard/` + `results/`) to the Space repo.
3. Add a `requirements.txt` at the Space root containing:
   ```
   gradio>=4.0
   ```
4. The Space will auto-launch `app.py` on port 7860.

HF Spaces auto-detects `app.py` at the root. If you push the full repo,
add a `README.md` at repo root with the Space header:

```yaml
---
title: KazBench Leaderboard
emoji: kz
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "4.0"
app_file: leaderboard/app.py
pinned: false
---
```

## Updating the leaderboard

A new model result is added by:

1. Submitter runs `python harness/run.py --model <adapter> ...` which writes
   `results/<model-label>.json`.
2. Submitter runs the verifier gate:
   ```bash
   python tools/verify_submission.py results/<model-label>.json
   ```
3. Submitter opens a PR adding the results file.
4. A maintainer verifies on the private TEST split and merges.
5. The HF Space auto-refreshes from the merged results.

## Build leaderboard.md (static export)

```bash
python tools/build_leaderboard.py --results results/ --out leaderboard.md --date 2026-06-14
```
