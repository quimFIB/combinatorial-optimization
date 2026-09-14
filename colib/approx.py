"""Instances and helpers for the approximation units (23, 24, 26).

Metric instances are the shortest-path closure of rounded Euclidean distances: rounding to integers can
break the triangle inequality by one unit, and every guarantee in Part V needs it exactly.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import networkx as nx

from colib.problems import TSP


def metric_closure(dist):
    """All-pairs shortest path lengths (Floyd-Warshall) of a symmetric nonnegative matrix."""
    n = len(dist)
    d = [list(row) for row in dist]
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            row = d[i]
            for j in range(n):
                if dik + dk[j] < row[j]:
                    row[j] = dik + dk[j]
    return tuple(tuple(row) for row in d)


def metric_tsp(n: int, seed=0, side: float = 100.0):
    """n random points in a side x side square; integer distances satisfying the triangle inequality."""
    r = random.Random(seed)
    pts = [(r.uniform(0, side), r.uniform(0, side)) for _ in range(n)]
    return TSP(metric_closure([[int(math.dist(a, b) + 0.5) for b in pts] for a in pts]))


def is_metric(dist) -> bool:
    n = len(dist)
    return all(dist[i][i] == 0 for i in range(n)) and all(
        dist[i][j] == dist[j][i] and dist[i][j] <= dist[i][k] + dist[k][j]
        for i in range(n) for j in range(n) for k in range(n))


def min_weight_perfect_matching(vertices, dist):
    """A minimum-weight perfect matching on an even set of vertices of a complete graph with weights dist,
    as a sorted list of pairs (u, v), u < v. Edmonds' weighted blossom algorithm (networkx): unit 15 built the
    cardinality version, and the weighted one adds dual variables on blossoms to it."""
    vertices = list(vertices)
    assert len(vertices) % 2 == 0, "a perfect matching needs an even number of vertices"
    if not vertices:
        return []
    g = nx.Graph()
    big = 1 + max(dist[u][v] for u in vertices for v in vertices)
    g.add_weighted_edges_from((u, v, big - dist[u][v]) for i, u in enumerate(vertices) for v in vertices[i + 1:])
    m = nx.max_weight_matching(g, maxcardinality=True)
    return sorted(tuple(sorted(e)) for e in m)


def random_processing_times(n: int, seed=0, low: int = 1, high: int = 100):
    r = random.Random(seed)
    return [r.randint(low, high) for _ in range(n)]


def covering_lp(A, c, upper=1.0):
    """min c.x  s.t.  A x >= 1,  0 <= x <= upper, with HiGHS. A is a 0/1 matrix (rows = elements to cover).
    Returns (value, x, y): x the primal as a list of floats, y the row duals (>= 0), so sum(y) == value."""
    from colib.solvers import highs_lp
    import numpy as np
    A = np.asarray(A, float)
    m, n = A.shape
    info = highs_lp(A, np.full(m, np.inf), c, sense="min", row_lower=np.ones(m), lower=0.0,
                    upper=None if upper is None else np.full(n, float(upper)))
    assert info.status == "optimal", info.status
    return info.value, [float(v) for v in info.x], [abs(float(v)) for v in info.row_duals]



@dataclass(frozen=True)
class FacilityLocation:
    """Uncapacitated facility location: open_cost[i] for facility i, dist[i][j] from facility i to client j.
    Distances are integers and metric (the closure of rounded Euclidean distances over facilities and
    clients together)."""
    open_cost: tuple
    dist: tuple

    @property
    def nf(self):
        return len(self.open_cost)

    @property
    def nc(self):
        return len(self.dist[0])

    def cost(self, opened, assign=None):
        """Total cost of opening `opened` and sending each client to assign[j] (default: its nearest open)."""
        opened = sorted(set(opened))
        if assign is None:
            assign = [min(opened, key=lambda i: (self.dist[i][j], i)) for j in range(self.nc)]
        assert all(a in opened for a in assign)
        return sum(self.open_cost[i] for i in opened) + sum(self.dist[assign[j]][j] for j in range(self.nc))

    @classmethod
    def random(cls, nf: int, nc: int, seed=0, side: float = 100.0, cost_low: int = 20, cost_high: int = 120):
        r = random.Random(seed)
        pts = [(r.uniform(0, side), r.uniform(0, side)) for _ in range(nf + nc)]
        closure = metric_closure([[int(math.dist(a, b) + 0.5) for b in pts] for a in pts])
        return cls(tuple(r.randint(cost_low, cost_high) for _ in range(nf)),
                   tuple(tuple(closure[i][nf + j] for j in range(nc)) for i in range(nf)))

    def milp(self):
        """y_i (open, integer), x_ij (assign): min sum f y + sum d x, sum_i x_ij = 1, x_ij <= y_i."""
        from colib.mip import MILP
        nf, nc = self.nf, self.nc
        nv = nf + nf * nc
        X = lambda i, j: nf + i * nc + j
        c = tuple(self.open_cost) + tuple(self.dist[i][j] for i in range(nf) for j in range(nc))
        A_eq = tuple(tuple(1 if k in {X(i, j) for i in range(nf)} else 0 for k in range(nv)) for j in range(nc))
        A_ub = tuple(tuple(1 if k == X(i, j) else -1 if k == i else 0 for k in range(nv))
                     for i in range(nf) for j in range(nc))
        return MILP(c=c, A_ub=A_ub, b_ub=(0,) * len(A_ub), A_eq=A_eq, b_eq=(1,) * nc, ub=(1,) * nv,
                    integer=(True,) * nf + (False,) * (nf * nc))   # integral y makes some optimal x integral
