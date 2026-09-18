"""Unit 24 lab — LP rounding and the primal-dual method.  REFERENCE SOLUTION, imperative.

LPs are solved by colib.approx.covering_lp (HiGHS): min c.x, A x >= 1, 0 <= x <= 1, returning the value, the
primal x and the duals y. Everything else is yours. Set cover and vertex cover instances are unit 00's classes;
facility location is colib.approx.FacilityLocation. Dual values in the primal-dual algorithms are exact
Fractions, so "tight" means equal, not close.
"""

from __future__ import annotations

import math
from fractions import Fraction

from colib.approx import covering_lp
from colib.problems import SetCover, VertexCover

EPS = 1e-9


# ---------------------------------------------------------------- step 1 ---

def vertex_cover_lp(n, edges, weights):
    """The LP relaxation of weighted vertex cover: min w.x, x_u + x_v >= 1 per edge, 0 <= x <= 1.
    Returns (value, x) with x a list of floats."""
    if not edges:
        return 0.0, [0.0] * n
    A = [[1 if v in e else 0 for v in range(n)] for e in edges]
    value, x, _ = covering_lp(A, weights)
    return value, x


def threshold_rounding(x, t):
    """1 where x_v >= t (up to 1e-9), else 0."""
    return [1 if xv >= t - EPS else 0 for xv in x]


def vertex_cover_rounding(n, edges, weights):
    """Solve the LP and round at 1/2: a cover of weight <= 2 LP. Returns (cover, lp value)."""
    value, x = vertex_cover_lp(n, edges, weights)
    return threshold_rounding(x, 0.5), value


# ---------------------------------------------------------------- step 2 ---

def set_cover_lp(sc):
    """The LP relaxation of set cover: one constraint per element, one variable per set. Returns (value, x)."""
    A = [[1 if e in s else 0 for s in sc.sets] for e in range(sc.universe)]
    value, x, _ = covering_lp(A, sc.costs)
    return value, x


def randomized_rounding(sc, x, rounds, rng):
    """`rounds` independent rounds; in each, set j is picked with probability x_j (rng.random() < x_j).
    Returns the 0/1 union of all rounds (which may fail to be a cover)."""
    chosen = [0] * sc.n
    for _ in range(rounds):
        for j in range(sc.n):
            if rng.random() < x[j]:
                chosen[j] = 1
    return chosen


def uncovered_probability(sc, x, rounds):
    """For each element e, the exact probability that randomized_rounding leaves it uncovered:
    the product over sets j containing e of (1 - x_j)^rounds."""
    prob = [1.0] * sc.universe
    for j, s in enumerate(sc.sets):
        miss = max(0.0, 1.0 - x[j]) ** rounds
        for e in s:
            prob[e] *= miss
    return prob


def expected_cost(sc, x, rounds):
    """The exact expected cost of randomized_rounding: sum_j c_j (1 - (1 - x_j)^rounds)."""
    return sum(c * (1.0 - max(0.0, 1.0 - xj) ** rounds) for c, xj in zip(sc.costs, x))


def failure_bound(universe, rounds):
    """The union bound on failing to cover: universe * e^(-rounds), using prod (1 - x_j) <= e^(-sum x_j) <= 1/e."""
    return universe * math.exp(-rounds)


# ---------------------------------------------------------------- step 3 ---

def frequency(sc):
    """f: the largest number of sets containing one element."""
    count = [0] * sc.universe
    for s in sc.sets:
        for e in s:
            count[e] += 1
    return max(count, default=0)


def primal_dual_set_cover(sc):
    """For each element e in increasing order, if uncovered: raise y_e until some set containing e is tight
    (sum of y over its elements equals its cost), then buy every set containing e that is now tight.
    Returns (x, y): x 0/1 over sets, y a list of Fractions over elements. Every bought set is tight, y is
    dual feasible, and cost(x) <= f * sum(y) <= f * OPT."""
    y = [Fraction(0)] * sc.universe
    paid = [Fraction(0)] * sc.n
    x = [0] * sc.n
    covered = [False] * sc.universe
    containing = [[j for j, s in enumerate(sc.sets) if e in s] for e in range(sc.universe)]
    for e in range(sc.universe):
        if covered[e]:
            continue
        delta = min(sc.costs[j] - paid[j] for j in containing[e])
        y[e] += delta
        for j in containing[e]:
            paid[j] += delta
        for j in containing[e]:
            if paid[j] == sc.costs[j] and not x[j]:
                x[j] = 1
                for u in sc.sets[j]:
                    covered[u] = True
    return x, y


