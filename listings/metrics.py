from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def classification_metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, Any]:
    from sklearn.metrics import accuracy_score, f1_score  # type: ignore[import-untyped]

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def coverage(predictions: Sequence[str], *, other_label: str = "other") -> float:
    if not predictions:
        return 0.0
    accepted = sum(1 for p in predictions if p != other_label)
    return accepted / len(predictions)


def other_rate(predictions: Sequence[str], *, other_label: str = "other") -> float:
    if not predictions:
        return 0.0
    return sum(1 for p in predictions if p == other_label) / len(predictions)


def per_class_metrics(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> dict[str, dict[str, float]]:
    from sklearn.metrics import precision_recall_fscore_support

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(labels), zero_division=0
    )
    return {
        label: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(labels)
    }


def confusion_matrix_labeled(
    y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]
) -> list[list[int]]:
    from sklearn.metrics import confusion_matrix

    matrix = confusion_matrix(y_true, y_pred, labels=list(labels))
    result: list[list[int]] = matrix.tolist()
    return result


def threshold_sweep(
    y_true: Sequence[str],
    probabilities: Sequence[Sequence[float]],
    labels: Sequence[str],
    *,
    thresholds: Sequence[float],
    other_label: str = "other",
) -> list[dict[str, Any]]:
    from sklearn.metrics import f1_score

    rows: list[dict[str, Any]] = []
    for tau in thresholds:
        predictions: list[str] = []
        for probs in probabilities:
            best_index = max(range(len(probs)), key=lambda i: probs[i])
            predictions.append(
                labels[best_index] if probs[best_index] >= tau else other_label
            )
        rows.append(
            {
                "tau": tau,
                "coverage": coverage(predictions, other_label=other_label),
                "other_rate": other_rate(predictions, other_label=other_label),
                "macro_f1": float(
                    f1_score(y_true, predictions, average="macro", zero_division=0)
                ),
            }
        )
    return rows
