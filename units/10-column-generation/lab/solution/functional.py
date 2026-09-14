"""Unit 10 lab — column generation.  REFERENCE SOLUTION, functional.

Column generation is an unfold: the state is the set of columns (plus the
stabilisation centre and best bound), each step solves the master and prices,
and the sequence stops at the first state whose pricing finds nothing. The LP
solves are calls to HiGHS, which is fine: a pure function of the columns.
ESPPRC labelling is a fold over path lengths, each layer the non-dominated
extensions of the previous one.
"""

from __future__ import annotations

import math

import numpy as np
import toolz as tz

from colib.mip import MILP, highs_mip
from colib.ref import unit
from colib.solvers import highs_lp

INF = float("inf")
TOL = 1e-9


# ---------------------------------------------------------------- step 1 ---

def initial_patterns(W, widths):
    return [tuple(W // w if j == i else 0 for j in range(len(widths))) for i, w in enumerate(widths)]


def solve_master(patterns, demands):
    A = np.array([[p[i] for p in patterns] for i in range(len(demands))], dtype=float)
    info = highs_lp(A, np.full(len(demands), INF), np.ones(len(patterns)), sense="min",
                    row_lower=np.array(demands, float))
    return info.value, list(info.x), [max(0.0, float(y)) for y in info.row_duals]


# ---------------------------------------------------------------- step 2 ---

def price(W, widths, duals):
    value, counts = unit("16").unbounded_knapsack(list(duals), list(widths), W)
    return value, tuple(counts)


def farley_bound(demands, duals, price_value):
    return sum(d * y for d, y in zip(demands, duals)) / price_value if price_value > TOL else 0.0


# ---------------------------------------------------------------- step 3 ---

def _generate(W, widths, demands, step, start, max_iter):
    states = tz.take(max_iter, tz.iterate(step, start))
    final = next((s for s in states if s["done"]), None)
    if final is None:
        raise RuntimeError("column generation did not converge")
    return final["value"], final["patterns"], final["x"], final["history"]


def column_generation(W, widths, demands, max_iter=10_000):
    def step(s):
        value, x, duals = solve_master(s["patterns"], demands)
        pv, pattern = price(W, widths, duals)
        best = max(s["best"], farley_bound(demands, duals, pv))
        done = 1 - pv >= -TOL
        return dict(patterns=s["patterns"] if done else s["patterns"] + [pattern], value=value, x=x,
                    best=best, history=s["history"] + [(value, best)], done=done)

    start = dict(patterns=initial_patterns(W, widths), best=0.0, history=[], done=False)
    return _generate(W, widths, demands, step, step(start), max_iter)


# ---------------------------------------------------------------- step 4 ---

def round_up(patterns, x):
    counts = [math.ceil(v - 1e-9) for v in x]
    return sum(counts), counts


def restricted_master_ip(patterns, demands, time_limit=30.0):
    P = len(patterns)
    milp = MILP(c=(1,) * P, A_ub=tuple(tuple(-p[i] for p in patterns) for i in range(len(demands))),
                b_ub=tuple(-d for d in demands), integer=(True,) * P)
    counts = [int(round(v)) for v in highs_mip(milp, time_limit=time_limit).x]
    return sum(counts), counts


# ---------------------------------------------------------------- step 5 ---

def stabilised_column_generation(W, widths, demands, alpha=0.8, max_iter=10_000):
    reduced = lambda pattern, duals: 1 - sum(a * y for a, y in zip(pattern, duals))

    def step(s):
        value, x, duals = solve_master(s["patterns"], demands)
        centre, best = s["centre"], s["best"]
        smoothed = None
        if centre is not None and alpha > 0:
            sep = [alpha * c + (1 - alpha) * y for c, y in zip(centre, duals)]
            pv, pattern = price(W, widths, sep)
            b = farley_bound(demands, sep, pv)
            best, centre = (b, sep) if b > best else (best, centre)
            smoothed = pattern if reduced(pattern, duals) < -TOL else None
        if smoothed is not None:
            return dict(s, patterns=s["patterns"] + [smoothed], value=value, x=x, centre=centre, best=best,
                        history=s["history"] + [(value, best)], done=False)
        pv, pattern = price(W, widths, duals)
        b = farley_bound(demands, duals, pv)
        best, centre = (max(best, b), duals) if (b > best or centre is None) else (best, centre)
        done = 1 - pv >= -TOL
        return dict(patterns=s["patterns"] if done else s["patterns"] + [pattern], value=value, x=x,
                    centre=centre, best=best, history=s["history"] + [(value, best)], done=done)

    start = dict(patterns=initial_patterns(W, widths), centre=None, best=0.0, history=[], done=False)
    return _generate(W, widths, demands, step, step(start), max_iter)


# ---------------------------------------------------------------- step 6 ---

def _dominates(a, b):
    """Label a = (rc, load, visited frozenset, last, route) dominates b at the same vertex."""
    return a[0] <= b[0] + TOL and a[1] <= b[1] and a[2] <= b[2]


def espprc(cvrp, duals, max_routes=10):
    n, dist, dem, Q = cvrp.n, cvrp.dist, cvrp.demand, cvrp.capacity
    first = [(dist[0][v] - duals[v], dem[v], frozenset([v]), v, (v,)) for v in range(1, n + 1) if dem[v] <= Q]

    def extend(state):
        kept, frontier, finished = state
        candidates = [(rc + dist[last][w] - duals[w], load + dem[w], seen | {w}, w, route + (w,))
                      for rc, load, seen, last, route in frontier
                      for w in range(1, n + 1) if w not in seen and load + dem[w] <= Q]

        def admit(kept, lab):
            here = kept.get(lab[3], ())
            if any(_dominates(o, lab) for o in here):
                return kept
            return tz.assoc(kept, lab[3], tuple(o for o in here if not _dominates(lab, o)) + (lab,))

        kept2 = tz.reduce(admit, candidates, kept)
        alive = {id(l) for labs in kept2.values() for l in labs}
        closed = [(rc + dist[last][0], route) for rc, _, _, last, route in frontier]
        return kept2, [l for l in candidates if id(l) in alive], finished + closed

    start = (tz.groupby(3, first), first, [])
    _, _, finished = next(s for s in tz.iterate(extend, start) if not s[1])
    return sorted(finished)[:max_routes]


def vrp_column_generation(cvrp, max_iter=1000):
    n = cvrp.n

    def step(s):
        routes = s["routes"]
        A = np.array([[1.0 if v in r else 0.0 for r in routes] for v in range(1, n + 1)])
        info = highs_lp(A, np.ones(n), np.array([cvrp.route_cost(r) for r in routes], float),
                        sense="min", row_lower=np.ones(n))
        duals = [0.0] + [float(y) for y in info.row_duals]
        new = list(dict.fromkeys(r for rc, r in espprc(cvrp, duals) if rc < -1e-6 and r not in routes))
        return dict(routes=routes + new, value=info.value, x=list(info.x), done=not new)

    final = next((s for s in tz.take(max_iter, tz.iterate(step, step(dict(routes=[(v,) for v in range(1, n + 1)]))))
                  if s["done"]), None)
    if final is None:
        raise RuntimeError("column generation did not converge")
    return final["value"], final["routes"], final["x"]
