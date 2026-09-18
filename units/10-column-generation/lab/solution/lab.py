"""Unit 10 lab — column generation.  REFERENCE SOLUTION, imperative.

Cutting stock: roll width W, item widths, demands. A pattern is a tuple of counts,
one per item. The master LP is

    min  sum_p x_p   s.t.  sum_p a_ip x_p >= d_i  for every item i,   x >= 0.

CVRP: see colib.colgen.CVRP. A route is a tuple of customers (the depot is implicit
at both ends). The master is the set-partitioning LP over routes.
"""

from __future__ import annotations

import math

import numpy as np

from colib.mip import MILP, highs_mip
from colib.ref import unit
from colib.solvers import highs_lp

INF = float("inf")
TOL = 1e-9


# ---------------------------------------------------------------- step 1 ---

def initial_patterns(W, widths):
    """One homogeneous pattern per item: as many copies of it as fit in a roll."""
    m = len(widths)
    return [tuple(W // widths[i] if j == i else 0 for j in range(m)) for i in range(m)]


def solve_master(patterns, demands):
    """The restricted master LP. Returns (value, x, duals), x[p] per pattern and
    duals[i] >= 0 per demand constraint."""
    m, P = len(demands), len(patterns)
    A = np.array([[patterns[p][i] for p in range(P)] for i in range(m)], dtype=float)
    info = highs_lp(A, np.full(m, INF), np.ones(P), sense="min", row_lower=np.array(demands, float))
    assert info.status == "optimal", info.status
    return info.value, list(info.x), [max(0.0, float(y)) for y in info.row_duals]


# ---------------------------------------------------------------- step 2 ---

def price(W, widths, duals):
    """The pricing problem: the pattern of greatest total dual value. Returns
    (value, pattern). Its reduced cost is 1 - value."""
    value, counts = unit("16").unbounded_knapsack(list(duals), list(widths), W)
    return value, tuple(counts)


def farley_bound(demands, duals, price_value):
    """A lower bound on the master LP from any duals >= 0: scaled by the pricing value
    they become dual feasible, so d . duals / price_value bounds the LP from below."""
    if price_value <= TOL:
        return 0.0
    return sum(d * y for d, y in zip(demands, duals)) / price_value


# ---------------------------------------------------------------- step 3 ---

def column_generation(W, widths, demands, max_iter=10_000):
    """Returns (value, patterns, x, history) where history[k] = (master value, best lower
    bound so far) at iteration k. Stops when no pattern has reduced cost below -1e-9."""
    patterns = initial_patterns(W, widths)
    history, best = [], 0.0
    for _ in range(max_iter):
        value, x, duals = solve_master(patterns, demands)
        pv, pattern = price(W, widths, duals)
        best = max(best, farley_bound(demands, duals, pv))
        history.append((value, best))
        if 1 - pv >= -TOL:
            return value, patterns, x, history
        patterns.append(pattern)
    raise RuntimeError("column generation did not converge")


# ---------------------------------------------------------------- step 4 ---

def round_up(patterns, x):
    """Integer solution by rounding every x_p up. Returns (rolls, counts)."""
    counts = [math.ceil(v - 1e-9) for v in x]
    return sum(counts), counts


def restricted_master_ip(patterns, demands, time_limit=30.0):
    """The master with integrality, over the generated patterns only (price-and-branch).
    Returns (rolls, counts)."""
    m, P = len(demands), len(patterns)
    milp = MILP(c=(1,) * P, A_ub=tuple(tuple(-patterns[p][i] for p in range(P)) for i in range(m)),
                b_ub=tuple(-d for d in demands), integer=(True,) * P)
    res = highs_mip(milp, time_limit=time_limit)
    counts = [int(round(v)) for v in res.x]
    return sum(counts), counts


# ---------------------------------------------------------------- step 5 ---

def stabilised_column_generation(W, widths, demands, alpha=0.8, max_iter=10_000):
    """Column generation with Wentges dual smoothing. Price at
    alpha * centre + (1 - alpha) * master duals, where the centre is the duals with the
    best Farley bound so far. If that finds no column with negative reduced cost at the
    master duals (a mis-price), price at the master duals themselves.
    Returns (value, patterns, x, history) as in step 3."""
    patterns = initial_patterns(W, widths)
    history, best, centre = [], 0.0, None
    for _ in range(max_iter):
        value, x, duals = solve_master(patterns, demands)
        column = None
        if centre is not None and alpha > 0:
            sep = [alpha * c + (1 - alpha) * y for c, y in zip(centre, duals)]
            pv, pattern = price(W, widths, sep)
            bound = farley_bound(demands, sep, pv)
            if bound > best:
                best, centre = bound, sep
            if 1 - sum(a * y for a, y in zip(pattern, duals)) < -TOL:
                column = pattern
        if column is None:                                    # no centre yet, or a mis-price
            pv, pattern = price(W, widths, duals)
            bound = farley_bound(demands, duals, pv)
            if bound > best or centre is None:
                best, centre = max(best, bound), duals
            if 1 - pv >= -TOL:
                history.append((value, best))
                return value, patterns, x, history
            column = pattern
        history.append((value, best))
        patterns.append(column)
    raise RuntimeError("column generation did not converge")


# ---------------------------------------------------------------- step 6 ---

def espprc(cvrp, duals, max_routes=10):
    """Elementary shortest path with resource constraints, by labelling with dominance.
    duals[v] for customers 1..n (duals[0] is ignored). The reduced cost of a route r is
    cost(r) - sum of duals over its customers. Returns up to max_routes routes with the
    most negative reduced costs, as a list of (reduced cost, route), sorted."""
    n, dist, dem, Q = cvrp.n, cvrp.dist, cvrp.demand, cvrp.capacity
    # a label: (reduced cost so far, load, visited bitmask, last vertex, route tuple)
    buckets = {v: [] for v in range(1, n + 1)}
    frontier = []
    for v in range(1, n + 1):
        if dem[v] <= Q:
            lab = (dist[0][v] - duals[v], dem[v], 1 << v, v, (v,))
            buckets[v].append(lab)
            frontier.append(lab)
    finished = []
    while frontier:
        new = []
        for rc, load, mask, last, route in frontier:
            finished.append((rc + dist[last][0], route))
            for w in range(1, n + 1):
                if mask >> w & 1 or load + dem[w] > Q:
                    continue
                lab = (rc + dist[last][w] - duals[w], load + dem[w], mask | 1 << w, w, route + (w,))
                if any(o[0] <= lab[0] + TOL and o[1] <= lab[1] and o[2] & lab[2] == o[2]
                       for o in buckets[w]):
                    continue                                  # dominated by an existing label
                buckets[w] = [o for o in buckets[w]
                              if not (lab[0] <= o[0] + TOL and lab[1] <= o[1] and lab[2] & o[2] == lab[2])]
                buckets[w].append(lab)
                new.append(lab)
        alive = {id(l) for b in buckets.values() for l in b}
        frontier = [l for l in new if id(l) in alive]
    finished.sort()
    return finished[:max_routes]


def vrp_column_generation(cvrp, max_iter=1000):
    """The set-partitioning LP bound for CVRP by column generation with espprc pricing.
    Starts from one out-and-back route per customer. Returns (value, routes, x)."""
    n = cvrp.n
    routes = [(v,) for v in range(1, n + 1)]
    for _ in range(max_iter):
        A = np.array([[1.0 if v in r else 0.0 for r in routes] for v in range(1, n + 1)])
        costs = np.array([cvrp.route_cost(r) for r in routes], float)
        info = highs_lp(A, np.ones(n), costs, sense="min", row_lower=np.ones(n))
        duals = [0.0] + [float(y) for y in info.row_duals]
        new = [r for rc, r in espprc(cvrp, duals) if rc < -1e-6 and r not in routes]
        if not new:
            return info.value, routes, list(info.x)
        routes.extend(dict.fromkeys(new))
    raise RuntimeError("column generation did not converge")
