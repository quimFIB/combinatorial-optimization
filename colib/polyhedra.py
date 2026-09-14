"""Exact linear inequality systems  A x <= b,  for units 01-03.

A system is a list of rows; a row is `(a, b)` with `a` a tuple of ints (or
Fractions) and `b` a number, meaning  a . x <= b.  Integer data and exact
arithmetic throughout: a Farkas certificate is a proof, and a proof checked with
a tolerance is not one.
"""

from __future__ import annotations

import math
import random as _random
from fractions import Fraction
from typing import Sequence

Row = tuple[tuple, object]
System = list[Row]


def dot(a: Sequence, x: Sequence):
    return sum(ai * xi for ai, xi in zip(a, x))


def satisfies(system: System, x, strict: bool = False) -> bool:
    return all((dot(a, x) < b) if strict else (dot(a, x) <= b) for a, b in system)


def normalize(row: Row) -> Row:
    """Divide an integer row by the gcd of all its entries (a positive scalar,
    so the inequality means the same thing). Fraction rows are cleared to
    integers first. The zero row is returned unchanged."""
    a, b = row
    vals = [*a, b]
    if any(isinstance(v, Fraction) for v in vals):
        den = math.lcm(*(Fraction(v).denominator for v in vals))
        vals = [int(Fraction(v) * den) for v in vals]
    g = math.gcd(*(int(v) for v in vals))
    if g in (0, 1):
        return tuple(vals[:-1]), vals[-1]
    return tuple(v // g for v in vals[:-1]), vals[-1] // g


def solve_exact(A: Sequence[Sequence], b: Sequence):
    """Solve the square system A x = b exactly. Return a tuple of Fractions, or
    None if A is singular."""
    n = len(A)
    M = [[Fraction(v) for v in row] + [Fraction(bi)] for row, bi in zip(A, b)]
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        M[col] = [v / p for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [vr - f * vc for vr, vc in zip(M[r], M[col])]
    return tuple(M[r][n] for r in range(n))


def rank(A: Sequence[Sequence]) -> int:
    M = [[Fraction(v) for v in row] for row in A]
    r = 0
    cols = len(M[0]) if M else 0
    for c in range(cols):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [vi - f * vr for vi, vr in zip(M[i], M[r])]
        r += 1
    return r


# ---------------------------------------------------------------- generators

def box(n: int, R: int = 10) -> System:
    """-R <= x_i <= R for every i."""
    rows = []
    for i in range(n):
        e = tuple(1 if j == i else 0 for j in range(n))
        rows.append((e, R))
        rows.append((tuple(-v for v in e), R))
    return rows


def random_polytope(n: int, m: int, seed=0, R: int = 10) -> System:
    """m random cuts intersected with the box [-R, R]^n.

    Every cut has a positive right-hand side, so the origin is strictly inside:
    the result is bounded and full-dimensional. Box rows come last.
    """
    r = _random.Random(seed)
    rows = []
    while len(rows) < m:
        a = tuple(r.randint(-5, 5) for _ in range(n))
        if any(a):
            rows.append((a, r.randint(1, 4 * R)))
    return rows + box(n, R)


def random_infeasible(n: int, m: int, seed=0) -> System:
    """A random system with infeasibility planted in it.

    Starts from m random rows (feasible or not), picks a nonnegative
    combination of some of them, and appends the row that contradicts it by 1,
    then shuffles. There is always a certificate; finding it is the exercise.
    """
    r = _random.Random(seed)
    rows = []
    while len(rows) < m:
        a = tuple(r.randint(-4, 4) for _ in range(n))
        if any(a):
            rows.append((a, r.randint(-6, 12)))
    chosen = r.sample(range(m), r.randint(1, min(m, n + 1)))
    y = {i: r.randint(1, 3) for i in chosen}
    c = tuple(sum(y[i] * rows[i][0][j] for i in chosen) for j in range(n))
    d = sum(y[i] * rows[i][1] for i in chosen)
    rows.append((tuple(-v for v in c), -d - 1))
    r.shuffle(rows)
    return rows


def shifted_polytope(n: int, m: int, seed=0, R: int = 10, shift: float = 40.0):
    """A random polytope moved away from the origin, as float arrays (A, b, center).

    It is random_polytope(n, m, seed, R) translated by a random vector of length
    `shift`; `center` is where the origin went, a point strictly inside. Used to
    give the ellipsoid method something to find.
    """
    import numpy as np
    rows = random_polytope(n, m, seed=seed, R=R)
    A = np.array([a for a, _ in rows], dtype=float)
    b = np.array([bb for _, bb in rows], dtype=float)
    rng = np.random.default_rng(seed)
    p = rng.normal(size=n)
    p *= shift / np.linalg.norm(p)
    return A, b + A @ p, p


def inscribed_radius(A, b, x):
    """Radius of the largest ball around x inside {A z <= b}: min slack / row norm."""
    import numpy as np
    A, b, x = np.asarray(A, float), np.asarray(b, float), np.asarray(x, float)
    return float(np.min((b - A @ x) / np.linalg.norm(A, axis=1)))
