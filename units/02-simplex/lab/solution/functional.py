"""Unit 02 lab — simplex, honestly.  REFERENCE SOLUTION, functional.

The tableau is a tuple of tuples and is never mutated: `pivot` returns a new
one. The pivoting loop is an unfold, `iterate(step, state)`, read until the
first state that has a status. Same tableau layout as solution/lab.py.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import reduce
from itertools import dropwhile

import toolz as tz

from colib.lp import Cycling, LPResult


# ---------------------------------------------------------------- step 1 ---

def initial_tableau(A, b, c):
    m, n = len(A), len(c)
    rows = tuple(tuple(A[i]) + tuple(int(k == i) for k in range(m)) + (b[i],) for i in range(m))
    return rows + (tuple(-v for v in c) + (0,) * m + (0,),), tuple(range(n, n + m))


def pivot(T, basis, row, col):
    pivot_row = tuple(v / T[row][col] for v in T[row])
    eliminate = lambda i, r: pivot_row if i == row else tuple(
        v - r[col] * p for v, p in zip(r, pivot_row))
    return (tuple(eliminate(i, r) for i, r in enumerate(T)),
            tuple(col if i == row else j for i, j in enumerate(basis)))


# ---------------------------------------------------------------- step 2 ---

def entering(T, rule="bland", eps=0):
    z = T[-1]
    candidates = [j for j in range(len(z) - 1) if z[j] < -eps]
    if not candidates:
        return None
    return candidates[0] if rule == "bland" else min(candidates, key=lambda j: (z[j], j))


def leaving(T, basis, col, rule="bland", eps=0):
    ratios = {i: T[i][-1] / T[i][col] for i in range(len(T) - 1) if T[i][col] > eps}
    if not ratios:
        return None
    best = min(ratios.values())
    ties = [i for i, q in ratios.items() if q - best <= eps]
    return min(ties, key=lambda i: basis[i]) if rule == "bland" else ties[0]


# ---------------------------------------------------------------- step 3 ---

@dataclass(frozen=True)
class State:
    T: tuple
    basis: tuple
    pivots: int
    seen: frozenset
    status: str | None = None


def run(T, basis, rule, eps, pivots=0) -> State:
    """Pivot until a status appears. `iterate` unfolds the states lazily."""
    def step(s: State) -> State:
        col = entering(s.T, rule, eps)
        if col is None:
            return replace(s, status="optimal")
        row = leaving(s.T, s.basis, col, rule, eps)
        if row is None:
            return replace(s, status="unbounded")
        T2, basis2 = pivot(s.T, s.basis, row, col)
        if basis2 in s.seen:
            raise Cycling(f"basis {basis2} repeated after {s.pivots + 1} pivots")
        return State(T2, basis2, s.pivots + 1, s.seen | {basis2})

    start = State(tuple(map(tuple, T)), tuple(basis), pivots, frozenset({tuple(basis)}))
    return tz.first(dropwhile(lambda s: s.status is None, tz.iterate(step, start)))


def result(s: State, n: int) -> LPResult:
    if s.status != "optimal":
        return LPResult(s.status, basis=s.basis, pivots=s.pivots, tableau=s.T)
    value_of = dict(zip(s.basis, (row[-1] for row in s.T)))
    x = tuple(value_of.get(j, 0) for j in range(n))
    return LPResult("optimal", x, s.T[-1][-1], s.basis, s.pivots, s.T)


def simplex(A, b, c, rule="bland", eps=0):
    if any(v < 0 for v in b):
        raise ValueError("simplex() needs b >= 0; use two_phase() otherwise")
    return result(run(*initial_tableau(A, b, c), rule, eps), len(c))


# ---------------------------------------------------------------- step 4 ---

def price_out(obj, T, basis):
    """Make the objective row zero on every basic column."""
    return reduce(lambda o, ib: tuple(v - o[ib[1]] * t for v, t in zip(o, T[ib[0]])),
                  enumerate(basis), tuple(obj))


def two_phase(A, b, c, rule="bland", eps=0):
    m, n = len(A), len(c)
    neg = tuple(i for i in range(m) if b[i] < 0)
    art_col = {i: n + m + k for k, i in enumerate(neg)}
    sign = lambda i: -1 if i in art_col else 1
    rows = tuple(tuple(sign(i) * v for v in A[i])
                 + tuple(sign(i) * int(k == i) for k in range(m))
                 + tuple(int(art_col.get(i) == n + m + k) for k in range(len(neg)))
                 + (sign(i) * b[i],) for i in range(m))
    basis = tuple(art_col.get(i, n + i) for i in range(m))
    zero = rows[0][0] * 0
    width = n + m + len(neg)

    if not neg:
        s = State(rows, basis, 0, frozenset())
    else:
        phase1_obj = tuple(zero + (1 if j in art_col.values() else 0) for j in range(width)) + (zero,)
        s = run(rows + (price_out(phase1_obj, rows, basis),), basis, rule, eps)
        if s.T[-1][-1] < -eps:
            return LPResult("infeasible", basis=s.basis, pivots=s.pivots, tableau=s.T)
        s = drive_out(s, set(art_col.values()), n + m, eps)

    body = tuple(r[:n + m] + (r[-1],) for r in s.T[:len(s.basis)])
    obj = tuple(-v for v in c) + (zero,) * m + (zero,)
    final = run(body + (price_out(obj, body, s.basis),), s.basis, rule, eps, s.pivots)
    return result(final, n)


def drive_out(s: State, artificial: set, real_cols: int, eps) -> State:
    """Pivot every zero-level artificial out of the basis, or drop its row if redundant."""
    def one(st: State, i: int) -> State:
        if st.basis[i] not in artificial:
            return st
        col = next((j for j in range(real_cols) if abs(st.T[i][j]) > eps), None)
        if col is None:
            keep = [k for k in range(len(st.T)) if k != i]
            return replace(st, T=tuple(st.T[k] for k in keep),
                           basis=tuple(b for k, b in enumerate(st.basis) if k != i))
        T2, basis2 = pivot(st.T, st.basis, i, col)
        return replace(st, T=T2, basis=basis2, pivots=st.pivots + 1)
    return reduce(one, reversed(range(len(s.basis))), s)


# ---------------------------------------------------------------- step 5 ---

def klee_minty(n):
    A = tuple(tuple(2 * 10 ** (i - j) if j < i else int(j == i) for j in range(n)) for i in range(n))
    return A, tuple(100 ** i for i in range(n)), tuple(10 ** (n - 1 - j) for j in range(n))
