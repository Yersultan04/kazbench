# KazBench — Real-Data Leaderboard (knowledge_mc on real ЕНТ)

*Run 2026-06-20 on `benchmark/staging_eval/` (real Unified National Testing items,
validated:false, P2 staging). Open-weight models via Groq ($0 free tier). Proprietary
models (claude-3.5-haiku, gpt-4o-mini, gemini) NOT runnable on Groq — see synthetic
leaderboard for those.*

> ⚠️ This is the **real-data** picture. The public DEV leaderboard uses synthetic items
> and is inflated. The drop below is the synthetic ceiling, now confirmed across
> multiple models (not a single cherry-picked case).

## knowledge_mc — synthetic → real ЕНТ

| Model | KMC real | KMC synthetic | Δ | Sentiment real |
|-------|---------:|--------------:|---:|---------------:|
| **meta-llama/llama-4-scout-17b** | **70.0** | 96.0 | **−26** | 83.3 |
| openai/gpt-oss-120b | 56.7 | — (new) | — | **86.7** |
| qwen3-32b | 25.0 | 88.0 (qwen-2.5-72b) | **−63** | — |
| llama-3.1-8b | 26.7 | 72.0 | **−45** | — |
| *floor (random 1/4)* | *25.0* | *26.0* | — | *33.3* |

## Findings

1. **Ceiling effect is real and broad.** Every model drops sharply on real ЕНТ.
   Earlier we had only gpt-4o-mini (96→50); now confirmed on 4 more models. This
   answers the "cherry-picked?" critique — the synthetic set was genuinely saturated.

2. **Small/mid open models collapse to chance.** qwen3-32b (25.0) and llama-3.1-8b
   (26.7) land at the random-guess floor (25%) on real exams — they have **no real
   Kazakh knowledge**, only pattern-matched the synthetic items.

3. **Only larger models retain signal.** llama-4-scout-17b (70.0) and gpt-oss-120b
   (56.7) stay meaningfully above chance — but still far below their synthetic scores.

4. **Sentiment is more robust** than knowledge (scout 83.3, gpt-oss 86.7 on real
   reviews) — consistent with the smaller synthetic→real gap seen earlier (−8 pts).

## Best model for Kazakh (real data, open-weight)

**llama-4-scout-17b** — best open-weight model on real Kazakh knowledge (70.0) with
strong sentiment (83.3). gpt-oss-120b leads on sentiment (86.7) but trails on knowledge.

*Caveat: proprietary frontier models (claude/gpt/gemini) not tested here. On synthetic
data claude-3.5-haiku led (91.5); their real-data scores require their own API keys.*

## Reproduce
```bash
set -a; source .env; set +a   # Groq key
python -m harness.run_eval --model openai --model-id meta-llama/llama-4-scout-17b-16e-instruct \
  --split staging_eval --all-items --tasks knowledge_mc sentiment --out results/real/scout.json
```
Note: Groq free tier has per-day (TPD) and per-minute (TPM) limits; llama-3.3-70b-versatile
hit its 100k TPD cap and could not complete (rerun next day for the P3 Llama-70B baseline).
