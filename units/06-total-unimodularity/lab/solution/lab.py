"""Unit 06 lab — total unimodularity.  REFERENCE SOLUTION, imperative.

Matrices are lists of lists of small integers. Everything is exact.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations, product

import numpy as np

from colib.solvers import highs_lp


def det_int(M) -> int:
    """Exact integer determinant by Bareiss fraction-free elimination."""
    M = [list(r) for r in M]
    n = len(M)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if M[i][k] != 0), None)
            if swap is None:
                return 0
            M[k], M[swap] = M[swap], M[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


# ---------------------------------------------------------------- step 1 ---

def is_tu(A) -> bool:
    m, n = len(A), len(A[0]) if A else 0
    if any(v not in (-1, 0, 1) for row in A for v in row):
        return False
    for k in range(2, min(m, n) + 1):
        for rows in combinations(range(m), k):
            for cols in combinations(range(n), k):
                if det_int([[A[i][j] for j in cols] for i in rows]) not in (-1, 0, 1):
                    return False
    return True


# ---------------------------------------------------------------- step 2 ---

def ghouila_houri(A):
    """Return None if every row subset has an equitable signing (A is TU),
    else a row subset (tuple of row indices) that has none."""
    m, n = len(A), len(A[0]) if A else 0
    for k in range(1, m + 1):
        for rows in combinations(range(m), k):
            ok = False
            for signs in product((1, -1), repeat=k - 1):
                sigma = (1,) + signs                # the first sign can be fixed: negate all
                if all(abs(sum(s * A[r][j] for s, r in zip(sigma, rows))) <= 1 for j in range(n)):
                    ok = True
                    break
            if not ok:
                return rows
    return None


# ---------------------------------------------------------------- step 3 ---

def incidence_matrix(n, edges):
    """Vertex-edge incidence matrix: row v, column e is 1 if v is an endpoint of e."""
    M = [[0] * len(edges) for _ in range(n)]
    for e, (u, v) in enumerate(edges):
        M[u][e] = 1
        M[v][e] = 1
    return M


def interval_matrix(n, intervals):
    """Rows are the given half-open intervals [a, b) of columns 0..n-1: consecutive ones."""
    return [[1 if a <= j < b else 0 for j in range(n)] for a, b in intervals]


# ---------------------------------------------------------------- step 4 ---

def assignment_lp(cost):
    """Solve the assignment LP (no integrality!) with HiGHS's simplex and return
    the n x n solution matrix as floats."""
    n = len(cost)
    A_eq = []
    for i in range(n):                                   # each worker once
        A_eq.append([1 if k // n == i else 0 for k in range(n * n)])
    for j in range(n):                                   # each job once
        A_eq.append([1 if k % n == j else 0 for k in range(n * n)])
    b = [1] * (2 * n)
    c = [cost[i][j] for i in range(n) for j in range(n)]
    res = highs_lp(A_eq, b, c, sense="min", row_lower=b)
    return np.array(res.x).reshape(n, n)


# ---------------------------------------------------------------- step 5 ---

def odd_cycle(n, edges):
    """An odd cycle as a list of vertices [v0, v1, ..., vk-1] (consecutive ones
    adjacent, and vk-1 adjacent to v0), or None if the graph is bipartite."""
    adj = {v: [] for v in range(n)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent, depth = {}, {}
    for s in range(n):
        if s in depth:
            continue
        parent[s], depth[s] = None, 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for w in adj[u]:
                if w not in depth:
                    parent[w], depth[w] = u, depth[u] + 1
                    queue.append(w)
                elif depth[w] % 2 == depth[u] % 2:      # same side of the 2-colouring
                    a, b = u, w
                    left, right = [a], [b]
                    while depth[a] > depth[b]:
                        a = parent[a]
                        left.append(a)
                    while depth[b] > depth[a]:
                        b = parent[b]
                        right.append(b)
                    while a != b:                       # climb together to the common ancestor
                        a, b = parent[a], parent[b]
                        left.append(a)
                        right.append(b)
                    return left + right[-2::-1]          # u .. ancestor .. w, and w is adjacent to u
    return None


def fractional_matching_on_cycle(cycle):
    """The half-integral LP vertex on an odd cycle: 1/2 on each cycle edge,
    as a dict {frozenset({u, v}): 0.5}."""
    k = len(cycle)
    return {frozenset((cycle[i], cycle[(i + 1) % k])): 0.5 for i in range(k)}
