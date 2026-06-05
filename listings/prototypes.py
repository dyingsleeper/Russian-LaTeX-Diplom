from __future__ import annotations

import numpy as np


def l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalization; zero rows are left as zeros."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    normalized: np.ndarray = matrix / norms
    return normalized


def build_class_prototypes(
    vectors: np.ndarray,
    *,
    max_per_class: int,
    min_support_per_prototype: int,
    random_seed: int,
) -> np.ndarray:
    """Return 1..k L2-normalized centroids for one class.

    Small classes collapse to a single centroid. Larger classes are
    sub-clustered with KMeans into k = min(max_per_class,
    n // min_support_per_prototype) prototypes so multimodal classes are not
    smeared into one point.
    """
    normalized = l2_normalize(vectors.astype(np.float32))
    n = normalized.shape[0]
    k = min(max_per_class, n // max(min_support_per_prototype, 1))
    if k <= 1:
        centroid = normalized.mean(axis=0, keepdims=True)
        return l2_normalize(centroid)

    from sklearn.cluster import KMeans  # type: ignore[import-untyped]

    labels = KMeans(n_clusters=k, random_state=random_seed, n_init=10).fit_predict(
        normalized
    )
    centroids = np.vstack(
        [normalized[labels == c].mean(axis=0) for c in sorted(set(labels))]
    )
    return l2_normalize(centroids)


def class_conflicts(
    prototypes_by_class: dict[str, np.ndarray],
    *,
    threshold: float,
) -> list[tuple[str, str, float]]:
    """Report class pairs whose closest prototypes are >= threshold apart.

    Each input matrix is assumed L2-normalized, so a dot product is cosine
    similarity. Returns (class_a, class_b, max_similarity) sorted descending.
    """
    names = sorted(prototypes_by_class)
    conflicts: list[tuple[str, str, float]] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = prototypes_by_class[names[i]]
            b = prototypes_by_class[names[j]]
            sim = float((a @ b.T).max())
            if sim >= threshold:
                conflicts.append((names[i], names[j], sim))
    conflicts.sort(key=lambda triple: triple[2], reverse=True)
    return conflicts
