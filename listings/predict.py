from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from diplom_ai.classifier.contracts import Prediction, PrototypeWithClass
from diplom_ai.classifier.prototypes import l2_normalize


@dataclass(frozen=True)
class PrototypeMatrix:
    vectors: np.ndarray
    class_names: tuple[str, ...]


def build_prototype_matrix(
    prototypes: list[PrototypeWithClass],
) -> PrototypeMatrix:
    if not prototypes:
        return PrototypeMatrix(
            vectors=np.zeros((0, 0), dtype=np.float32), class_names=()
        )
    vectors = np.vstack(
        [np.asarray(p.vector, dtype=np.float32) for p in prototypes]
    )
    names = tuple(p.class_name for p in prototypes)
    vectors = l2_normalize(vectors)
    return PrototypeMatrix(vectors=vectors, class_names=names)


def predict_one(
    embedding: np.ndarray,
    matrix: PrototypeMatrix,
    *,
    tau: float,
    other_label: str = "other",
) -> Prediction:
    if matrix.vectors.shape[0] == 0:
        return Prediction(label=other_label, score=0.0, class_scores={})

    vec = embedding.astype(np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 0.0:
        vec = vec / norm

    sims = matrix.vectors @ vec  # cosine, both sides normalized
    class_scores: dict[str, float] = {}
    for name, sim in zip(matrix.class_names, sims, strict=True):
        value = float(sim)
        if name not in class_scores or value > class_scores[name]:
            class_scores[name] = value

    best = max(class_scores, key=lambda name: class_scores[name])
    score = class_scores[best]
    label = best if score >= tau else other_label
    return Prediction(label=label, score=score, class_scores=class_scores)
