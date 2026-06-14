# KazBench Test Suite

All tests are offline (DummyModel only). No API keys required.

## Run locally

```bash
# From repo root
pip install pytest
python -m pytest tests/ -v
```

## What is tested

| Module | Coverage |
|--------|---------|
| `harness.models` | DummyModel.generate returns str; IS_DUMMY flag; build_model factory; unknown name raises |
| `harness.metrics` | accuracy (perfect/zero/partial/string labels/errors); chrF identical~100/disjoint~low/empty/corpus |
| `harness.run_eval` | end-to-end subprocess: exit 0, JSON has all 6 tasks, overall in [0,100], task scores in range, metadata fields |
| `tools/data/validate.py` | passes on benchmark/dev/; prints RESULT: PASS; exits non-zero on bad JSON and missing fields |

## Docker

```bash
docker build -t kazbench .
docker run --rm kazbench                      # dummy eval
docker run --rm kazbench python -m pytest tests/ -v  # test suite
```
