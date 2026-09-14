"""Unit 05 lab — formulations and the integrality gap.  REFERENCE SOLUTION, imperative.

Every formulation uses the variable order of colib.mip.facility_names:
y_0..y_{F-1} (open facility i), then x_ij row-major (fraction of customer j's
demand served by facility i). All are minimization MILPs.
"""

from __future__ import annotations

from itertools import combinations

from colib.mip import MILP, FacilityLocation, facility_names


def _x(inst, i, j):
    return inst.F + i * inst.C + j


def _common(inst):
    F, C = inst.F, inst.C
    n = F + F * C
    c = list(inst.open_cost) + [inst.serve_cost[i][j] for i in range(F) for j in range(C)]
    A_eq, b_eq = [], []
    for j in range(C):                                  # every customer fully served
        row = [0] * n
        for i in range(F):
            row[_x(inst, i, j)] = 1
        A_eq.append(row)
        b_eq.append(1)
    ub = [1] * n
    integer = [True] * F + [False] * (F * C)
    return n, c, A_eq, b_eq, ub, integer


# ---------------------------------------------------------------- step 1 ---

def ufl_aggregated(inst: FacilityLocation, M) -> MILP:
    n, c, A_eq, b_eq, ub, integer = _common(inst)
    A_ub, b_ub = [], []
    for i in range(inst.F):                             # sum_j x_ij <= M y_i
        row = [0] * n
        for j in range(inst.C):
            row[_x(inst, i, j)] = 1
        row[i] = -M
        A_ub.append(row)
        b_ub.append(0)
    return MILP(tuple(c), tuple(map(tuple, A_ub)), tuple(b_ub), tuple(map(tuple, A_eq)), tuple(b_eq),
                None, tuple(ub), tuple(integer), facility_names(inst.F, inst.C))


# ---------------------------------------------------------------- step 2 ---

def ufl_disaggregated(inst: FacilityLocation) -> MILP:
    n, c, A_eq, b_eq, ub, integer = _common(inst)
    A_ub, b_ub = [], []
    for i in range(inst.F):                             # x_ij <= y_i
        for j in range(inst.C):
            row = [0] * n
            row[_x(inst, i, j)] = 1
            row[i] = -1
            A_ub.append(row)
            b_ub.append(0)
    return MILP(tuple(c), tuple(map(tuple, A_ub)), tuple(b_ub), tuple(map(tuple, A_eq)), tuple(b_eq),
                None, tuple(ub), tuple(integer), facility_names(inst.F, inst.C))


# ---------------------------------------------------------------- step 3 ---

def ufl_brute_force(inst: FacilityLocation):
    best = None
    for k in range(1, inst.F + 1):
        for S in combinations(range(inst.F), k):
            cost = sum(inst.open_cost[i] for i in S)
            for j in range(inst.C):
                cost += min(inst.serve_cost[i][j] for i in S)
            if best is None or cost < best[0]:
                best = (cost, S)
    return best


# ---------------------------------------------------------------- step 4 ---

def cfl(inst: FacilityLocation, strong: bool) -> MILP:
    n, c, A_eq, b_eq, ub, integer = _common(inst)
    A_ub, b_ub = [], []
    for i in range(inst.F):                             # sum_j d_j x_ij <= u_i y_i
        row = [0] * n
        for j in range(inst.C):
            row[_x(inst, i, j)] = inst.demand[j]
        row[i] = -inst.capacity[i]
        A_ub.append(row)
        b_ub.append(0)
    if strong:
        for i in range(inst.F):                         # x_ij <= y_i
            for j in range(inst.C):
                row = [0] * n
                row[_x(inst, i, j)] = 1
                row[i] = -1
                A_ub.append(row)
                b_ub.append(0)
        row = [0] * n                                   # sum_i u_i y_i >= total demand
        for i in range(inst.F):
            row[i] = -inst.capacity[i]
        A_ub.append(row)
        b_ub.append(-sum(inst.demand))
    return MILP(tuple(c), tuple(map(tuple, A_ub)), tuple(b_ub), tuple(map(tuple, A_eq)), tuple(b_eq),
                None, tuple(ub), tuple(integer), facility_names(inst.F, inst.C))


# ---------------------------------------------------------------- step 5 ---

def gap_closed(weak_bound, strong_bound, optimum):
    """Fraction of the weak formulation's integrality gap that the strong one closes."""
    if optimum - weak_bound <= 1e-9:
        return 1.0
    return (strong_bound - weak_bound) / (optimum - weak_bound)
