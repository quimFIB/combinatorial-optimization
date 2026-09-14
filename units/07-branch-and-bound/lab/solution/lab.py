"""Unit 07 lab — branch and bound.  REFERENCE SOLUTION, imperative.

MILPs are minimization (colib.mip.MILP). A node is (lb, ub, lp): its variable
bounds and its solved LP relaxation (colib.bb.NodeLP). A branching rule is a
function rule(milp, node, stats) -> index of the variable to branch on.
`stats` is a dict the tree shares with the rules:
    stats["lp_solves"]           every LP solved, including probes by rules
    stats["pseudo"][(j, dir)]    list of per-unit objective gains seen when
                                 branching on x_j in direction dir ("down"/"up")
"""

from __future__ import annotations

import heapq
import math
from itertools import count

from colib.bb import INT_TOL, BBResult, is_integral, solve_node
from colib.mip import MILP


def fractionality(v):
    return min(v - math.floor(v), math.ceil(v) - v)


# ---------------------------------------------------------------- step 1 ---

def most_fractional(milp: MILP, node, stats):
    _, _, lp = node
    best, best_frac = None, INT_TOL
    for j, (flag, v) in enumerate(zip(milp.integer, lp.x)):
        if flag and fractionality(v) > best_frac:
            best, best_frac = j, fractionality(v)
    return best


def children(lb, ub, j, value):
    """((lb, ub) of the down child x_j <= floor(value), (lb, ub) of the up child x_j >= ceil(value))."""
    down_ub = list(ub)
    down_ub[j] = math.floor(value)
    up_lb = list(lb)
    up_lb[j] = math.ceil(value)
    return (tuple(lb), tuple(down_ub)), (tuple(up_lb), tuple(ub))


# ---------------------------------------------------------------- step 2 ---

def branch_and_bound(milp: MILP, rule=most_fractional, selection="best", node_limit=50_000):
    lb, ub = (tuple(float(v) for v in b) for b in milp.bounds())
    stats = {"lp_solves": 1, "pseudo": {}}
    root = solve_node(milp, lb, ub)
    if root.status != "optimal":
        return BBResult("infeasible", None, None, 1, 1)

    incumbent, best_x, nodes = math.inf, None, 1
    tie = count()
    frontier = [(root.value, next(tie), (lb, ub, root))]    # heap for "best", stack for "dfs"

    while frontier:
        _, _, node = heapq.heappop(frontier) if selection == "best" else frontier.pop()
        nlb, nub, lp = node
        if lp.value >= incumbent - 1e-9:
            continue                                         # pruned: cannot beat the incumbent
        if is_integral(milp, lp.x):
            incumbent, best_x = lp.value, lp.x                # new incumbent
            continue
        j = rule(milp, node, stats)
        frac_down = lp.x[j] - math.floor(lp.x[j])
        for direction, (clb, cub) in zip(("down", "up"), children(nlb, nub, j, lp.x[j])):
            if nodes >= node_limit:
                return BBResult("node_limit", None if best_x is None else incumbent, best_x,
                                nodes, stats["lp_solves"])
            child = solve_node(milp, clb, cub)
            stats["lp_solves"] += 1
            nodes += 1
            if child.status != "optimal":
                continue                                     # infeasible child: pruned
            frac = frac_down if direction == "down" else 1 - frac_down
            stats["pseudo"].setdefault((j, direction), []).append(
                max(child.value - lp.value, 0.0) / frac)
            if child.value < incumbent - 1e-9:
                entry = (child.value, next(tie), (clb, cub, child))
                if selection == "best":
                    heapq.heappush(frontier, entry)
                else:
                    frontier.append(entry)
    if best_x is None:
        return BBResult("infeasible", None, None, nodes, stats["lp_solves"])
    return BBResult("optimal", incumbent, best_x, nodes, stats["lp_solves"])


# ---------------------------------------------------------------- step 3 ---

def product_score(down_gain, up_gain, eps=1e-6):
    return max(down_gain, eps) * max(up_gain, eps)


# ---------------------------------------------------------------- step 4 ---

def pseudocost(milp: MILP, node, stats):
    _, _, lp = node
    pseudo = stats["pseudo"]
    seen = [sum(g) / len(g) for g in pseudo.values() if g]
    default = sum(seen) / len(seen) if seen else 1.0
    average = lambda key: sum(pseudo[key]) / len(pseudo[key]) if pseudo.get(key) else default
    best, best_score = None, -1.0
    for j, (flag, v) in enumerate(zip(milp.integer, lp.x)):
        if not flag or fractionality(v) <= INT_TOL:
            continue
        f = v - math.floor(v)
        score = product_score(f * average((j, "down")), (1 - f) * average((j, "up")))
        if score > best_score:
            best, best_score = j, score
    return best


# ---------------------------------------------------------------- step 5 ---

def strong_branching(milp: MILP, node, stats, max_candidates=8):
    lb, ub, lp = node
    candidates = sorted(((fractionality(v), j) for j, (flag, v) in enumerate(zip(milp.integer, lp.x))
                         if flag and fractionality(v) > INT_TOL), reverse=True)[:max_candidates]
    best, best_score = None, -1.0
    for _, j in candidates:
        gains = []
        for clb, cub in children(lb, ub, j, lp.x[j]):
            probe = solve_node(milp, clb, cub)
            stats["lp_solves"] += 1
            gains.append(1e9 if probe.status != "optimal" else probe.value - lp.value)
        score = product_score(*gains)
        if score > best_score:
            best, best_score = j, score
    return best
