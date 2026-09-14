"""Unit 07 lab — branch and bound.  REFERENCE SOLUTION, functional.

The search is an unfold over an immutable state: the frontier (a tuple kept
sorted for best-first, used as a stack for depth-first), the incumbent, and
the statistics. Nothing is mutated; each step returns a new state.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, replace
from itertools import dropwhile

import toolz as tz

from colib.bb import INT_TOL, BBResult, is_integral, solve_node
from colib.mip import MILP


def fractionality(v):
    return min(v - math.floor(v), math.ceil(v) - v)


# ---------------------------------------------------------------- step 1 ---

def most_fractional(milp: MILP, node, stats):
    _, _, lp = node
    candidates = [(fractionality(v), -j, j) for j, (flag, v) in enumerate(zip(milp.integer, lp.x))
                  if flag and fractionality(v) > INT_TOL]
    return max(candidates)[2] if candidates else None


def children(lb, ub, j, value):
    return ((tuple(lb), tuple(math.floor(value) if k == j else u for k, u in enumerate(ub))),
            (tuple(math.ceil(value) if k == j else l for k, l in enumerate(lb)), tuple(ub)))


# ---------------------------------------------------------------- step 2 ---

@dataclass(frozen=True)
class Search:
    frontier: tuple            # of (bound, serial, node)
    incumbent: float
    best_x: tuple | None
    nodes: int
    stats: dict
    serial: int = 0
    stopped: str | None = None


def branch_and_bound(milp: MILP, rule=most_fractional, selection="best", node_limit=50_000):
    lb, ub = (tuple(float(v) for v in b) for b in milp.bounds())
    root = solve_node(milp, lb, ub)
    if root.status != "optimal":
        return BBResult("infeasible", None, None, 1, 1)

    def push(frontier, entry):
        if selection == "best":
            keys = [e[:2] for e in frontier]        # kept sorted by (bound, serial)
            i = bisect.bisect(keys, entry[:2])
            return frontier[:i] + (entry,) + frontier[i:]
        return frontier + (entry,)

    def expand(s: Search, node, j):
        nlb, nub, lp = node
        f = lp.x[j] - math.floor(lp.x[j])

        def one_child(s: Search, labelled):
            direction, (clb, cub) = labelled
            if s.stopped or s.nodes >= node_limit:
                return replace(s, stopped="node_limit")
            child = solve_node(milp, clb, cub)
            stats = tz.assoc(s.stats, "lp_solves", s.stats["lp_solves"] + 1)
            s = replace(s, nodes=s.nodes + 1, stats=stats)
            if child.status != "optimal":
                return s
            gain = max(child.value - lp.value, 0.0) / (f if direction == "down" else 1 - f)
            pseudo = tz.assoc(s.stats["pseudo"], (j, direction), s.stats["pseudo"].get((j, direction), ()) + (gain,))
            s = replace(s, stats=tz.assoc(s.stats, "pseudo", pseudo))
            if child.value >= s.incumbent - 1e-9:
                return s
            return replace(s, frontier=push(s.frontier, (child.value, s.serial, (clb, cub, child))),
                           serial=s.serial + 1)

        return tz.reduce(one_child, zip(("down", "up"), children(nlb, nub, j, lp.x[j])), s)

    def step(s: Search) -> Search:
        if not s.frontier:
            return replace(s, stopped="done")
        entry, rest = (s.frontier[0], s.frontier[1:]) if selection == "best" else (s.frontier[-1], s.frontier[:-1])
        s = replace(s, frontier=rest)
        node = entry[2]
        lp = node[2]
        if lp.value >= s.incumbent - 1e-9:
            return s
        if is_integral(milp, lp.x):
            return replace(s, incumbent=lp.value, best_x=lp.x)
        j = rule(milp, node, s.stats)                # strong branching adds its probe LPs to the counter
        return expand(s, node, j)

    start = Search(((root.value, 0, (lb, ub, root)),), math.inf, None, 1,
                   {"lp_solves": 1, "pseudo": {}}, 1)
    final = tz.first(dropwhile(lambda s: s.stopped is None, tz.iterate(step, start)))
    if final.stopped == "node_limit":
        return BBResult("node_limit", None if final.best_x is None else final.incumbent, final.best_x,
                        final.nodes, final.stats["lp_solves"])
    if final.best_x is None:
        return BBResult("infeasible", None, None, final.nodes, final.stats["lp_solves"])
    return BBResult("optimal", final.incumbent, final.best_x, final.nodes, final.stats["lp_solves"])


# ---------------------------------------------------------------- step 3 ---

def product_score(down_gain, up_gain, eps=1e-6):
    return max(down_gain, eps) * max(up_gain, eps)


# ---------------------------------------------------------------- step 4 ---

def pseudocost(milp: MILP, node, stats):
    _, _, lp = node
    pseudo = stats["pseudo"]
    seen = [sum(g) / len(g) for g in pseudo.values() if g]
    default = sum(seen) / len(seen) if seen else 1.0
    average = lambda key: (sum(pseudo[key]) / len(pseudo[key])) if pseudo.get(key) else default
    scored = [(product_score(f * average((j, "down")), (1 - f) * average((j, "up"))), -j, j)
              for j, (flag, v) in enumerate(zip(milp.integer, lp.x))
              if flag and fractionality(v) > INT_TOL
              for f in [v - math.floor(v)]]
    return max(scored)[2] if scored else None


# ---------------------------------------------------------------- step 5 ---

def strong_branching(milp: MILP, node, stats, max_candidates=8):
    lb, ub, lp = node
    candidates = sorted(((fractionality(v), j) for j, (flag, v) in enumerate(zip(milp.integer, lp.x))
                         if flag and fractionality(v) > INT_TOL), reverse=True)[:max_candidates]

    def gain(probe):
        return 1e9 if probe.status != "optimal" else probe.value - lp.value

    probes = {j: tuple(solve_node(milp, clb, cub) for clb, cub in children(lb, ub, j, lp.x[j]))
              for _, j in candidates}
    stats["lp_solves"] += 2 * len(probes)       # the one mutation: the tree's shared counter
    scored = [(product_score(gain(d), gain(u)), -j, j) for j, (d, u) in probes.items()]
    return max(scored)[2] if scored else None
