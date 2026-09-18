"""Unit 03 lab — duality.  REFERENCE SOLUTION, imperative.

Steps 2–5 work on the tableau your unit-02 simplex returns
(`LPResult.tableau`, layout [A | I | b] over [-c | 0 | z]), for LPs of the form
max c.x, A x <= b, x >= 0 with m constraints and n variables.
"""

from __future__ import annotations

from colib import ref
from colib.lp import GeneralLP, LPResult

simplex = ref.unit("02")          # reference two_phase and pivot; CO_MINE=02 uses yours


# ---------------------------------------------------------------- step 1 ---

def dual(lp: GeneralLP) -> GeneralLP:
    # For a max primal: constraint <= -> y >= 0, >= -> y <= 0, = -> free;
    #                   x >= 0 -> dual constraint >=, x <= 0 -> <=, free -> =.
    # For a min primal every sign flips.
    flip = {"max": False, "min": True}[lp.sense]
    row_to_sign = {"<=": ">=0", ">=": "<=0", "=": "free"}
    sign_to_row = {">=0": ">=", "<=0": "<=", "free": "="}
    other = {">=0": "<=0", "<=0": ">=0", "free": "free", ">=": "<=", "<=": ">=", "=": "="}

    signs = []
    for s in lp.senses:
        y = row_to_sign[s]
        signs.append(other[y] if flip else y)
    senses = []
    for s in lp.signs:
        r = sign_to_row[s]
        senses.append(other[r] if flip else r)
    At = tuple(tuple(lp.A[i][j] for i in range(lp.m)) for j in range(lp.n))
    return GeneralLP("min" if lp.sense == "max" else "max", tuple(lp.b), At,
                     tuple(senses), tuple(lp.c), tuple(signs))


# ---------------------------------------------------------------- step 2 ---

def duals_from_tableau(res: LPResult, n: int, m: int):
    if res.status != "optimal":
        raise ValueError(f"no duals for a {res.status} LP")
    z = res.tableau[-1]
    return tuple(z[n + i] for i in range(m))


# ---------------------------------------------------------------- step 3 ---

def certify_optimal(A, b, c, x, y) -> tuple[bool, str]:
    m, n = len(A), len(c)
    if any(v < 0 for v in x):
        return False, "x has a negative entry"
    for i in range(m):
        if sum(A[i][j] * x[j] for j in range(n)) > b[i]:
            return False, f"primal constraint {i} violated"
    if any(v < 0 for v in y):
        return False, "y has a negative entry"
    for j in range(n):
        if sum(A[i][j] * y[i] for i in range(m)) < c[j]:
            return False, f"dual constraint {j} violated"
    for i in range(m):
        slack = b[i] - sum(A[i][j] * x[j] for j in range(n))
        if y[i] != 0 and slack != 0:
            return False, f"complementary slackness fails on primal constraint {i}"
    for j in range(n):
        reduced = sum(A[i][j] * y[i] for i in range(m)) - c[j]
        if x[j] != 0 and reduced != 0:
            return False, f"complementary slackness fails on variable {j}"
    return True, "optimal"


# ---------------------------------------------------------------- step 4 ---

def add_constraint(res: LPResult, a, beta):
    """Append a.x <= beta (with a new slack) to an optimal tableau, in basis form."""
    T = [list(row) for row in res.tableau]
    basis = list(res.basis)
    width = len(T[0]) - 1                          # columns before rhs
    n = len(a)
    for row in T:
        row.insert(width, row[0] * 0)              # new slack column, 0 in old rows
    new = list(a) + [a[0] * 0] * (width - n) + [a[0] * 0 + 1, a[0] * 0 + beta]
    for i, j in enumerate(basis):                  # eliminate basic columns from the new row
        if j < width and new[j] != 0:
            f = new[j]
            new = [v - f * t for v, t in zip(new, T[i])]
    T.insert(len(T) - 1, new)
    basis.append(width)
    return T, basis


def dual_simplex(T, basis, n, eps=0):
    T = [list(row) for row in T]
    basis = list(basis)
    pivots = 0
    while True:
        rows = [i for i in range(len(T) - 1) if T[i][-1] < -eps]
        if not rows:
            status = "optimal"
            break
        r = min(rows, key=lambda i: (T[i][-1], i))
        cols = [j for j in range(len(T[0]) - 1) if T[r][j] < -eps]
        if not cols:
            status = "infeasible"
            break
        s = min(cols, key=lambda j: (T[-1][j] / -T[r][j], j))
        simplex.pivot(T, basis, r, s)
        pivots += 1
    if status != "optimal":
        return LPResult(status, basis=tuple(basis), pivots=pivots, tableau=T)
    x = [T[0][0] * 0] * n
    for i, j in enumerate(basis):
        if j < n:
            x[j] = T[i][-1]
    return LPResult("optimal", tuple(x), T[-1][-1], tuple(basis), pivots, T)


# ---------------------------------------------------------------- step 5 ---

def rhs_range(res: LPResult, n: int, i: int):
    """Interval (lo, hi) of delta for which the basis stays optimal when b_i += delta.
    None stands for an infinite end."""
    T = res.tableau
    col = n + i
    lo = hi = None
    for r in range(len(T) - 1):
        d, v = T[r][col], T[r][-1]
        if d > 0:
            bound = -v / d
            lo = bound if lo is None else max(lo, bound)
        elif d < 0:
            bound = -v / d
            hi = bound if hi is None else min(hi, bound)
    return lo, hi


def predict_objective(res: LPResult, n: int, m: int, i: int, delta):
    lo, hi = rhs_range(res, n, i)
    if (lo is not None and delta < lo) or (hi is not None and delta > hi):
        return None
    return res.value + duals_from_tableau(res, n, m)[i] * delta
