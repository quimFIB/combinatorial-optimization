"""Linear programs in the form the simplex units use.

    maximize  c . x   subject to   A x <= b,   x >= 0

A, b, c are nested lists/tuples of ints or Fractions (exact) or floats. The
results type, the cycling exception and instance generators live here so that
units 02, 03, 07 and 08 agree on them.
"""

from __future__ import annotations

import random as _random
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class LPResult:
    status: str                      # "optimal" | "unbounded" | "infeasible"
    x: tuple | None = None           # optimal primal point (original variables only)
    value: Any = None                # optimal objective value
    basis: tuple | None = None       # final basis: column index basic in each row
    pivots: int = 0                  # pivots performed (both phases)
    tableau: Any = field(default=None, repr=False, compare=False)  # final tableau


class Cycling(RuntimeError):
    """Raised when the simplex method revisits a basis: it would loop forever."""


def fractions(A, b, c):
    """The same LP with every entry converted to Fraction."""
    F = Fraction
    return ([[F(v) for v in row] for row in A], [F(v) for v in b], [F(v) for v in c])


def random_lp(m: int, n: int, seed=0, kind: str = "any"):
    """A random integer LP with m constraints and n variables.

    kind="bounded":  b > 0 and every column has a positive entry, so the origin
                     is feasible and the LP is bounded (optimal).
    kind="any":      b may be negative (needs phase 1), and the LP may be
                     infeasible or unbounded.
    """
    r = _random.Random(seed)
    if kind == "bounded":
        A = [[r.randint(-3, 9) for _ in range(n)] for _ in range(m)]
        for j in range(n):
            if all(A[i][j] <= 0 for i in range(m)):
                A[r.randrange(m)][j] = r.randint(1, 9)
        b = [r.randint(1, 30) for _ in range(m)]
    else:
        A = [[r.randint(-6, 9) for _ in range(n)] for _ in range(m)]
        b = [r.randint(-10, 30) for _ in range(m)]
    c = [r.randint(-5, 9) for _ in range(n)]
    return A, b, c


def beale():
    """Beale's 1955 example: degenerate at the origin, and the textbook simplex
    (largest coefficient, ties broken by lowest row) cycles on it forever.

        max  3/4 x1 - 20 x2 + 1/2 x3 - 6 x4
        s.t. 1/4 x1 -  8 x2 -     x3 + 9 x4 <= 0
             1/2 x1 - 12 x2 - 1/2 x3 + 3 x4 <= 0
                                  x3        <= 1
    Optimum 5/4 at x = (1, 0, 1, 0).
    """
    F = Fraction
    A = [[F(1, 4), F(-8), F(-1), F(9)],
         [F(1, 2), F(-12), F(-1, 2), F(3)],
         [F(0), F(0), F(1), F(0)]]
    return A, [F(0), F(0), F(1)], [F(3, 4), F(-20), F(1, 2), F(-6)]


# ---------------------------------------------------------------- general form (unit 03)

ROW_SENSES = ("<=", ">=", "=")
VAR_SIGNS = (">=0", "<=0", "free")


@dataclass(frozen=True)
class GeneralLP:
    """  sense  c.x   s.t.  a_i.x  (senses[i])  b_i,   x_j  (signs[j])

    sense is "max" or "min"; senses[i] in ROW_SENSES; signs[j] in VAR_SIGNS.
    """
    sense: str
    c: tuple
    A: tuple
    senses: tuple
    b: tuple
    signs: tuple

    @property
    def m(self):
        return len(self.A)

    @property
    def n(self):
        return len(self.c)


def random_general_lp(m: int, n: int, seed=0) -> GeneralLP:
    """A random general-form LP built to be feasible and bounded more often than not:
    b is chosen so a random point satisfies every row."""
    r = _random.Random(seed)
    A = tuple(tuple(r.randint(-5, 6) for _ in range(n)) for _ in range(m))
    signs = tuple(r.choice(VAR_SIGNS) for _ in range(n))
    x0 = [r.randint(0, 3) * (1 if s == ">=0" else -1 if s == "<=0" else r.choice((1, -1)))
          for s in signs]
    senses = tuple(r.choice(ROW_SENSES) for _ in range(m))
    b = []
    for row, s in zip(A, senses):
        v = sum(a * x for a, x in zip(row, x0))
        b.append(v + (r.randint(0, 5) if s == "<=" else -r.randint(0, 5) if s == ">=" else 0))
    return GeneralLP(r.choice(("max", "min")), tuple(r.randint(-6, 6) for _ in range(n)),
                     A, senses, tuple(b), signs)
