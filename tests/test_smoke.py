"""
KazBench smoke tests.

All tests are offline (DummyModel only) and have no external dependencies
beyond pytest. They cover:
  - harness imports and DummyModel.generate
  - metrics: accuracy, chrF
  - run_eval end-to-end -> results JSON with 6 tasks + overall in [0, 100]
  - data validator passes on benchmark/dev/
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Resolve repo root so tests work regardless of CWD
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent


# ===========================================================================
# 1. Harness imports and DummyModel
# ===========================================================================

class TestDummyModel:
    def test_import_harness_package(self):
        """harness package is importable and exposes __version__."""
        from harness import __version__  # noqa: F401
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_build_model_returns_dummy(self):
        """build_model('dummy') returns a DummyModel instance."""
        from harness.models import build_model, DummyModel
        model = build_model("dummy")
        assert isinstance(model, DummyModel)

    def test_dummy_generate_returns_str(self):
        """DummyModel.generate always returns a str."""
        from harness.models import DummyModel
        model = DummyModel()
        result = model.generate("Test prompt")
        assert isinstance(result, str)

    def test_dummy_mc_response(self):
        """DummyModel returns '0' for MC-style prompts."""
        from harness.models import DummyModel
        model = DummyModel()
        assert model.generate("Choose: Jawap nomerin jazyn") == "0"

    def test_dummy_translation_response(self):
        """DummyModel returns a stub string for translation prompts."""
        from harness.models import DummyModel
        model = DummyModel()
        resp = model.generate("аудар: Казакстан")
        assert isinstance(resp, str)
        assert len(resp) > 0

    def test_dummy_is_dummy_flag(self):
        """DummyModel.IS_DUMMY is True (used by judge_score short-circuit)."""
        from harness.models import DummyModel
        model = DummyModel()
        assert getattr(model, "IS_DUMMY", False) is True

    def test_build_model_unknown_raises(self):
        """build_model raises ValueError on unknown model name."""
        from harness.models import build_model
        with pytest.raises(ValueError, match="Unknown model name"):
            build_model("nonexistent_model_xyz")


# ===========================================================================
# 2. Metrics
# ===========================================================================

class TestAccuracy:
    def test_perfect_accuracy(self):
        from harness.metrics import accuracy
        assert accuracy([0, 1, 2], [0, 1, 2]) == pytest.approx(1.0)

    def test_zero_accuracy(self):
        from harness.metrics import accuracy
        assert accuracy([0, 0, 0], [1, 2, 3]) == pytest.approx(0.0)

    def test_partial_accuracy(self):
        from harness.metrics import accuracy
        assert accuracy([0, 1, 0, 1], [0, 0, 0, 1]) == pytest.approx(0.75)

    def test_string_labels(self):
        from harness.metrics import accuracy
        assert accuracy(["on", "teris"], ["on", "on"]) == pytest.approx(0.5)

    def test_length_mismatch_raises(self):
        from harness.metrics import accuracy
        with pytest.raises(ValueError, match="Length mismatch"):
            accuracy([0, 1], [0])

    def test_empty_raises(self):
        from harness.metrics import accuracy
        with pytest.raises(ValueError, match="Empty"):
            accuracy([], [])


class TestChrF:
    def test_identical_strings_near_100(self):
        """chrF of identical non-empty strings should be ~100."""
        from harness.metrics import chrf_sentence
        score = chrf_sentence("Hello world", "Hello world")
        assert score == pytest.approx(100.0, abs=1e-3)

    def test_disjoint_strings_low(self):
        """chrF of completely different strings should be very low."""
        from harness.metrics import chrf_sentence
        # Use strings with no shared characters
        score = chrf_sentence("aaaa", "bbbb")
        assert score < 5.0, f"Expected low score for disjoint strings, got {score}"

    def test_empty_hypothesis_zero(self):
        from harness.metrics import chrf_sentence
        assert chrf_sentence("", "reference text") == pytest.approx(0.0)

    def test_empty_reference_zero(self):
        from harness.metrics import chrf_sentence
        assert chrf_sentence("hypothesis text", "") == pytest.approx(0.0)

    def test_partial_overlap(self):
        """Partial overlap should produce a score between 0 and 100."""
        from harness.metrics import chrf_sentence
        score = chrf_sentence("the cat sat", "the dog sat")
        assert 0.0 < score < 100.0

    def test_corpus_chrf_average(self):
        """chrf_corpus returns macro-average of sentence scores."""
        from harness.metrics import chrf_sentence, chrf_corpus
        s1 = chrf_sentence("abc", "abc")
        s2 = chrf_sentence("xyz", "xyz")
        corpus = chrf_corpus(["abc", "xyz"], ["abc", "xyz"])
        expected = (s1 + s2) / 2
        assert corpus == pytest.approx(expected, abs=1e-9)

    def test_corpus_length_mismatch_raises(self):
        from harness.metrics import chrf_corpus
        with pytest.raises(ValueError, match="Length mismatch"):
            chrf_corpus(["a", "b"], ["a"])


# ===========================================================================
# 3. run_eval end-to-end
# ===========================================================================

ALL_TASKS = [
    "knowledge_mc",
    "reading_comprehension",
    "grammar_morphology",
    "sentiment",
    "translation",
    "instruction_following",
]


class TestRunEval:
    """Run the dummy eval via subprocess and assert on the output JSON."""

    @pytest.fixture(scope="class")
    def results_json(self, tmp_path_factory):
        """Run dummy eval once per class; cache result."""
        out = tmp_path_factory.mktemp("results") / "dummy.json"
        proc = subprocess.run(
            [
                sys.executable, "-m", "harness.run_eval",
                "--model", "dummy",
                "--split", "dev",
                "--out", str(out),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, (
            f"run_eval exited {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
        return json.loads(out.read_text(encoding="utf-8"))

    def test_exit_code_zero(self, results_json):
        """Fixture already asserts returncode==0; this is a named marker."""
        assert results_json is not None

    def test_has_overall_key(self, results_json):
        assert "overall" in results_json

    def test_overall_in_range(self, results_json):
        overall = results_json["overall"]
        assert 0.0 <= overall <= 100.0, f"overall={overall} out of [0, 100]"

    def test_has_all_six_tasks(self, results_json):
        tasks = results_json.get("tasks", {})
        for task in ALL_TASKS:
            assert task in tasks, f"Missing task '{task}' in results"

    def test_each_task_has_required_keys(self, results_json):
        tasks = results_json.get("tasks", {})
        for task_name, info in tasks.items():
            for key in ("metric", "score", "n"):
                assert key in info, f"Task '{task_name}' missing key '{key}'"

    def test_each_task_score_in_range(self, results_json):
        tasks = results_json.get("tasks", {})
        for task_name, info in tasks.items():
            score = info["score"]
            metric = info["metric"]
            if metric == "chrF":
                # chrF is in [0, 100]
                assert 0.0 <= score <= 100.0, (
                    f"Task '{task_name}' chrF score {score} out of [0, 100]"
                )
            else:
                # accuracy and judge are in [0, 1]
                assert 0.0 <= score <= 1.0, (
                    f"Task '{task_name}' {metric} score {score} out of [0, 1]"
                )

    def test_task_n_positive(self, results_json):
        tasks = results_json.get("tasks", {})
        for task_name, info in tasks.items():
            assert info["n"] > 0, f"Task '{task_name}' has n={info['n']}"

    def test_has_metadata_fields(self, results_json):
        for key in ("model", "adapter", "kazbench_version", "split"):
            assert key in results_json, f"Missing metadata key '{key}'"

    def test_split_is_dev(self, results_json):
        assert results_json["split"] == "dev"

    def test_has_run_metadata(self, results_json):
        """run_metadata block must be present with reproducibility fields."""
        assert "run_metadata" in results_json, "Missing 'run_metadata' key"
        meta = results_json["run_metadata"]
        for key in ("validated_only", "n_total", "n_validated", "temperature", "seed", "timestamp"):
            assert key in meta, f"run_metadata missing '{key}'"

    def test_run_metadata_validated_only_default_true(self, results_json):
        """Default run (no --all-items) must have validated_only=True."""
        assert results_json["run_metadata"]["validated_only"] is True

    def test_run_metadata_counts_sane(self, results_json):
        """n_validated <= n_total."""
        meta = results_json["run_metadata"]
        assert meta["n_validated"] <= meta["n_total"]

    def test_run_metadata_timestamp_format(self, results_json):
        """timestamp must be ISO 8601 UTC string."""
        import re
        ts = results_json["run_metadata"]["timestamp"]
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts), (
            f"timestamp '{ts}' does not match YYYY-MM-DDTHH:MM:SSZ"
        )

    def test_overall_matches_tasks(self, results_json):
        """Overall should be macro-average of per-task scores scaled to [0,100]."""
        tasks = results_json.get("tasks", {})
        values = []
        for info in tasks.values():
            if info["n"] == 0:
                continue
            if info["metric"] == "chrF":
                values.append(info["score"])
            else:
                values.append(info["score"] * 100.0)
        expected = sum(values) / len(values) if values else 0.0
        assert results_json["overall"] == pytest.approx(expected, abs=0.01)


# ===========================================================================
# 3b. run_eval --all-items flag
# ===========================================================================

class TestRunEvalAllItems:
    """Verify --all-items overrides validated_only and n_total >= n_validated."""

    @pytest.fixture(scope="class")
    def results_all(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("results_all") / "dummy_all.json"
        proc = subprocess.run(
            [
                sys.executable, "-m", "harness.run_eval",
                "--model", "dummy",
                "--split", "dev",
                "--all-items",
                "--out", str(out),
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, (
            f"run_eval --all-items exited {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
        return json.loads(out.read_text(encoding="utf-8"))

    def test_validated_only_is_false(self, results_all):
        assert results_all["run_metadata"]["validated_only"] is False

    def test_n_total_gte_n_validated(self, results_all):
        meta = results_all["run_metadata"]
        assert meta["n_total"] >= meta["n_validated"]


# ===========================================================================
# 4. Data validator
# ===========================================================================

class TestDataValidator:
    def test_validator_passes_on_dev(self):
        """tools/data/validate.py must exit 0 on benchmark/dev/."""
        dev_dir = REPO_ROOT / "benchmark" / "dev"
        assert dev_dir.is_dir(), f"benchmark/dev/ not found at {dev_dir}"

        proc = subprocess.run(
            [sys.executable, "tools/data/validate.py", str(dev_dir)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, (
            f"Data validator failed (exit {proc.returncode})\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )

    def test_validator_output_contains_pass(self):
        """Validator prints 'RESULT: PASS' when data is clean."""
        dev_dir = REPO_ROOT / "benchmark" / "dev"
        proc = subprocess.run(
            [sys.executable, "tools/data/validate.py", str(dev_dir)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert "RESULT: PASS" in proc.stdout, (
            f"Expected 'RESULT: PASS' in output\nSTDOUT:\n{proc.stdout}"
        )

    def test_validator_error_on_bad_json(self, tmp_path):
        """Validator exits non-zero on malformed JSONL."""
        bad = tmp_path / "knowledge_mc.jsonl"
        bad.write_text("{not valid json}\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "tools/data/validate.py", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode != 0

    def test_validator_error_on_missing_field(self, tmp_path):
        """Validator exits non-zero when a required field is absent."""
        bad = tmp_path / "sentiment.jsonl"
        item = {"task": "sentiment", "source": "seed", "validated": False}
        # missing 'id', 'text', 'label'
        bad.write_text(json.dumps(item) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "tools/data/validate.py", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        assert proc.returncode != 0
