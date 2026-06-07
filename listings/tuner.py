from __future__ import annotations

import numpy as np

from diplom_ai.clustering.pipeline import (
    HdbscanParams,
    TunerConfig,
    hdbscan_inputs_for_metric,
)


def find_optimal_hdbscan_params(
    matrix: np.ndarray,
    tuner: TunerConfig,
    random_seed: int,
    metric: str,
    cluster_selection_method: str,
) -> HdbscanParams:
    import hdbscan  # type: ignore[import-untyped]
    import optuna
    from hdbscan.validity import validity_index  # type: ignore[import-untyped]
    from loguru import logger
    from sklearn.metrics import pairwise_distances  # type: ignore[import-untyped]

    optuna.logging.set_verbosity(optuna.logging.INFO)

    cluster_matrix, eff_metric = hdbscan_inputs_for_metric(matrix, metric)
    n = len(cluster_matrix)
    mcs_low = max(5, n // 200)
    mcs_high = max(10, n // 20)

    distance_matrix = pairwise_distances(
        cluster_matrix.astype(np.float64), metric=eff_metric
    )

    def objective(trial: optuna.Trial) -> float:
        mcs = trial.suggest_int("min_cluster_size", mcs_low, mcs_high)
        ms = trial.suggest_int("min_samples", 1, min(15, mcs))

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=mcs,
            min_samples=ms,
            metric=eff_metric,
            cluster_selection_method=cluster_selection_method,
        )
        labels = clusterer.fit_predict(cluster_matrix)

        mask = labels != -1
        unique_clusters = set(labels[mask].tolist())
        n_clusters = len(unique_clusters)
        n_noise = int((~mask).sum())
        noise_ratio = n_noise / n

        if n_clusters >= 2:
            dbcv = float(
                validity_index(distance_matrix, labels, metric="precomputed", d=2)
            )
        else:
            dbcv = -1.0
        trial.set_user_attr("dbcv", dbcv)
        trial.set_user_attr("n_clusters", n_clusters)
        trial.set_user_attr("noise_ratio", noise_ratio)

        if n_clusters < tuner.n_clusters_min:
            trial.set_user_attr("infeasible_reason", "n_clusters_below_min")
            return -1.0
        if n_clusters > tuner.n_clusters_max:
            trial.set_user_attr("infeasible_reason", "n_clusters_above_max")
            return -1.0
        if noise_ratio > tuner.noise_ratio_cap:
            trial.set_user_attr("infeasible_reason", "noise_ratio_above_cap")
            return -1.0

        _, counts = np.unique(labels[mask], return_counts=True)
        median_size = float(np.median(counts))
        trial.set_user_attr("median_size", median_size)
        if median_size < tuner.median_size_min:
            trial.set_user_attr("infeasible_reason", "median_size_below_min")
            return -1.0

        mean_persistence = float(np.mean(clusterer.cluster_persistence_))
        # probabilities_ для noise точек равны 0 — усредняем только по
        # назначенным, чтобы шумовой штраф не дублировался ниже через
        # mean_membership.
        mean_membership = float(np.mean(clusterer.probabilities_[mask]))
        noise_excess = max(0.0, noise_ratio - tuner.noise_soft_threshold)

        score = (
            dbcv
            + tuner.persistence_weight * mean_persistence
            + tuner.membership_weight * mean_membership
            - tuner.noise_penalty_weight * noise_excess
        )
        trial.set_user_attr("mean_persistence", mean_persistence)
        trial.set_user_attr("mean_membership", mean_membership)
        trial.set_user_attr("score", score)
        return score

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=random_seed),
    )
    study.optimize(objective, n_trials=tuner.n_trials)

    best = study.best_trial
    if best.value == -1.0:
        candidates = [
            t for t in study.trials
            if t.user_attrs.get("dbcv", -1.0) > -1.0
        ]
        if candidates:
            best = max(candidates, key=lambda t: t.user_attrs["dbcv"])

    logger.info(
        "hdbscan tuning complete mcs={} ms={} score={:.4f} dbcv={:.4f} "
        "n_clusters={} noise_ratio={:.3f} median_size={:.1f}",
        best.params["min_cluster_size"],
        best.params["min_samples"],
        best.value,
        best.user_attrs.get("dbcv", float("nan")),
        best.user_attrs.get("n_clusters", 0),
        best.user_attrs.get("noise_ratio", float("nan")),
        best.user_attrs.get("median_size", float("nan")),
    )

    return HdbscanParams(
        min_cluster_size=int(best.params["min_cluster_size"]),
        min_samples=int(best.params["min_samples"]),
        metric=metric,
        cluster_selection_method=cluster_selection_method,
    )
