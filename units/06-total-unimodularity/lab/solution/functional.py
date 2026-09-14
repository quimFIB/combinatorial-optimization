"""Unit 06 lab — total unimodularity.  REFERENCE SOLUTION, functional.

Both TU tests are quantifiers over finite sets, which is to say `all` and `any`
over `combinations` and `product`. The odd-cycle search is BFS written as an
unfold over frontiers, then two walks up a parent map.
"""

from __future__ import annotations

from fractions import Fraction
from functools import reduce
from itertools import chain, combinations, product, takewhile

import numpy as np
import toolz as tz

from colib.solvers import highs_lp


def det_exact(M):
    """Determinant by exact Gaussian elimination over Fractions, as a fold over pivots."""
    n = len(M)

    def eliminate(state, k):
        rows, det = state
        if det == 0:
            return state
        pivot = next((i for i in range(k, n) if rows[i][k] != 0), None)
        if pivot is None:
            return rows, Fraction(0)
        rows = rows[:k] + (rows[pivot],) + tuple(r for i, r in enumerate(rows) if i >= k and i != pivot)
        p = rows[k]
        det = det * p[k] * (-1 if pivot != k else 1)
        below = tuple(tuple(v - r[k] / p[k] * pv for v, pv in zip(r, p)) for r in rows[k + 1:])
        return rows[:k + 1] + below, det

    rows = tuple(tuple(Fraction(v) for v in r) for r in M)
    return reduce(eliminate, range(n), (rows, Fraction(1)))[1]


# ---------------------------------------------------------------- step 1 ---

def is_tu(A) -> bool:
    m, n = len(A), len(A[0]) if A else 0
    squares = ((rows, cols) for k in range(1, min(m, n) + 1)
               for rows in combinations(range(m), k) for cols in combinations(range(n), k))
    return all(det_exact([[A[i][j] for j in cols] for i in rows]) in (-1, 0, 1) for rows, cols in squares)


# ---------------------------------------------------------------- step 2 ---

def ghouila_houri(A):
    m, n = len(A), len(A[0]) if A else 0
    equitable = lambda rows, sigma: all(abs(sum(s * A[r][j] for s, r in zip(sigma, rows))) <= 1
                                        for j in range(n))
    has_signing = lambda rows: any(equitable(rows, (1,) + signs)
                                   for signs in product((1, -1), repeat=len(rows) - 1))
    subsets = chain.from_iterable(combinations(range(m), k) for k in range(1, m + 1))
    return next((rows for rows in subsets if not has_signing(rows)), None)


# ---------------------------------------------------------------- step 3 ---

def incidence_matrix(n, edges):
    return [[int(v in e) for e in edges] for v in range(n)]


def interval_matrix(n, intervals):
    return [[int(a <= j < b) for j in range(n)] for a, b in intervals]


# ---------------------------------------------------------------- step 4 ---

def assignment_lp(cost):
    n = len(cost)
    rows = ([int(k // n == i) for k in range(n * n)] for i in range(n))
    cols = ([int(k % n == j) for k in range(n * n)] for j in range(n))
    b = [1] * (2 * n)
    res = highs_lp(list(chain(rows, cols)), b, [v for row in cost for v in row], sense="min", row_lower=b)
    return np.array(res.x).reshape(n, n)


# ---------------------------------------------------------------- step 5 ---

def bfs_tree(n, adj):
    """(parent, depth) of a BFS forest, as an unfold over frontiers."""
    def grow(state):
        parent, depth, frontier = state
        new = {w: u for u in frontier for w in adj[u] if w not in depth}
        nxt = tuple(dict.fromkeys(new))
        return ({**parent, **new}, {**depth, **{w: depth[new[w]] + 1 for w in nxt}}, nxt)

    def component(state, s):
        parent, depth = state
        if s in depth:
            return state
        start = ({**parent, s: None}, {**depth, s: 0}, (s,))
        final = tz.last(takewhile(lambda st: st[2], tz.iterate(grow, start)))
        return final[0], final[1]

    return reduce(component, range(n), ({}, {}))


def odd_cycle(n, edges):
    adj = {v: tuple(w for e in edges for w in e if v in e and w != v) for v in range(n)}
    parent, depth = bfs_tree(n, adj)
    clash = next(((u, w) for u, w in edges if depth[u] % 2 == depth[w] % 2), None)
    if clash is None:
        return None
    up = lambda v: list(takewhile(lambda x: x is not None, tz.iterate(lambda x: parent[x], v)))
    left, right = up(clash[0]), up(clash[1])
    ancestors = set(left) & set(right)
    lca = next(v for v in left if v in ancestors)
    left, right = left[:left.index(lca) + 1], right[:right.index(lca)]
    return left + right[::-1]


def fractional_matching_on_cycle(cycle):
    k = len(cycle)
    return {frozenset((cycle[i], cycle[(i + 1) % k])): 0.5 for i in range(k)}
