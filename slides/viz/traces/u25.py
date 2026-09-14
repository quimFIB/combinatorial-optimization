"""Unit 25's recorded data, for units/25-semidefinite/explore.html.

Goemans–Williamson: the reference `maxcut_sdp` and `vectors_from_gram` on odd cycles and a
triangle, whose optimal vectors lie in a plane, drawn in that plane, and one random graph whose
vectors do not (histogram only); the exact expected cut
from `expected_cut`; and 2000 seeded runs of the reference `hyperplane_round` recorded as a
histogram of cut sizes. The optimum is by brute force. `co viz 25` writes the data file.
"""

from __future__ import annotations

from itertools import product

import numpy as np

from colib import ref
from colib.problems import MaxCut

L = ref.unit("25")
ROUNDS = 2000


def cycle(n):
    return MaxCut(n, tuple((i, (i + 1) % n) for i in range(n)), (1,) * n)


def run(title, mc, seed):
    value, X = L.maxcut_sdp(mc)
    V = L.vectors_from_gram(X)
    vals, vecs = np.linalg.eigh((X + X.T) / 2)
    rank = int((vals > 1e-4).sum())
    # coordinates in the plane spanned by the top two eigenvectors, rotated so vertex 0 points along +x
    P = vecs[:, -2:] * np.sqrt(np.clip(vals[-2:], 0, None))
    P = P / np.linalg.norm(P, axis=1, keepdims=True)
    ang0 = np.arctan2(P[0, 1], P[0, 0])
    R = np.array([[np.cos(-ang0), -np.sin(-ang0)], [np.sin(-ang0), np.cos(-ang0)]])
    P = P @ R.T
    if mc.n > 1 and P[1, 1] < 0:
        P[:, 1] *= -1                                   # vertex 1 above the axis, for a stable picture
    rng = np.random.default_rng(seed)
    hist = {}
    for _ in range(ROUNDS):
        x = L.hyperplane_round(V, rng)
        w = sum(wt for (u, v), wt in zip(mc.edges, mc.weights) if x[u] != x[v])
        hist[w] = hist.get(w, 0) + 1
    opt = max(sum(wt for (u, v), wt in zip(mc.edges, mc.weights) if x[u] != x[v])
              for x in product((0, 1), repeat=mc.n))
    planar = rank <= 2
    return {"title": title, "n": mc.n, "planar": planar, "rank": rank, "edges": [list(e) for e in mc.edges], "weights": list(mc.weights),
            "vectors": P.round(6).tolist() if planar else None, "sdp": value, "expected": L.expected_cut(mc, V), "opt": opt,
            "gram_offdiag": float(X[0, 1]), "hist": {str(k): v for k, v in sorted(hist.items())}, "rounds": ROUNDS,
            "alpha": L.gw_constant(20_000)[0]}


def data():
    return {"gw": [run("the 5-cycle (the deck's)", cycle(5), 0),
                   run("the triangle", cycle(3), 1),
                   run("the 7-cycle", cycle(7), 2),
                   run("a random weighted graph on 8 vertices", MaxCut.random(8, seed=3), 3)]}
