"""Symmetric TSP as an edge-variable MILP (units 09, 11, 23, 26).

Edges of the complete graph on n vertices are indexed in the order of
itertools.combinations(range(n), 2). x_e = 1 if edge e is in the tour.
"""

from __future__ import annotations

from itertools import combinations

from colib.mip import MILP
from colib.problems import TSP


def edges(n: int):
    return list(combinations(range(n), 2))


def edge_index(n: int):
    return {e: k for k, e in enumerate(edges(n))}


def degree_milp(tsp: TSP, integer: bool) -> MILP:
    """min sum c_e x_e  s.t.  sum_{e incident to v} x_e = 2 for every v,  0 <= x_e <= 1."""
    n = tsp.n
    E = edges(n)
    A_eq = tuple(tuple(1 if v in e else 0 for e in E) for v in range(n))
    return MILP(c=tuple(tsp.dist[i][j] for i, j in E), A_eq=A_eq, b_eq=(2,) * n,
                ub=(1,) * len(E), integer=(integer,) * len(E))


def tour_length(tsp: TSP, order) -> int:
    return sum(tsp.dist[order[k]][order[(k + 1) % len(order)]] for k in range(len(order)))


def tour_from_edges(n: int, x, tol: float = 0.5):
    """The vertex order of the tour chosen by a 0/1 edge vector, or None if the
    chosen edges do not form a single Hamiltonian cycle."""
    adj = {v: [] for v in range(n)}
    for (i, j), v in zip(edges(n), x):
        if v > tol:
            adj[i].append(j)
            adj[j].append(i)
    if any(len(a) != 2 for a in adj.values()):
        return None
    order, prev = [0], None
    while True:
        cur = order[-1]
        nxt = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
        if nxt == 0:
            break
        order.append(nxt)
        prev = cur
        if len(order) > n:
            return None
    return order if len(order) == n else None
