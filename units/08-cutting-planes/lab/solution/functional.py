"""Unit 08 lab — cutting planes.  REFERENCE SOLUTION, functional.

The cutting loops are unfolds over (model, history). The cover separation DP is a
fold over items whose accumulator is the table of best partial covers; lifting is
a fold over the variables outside the cover whose accumulator is the coefficients.
"""

from __future__ import annotations

import math
from dataclasses import replace
from fractions import Fraction
from functools import reduce
from itertools import chain, combinations

import toolz as tz

from colib import ref
from colib.mip import MILP, lp_relaxation

simplex = ref.unit("02")


def frac(v):
    return v - math.floor(v)


# ---------------------------------------------------------------- step 1 ---

def gomory_cut(res, A, b, row):
    m, n = len(A), len(A[0])
    f = [frac(v) for v in res.tableau[row][:n + m]]
    f0 = frac(res.tableau[row][-1])
    coef = [sum(f[n + k] * A[k][j] for k in range(m)) - f[j] for j in range(n)]
    rhs = sum(f[n + k] * b[k] for k in range(m)) - f0
    den = math.lcm(*(Fraction(v).denominator for v in coef + [rhs]))
    return [int(v * den) for v in coef], int(rhs * den)


def fractional_row(res, n):
    scored = [(min(frac(res.tableau[i][-1]), 1 - frac(res.tableau[i][-1])), -i, i)
              for i, j in enumerate(res.basis) if j < n]
    best = max(scored, default=(0, 0, None))
    return best[2] if best[0] > 0 else None


# ---------------------------------------------------------------- step 2 ---

def gomory_loop(A, b, c, rounds=50):
    c = [Fraction(v) for v in c]
    n = len(c)

    def step(state):
        A, b, bounds, cuts, res, done = state
        row = None if done else fractional_row(res, n)
        if row is None:
            return A, b, bounds, cuts, res, True
        a, beta = gomory_cut(res, A, b, row)
        A2, b2 = A + [[Fraction(v) for v in a]], b + [Fraction(beta)]
        res2 = simplex.two_phase(A2, b2, c)
        return A2, b2, bounds + [res2.value], cuts + [(a, beta)], res2, False

    A0 = [[Fraction(v) for v in r] for r in A]
    b0 = [Fraction(v) for v in b]
    res0 = simplex.two_phase(A0, b0, c)
    states = tz.iterate(step, (A0, b0, [res0.value], [], res0, False))
    final = next(s for k, s in enumerate(states) if s[5] or k == rounds)
    return final[2], final[3], final[4]


# ---------------------------------------------------------------- step 3 ---

def separate_cover(weights, capacity, x):
    need = capacity + 1
    start = {0: (0.0, ())}                     # reached weight (capped) -> (cost, set)

    def add_item(table, j):
        # several partial covers can reach the same capped weight: keep the cheapest
        cand = [(min(need, t + weights[j]), (cost + 1 - x[j], chosen + (j,)))
                for t, (cost, chosen) in table.items()]
        extended = {k: min((v for _, v in kvs), key=lambda p: p[0])
                    for k, kvs in tz.groupby(lambda kv: kv[0], cand).items()}
        return tz.merge_with(lambda opts: min(opts, key=lambda p: p[0]), table, extended)

    best = reduce(add_item, range(len(weights)), start).get(need)
    return tuple(sorted(best[1])) if best is not None and best[0] < 1 - 1e-9 else None


# ---------------------------------------------------------------- step 4 ---

def lift_cover(weights, capacity, cover):
    rhs = len(cover) - 1
    start = (tuple(1 if j in cover else 0 for j in range(len(weights))), tuple(cover))

    def lift(state, j):
        alpha, lifted = state
        room = capacity - weights[j]
        subsets = chain.from_iterable(combinations(lifted, k) for k in range(len(lifted) + 1))
        best = max((sum(alpha[i] for i in S) for S in subsets if sum(weights[i] for i in S) <= room),
                   default=None) if room >= 0 else None
        coef = rhs - best if best is not None else rhs
        return tuple(coef if k == j else a for k, a in enumerate(alpha)), lifted + (j,)

    outside = (j for j in range(len(weights)) if j not in cover)
    return list(reduce(lift, outside, start)[0])


# ---------------------------------------------------------------- step 5 ---

def age_pool(pool, x, max_age):
    aged = ((alpha, rhs, 0 if rhs - sum(a * v for a, v in zip(alpha, x)) <= 1e-6 else age + 1)
            for alpha, rhs, age in pool)
    return [c for c in aged if c[2] <= max_age]


def root_cut_loop(milp: MILP, rounds=20, max_age=3):
    def solve(pool):
        return lp_relaxation(replace(milp, A_ub=milp.A_ub + tuple(tuple(a) for a, _, _ in pool),
                                     b_ub=milp.b_ub + tuple(r for _, r, _ in pool)))

    def violated_cuts(x, present):
        candidates = ((tuple(lift_cover(list(w), int(cap), cover)), len(cover) - 1)
                      for w, cap in zip(milp.A_ub, milp.b_ub)
                      for cover in [separate_cover(list(w), int(cap), x)] if cover is not None)
        fresh = [(a, r) for a, r in candidates if sum(ai * v for ai, v in zip(a, x)) > r + 1e-6]
        return list(tz.unique(c for c in fresh if c not in present))

    def step(state):
        pool, bounds, sizes, added, done = state
        lp = solve(pool)
        aged = age_pool(pool, lp.x, max_age)
        new = violated_cuts(lp.x, {(tuple(a), r) for a, r, _ in aged})
        return (aged + [(a, r, 0) for a, r in new], bounds + [lp.value], sizes + [len(pool)],
                added + len(new), not new)

    states = tz.iterate(step, ([], [], [], 0, False))
    final = next(s for k, s in enumerate(states) if s[4] or k == rounds + 1)
    return final[1], final[2], final[3]
