"""Unit 05 lab — formulations and the integrality gap.

    uv run co test 05

You build MILPs (colib.mip.MILP, always *minimization*) for facility location:
open facilities (cost f_i each) and serve every customer from open facilities
(cost c_ij for serving all of customer j from facility i).

Variable order, fixed for every formulation (colib.mip.facility_names):
    y_0 .. y_{F-1}                     1 if facility i is open        (integer, 0..1)
    x_00, x_01, .., x_{F-1,C-1}        fraction of customer j served  (continuous, 0..1)
                                        by facility i, row-major: index F + i*C + j

Every formulation has the same objective (sum f_i y_i + sum c_ij x_ij), the same
assignment equalities (sum_i x_ij = 1 for every j), upper bounds of 1 on every
variable, and integer=True for the y's only. They differ in how x is linked to y.

A MILP is data: tuples of rows. Build it with loops or with generators of
(row, rhs) pairs; see FUNCTIONAL.md and solution/functional.py.
"""

from __future__ import annotations

from colib.mip import MILP, FacilityLocation, facility_names


# ---------------------------------------------------------------- step 1 ---

def ufl_aggregated(inst: FacilityLocation, M) -> MILP:
    """Uncapacitated facility location with one linking constraint per facility:

        sum_j x_ij <= M * y_i          (written as sum_j x_ij - M y_i <= 0)

    Return a MILP with A_eq = the C assignment rows, A_ub = these F rows.
    Include names=facility_names(inst.F, inst.C).
    """
    raise NotImplementedError("step 1: ufl_aggregated")


# ---------------------------------------------------------------- step 2 ---

def ufl_disaggregated(inst: FacilityLocation) -> MILP:
    """The same problem, with one linking constraint per (facility, customer) pair:

        x_ij <= y_i                    (x_ij - y_i <= 0), F*C rows in A_ub

    """
    raise NotImplementedError("step 2: ufl_disaggregated")


# ---------------------------------------------------------------- step 3 ---

def ufl_brute_force(inst: FacilityLocation):
    """The optimum by enumeration, with no solver: return (value, open_set), where
    open_set is a tuple of facility indices. Once the open set is fixed, every
    customer simply uses its cheapest open facility."""
    raise NotImplementedError("step 3: ufl_brute_force")


# ---------------------------------------------------------------- step 4 ---

def cfl(inst: FacilityLocation, strong: bool) -> MILP:
    """Capacitated facility location (demand may be split across facilities):

        sum_j demand_j x_ij <= capacity_i y_i       for every i    (always)

    If strong, also add, in this order after the capacity constraints:
        x_ij <= y_i                                  for every i, j
        sum_i capacity_i y_i >= sum_j demand_j       (one row, written as <=)

    A_ub has F rows (weak) or F + F*C + 1 rows (strong).
    """
    raise NotImplementedError("step 4: cfl")


# ---------------------------------------------------------------- step 5 ---

def gap_closed(weak_bound, strong_bound, optimum):
    """The fraction of the weak formulation's integrality gap closed by the strong
    one: (strong - weak) / (optimum - weak). If there is no gap to close, return 1.0.
    (Minimization: bounds are below the optimum.)"""
    raise NotImplementedError("step 5: gap_closed")
