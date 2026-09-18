"""Unit 03 lab — duality.  REFERENCE SOLUTION, functional.

Dualizing is a pair of table lookups plus a transpose. Certification is a
conjunction of predicates that also says which one failed. The dual simplex is
the same unfold as unit 02's primal loop, with rows and columns swapped in the
choice of pivot.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import dropwhile

import toolz as tz

from colib import ref
from colib.lp import GeneralLP, LPResult

simplex = ref.unit("02")


# ---------------------------------------------------------------- step 1 ---

FLIP = {">=0": "<=0", "<=0": ">=0", "free": "free", ">=": "<=", "<=": ">=", "=": "="}
ROW_TO_SIGN = {"<=": ">=0", ">=": "<=0", "=": "free"}     # for a max primal
SIGN_TO_ROW = {">=0": ">=", "<=0": "<=", "free": "="}


def dual(lp: GeneralLP) -> GeneralLP:
    adjust = (lambda s: FLIP[s]) if lp.sense == "min" else (lambda s: s)
    return GeneralLP(
        sense="min" if lp.sense == "max" else "max",
        c=tuple(lp.b),
        A=tuple(zip(*lp.A)) if lp.m else tuple(() for _ in range(lp.n)),
        senses=tuple(adjust(SIGN_TO_ROW[s]) for s in lp.signs),
        b=tuple(lp.c),
        signs=tuple(adjust(ROW_TO_SIGN[s]) for s in lp.senses))


# ---------------------------------------------------------------- step 2 ---

def duals_from_tableau(res: LPResult, n: int, m: int):
    if res.status != "optimal":
        raise ValueError(f"no duals for a {res.status} LP")
    return tuple(res.tableau[-1][n:n + m])


# ---------------------------------------------------------------- step 3 ---

def certify_optimal(A, b, c, x, y) -> tuple[bool, str]:
    m, n = len(A), len(c)
    Ax = [sum(a * v for a, v in zip(row, x)) for row in A]
    Aty = [sum(A[i][j] * y[i] for i in range(m)) for j in range(n)]
    checks = (
        (all(v >= 0 for v in x), "x has a negative entry"),
        (all(l <= r for l, r in zip(Ax, b)), "a primal constraint is violated"),
        (all(v >= 0 for v in y), "y has a negative entry"),
        (all(l >= r for l, r in zip(Aty, c)), "a dual constraint is violated"),
        (all(yi == 0 or bi == axi for yi, bi, axi in zip(y, b, Ax)),
         "complementary slackness fails on a primal constraint"),
        (all(xj == 0 or aty == cj for xj, aty, cj in zip(x, Aty, c)),
         "complementary slackness fails on a variable"),
    )
    return next(((False, why) for ok, why in checks if not ok), (True, "optimal"))


# ---------------------------------------------------------------- step 4 ---

def add_constraint(res: LPResult, a, beta):
    T, basis = res.tableau, tuple(res.basis)
    width = len(T[0]) - 1
    zero = T[0][0] * 0
    widen = lambda row, v: tuple(row[:width]) + (v,) + (row[-1],)
    raw = tuple(a) + (zero,) * (width - len(a)) + (zero + 1, zero + beta)
    old = tuple(widen(row, zero) for row in T)
    new = tz.reduce(lambda r, ib: tuple(v - r[ib[1]] * t for v, t in zip(r, old[ib[0]])),
                    enumerate(basis), raw)
    return old[:-1] + (new,) + old[-1:], basis + (width,)


@dataclass(frozen=True)
class State:
    T: tuple
    basis: tuple
    pivots: int = 0
    status: str | None = None


def dual_simplex(T, basis, n, eps=0):
    def step(s: State) -> State:
        body = range(len(s.T) - 1)
        rows = [i for i in body if s.T[i][-1] < -eps]
        if not rows:
            return replace(s, status="optimal")
        r = min(rows, key=lambda i: (s.T[i][-1], i))
        cols = [j for j in range(len(s.T[0]) - 1) if s.T[r][j] < -eps]
        if not cols:
            return replace(s, status="infeasible")
        col = min(cols, key=lambda j: (s.T[-1][j] / -s.T[r][j], j))
        T2, basis2 = simplex.pivot([list(row) for row in s.T], list(s.basis), r, col)
        return State(tuple(map(tuple, T2)), tuple(basis2), s.pivots + 1)

    final = tz.first(dropwhile(lambda s: s.status is None,
                               tz.iterate(step, State(tuple(map(tuple, T)), tuple(basis)))))
    if final.status != "optimal":
        return LPResult(final.status, basis=final.basis, pivots=final.pivots, tableau=final.T)
    value_of = dict(zip(final.basis, (row[-1] for row in final.T)))
    zero = final.T[0][0] * 0
    return LPResult("optimal", tuple(value_of.get(j, zero) for j in range(n)), final.T[-1][-1],
                    final.basis, final.pivots, final.T)


# ---------------------------------------------------------------- step 5 ---

def rhs_range(res: LPResult, n: int, i: int):
    pairs = [(row[n + i], row[-1]) for row in res.tableau[:-1]]
    lows = [-v / d for d, v in pairs if d > 0]
    highs = [-v / d for d, v in pairs if d < 0]
    return (max(lows) if lows else None), (min(highs) if highs else None)


def predict_objective(res: LPResult, n: int, m: int, i: int, delta):
    lo, hi = rhs_range(res, n, i)
    inside = (lo is None or delta >= lo) and (hi is None or delta <= hi)
    return res.value + duals_from_tableau(res, n, m)[i] * delta if inside else None
