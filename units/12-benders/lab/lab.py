"""Unit 12 lab — Benders decomposition.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 12
after each. Read README.md first; HINTS.org has a ladder of hints per step.

The instance is colib.colgen.StochasticFacility, with fields F, C, S, open_cost[i],
capacity[i], cost[i][j] (per unit), demand[s][j], prob[s], and penalty (per unit of unmet
demand, or None when all demand must be met).

First stage: y[i] in {0, 1}, open facility i. Second stage, scenario s, for fixed y:
    Q_s(y) = min  sum_ij cost_ij x_ij + penalty * sum_j z_j
             s.t. sum_i x_ij + z_j >= demand_sj   (dual v_j >= 0)
                  sum_j x_ij <= capacity_i y_i    (dual alpha_i >= 0)
                  x, z >= 0                        (no z when penalty is None)
A cut is a pair (const, coef) over y:
    optimality cut for scenario s:  theta_s >= const + coef . y
    feasibility cut:                          const + coef . y <= 0

Given: colib.solvers.highs_lp (LPs with row duals), colib.mip.MILP and highs_mip (the master).
"""

from __future__ import annotations

import numpy as np

from colib.colgen import StochasticFacility
from colib.mip import MILP, highs_mip
from colib.solvers import highs_lp

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def second_stage(inst: StochasticFacility, s, y):
    """Solve scenario s's recourse LP at y (y may be fractional). Returns (value, v, alpha) with
    v (one per customer) and alpha (one per facility) nonnegative, so that
    value == sum_j demand[s][j] v[j] - sum_i capacity[i] y[i] alpha[i].
    Returns (INF, None, None) if the LP is infeasible.

    With highs_lp(..., sense="min"), a >= constraint has a dual >= 0 and a <= constraint a dual <= 0."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def optimality_cut(inst: StochasticFacility, s, v, alpha):
    """The cut theta_s >= sum_j demand[s][j] v[j] - sum_i (capacity[i] alpha[i]) y[i],
    as (const, coef) with coef a list of length F."""
    raise NotImplementedError  # TODO step 2


def feasibility_cut(inst: StochasticFacility, s, y):
    """If scenario s is infeasible at y, return a cut (const, coef) with const + coef . y > 0 that
    every y with a feasible scenario s satisfies with <= 0. Otherwise return None.

    Solve the phase-one LP  min sum_j z_j  over the same constraints (always with z). A positive value
    means infeasible, and its duals give the cut in the same form as optimality_cut."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def solve_master(inst: StochasticFacility, opt_cuts, feas_cuts, multicut=True, relax=False):
    """The master problem:
        min  sum_i open_cost_i y_i + sum_s prob_s theta_s     (multicut: one theta per scenario)
        min  sum_i open_cost_i y_i + theta                    (single cut)
    over 0 <= y <= 1 (integer unless relax) and theta >= 0, subject to the cuts.
    opt_cuts is a list of (s, const, coef); s is None for aggregated single cuts.
    Returns (value, y, theta list): y as ints unless relax, theta of length S or 1."""
    raise NotImplementedError  # TODO step 3


def benders(inst: StochasticFacility, multicut=True, pareto=False, lp_first=False, tol=1e-6, max_iter=500):
    """Benders decomposition.

    Each iteration: solve the master (its value is a lower bound). For each scenario solve the
    recourse LP at the master's y: if infeasible, add a feasibility cut; otherwise collect an
    optimality cut. If every scenario is feasible, f.y + sum_s prob_s Q_s(y) is an upper bound;
    add the optimality cuts of the scenarios whose theta_s < Q_s - 1e-7 (multicut), or one
    aggregated cut (const and coef weighted by prob) if theta < sum_s prob_s Q_s - 1e-7.
    Record (lower, best upper) in history and stop when best upper < inf and
    best - lower <= tol * max(1, |best|).

    pareto=True (step 4): build optimality cuts with pareto_cut, using a core point that starts
    at 0.5 for every facility and is replaced by (core + y) / 2 after each master solve.
    lp_first=True (step 5): begin with relax=True; while relaxed, do everything above except
    recording history or updating the best bound, and switch to the integer master as soon as
    the relaxed iteration's (f.y + expected recourse) - lower <= tol * max(1, |that|).
    Returns (best upper bound, its y, history)."""
    raise NotImplementedError  # TODO steps 3, 4 and 5


# ---------------------------------------------------------------- step 4 ---

def pareto_cut(inst: StochasticFacility, s, y, core, q):
    """A Magnanti–Wong optimality cut. Among the dual solutions that are optimal at y, choose the
    one whose cut is highest at the core point:
        max  sum_j d_j v_j - sum_i u_i core_i alpha_i
        s.t. v_j - alpha_i <= cost_ij          for all i, j
             sum_j d_j v_j - sum_i u_i y_i alpha_i >= q - 1e-7 * max(1, |q|)
             0 <= v_j <= penalty,  alpha_i >= 0
    Returns the cut (const, coef) for that (v, alpha)."""
    raise NotImplementedError  # TODO step 4
