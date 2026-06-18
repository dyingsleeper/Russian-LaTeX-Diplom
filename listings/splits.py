from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def grouped_train_test_split(
    items: Sequence[T],
    cluster_ids: Sequence[int],
    *,
    test_fraction: float,
    seed: int,
) -> tuple[list[int], list[int]]:
    if len(items) != len(cluster_ids):
        raise ValueError("items and cluster_ids must be the same length")
    clusters = sorted(set(cluster_ids))
    random.Random(seed).shuffle(clusters)
    test_cluster_count = max(1, round(len(clusters) * test_fraction))
    test_clusters = set(clusters[:test_cluster_count])
    train_indices: list[int] = []
    test_indices: list[int] = []
    for index, cluster in enumerate(cluster_ids):
        target = (
            test_indices if cluster in test_clusters else train_indices
        )
        target.append(index)
    return train_indices, test_indices


def stratified_train_test_split(
    items: Sequence[T],
    labels: Sequence[str],
    *,
    test_fraction: float,
    seed: int,
) -> tuple[list[int], list[int]]:
    if len(items) != len(labels):
        raise ValueError("items and labels must be the same length")
    by_label: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        by_label[label].append(index)
    rng = random.Random(seed)
    train_indices: list[int] = []
    test_indices: list[int] = []
    for label in sorted(by_label):
        indices = by_label[label][:]
        rng.shuffle(indices)
        n = len(indices)
        if n == 1:
            train_indices.extend(indices)
            continue
        test_count = min(max(1, round(test_fraction * n)), n - 1)
        test_indices.extend(indices[:test_count])
        train_indices.extend(indices[test_count:])
    return train_indices, test_indices
