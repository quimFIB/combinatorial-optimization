"""Unit 02 lab — simplex, honestly.  REFERENCE SOLUTION, imperative.

Tableau layout, for  max c.x  s.t.  A x <= b, x >= 0  with m rows, n variables:

    rows 0..m-1   [ A | I | b ]        one row per constraint
    row  m        [ -c | 0 | z ]       reduced costs, and the objective value z

Columns 0..n-1 are the original variables, n..n+m-1 the slacks, the last column
the right-hand side. basis[i] is the column basic in row i.
"""

from __future__ import annotations

from colib.lp import Cycling, LPResult


# ---------------------------------------------------------------- step 1 ---

def initial_tableau(A, b, c):
    m, n = len(A), len(c)
    T = [list(A[i]) + [1 if k == i else 0 for k in range(m)] + [b[i]] for i in range(m)]
    T.append([-v for v in c] + [0] * m + [0])
    return T, list(range(n, n + m))


def pivot(T, basis, row, col):
    p = T[row][col]
    T[row] = [v / p for v in T[row]]
    for i in range(len(T)):
        if i != row and T[i][col] != 0:
            f = T[i][col]
            T[i] = [vi - f * vr for vi, vr in zip(T[i], T[row])]
    basis[row] = col
    return T, basis


# ---------------------------------------------------------------- step 2 ---

def entering(T, rule="bland", eps=0):
    z = T[-1]
    candidates = [j for j in range(len(z) - 1) if z[j] < -eps]
    if not candidates:
        return None
    if rule == "bland":
        return candidates[0]
    return min(candidates, key=lambda j: (z[j], j))           # dantzig


def leaving(T, basis, col, rule="bland", eps=0):
    rows = [i for i in range(len(T) - 1) if T[i][col] > eps]
    if not rows:
        return None
    ratio = lambda i: T[i][-1] / T[i][col]
    best = min(ratio(i) for i in rows)
    ties = [i for i in rows if ratio(i) - best <= eps]
    if rule == "bland":
        return min(ties, key=lambda i: basis[i])
    return ties[0]                                             # dantzig: lowest row


# ---------------------------------------------------------------- step 3 ---

def _iterate(T, basis, rule, eps, pivots):
    """Pivot until optimal or unbounded. Returns (status, pivots)."""
    seen = {tuple(basis)}
    while True:
        col = entering(T, rule, eps)
        if col is None:
            return "optimal", pivots
        row = leaving(T, basis, col, rule, eps)
        if row is None:
            return "unbounded", pivots
        pivot(T, basis, row, col)
        pivots += 1
        key = tuple(basis)
        if key in seen:
            raise Cycling(f"basis {key} repeated after {pivots} pivots")
        seen.add(key)


def _result(status, T, basis, n, pivots):
    if status != "optimal":
        return LPResult(status, pivots=pivots, basis=tuple(basis), tableau=T)
    x = [0] * n
    for i, j in enumerate(basis):
        if j < n:
            x[j] = T[i][-1]
    return LPResult("optimal", tuple(x), T[-1][-1], tuple(basis), pivots, T)


def simplex(A, b, c, rule="bland", eps=0):
    if any(v < 0 for v in b):
        raise ValueError("simplex() needs b >= 0; use two_phase() otherwise")
    T, basis = initial_tableau(A, b, c)
    status, pivots = _iterate(T, basis, rule, eps, 0)
    return _result(status, T, basis, len(c), pivots)


# ---------------------------------------------------------------- step 4 ---

def two_phase(A, b, c, rule="bland", eps=0):
    m, n = len(A), len(c)
    neg = [i for i in range(m) if b[i] < 0]
    art = {i: n + m + k for k, i in enumerate(neg)}           # row -> artificial column
    width = n + m + len(neg)

    T, basis = [], []
    for i in range(m):
        sign = -1 if i in art else 1
        row = [sign * v for v in A[i]] + [sign * (1 if k == i else 0) for k in range(m)]
        row += [1 if art.get(i) == n + m + k else 0 for k in range(len(neg))]
        T.append(row + [sign * b[i]])
        basis.append(art.get(i, n + i))
    zero = T[0][0] - T[0][0] if T else 0
    obj = [zero] * width + [zero]
    for i, col in art.items():                                 # max -sum(a): row +1 on a, then price out
        obj[col] += 1
    for i in art:
        obj = [o - v for o, v in zip(obj, T[i])]
    T.append(obj)

    pivots = 0
    if art:
        status, pivots = _iterate(T, basis, rule, eps, 0)
        if T[-1][-1] < -eps:
            return LPResult("infeasible", pivots=pivots, basis=tuple(basis), tableau=T)
        artificial = set(art.values())
        for i in range(m - 1, -1, -1):                         # drive zero-level artificials out
            if basis[i] in artificial:
                col = next((j for j in range(n + m) if abs(T[i][j]) > eps), None)
                if col is None:                                # redundant row
                    del T[i], basis[i]
                else:
                    pivot(T, basis, i, col)
                    pivots += 1

    T = [row[:n + m] + [row[-1]] for row in T]                 # drop artificial columns
    obj = [-v for v in c] + [zero] * m + [zero]
    for i, j in enumerate(basis):
        if obj[j] != 0:
            f = obj[j]
            obj = [o - f * v for o, v in zip(obj, T[i])]
    T[-1] = obj
    status, pivots = _iterate(T, basis, rule, eps, pivots)
    return _result(status, T, basis, n, pivots)


# ---------------------------------------------------------------- step 5 ---

def klee_minty(n):
    """Chvátal's form: max sum 10^(n-j) x_j  s.t.  2 sum_{j<i} 10^(i-j) x_j + x_i <= 100^(i-1)."""
    A = [[2 * 10 ** (i - j) if j < i else (1 if j == i else 0) for j in range(n)] for i in range(n)]
    b = [100 ** i for i in range(n)]
    c = [10 ** (n - 1 - j) for j in range(n)]
    return A, b, c
