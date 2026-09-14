"""Unit 05 lab — formulations.  REFERENCE SOLUTION, functional.

A formulation is data. Each constraint family is a generator of (row, rhs) pairs,
and a model is the concatenation of the families it uses.
"""

from __future__ import annotations

from itertools import chain, combinations

from colib.mip import MILP, FacilityLocation, facility_names


def unit_row(n, entries):
    """A row of length n with the given {index: value} entries."""
    return tuple(entries.get(k, 0) for k in range(n))


def xi(inst, i, j):
    return inst.F + i * inst.C + j


def size(inst):
    return inst.F + inst.F * inst.C


def assignment_rows(inst):
    n = size(inst)
    return ((unit_row(n, {xi(inst, i, j): 1 for i in range(inst.F)}), 1) for j in range(inst.C))


def aggregated_rows(inst, M):
    n = size(inst)
    return ((unit_row(n, {**{xi(inst, i, j): 1 for j in range(inst.C)}, i: -M}), 0) for i in range(inst.F))


def linking_rows(inst):
    n = size(inst)
    return ((unit_row(n, {xi(inst, i, j): 1, i: -1}), 0) for i in range(inst.F) for j in range(inst.C))


def capacity_rows(inst):
    n = size(inst)
    return ((unit_row(n, {**{xi(inst, i, j): inst.demand[j] for j in range(inst.C)}, i: -inst.capacity[i]}), 0)
            for i in range(inst.F))


def cover_row(inst):
    n = size(inst)
    return iter([(unit_row(n, {i: -inst.capacity[i] for i in range(inst.F)}), -sum(inst.demand))])


def model(inst, inequality_families) -> MILP:
    ub_rows = tuple(chain.from_iterable(inequality_families))
    eq_rows = tuple(assignment_rows(inst))
    F, C = inst.F, inst.C
    return MILP(
        c=tuple(inst.open_cost) + tuple(inst.serve_cost[i][j] for i in range(F) for j in range(C)),
        A_ub=tuple(r for r, _ in ub_rows), b_ub=tuple(b for _, b in ub_rows),
        A_eq=tuple(r for r, _ in eq_rows), b_eq=tuple(b for _, b in eq_rows),
        ub=(1,) * size(inst), integer=(True,) * F + (False,) * (F * C), names=facility_names(F, C))


# ---------------------------------------------------------------- steps 1, 2, 4

def ufl_aggregated(inst: FacilityLocation, M) -> MILP:
    return model(inst, [aggregated_rows(inst, M)])


def ufl_disaggregated(inst: FacilityLocation) -> MILP:
    return model(inst, [linking_rows(inst)])


def cfl(inst: FacilityLocation, strong: bool) -> MILP:
    return model(inst, [capacity_rows(inst)] + ([linking_rows(inst), cover_row(inst)] if strong else []))


# ---------------------------------------------------------------- step 3 ---

def ufl_brute_force(inst: FacilityLocation):
    subsets = chain.from_iterable(combinations(range(inst.F), k) for k in range(1, inst.F + 1))
    cost = lambda S: (sum(inst.open_cost[i] for i in S)
                      + sum(min(inst.serve_cost[i][j] for i in S) for j in range(inst.C)))
    return min(((cost(S), S) for S in subsets), key=lambda p: p[0])


# ---------------------------------------------------------------- step 5 ---

def gap_closed(weak_bound, strong_bound, optimum):
    return 1.0 if optimum - weak_bound <= 1e-9 else (strong_bound - weak_bound) / (optimum - weak_bound)
