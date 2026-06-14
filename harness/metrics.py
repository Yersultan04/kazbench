"""
KazBench evaluation metrics.

All implementations are pure Python (no nltk, no sacrebleu) so the harness
has zero heavy dependencies.

Public API:
    accuracy(predictions, references)          -> float  in [0, 1]
    chrf_sentence(hypothesis, reference, ...)  -> float  in [0, 100]
    chrf_corpus(hypotheses, references, ...)   -> float  in [0, 100]
    judge_score(response, rubric, model)       -> float  in [0, 1]
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Sequence


# ---------------------------------------------------------------------------
# Accuracy
# ---------------------------------------------------------------------------

def accuracy(
    predictions: Sequence[int | str],
    references: Sequence[int | str],
) -> float:
    """
    Compute exact-match accuracy.

    Args:
        predictions: Sequence of predicted labels/indices.
        references:  Sequence of gold labels/indices.

    Returns:
        Fraction of correct predictions in [0, 1].

    Raises:
        ValueError: If lengths differ or sequences are empty.
    """
    if len(predictions) != len(references):
        raise ValueError(
            f"Length mismatch: predictions={len(predictions)}, "
            f"references={len(references)}"
        )
    if not predictions:
        raise ValueError("Empty sequences passed to accuracy().")
    correct = sum(p == r for p, r in zip(predictions, references))
    return correct / len(predictions)


# ---------------------------------------------------------------------------
# chrF (character n-gram F-score)
# ---------------------------------------------------------------------------
# Reference: Popovic (2015) "chrF: character n-gram F-score for automatic MT
# evaluation". We implement n=1..6, beta=2, no word boundary bonus (chrF not
# chrF++) for simplicity and full reproducibility without dependencies.

def _char_ngrams(text: str, n: int) -> Counter:
    """Return a Counter of all character n-grams in *text*."""
    return Counter(text[i : i + n] for i in range(len(text) - n + 1))


def _chrf_ngram_precision_recall(
    hypothesis: str,
    reference: str,
    n: int,
) -> tuple[float, float]:
    """
    Compute character n-gram precision and recall for a single (hyp, ref) pair.

    Returns:
        (precision, recall) both in [0, 1].
    """
    hyp_ngrams = _char_ngrams(hypothesis, n)
    ref_ngrams = _char_ngrams(reference, n)

    # Clipped intersection
    matches = sum((hyp_ngrams & ref_ngrams).values())

    total_hyp = sum(hyp_ngrams.values())
    total_ref = sum(ref_ngrams.values())

    precision = matches / total_hyp if total_hyp > 0 else 0.0
    recall = matches / total_ref if total_ref > 0 else 0.0
    return precision, recall


def _chrf_score(
    hypothesis: str,
    reference: str,
    max_n: int = 6,
    beta: float = 2.0,
) -> float:
    """
    Compute chrF score in [0, 100] for one sentence pair.

    chrF = (1 + beta^2) * chrP * chrR / (beta^2 * chrP + chrR)
    where chrP and chrR are averages over n=1..max_n.
    """
    hypothesis = hypothesis.strip()
    reference = reference.strip()

    if not hypothesis or not reference:
        return 0.0

    precisions: list[float] = []
    recalls: list[float] = []

    for n in range(1, max_n + 1):
        if len(hypothesis) < n or len(reference) < n:
            break
        p, r = _chrf_ngram_precision_recall(hypothesis, reference, n)
        precisions.append(p)
        recalls.append(r)

    if not precisions:
        return 0.0

    avg_p = sum(precisions) / len(precisions)
    avg_r = sum(recalls) / len(recalls)

    if avg_p + avg_r == 0.0:
        return 0.0

    beta_sq = beta ** 2
    score = (1 + beta_sq) * avg_p * avg_r / (beta_sq * avg_p + avg_r)
    return score * 100.0


def chrf_sentence(
    hypothesis: str,
    reference: str,
    max_n: int = 6,
    beta: float = 2.0,
) -> float:
    """
    Compute sentence-level chrF score.

    Args:
        hypothesis: Model output string.
        reference:  Gold reference string.
        max_n:      Maximum n-gram order (default 6, matching standard chrF).
        beta:       Beta for F-score (default 2.0 -> recall-weighted).

    Returns:
        chrF score in [0, 100].
    """
    return _chrf_score(hypothesis, reference, max_n=max_n, beta=beta)


def chrf_corpus(
    hypotheses: Sequence[str],
    references: Sequence[str],
    max_n: int = 6,
    beta: float = 2.0,
) -> float:
    """
    Compute corpus-level chrF as the macro-average of sentence-level scores.

    Args:
        hypotheses: Sequence of model output strings.
        references: Sequence of gold reference strings.
        max_n:      Maximum n-gram order (default 6).
        beta:       Beta for F-score (default 2.0).

    Returns:
        Corpus chrF score in [0, 100].

    Raises:
        ValueError: If lengths differ or sequences are empty.
    """
    if len(hypotheses) != len(references):
        raise ValueError(
            f"Length mismatch: hypotheses={len(hypotheses)}, "
            f"references={len(references)}"
        )
    if not hypotheses:
        raise ValueError("Empty sequences passed to chrf_corpus().")
    scores = [
        _chrf_score(h, r, max_n=max_n, beta=beta)
        for h, r in zip(hypotheses, references)
    ]
    return sum(scores) / len(scores)


# ---------------------------------------------------------------------------
# Instruction-following judge
# ---------------------------------------------------------------------------

_JUDGE_SCORE_RE = re.compile(r"\b([0-9]+(?:\.[0-9]+)?)\s*/\s*10\b")
_JUDGE_SCORE_BARE_RE = re.compile(r"\bscore[:\s]+([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE)


def judge_score(
    response: str,
    rubric: str,
    model,  # BaseModel instance — avoids circular import
    *,
    dummy_fixed_score: float = 0.2,
) -> float:
    """
    Use an LLM judge to score an instruction-following response.

    The judge prompt asks for a score in 0–10 format; we normalise to [0, 1].
    If the judge is a DummyModel, return *dummy_fixed_score* immediately
    (no API call needed for end-to-end harness testing).

    Args:
        response:          The model's response text.
        rubric:            Evaluation criteria string from the item.
        model:             A BaseModel instance used as the judge.
        dummy_fixed_score: Score returned when model is DummyModel (default 0.2).

    Returns:
        Score in [0, 1].
    """
    # Short-circuit for offline testing
    if getattr(model, "IS_DUMMY", False):
        return dummy_fixed_score

    judge_prompt = (
        "You are a strict but fair evaluator for Kazakh-language AI outputs.\n\n"
        f"RUBRIC:\n{rubric}\n\n"
        f"MODEL RESPONSE:\n{response}\n\n"
        "Score the response from 0 to 10 based on the rubric. "
        'Reply with ONLY: "Score: X/10" where X is an integer or decimal.'
    )
    judge_output = model.generate(judge_prompt)

    # Parse "X/10" or "Score: X"
    m = _JUDGE_SCORE_RE.search(judge_output)
    if m:
        raw = float(m.group(1))
        return min(max(raw / 10.0, 0.0), 1.0)

    m = _JUDGE_SCORE_BARE_RE.search(judge_output)
    if m:
        raw = float(m.group(1))
        # Could be 0–10 or 0–1; normalise assuming 0–10
        if raw > 1.0:
            raw = raw / 10.0
        return min(max(raw, 0.0), 1.0)

    # Fallback: could not parse; assign 0
    return 0.0
