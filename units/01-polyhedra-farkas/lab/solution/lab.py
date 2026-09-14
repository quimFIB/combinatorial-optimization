"""Unit 01 lab — polyhedra, Fourier–Motzkin, and Farkas.  REFERENCE SOLUTION."""

from __future__ import annotations

import itertools

from colib.polyhedra import dot, normalize, satisfies, solve_exact


# ---------------------------------------------------------------- step 1 ---

def eliminate(system, k):
    zero, pos, neg = [], [], []
    for a, b in system:
        (pos if a[k] > 0 else neg if a[k] < 0 else zero).append((a, b))
    out = list(zero)
    for (ap, bp), (aq, bq) in itertools.product(pos, neg):
        lp, lq = -aq[k], ap[k]                       # both positive
        a = tuple(lp * x + lq * y for x, y in zip(ap, aq))
        out.append((a, lp * bp + lq * bq))
    seen, result = set(), []
    for row in map(normalize, out):
        a, b = row
        if not any(a) and b >= 0:                    # 0 <= nonnegative: says nothing
            continue
        if row not in seen:
            seen.add(row)
            result.append(row)
    return result


# ---------------------------------------------------------------- step 2 ---

def fm_feasible(system) -> bool:
    n = len(system[0][0])
    for k in range(n):
        system = eliminate(system, k)
    return all(b >= 0 for _, b in system)


# ---------------------------------------------------------------- step 3 ---

def vertices(system):
    n = len(system[0][0])
    found = set()
    for rows in itertools.combinations(system, n):
        x = solve_exact([a for a, _ in rows], [b for _, b in rows])
        if x is not None and satisfies(system, x):
            found.add(x)
    return sorted(found)


# ---------------------------------------------------------------- step 4 ---

def is_farkas_certificate(system, y) -> bool:
    if len(y) != len(system) or any(yi < 0 for yi in y):
        return False
    n = len(system[0][0])
    combo = [sum(yi * a[j] for yi, (a, _) in zip(y, system)) for j in range(n)]
    return all(c == 0 for c in combo) and dot(y, [b for _, b in system]) < 0


# ---------------------------------------------------------------- step 5 ---

def farkas_certificate(system):
    m, n = len(system), len(system[0][0])
    tagged = [(a + tuple(int(i == j) for j in range(m)), b) for i, (a, b) in enumerate(system)]
    for k in range(n):
        tagged = eliminate(tagged, k)
    for a, b in tagged:
        if not any(a[:n]) and b < 0:
            return tuple(a[n:])
    return None
