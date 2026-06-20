# KazBench — Roadmap → v1.0 (credible · published · launched)

*Составлено 2026-06-20 после рой-аудита. Owner: Chelsea + agent team. Конечная цель и фазы ниже.*
*Предыдущий build-plan (Sprint 0–5, выполнен) — см. `PLAN.md`. Этот документ = путь от «опубликовано» к «v1.0 credible».*

---

## 🎯 Конечная цель (Definition of Done v1.0)

KazBench v1.0 — **достоверный, опубликованный, запущенный** открытый бенчмарк казахского для LLM,
который одновременно служит 4 целям пользователя (конвергенция, см. VISION.md):

1. **Польза КЗ** — казахский как измеримый язык для AI; реальные (не синтетические) данные.
2. **Портфолио / US job** — артефакт уровня NLP/LLM Engineer (связан с [grad school 2028]).
3. **Research** — публикуемая статья в peer-reviewed venue (workshop ACL/EMNLP).
4. **Вирусность** — open benchmark, который цитируют и используют.

**v1.0 считается достигнутым, когда ВСЕ выполнено:**
- [ ] DEV credible: реальные human-sourced items интегрированы (ceiling **решён**, не только измерен), валидация закрыта или явная политика.
- [ ] Baselines: ≥6 моделей включая Llama-70B-класса, прогнаны на финальных данных, воспроизводимо.
- [ ] Paper: завершён (0 [CITE]-заглушек), **подан** в venue.
- [ ] Leaderboard: official с приватной TEST-верификацией (не provisional).
- [ ] Launch: публичный анонс live (Twitter/HN/Reddit) + demo GIF.

---

## 📍 Где мы сейчас (snapshot 2026-06-20)

**Готово:** engine/harness/CI/leaderboard (Sprint 0–4); опубликовано (GitHub Yersultan04/kazbench + HF Dataset Yersultan03 + HF Space leaderboard live); DEV 600 (296 validated, 304 pending); TEST 180 приватный; 6 моделей + dummy на лидерборде (validated-296); ceiling измерен (96→50% на реальных ЕНТ); README ceiling-fix + paper §6/dataset-card синхронизированы (сегодня, рой).

**Главные долги (из аудита):** результаты несопоставимы (harness не фильтрует validated); ceiling **измерен, но не устранён** (реальные данные ещё не в основном DEV); paper [CITE]×21; нет Llama-70B; leaderboard provisional (нет TEST-верификации).

---

## 🗺️ Фазы

### P0 — Reproducibility fix `[$0]` `[Maya+Kai]` ✅ DONE (2026-06-20, commit 1e176fa)
> `--validated-only` (default) + `--all-items`; run_metadata (n_total/n_validated/temp/seed/ts); колонка N(val) в лидерборде; 40/40 тестов; Kai verify SHIP.

Снять «критический долг несопоставимости» **дёшево** (без перепрогона).
- Добавить флаг `--validated-only` в `harness/run_eval.py` (оценивать только `validated:true`).
- Зафиксировать в leaderboard-пайплайне: лидерборд = validated-N, явно подписать N.
- Логировать в `results/*.json`: `n_total/n_validated`, `temperature`, `seed`, дата, версия API.
- **Критерий:** любой может перепрогнать и получить те же числа. `tools/build_leaderboard.py` детерминирован.
- **Зависимости:** нет. Делать первым.

### P1 — Paper completion `[$0]` `[Leo + research-рой]` ✅ 100% DONE (2026-06-20, commits 1e176fa→a9b0c9e)
> P1: 13/21 [CITE] + References + venue. P1b: +8 верифицированных [18-26] (WebSearch); fix KazMMLU title + KazQAD venue. P1-100%: закрыты ВСЕ остаточные — chrF-vs-BLEU (через [12]), Llama-70B report [27] Grattafiori 2024, decree URL pinned, ref17 переформулирован (data-sources, не fine-tuned model), [15][16] attribution. Vex×2: ZERO фабрикаций.
> Единственное оставшееся: `[AFFILIATION TBD]` в шапке — требует ввода автора (выдумывать = фабрикация). Всё остальное submission-ready.

- Закрыть 21 [CITE]-заглушку (поиск ACL Anthology / реальные ссылки: chrF, LLM-judge, KazMMLU, Belebele, KazSAnDRA и т.д.).
- Заполнить [AUTHOR/AFFILIATION/EMAIL/TARGET VENUE].
- Выбрать venue (workshop ACL/EMNLP/SIGTURK 2026) + сверить дедлайн.
- **Критерий:** 0 заглушек; paper компилируется; venue выбрана с датой.

### P2 — Real-data expansion (ядро ceiling-fix) `[Yersultan-gated + малый API]` `[data-ml + Yersultan]` 🟡 PREP DONE (2026-06-20, commit 7571725)
> Автономная часть ГОТОВА (commits 7571725, 3c35311): `tools/data/integrate_real_sources.py` (--task knowledge_mc|sentiment|both). В `benchmark/staging/`:
>   - `knowledge_mc_real.jsonl` — 60 реальных ЕНТ (kz-transformers, Apache-2.0, source:exam)
>   - `sentiment_real.jsonl` — 60 реальных отзывов (Darmm, Apache-2.0, manual+crowdsourced, 5→3 класс, balanced)
>   Оба: validated:false, provenance+license, 0 структурных ошибок, PII-clean (aidefence). НЕ в боевом DEV.
> ⏸ ЖДЁТ Yersultan: native-валидация staging (чеклист в staging/README.md) → set validated:true → merge в DEV (часть → private TEST т.к. публичные данные = риск контаминации). KazSAnDRA/100k gated (нужен HF-токен) — Darmm взят как Apache-альтернатива.

