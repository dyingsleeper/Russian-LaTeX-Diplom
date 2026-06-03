"""Synthetic-data figures for Chapter 1 (mutual reachability, DBCV density validity).

Run with the diplom2.0 venv:
    /home/dyingsleeper/PycharmProjects/diplom2.0/.venv/bin/python \
        Dissertation/images/synthetic_plots.py

Outputs (vector PDF, grayscale, print-friendly):
    Dissertation/images/hdbscan_mreach.pdf
    Dissertation/images/dbcv_density_validity.pdf
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402
from scipy.sparse.csgraph import minimum_spanning_tree  # noqa: E402
from scipy.spatial.distance import cdist  # noqa: E402

OUT = Path(__file__).resolve().parent
plt.rcParams.update(
    {
        "font.size": 11,
        "font.family": "serif",
        "mathtext.fontset": "dejavuserif",
        "axes.linewidth": 0.8,
    }
)
GREY = "0.45"
DARK = "0.10"


def core_distance(points: np.ndarray, m: int) -> np.ndarray:
    """Distance to the m-th nearest neighbour (column 0 is self == 0.0)."""
    d = cdist(points, points)
    d.sort(axis=1)
    return d[:, m]


def mutual_reachability(points: np.ndarray, m: int) -> np.ndarray:
    d = cdist(points, points)
    dc = core_distance(points, m)
    mreach = np.maximum(np.maximum(d, dc[:, None]), dc[None, :])
    np.fill_diagonal(mreach, 0.0)
    return mreach


def fig_mreach() -> None:
    rng = np.random.default_rng(11)
    dense = rng.normal(loc=[0.0, 0.0], scale=0.20, size=(8, 2))
    b = np.array([2.3, 0.7])  # point in a sparse region => large core distance
    pts = np.vstack([dense, b])
    m = 3
    dc = core_distance(pts, m)

    a_idx = int(np.argmax(dense[:, 0]))  # rightmost dense point, closest to b
    b_idx = len(pts) - 1
    a = pts[a_idx]
    d_ab = float(np.linalg.norm(a - b))
    dmreach = max(dc[a_idx], dc[b_idx], d_ab)

    arrow = {"arrowstyle": "-", "color": GREY, "lw": 0.9}
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    ax.scatter(dense[:, 0], dense[:, 1], s=26, c="white", edgecolors=DARK, zorder=3)
    for idx, lab, off in ((a_idx, "$a$", (8, 8)), (b_idx, "$b$", (8, 8))):
        ax.scatter(*pts[idx], s=48, c=DARK, zorder=4)
        ax.annotate(lab, pts[idx], textcoords="offset points", xytext=off, fontsize=13)
    for idx in (a_idx, b_idx):
        ax.add_patch(
            Circle(pts[idx], dc[idx], fill=False, ls=":", ec=GREY, lw=1.2, zorder=2)
        )
    # core-distance labels with leader lines into empty space
    ax.annotate(
        r"$d_{\mathrm{core}}(a)$", xy=(a[0], a[1] - dc[a_idx]), xytext=(-1.0, -1.15),
        ha="center", color=GREY, arrowprops=arrow,
    )
    ax.annotate(
        r"$d_{\mathrm{core}}(b)$", xy=(b[0] + dc[b_idx], b[1]), xytext=(3.1, -1.15),
        ha="center", color=GREY, arrowprops=arrow,
    )
    ax.plot([a[0], b[0]], [a[1], b[1]], color=DARK, lw=1.4, zorder=2)
    mid = (a + b) / 2
    ax.annotate(r"$d(a,b)$", mid, textcoords="offset points", xytext=(0, 9), ha="center")
    ax.set_title(
        r"$d_{\mathrm{mreach}}(a,b)=\max\{d_{\mathrm{core}}(a),"
        r"d_{\mathrm{core}}(b),d(a,b)\}=" + f"{dmreach:.2f}$",
        fontsize=12,
    )
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.margins(0.18)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "hdbscan_mreach.pdf")
    plt.close(fig)


def fig_dbcv() -> None:
    rng = np.random.default_rng(3)
    c1 = rng.normal(loc=[0.0, 0.0], scale=0.24, size=(14, 2))
    c2 = rng.normal(loc=[2.6, 0.1], scale=0.24, size=(14, 2))
    pts = np.vstack([c1, c2])
    labels = np.array([0] * len(c1) + [1] * len(c2))
    m = 3
    mreach = mutual_reachability(pts, m)

    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    markers = {0: "o", 1: "s"}
    for lab in (0, 1):
        mask = labels == lab
        ax.scatter(
            pts[mask, 0], pts[mask, 1], s=26, c="white",
            edgecolors=DARK, marker=markers[lab], zorder=3,
        )

    dsc_edges = []
    for lab in (0, 1):
        idx = np.where(labels == lab)[0]
        sub = mreach[np.ix_(idx, idx)]
        mst = minimum_spanning_tree(sub).toarray()
        for i in range(len(idx)):
            for j in range(len(idx)):
                if mst[i, j] > 0:
                    ax.plot(
                        pts[[idx[i], idx[j]], 0], pts[[idx[i], idx[j]], 1],
                        color=GREY, lw=0.8, zorder=1,
                    )
        fi, fj = np.unravel_index(np.argmax(mst), mst.shape)
        dsc_edges.append((idx[fi], idx[fj], mst[fi, fj]))
    dsc = max(dsc_edges, key=lambda e: e[2])
    ax.plot(
        pts[[dsc[0], dsc[1]], 0], pts[[dsc[0], dsc[1]], 1],
        color=DARK, lw=2.4, zorder=2,
    )
    ax.annotate(
        "DSC", (pts[dsc[0]] + pts[dsc[1]]) / 2,
        textcoords="offset points", xytext=(0, 8), ha="center",
    )

    cross = mreach[np.ix_(np.where(labels == 0)[0], np.where(labels == 1)[0])]
    ci, cj = np.unravel_index(np.argmin(cross), cross.shape)
    p0 = pts[np.where(labels == 0)[0][ci]]
    p1 = pts[np.where(labels == 1)[0][cj]]
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=DARK, lw=2.0, ls="--", zorder=2)
    ax.annotate(
        "DSPC", (p0 + p1) / 2, textcoords="offset points", xytext=(0, -14), ha="center"
    )

    ax.set_title(
        r"$V(C_i)=\dfrac{\mathrm{DSPC}-\mathrm{DSC}}{\max\{\mathrm{DSPC},\mathrm{DSC}\}}$",
        fontsize=12,
    )
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "dbcv_density_validity.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_mreach()
    fig_dbcv()
    print("wrote", OUT / "hdbscan_mreach.pdf")
    print("wrote", OUT / "dbcv_density_validity.pdf")
