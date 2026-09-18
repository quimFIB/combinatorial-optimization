"""Unit 02's recorded simplex runs, for units/02-simplex/explore.html.

Every number the stepper shows comes from here: the reference `initial_tableau`,
`entering`, `leaving` and `pivot`, run in exact Fractions. `uv run co viz 02` writes
units/02-simplex/viz-data.js (see slides/viz/traces/__init__.py).
"""

from __future__ import annotations

from fractions import Fraction as F

from colib import ref

L = ref.unit("02")


def fmt(v: F) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def trace(A, b, c, rule, slacks=None, max_pivots=50):
    """Pivot until optimal, unbounded or a repeated basis. Returns a list of states.

    slacks names the slack columns when the slides number them differently from 1..m."""
    A = [[F(v) for v in row] for row in A]
    b, c = [F(v) for v in b], [F(v) for v in c]
    n, m = len(c), len(A)
    names = [f"x{j + 1}" for j in range(n)] + (slacks or [f"s{i + 1}" for i in range(m)])
    T, basis = L.initial_tableau(A, b, c)
    states, seen = [], [tuple(basis)]

    def snapshot(note, col=None, row=None, ratios=None):
        x = [F(0)] * n
        for i, j in enumerate(basis):
            if j < n:
                x[j] = T[i][-1]
        states.append({
            "tableau": [[fmt(v) for v in r] for r in T],
            "basis": [names[j] for j in basis],
            "point": [float(v) for v in x],
            "point_exact": [fmt(v) for v in x],
            "z": fmt(T[-1][-1]),
            "enter": col, "leave": row,
            "ratios": ratios, "note": note,
        })

    for _ in range(max_pivots):
        col = L.entering(T, rule)
        if col is None:
            snapshot("optimal: no negative entry in the objective row")
            return states, names
        row = L.leaving(T, basis, col, rule)
        ratios = [None if T[i][col] <= 0 else fmt(T[i][-1] / T[i][col]) for i in range(m)]
        if row is None:
            snapshot(f"{names[col]} can grow forever: unbounded", col, None, ratios)
            return states, names
        snapshot(f"enter {names[col]}, leave {names[basis[row]]}", col, row, ratios)
        L.pivot(T, basis, row, col)
        if tuple(basis) in seen:
            snapshot("basis repeats: cycling")
            return states, names
        seen.append(tuple(basis))
    snapshot("pivot limit reached")
    return states, names


INSTANCES = [
    ("polygon-dantzig", "Unit 01's polygon, max 2x + y, Dantzig's rule",
     [[1, 1], [1, -1]], [4, 1], [2, 1], "dantzig"),
    ("polygon-steep", "Unit 01's polygon, max x + 3y, Dantzig's rule",
     [[1, 1], [1, -1]], [4, 1], [1, 3], "dantzig"),
    # s5: the slides call it the slack of unit 01's constraint 5, not s3 (s3 is phase 1's surplus)
    ("degenerate", "Polygon plus constraint 5, 3x − y ≤ 6, max 2x + y, Bland's rule",
     [[1, 1], [1, -1], [3, -1]], [4, 1, 6], [2, 1], "bland", ["s1", "s2", "s5"]),
    ("klee-minty-2", "Klee–Minty cube, n = 2, Dantzig's rule",
     [[1, 0], [20, 1]], [1, 100], [10, 1], "dantzig"),
]


def data():
    """Everything explore.html needs, keyed by run: title, rows, rule, columns, states."""
    out = {}
    for key, title, A, b, c, rule, *slacks in INSTANCES:
        states, names = trace(A, b, c, rule, *slacks)
        out[key] = {"title": title, "A": A, "b": b, "c": c, "rule": rule, "columns": names, "states": states}
    return out