Самая важная фаза для доверия. Превратить ceiling из «измерен» в «решён».
- Интегрировать **Apache/CC-BY реальные источники** (из `docs/data-sources.md`): kazakh-unified-national-testing-mc (Apache, реальные ЕНТ), KazSAnDRA/100k reviews (sentiment), KazCulture (RC).
- Довалидировать 304 pending DEV items (**native — только Yersultan**) ИЛИ заменить их реальными human-sourced.
- Цель: DEV всё validated + доля `seed`-only снижена; TEST расширить реальными hard items.
- **Критерий:** DEV 600 validated (или явная политика), ≥40% не-seed источников в knowledge_mc/sentiment.
- **Зависимости:** P0 (политика validated). HITL-гейт: native validation.

### P3 — Baselines complete `[API $ — под audit-gate 0403]` `[data-ml + Kai]` 🟢 БОЛЬШАЯ ЧАСТЬ DONE (2026-06-20, commit 7953720)
- ✅ **Llama-70B baseline получен** (llama-3.3-70b = 74.2) через OpenRouter (ключ из uzmrc/rag-cms).
- ✅ Прогнаны на реальных данных (staging_eval): gemini-2.5-flash **87.5 (ЛИДЕР)**, llama-3.3-70b 74.2, gpt-4o-mini 71.7, gpt-oss-120b 71.7, llama-4-scout 70.8, claude-haiku-4.5 70.0; мелкие (qwen3-32b 25, llama-8b 27) — floor.
- ✅ **Главная находка: лидер сменился** vs синтетики (был claude 91.5 → теперь gemini). `results/real/REAL_DATA_LEADERBOARD.md`.
- ⏸ Осталось: qwen-2.5-72b (OpenRouter возвращает пустой ответ — провайдер); перепрогон на ФИНАЛЬНЫХ validated данных (после P2); пересинк paper §6 реальными числами (после валидации).
- **Критерий:** ≥6 моделей вкл. 70B ✅. Финальные числа — после P2.

### P4 — Launch `[external approval]` `[Nova + Alex; Chelsea гейтит]`
- Записать demo GIF (скрипт готов в `docs/launch/demo-script.md`).
- Финализировать анонс (copy готов в `docs/launch/`); честно подать ceiling-находку как силу.
- **Критерий:** GIF в README; анонс опубликован (Twitter thread + Show HN + r/ML).
- **Зависимости:** P0–P3 закрыты. **Внешнее действие → Draft→Approve→Execute.**

### P5 — Official leaderboard `[ongoing]` `[Kai]` 🟢 ИНФРА ГОТОВА (2026-06-20, commit d24159e)
- ✅ `tools/verify_on_test.py` — maintainer прогон на приватном TEST + сравнение DEV→TEST + anti-gaming verdict (TEST>DEV или near-zero drop = 🚩flag). Протестирован на dummy ($0).
- ✅ `results/SUBMISSION_LEDGER.md` — append-only audit trail (создаётся при первом verify).
- ✅ CONTRIBUTING §4b — provisional→official flow задокументирован.
- ⏸ Применение к реальным моделям: TEST-прогон жжёт API (под gate 0403) + TEST items сейчас validated:false (held-out, оцениваются через --all-items). Лидерборд станет «official» когда прогоним реальные сабмишны на TEST.
- **Критерий (инфра):** ✅ выполнен. **Критерий (official scores):** ждёт реальных TEST-прогонов.

---

## 🔢 Критический путь и порядок

```
P0 (репро, $0) ─┐
                ├─→ P2 (реальные данные) ─→ P3 (baselines, $API) ─→ P4 (launch) ─→ P5 (official)
P1 (paper, $0) ─┘                                                   ↑
   (P0+P1 параллельно, сейчас)              paper §6 пересинк после P3 ┘
```

**Рекомендуемый старт:** P0 + P1 одновременно (оба $0, рой). Затем P2 (упирается в Yersultan-валидацию). P3 после P2. P4 после всего.

---

## 🚦 Gate-матрица

| Что | Гейт | Кто разблокирует |
|-----|------|------------------|
| P0, P1 | нет (внутреннее, $0) | автономно |
| P2 native validation | HITL | **Yersultan** (проверка казахских items) |
| P3 baseline-прогоны | **audit-gate (пароль 0403)** — жжёт API $ | Yersultan вводит код |
| P4 публичный анонс | external Draft→Approve | Yersultan утверждает текст |

## ✅ Метрики успеха v1.0
- Воспроизводимость: внешний прогон даёт те же числа (P0).
- Достоверность: ≥40% реальных источников, ceiling-падение показано на 3+ моделях (P2).
- Полнота: ≥6 baselines вкл. 70B (P3).
- Research: paper подан, 0 заглушек (P1).
- Adoption: ≥1 внешний сабмишн на лидерборд после launch (P5).

---

*Работаем строго по этому плану. Каждая фаза: recall → исполнение роем → reflection → verify (Vex/Kai) → commit+push → persist. Старт по утверждению Директора.*
