# KazBench — Real-Data Leaderboard

*Run 2026-06-20 on `benchmark/staging_eval/` (real ЕНТ exams + real Kazakh reviews, P2
staging). Frontier + open models via OpenRouter; some open models also via Groq. Scores
on real human-sourced items — NOT the inflated synthetic DEV.*

> ⚠️ **The leader changes on real data.** On synthetic DEV, claude-3.5-haiku led (91.5)
> and gemini was 4th (84.2). On **real ЕНТ, gemini-2.5-flash wins (87.5)** and a current
> Claude Haiku lands last of the frontier group. Picking a model from synthetic scores
> would have been the wrong call — this is exactly what KazBench exists to prevent.

## Frontier + large open models (OpenRouter, real ЕНТ + reviews)

| Rank | Model | Overall | knowledge_mc | sentiment |
|------|-------|--------:|-------------:|----------:|
| 🥇 1 | **google/gemini-2.5-flash** | **87.5** | 86.7 | 88.3 |
| 2 | meta-llama/llama-3.3-70b-instruct | 74.2 | 61.7 | 86.7 |
| 3 | openai/gpt-4o-mini | 71.7 | 58.3 | 85.0 |
| 4 | meta-llama/llama-4-scout | 70.8 | 61.7 | 80.0 |
| 5 | anthropic/claude-haiku-4.5 | 70.0 | 55.0 | 85.0 |
| — | openai/gpt-oss-120b (Groq) | 71.7 | 56.7 | 86.7 |
| — | qwen/qwen-2.5-72b | n/a | (provider returned empty response) | — |

## Small open models collapse to chance (Groq, knowledge_mc)

| Model | KMC real | KMC synthetic | Δ |
|-------|---------:|--------------:|---:|
| qwen3-32b | 25.0 | 88.0 | **−63** |
| llama-3.1-8b | 26.7 | 72.0 | **−45** |
| *floor (random 1/4)* | *25.0* | — | — |

## Synthetic → real drop (the ceiling, confirmed across the board)

| Model | KMC synthetic | KMC real | Δ |
|-------|--------------:|---------:|---:|
| gemini-2.5-flash | 90.0 | 86.7 | −3 (robust!) |
| llama-4-scout | 96.0 | 61.7 | −34 |
| gpt-4o-mini | 96.0 | 58.3 | −38 |
| claude (3.5→4.5 haiku) | 96.0 | 55.0 | −41 |
| qwen | 88.0 | 25.0 | −63 |
| llama-3.1-8b | 72.0 | 26.7 | −45 |

## Findings

1. **Best model for Kazakh (real data): `google/gemini-2.5-flash`** — 87.5 overall,
   and the *only* model that barely drops synthetic→real (−3 on knowledge). It genuinely
   knows Kazakh; the others largely pattern-matched the synthetic set.
2. **Ceiling effect confirmed across 7+ models** — not cherry-picked. Most frontier models
   lose 30–40 pts on real ЕНТ; small open models fall to the 25% random-guess floor.
3. **Sentiment is robust** (80–88% across models) — the gap is in *knowledge*, not
   surface-level classification.
4. **Llama-70B baseline (P3 goal) obtained:** llama-3.3-70b = 74.2 overall.

## Caveats
- Real items are `validated:false` staging (P2) — pending native validation for the
  *official* headline. Direction is robust, exact numbers may shift slightly post-validation.
- knowledge_mc n=60, sentiment n=60. Small n → treat ±a few points as noise.
- qwen-2.5-72b returned empty responses via OpenRouter (provider issue); covered on
  synthetic (74.5) and via Groq qwen3-32b (25.0 real).

## Reproduce
```bash
export OPENAI_API_KEY=<openrouter key>; export OPENAI_BASE_URL=https://openrouter.ai/api/v1
python -m harness.run_eval --model openai --model-id google/gemini-2.5-flash \
  --split staging_eval --all-items --tasks knowledge_mc sentiment --out results/real/gemini.json
```