# ---------------------------------------------------------------- step 4 ---

def jv_dual_ascent(fl):
    """Phase 1 of Jain-Vazirani. All clients start active with alpha_j = t = 0, and t grows continuously.
    Facility i receives max(0, alpha_j - d_ij) from each client j, and opens *temporarily* at the moment its
    receipts reach its cost. An active client freezes (alpha_j stops growing) as soon as it is tight
    (alpha_j >= d_ij) with some temporarily open facility. Simultaneous events at the same t all happen.
    Returns (alpha, opened_at): alpha a list of Fractions, opened_at a dict {facility: opening time}."""
    nf, nc = fl.nf, fl.nc
    t = Fraction(0)
    alpha = [None] * nc                      # None while active
    opened_at = {}

    def receipts(i, time):
        return sum(max(Fraction(0), (time if alpha[j] is None else alpha[j]) - fl.dist[i][j]) for j in range(nc))

    while any(a is None for a in alpha):
        # at time t: open every facility that is paid, then freeze every active client tight with an open one
        changed = True
        while changed:
            changed = False
            for i in range(nf):
                if i not in opened_at and receipts(i, t) >= fl.open_cost[i]:
                    opened_at[i] = t
                    changed = True
            for j in range(nc):
                if alpha[j] is None and any(fl.dist[i][j] <= t for i in opened_at):
                    alpha[j] = t
                    changed = True
        active = [j for j in range(nc) if alpha[j] is None]
        if not active:
            break
        # next event: an active client reaching some facility, or a facility becoming paid
        candidates = [Fraction(fl.dist[i][j]) for i in range(nf) for j in active if fl.dist[i][j] > t]
        for i in range(nf):
            if i in opened_at:
                continue
            slope = sum(1 for j in active if fl.dist[i][j] <= t)
            if slope:
                candidates.append(t + (fl.open_cost[i] - receipts(i, t)) / slope)
        t = min(candidates)
    return alpha, opened_at


def jv_prune(fl, alpha, opened_at):
    """Phase 2: two temporarily open facilities conflict if some client pays both (alpha_j > d_ij for both).
    Scan them by opening time (ties: lower index) and keep each one that conflicts with none kept so far.
    Returns the sorted list of kept facilities."""
    kept = []
    for i in sorted(opened_at, key=lambda i: (opened_at[i], i)):
        pays_i = {j for j in range(fl.nc) if alpha[j] > fl.dist[i][j]}
        if all(not any(alpha[j] > fl.dist[k][j] for j in pays_i) for k in kept):
            kept.append(i)
    return sorted(kept)


def jain_vazirani(fl):
    """Both phases, then every client to its nearest kept facility (ties: lower index).
    Returns (opened, assign, alpha); cost <= 3 * sum(alpha) <= 3 * OPT on metric instances."""
    alpha, opened_at = jv_dual_ascent(fl)
    opened = jv_prune(fl, alpha, opened_at)
    assign = [min(opened, key=lambda i: (fl.dist[i][j], i)) for j in range(fl.nc)]
    return opened, assign, alpha


# ---------------------------------------------------------------- step 5 ---

def vertex_cover_gap_instance(n):
    """K_n with unit weights: the LP value is n/2 (all halves), the optimum n - 1."""
    return VertexCover(n, tuple((u, v) for u in range(n) for v in range(u + 1, n)))


def set_cover_gap_instance(k):
    """Elements and sets both indexed by the nonzero vectors of GF(2)^k, as integers 1 .. 2^k - 1 (element or
    set number = integer - 1). Set v contains element u iff the dot product u.v is odd (popcount(u & v) odd).
    Unit costs. Every set has 2^(k-1) elements, so the LP value is at most (2^k - 1) / 2^(k-1) < 2; any cover
    needs k sets."""
    N = (1 << k) - 1
    sets = tuple(frozenset(u - 1 for u in range(1, N + 1) if bin(u & v).count("1") % 2) for v in range(1, N + 1))
    return SetCover(N, sets, (1,) * N)


def uniform_fractional(sc):
    """The fractional solution x_j = 1 / (smallest number of sets containing any element): feasible for the
    LP, so its cost bounds the LP value from above. Returns (value, x) with Fractions."""
    count = [0] * sc.universe
    for s in sc.sets:
        for e in s:
            count[e] += 1
    x = [Fraction(1, min(count))] * sc.n
    return sum(c * xj for c, xj in zip(sc.costs, x)), x
