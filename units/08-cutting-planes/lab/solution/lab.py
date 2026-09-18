"""Unit 08 lab — cutting planes.  REFERENCE SOLUTION, imperative.

Part A (steps 1–2): Gomory fractional cuts for pure integer programs
    max c.x  s.t.  A x <= b,  x >= 0 integer,  A, b integer,
read off unit 02's exact simplex tableau (layout [A | I | b] over [-c | 0 | z]).
Part B (steps 3–5): knapsack cover cuts for 0/1 knapsack constraints w.x <= cap,
lifted, inside a root cutting loop on colib.mip MILPs (minimization).
"""

from __future__ import annotations

import math
from dataclasses import replace
from fractions import Fraction
from itertools import combinations

from colib import ref
from colib.mip import MILP, lp_relaxation

simplex = ref.unit("02")


def frac(v: Fraction) -> Fraction:
    return v - math.floor(v)


# ---------------------------------------------------------------- step 1 ---

def gomory_cut(res, A, b, row):
    """The Gomory fractional cut from tableau row `row`, in the original variables:
    returns (a, beta) with integer entries, meaning a.x <= beta."""
    T = res.tableau
    m, n = len(A), len(A[0])
    f = [frac(v) for v in T[row][:n + m]]
    f0 = frac(T[row][-1])
    # sum_j f_j x_j + sum_k f_{n+k} s_k >= f0, with s_k = b_k - a_k.x
    coef = [sum(f[n + k] * A[k][j] for k in range(m)) - f[j] for j in range(n)]
    rhs = sum(f[n + k] * b[k] for k in range(m)) - f0
    den = math.lcm(*(Fraction(v).denominator for v in coef + [rhs]))
    return [int(v * den) for v in coef], int(rhs * den)


def fractional_row(res, n):
    """The tableau row whose basic variable is an original x_j with the most
    fractional value; None if every x_j is integral."""
    best, best_f = None, Fraction(0)
    for i, j in enumerate(res.basis):
        if j < n:
            v = res.tableau[i][-1]
            fv = min(frac(v), 1 - frac(v))
            if fv > best_f:
                best, best_f = i, fv
    return best


# ---------------------------------------------------------------- step 2 ---

def gomory_loop(A, b, c, rounds=50):
    """Solve the LP, add a Gomory cut from the most fractional row, repeat.
    Returns (bounds, cuts, final LPResult): the LP bound before each round and
    after the last, and the cuts added."""
    A = [list(map(Fraction, r)) for r in A]
    b = list(map(Fraction, b))
    c = list(map(Fraction, c))
    n = len(c)
    res = simplex.two_phase(A, b, c)
    bounds, cuts = [res.value], []
    for _ in range(rounds):
        row = fractional_row(res, n)
        if row is None:
            break
        a, beta = gomory_cut(res, A, b, row)
        cuts.append((a, beta))
        A = A + [list(map(Fraction, a))]
        b = b + [Fraction(beta)]
        res = simplex.two_phase(A, b, c)
        bounds.append(res.value)
    return bounds, cuts, res


# ---------------------------------------------------------------- step 3 ---

def separate_cover(weights, capacity, x):
    """The most violated cover inequality sum_{j in C} x_j <= |C| - 1, found
    exactly: minimise sum_{j in C} (1 - x_j) subject to sum_{j in C} w_j > capacity.
    Returns the cover as a sorted tuple if its inequality is violated by x, else None."""
    n = len(weights)
    need = capacity + 1
    INF = float("inf")
    # dp[t] = min cost of a set with weight >= t (t capped at need); choice tracking for the set
    dp = [0.0] + [INF] * need
    choice = [()] + [None] * need
    for j in range(n):
        cost = 1 - x[j]
        for t in range(need, -1, -1):
            if dp[t] == INF:
                continue
            u = min(need, t + weights[j])
            if dp[t] + cost < dp[u] - 1e-12:
                dp[u] = dp[t] + cost
                choice[u] = choice[t] + (j,)
    if dp[need] < 1 - 1e-9:
        return tuple(sorted(choice[need]))
    return None


# ---------------------------------------------------------------- step 4 ---

def lift_cover(weights, capacity, cover):
    """Sequential up-lifting of sum_{j in C} x_j <= |C| - 1 over the variables
    outside C, in index order. Returns the coefficient list alpha (1 on C), so the
    lifted inequality is sum_j alpha_j x_j <= |C| - 1."""
    n = len(weights)
    alpha = [0] * n
    for j in cover:
        alpha[j] = 1
    rhs = len(cover) - 1
    lifted = list(cover)
    for j in range(n):
        if j in cover:
            continue
        # max sum of alpha over lifted vars, with weight <= capacity - w_j  (brute force: small n)
        room = capacity - weights[j]
        best = -1
        if room >= 0:
            best = 0
            for k in range(1, len(lifted) + 1):
                for S in combinations(lifted, k):
                    if sum(weights[i] for i in S) <= room:
                        best = max(best, sum(alpha[i] for i in S))
        alpha[j] = rhs - best if best >= 0 else rhs
        lifted.append(j)
    return alpha


# ---------------------------------------------------------------- step 5 ---

def age_pool(pool, x, max_age):
    """One round of cut-pool management. pool is a list of (alpha, rhs, age).
    A cut tight at x (slack <= 1e-6) gets age 0; a slack cut gets age + 1.
    Cuts older than max_age are dropped. Returns the new list, in the same order."""
    out = []
    for alpha, rhs, age in pool:
        slack = rhs - sum(a * v for a, v in zip(alpha, x))
        age = 0 if slack <= 1e-6 else age + 1
        if age <= max_age:
            out.append((alpha, rhs, age))
    return out


def root_cut_loop(milp: MILP, rounds=20, max_age=3):
    """Root cutting-plane loop for a 0/1 MILP whose A_ub rows are knapsacks with
    nonnegative integer weights. Each round: solve the LP with the pool's cuts,
    age the pool, separate a lifted cover cut from every knapsack constraint, and add the
    violated ones that are not already in the pool. Stop when a round adds nothing.
    Returns (bounds, pool_sizes, total_cuts_added): the LP bound and pool size at
    the start of every round."""
    pool, bounds, sizes, added = [], [], [], 0
    for _ in range(rounds + 1):
        lp = lp_relaxation(replace(milp, A_ub=milp.A_ub + tuple(tuple(a) for a, _, _ in pool),
                                   b_ub=milp.b_ub + tuple(r for _, r, _ in pool)))
        bounds.append(lp.value)
        sizes.append(len(pool))
        pool = age_pool(pool, lp.x, max_age)
        present = {(tuple(a), r) for a, r, _ in pool}
        new = []
        for w, cap in zip(milp.A_ub, milp.b_ub):
            cover = separate_cover(list(w), int(cap), lp.x)
            if cover is None:
                continue
            alpha = tuple(lift_cover(list(w), int(cap), cover))
            r = len(cover) - 1
            if sum(a * v for a, v in zip(alpha, lp.x)) > r + 1e-6 and (alpha, r) not in present:
                new.append((alpha, r, 0))
                present.add((alpha, r))
        if not new:
            break
        pool += new
        added += len(new)
    return bounds, sizes, added
