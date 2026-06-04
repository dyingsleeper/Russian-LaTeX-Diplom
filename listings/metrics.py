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
