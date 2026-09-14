"""Unit 24 lab — LP rounding and the primal-dual method.  REFERENCE SOLUTION, functional.

Rounding is a map. Probabilities are products. The primal-dual set cover is a fold over elements carrying
(y, paid, x). Jain-Vazirani's dual ascent is an unfold over events: the state is (t, alpha, opened_at), and
one step settles everything that happens at time t and jumps to the next event.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import reduce

import toolz as tz

from colib.approx import covering_lp
from colib.problems import SetCover, VertexCover

EPS = 1e-9


# ---------------------------------------------------------------- step 1 ---

def vertex_cover_lp(n, edges, weights):
    if not edges:
        return 0.0, [0.0] * n
    value, x, _ = covering_lp([[int(v in e) for v in range(n)] for e in edges], weights)
    return value, x


def threshold_rounding(x, t):
    return [int(xv >= t - EPS) for xv in x]


def vertex_cover_rounding(n, edges, weights):
    value, x = vertex_cover_lp(n, edges, weights)
    return threshold_rounding(x, 0.5), value


# ---------------------------------------------------------------- step 2 ---

def set_cover_lp(sc):
    value, x, _ = covering_lp([[int(e in s) for s in sc.sets] for e in range(sc.universe)], sc.costs)
    return value, x


def randomized_rounding(sc, x, rounds, rng):
    draws = [[rng.random() < xj for xj in x] for _ in range(rounds)]
    return [int(any(d[j] for d in draws)) for j in range(sc.n)]


def uncovered_probability(sc, x, rounds):
    return [math.prod(max(0.0, 1.0 - x[j]) ** rounds for j, s in enumerate(sc.sets) if e in s)
            for e in range(sc.universe)]


def expected_cost(sc, x, rounds):
    return sum(c * (1.0 - max(0.0, 1.0 - xj) ** rounds) for c, xj in zip(sc.costs, x))


def failure_bound(universe, rounds):
    return universe * math.exp(-rounds)


# ---------------------------------------------------------------- step 3 ---

def frequency(sc):
    return max(tz.frequencies(tz.concat(sc.sets)).values(), default=0)


def primal_dual_set_cover(sc):
    containing = [tuple(j for j, s in enumerate(sc.sets) if e in s) for e in range(sc.universe)]

    def visit(state, e):
        y, paid, x = state
        if any(x[j] for j in containing[e]):
            return state
        delta = min(sc.costs[j] - paid[j] for j in containing[e])
        paid = tuple(p + delta if j in containing[e] else p for j, p in enumerate(paid))
        x = tuple(int(xj or (j in containing[e] and paid[j] == sc.costs[j])) for j, xj in enumerate(x))
        return y[:e] + (y[e] + delta,) + y[e + 1:], paid, x

    y, _, x = reduce(visit, range(sc.universe), ((Fraction(0),) * sc.universe, (Fraction(0),) * sc.n, (0,) * sc.n))
    return list(x), list(y)


# ---------------------------------------------------------------- step 4 ---

def jv_dual_ascent(fl):
    nf, nc = fl.nf, fl.nc
    zero = Fraction(0)

    def receipts(i, t, alpha):
        return sum(max(zero, (t if a is None else a) - fl.dist[i][j]) for j, a in enumerate(alpha))

    def settle(state):
        """Open paid facilities and freeze tight clients at time t, until nothing changes."""
        t, alpha, opened = state
        opened2 = tz.merge(opened, {i: t for i in range(nf) if i not in opened and receipts(i, t, alpha) >= fl.open_cost[i]})
        alpha2 = tuple(t if a is None and any(fl.dist[i][j] <= t for i in opened2) else a for j, a in enumerate(alpha))
        return t, alpha2, opened2

    def step(state):
        t, alpha, opened = _fixpoint(settle, state)
        active = [j for j, a in enumerate(alpha) if a is None]
        if not active:
            return t, alpha, opened
        reach = [Fraction(fl.dist[i][j]) for i in range(nf) for j in active if fl.dist[i][j] > t]
        slopes = {i: sum(1 for j in active if fl.dist[i][j] <= t) for i in range(nf) if i not in opened}
        paid = [t + (fl.open_cost[i] - receipts(i, t, alpha)) / k for i, k in slopes.items() if k]
        return min(reach + paid), alpha, opened

    final = next(s for s in tz.iterate(step, (zero, (None,) * nc, {})) if all(a is not None for a in s[1]))
    return list(final[1]), final[2]


def _fixpoint(f, state):
    return next(b for a, b in tz.sliding_window(2, tz.iterate(f, state)) if a == b)


def jv_prune(fl, alpha, opened_at):
    pays = lambda i: frozenset(j for j in range(fl.nc) if alpha[j] > fl.dist[i][j])

    def keep(kept, i):
        return kept + (i,) if all(not (pays(i) & pays(k)) for k in kept) else kept

    return sorted(reduce(keep, sorted(opened_at, key=lambda i: (opened_at[i], i)), ()))


def jain_vazirani(fl):
    alpha, opened_at = jv_dual_ascent(fl)
    opened = jv_prune(fl, alpha, opened_at)
    return opened, [min(opened, key=lambda i: (fl.dist[i][j], i)) for j in range(fl.nc)], alpha


# ---------------------------------------------------------------- step 5 ---

def vertex_cover_gap_instance(n):
    return VertexCover(n, tuple((u, v) for u in range(n) for v in range(u + 1, n)))


def set_cover_gap_instance(k):
    N = (1 << k) - 1
    odd = lambda u, v: bin(u & v).count("1") % 2 == 1
    return SetCover(N, tuple(frozenset(u - 1 for u in range(1, N + 1) if odd(u, v)) for v in range(1, N + 1)), (1,) * N)


def uniform_fractional(sc):
    rarest = min(tz.frequencies(tz.concat(sc.sets)).get(e, 0) for e in range(sc.universe))
    x = [Fraction(1, rarest)] * sc.n
    return sum(c * xj for c, xj in zip(sc.costs, x)), x
