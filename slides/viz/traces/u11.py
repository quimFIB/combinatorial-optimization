"""Unit 11's recorded runs, for units/11-lagrangian-relaxation/explore.html.

The subgradient steps call unit 11's reference `subgradient_ascent` (with an oracle for the
deck's three-variable example that logs each multiplier it is asked about), and the
Held–Karp runs call the reference `one_tree` and `held_karp_bound`. The L(u) curve itself
is computed in the page from the costs and weights written there.
`uv run co viz 11` writes units/11-lagrangian-relaxation/viz-data.js.
"""

from __future__ import annotations

import itertools
import math

from colib import ref
from colib.problems import TSP, _rng

L = ref.unit("11")

C, W, B = [3, 5, 4], [2, 4, 3], 5          # min c.x  s.t.  w.x >= b,  x in {0,1}^3  (the deck's example)
UPPER = 7                                  # the integer optimum, used as the Polyak target


def lagrangian(u):
    x = [1 if c - u * w < 0 else 0 for c, w in zip(C, W)]
    value = u * B + sum((c - u * w) * xi for c, w, xi in zip(C, W, x))
    return value, x, B - sum(w * xi for w, xi in zip(W, x))


def subgradient_run(patience, lam=1.0, iterations=12):
    log = []

    def oracle(mult):
        value, x, g = lagrangian(mult[0])
        log.append({"u": mult[0], "L": value, "x": x, "g": g})
        return value, x, [g]

    best, _, _ = L.subgradient_ascent(oracle, [0.0], UPPER, iterations=iterations, lam=lam, patience=patience,
                                      project=lambda m: [max(0.0, m[0])])
    running = -math.inf
    for s in log:
        running = max(running, s["L"])
        s["best"] = running
    return log


def one_tree_run(dist, upper, iterations=60):
    log = []

    def oracle(pi):
        value, deg, edges = L.one_tree(dist, pi)
        log.append({"pi": list(pi), "L": value, "degrees": deg, "edges": [list(e) for e in edges]})
        return value, edges, [d - 2 for d in deg]

    L.subgradient_ascent(oracle, [0.0] * len(dist), upper, iterations)
    running = -math.inf
    for s in log:
        running = max(running, s["L"])
        s["best"] = running
        s["tour"] = all(d == 2 for d in s["degrees"])
    return log


def tsp_points(n, seed):
    r = _rng(seed)                          # the same draws TSP.random makes
    return [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(n)]


def optimum(dist):
    n = len(dist)
    return min(sum(dist[p[i]][p[(i + 1) % n]] for i in range(n)) for p in ([0] + list(q) for q in itertools.permutations(range(1, n))))


def data():
    five = [[0, 4, 5, 3, 2], [4, 0, 3, 5, 2], [5, 3, 0, 4, 3], [3, 5, 4, 0, 3], [2, 2, 3, 3, 0]]
    seven = TSP.random(7, seed=2)
    pts7 = tsp_points(7, 2)
    assert tuple(tuple(int(math.dist(a, b) + 0.5) for b in pts7) for a in pts7) == seven.dist
    return {
        "example": {"c": C, "w": W, "b": B, "upper": UPPER},
        "subgradient": [
            {"title": "λ = 1 fixed", "states": subgradient_run(patience=10 ** 9)},
            {"title": "λ = 1, halved after each step without a new best", "states": subgradient_run(patience=1)},
        ],
        "heldkarp": [
            {"title": "The deck's five cities (optimal tour 14)", "dist": five, "optimum": optimum(five),
             "points": [[20, 50], [55, 85], [85, 60], [60, 15], [45, 45]], "layout": "abstract",
             "states": one_tree_run(five, optimum(five))},
            {"title": "Seven random cities, TSP.random(7, seed=2)", "dist": [list(r) for r in seven.dist],
             "optimum": optimum(seven.dist), "points": [list(p) for p in pts7], "layout": "euclidean",
             "states": one_tree_run(seven.dist, optimum(seven.dist))},
        ],
    }
