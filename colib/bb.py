"""Shared pieces for branch-and-bound (units 07, 08, 31).

A node is described by its variable bounds. Solving a node means solving the LP
relaxation of the MILP with those bounds, which colib does with HiGHS so that
the lab can be about the tree, not the LP.
"""

from __future__ import annotations

import math
import random as _random
from dataclasses import dataclass, replace

import numpy as np

from colib.mip import MILP, lp_relaxation

INT_TOL = 1e-6


@dataclass(frozen=True)
class NodeLP:
    status: str                    # "optimal" | "infeasible" | other
    value: float | None = None
    x: tuple | None = None


def solve_node(milp: MILP, lb, ub) -> NodeLP:
    """The LP relaxation of milp with the given variable bounds."""
    if any(l > u + 1e-9 for l, u in zip(lb, ub)):
        return NodeLP("infeasible")
    info = lp_relaxation(replace(milp, lb=tuple(lb), ub=tuple(ub)))
    if info.status != "optimal":
        return NodeLP("infeasible" if "nfeasible" in info.status else info.status)
    return NodeLP("optimal", info.value, tuple(float(v) for v in info.x))


@dataclass(frozen=True)
class BBResult:
    status: str                    # "optimal" | "infeasible" | "node_limit"
    value: float | None
    x: tuple | None
    nodes: int                     # nodes whose LP was solved
    lp_solves: int                 # all LP solves, including strong-branching probes


def multi_knapsack(n: int, m: int = 2, seed=0, tightness: float = 0.5) -> MILP:
    """A correlated multi-dimensional 0/1 knapsack, written as a *minimization* MILP
    (minimize -value). Correlated values make the LP bound weak, which is what
    makes the tree interesting."""
    r = _random.Random(seed)
    W = [[r.randint(10, 60) for _ in range(n)] for _ in range(m)]
    value = [int(sum(W[k][j] for k in range(m)) / m) + r.randint(5, 15) for j in range(n)]
    cap = [int(tightness * sum(row)) for row in W]
    return MILP(c=tuple(-v for v in value), A_ub=tuple(map(tuple, W)), b_ub=tuple(cap),
                ub=(1,) * n, integer=(True,) * n)


def is_integral(milp: MILP, x, tol=INT_TOL) -> bool:
    return all(not flag or abs(v - round(v)) <= tol for flag, v in zip(milp.integer, x))
