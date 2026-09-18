"""Unit 01 lab — polyhedra, Fourier–Motzkin, and Farkas.  REFERENCE SOLUTION, functional.

Fourier–Motzkin is a fold: eliminating all variables is
`reduce(eliminate, range(n), system)`, and Farkas is the same fold over
constraints that carry their own multipliers. Checked by the same tests:
    uv run co test 01 --solution functional
"""

from __future__ import annotations

from functools import reduce
from itertools import chain, combinations, product

import toolz as tz
from toolz.curried import filter as cfilter, map as cmap

from colib.polyhedra import dot, normalize, satisfies, solve_exact


# ---------------------------------------------------------------- step 1 ---

def combine(p, q, k):
    """p has a[k] > 0, q has a[k] < 0: the positive combination that cancels x_k."""
    (ap, bp), (aq, bq) = p, q
    lp, lq = -aq[k], ap[k]
    return tuple(lp * x + lq * y for x, y in zip(ap, aq)), lp * bp + lq * bq


def says_something(row) -> bool:
    """False only for 0 <= (nonnegative), which every point satisfies."""
    a, b = row
    return any(a) or b < 0


def eliminate(system, k):
    zero = [r for r in system if r[0][k] == 0]
    pos = [r for r in system if r[0][k] > 0]
    neg = [r for r in system if r[0][k] < 0]
    return tz.pipe(chain(zero, (combine(p, q, k) for p, q in product(pos, neg))),
                   cmap(normalize),
                   cfilter(says_something),
                   tz.unique,
                   list)


# ---------------------------------------------------------------- step 2 ---

def fm_feasible(system) -> bool:
    n = len(system[0][0])
    return all(b >= 0 for _, b in reduce(eliminate, range(n), system))


# ---------------------------------------------------------------- step 3 ---

def vertices(system):
    n = len(system[0][0])
    solutions = (solve_exact([a for a, _ in rows], [b for _, b in rows])
                 for rows in combinations(system, n))
    return sorted({x for x in solutions if x is not None and satisfies(system, x)})


# ---------------------------------------------------------------- step 4 ---

def is_farkas_certificate(system, y) -> bool:
    n = len(system[0][0])
    return (len(y) == len(system)
            and all(v >= 0 for v in y)
            and all(sum(v * a[j] for v, (a, _) in zip(y, system)) == 0 for j in range(n))
            and dot(y, [b for _, b in system]) < 0)


# ---------------------------------------------------------------- step 5 ---

def farkas_certificate(system):
    m, n = len(system), len(system[0][0])
    unit = lambda i: tuple(int(i == j) for j in range(m))
    tagged = [(a + unit(i), b) for i, (a, b) in enumerate(system)]
    final = reduce(eliminate, range(n), tagged)
    return next((tuple(a[n:]) for a, b in final if not any(a[:n]) and b < 0), None)
