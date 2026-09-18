"""Unit 12 lab — Benders decomposition.  REFERENCE SOLUTION, imperative.

colib.colgen.StochasticFacility: open facilities y (first stage), then for each demand
scenario s serve customers (second stage). A cut is a pair (const, coef) over y:
  optimality cut for scenario s:  theta_s >= const + coef . y
  feasibility cut:                          const + coef . y <= 0
"""

from __future__ import annotations

import numpy as np

from colib.mip import MILP, highs_mip
from colib.solvers import highs_lp

INF = float("inf")


def _recourse_lp(inst, s, y, phase_one=False):
    """The scenario LP. Variables x_ij (row-major) then z_j. Rows: C demand rows, F capacity rows."""
    F, C = inst.F, inst.C
    with_z = phase_one or inst.penalty is not None
    nv = F * C + (C if with_z else 0)
    A = np.zeros((C + F, nv))
    for j in range(C):
        for i in range(F):
            A[j, i * C + j] = 1.0
        if with_z:
            A[j, F * C + j] = 1.0
    for i in range(F):
        A[C + i, i * C: i * C + C] = 1.0
    if phase_one:
        c = np.concatenate([np.zeros(F * C), np.ones(C)])
    else:
        c = np.array([inst.cost[i][j] for i in range(F) for j in range(C)] + ([inst.penalty] * C if with_z else []))
    lower = np.array(list(inst.demand[s]) + [-INF] * F, float)
    upper = np.array([INF] * C + [inst.capacity[i] * y[i] for i in range(F)], float)
    return highs_lp(A, upper, c, sense="min", row_lower=lower)


# ---------------------------------------------------------------- step 1 ---

def second_stage(inst, s, y):
    """Solve scenario s's recourse LP for fixed y. Returns (value, v, alpha): the optimal cost,
    the demand-constraint duals v[j] >= 0 and the capacity-constraint duals alpha[i] >= 0, so that
    value = sum_j d_sj v_j - sum_i u_i y_i alpha_i. Returns (INF, None, None) if infeasible."""
    info = _recourse_lp(inst, s, y)
    if info.status != "optimal":
        return INF, None, None
    duals = info.row_duals
    v = [max(0.0, float(d)) for d in duals[:inst.C]]
    alpha = [max(0.0, -float(d)) for d in duals[inst.C:]]
    return info.value, v, alpha


# ---------------------------------------------------------------- step 2 ---

def optimality_cut(inst, s, v, alpha):
    """theta_s >= sum_j d_sj v_j - sum_i (u_i alpha_i) y_i, as (const, coef)."""
    const = sum(d * vj for d, vj in zip(inst.demand[s], v))
    coef = [-inst.capacity[i] * alpha[i] for i in range(inst.F)]
    return const, coef


def feasibility_cut(inst, s, y):
    """If scenario s is infeasible at y, a cut violated by y from the phase-one LP
    min sum z (duals v <= 1): sum_j d_sj v_j - sum_i u_i alpha_i y_i <= 0. Otherwise None."""
    info = _recourse_lp(inst, s, y, phase_one=True)
    if info.value <= 1e-7:
        return None
    duals = info.row_duals
    v = [max(0.0, float(d)) for d in duals[:inst.C]]
    alpha = [max(0.0, -float(d)) for d in duals[inst.C:]]
    return optimality_cut(inst, s, v, alpha)


# ---------------------------------------------------------------- step 3 ---

def solve_master(inst, opt_cuts, feas_cuts, multicut=True, relax=False):
    """The master: min f.y + sum_s p_s theta_s (multicut) or f.y + theta (single cut), over
    0 <= y <= 1 (binary unless relax), theta >= 0, with the cuts so far. opt_cuts: list of
    (s, const, coef), s is None for an aggregated cut. Returns (value, y, theta list); y is
    rounded to integers unless relax."""
    F, S = inst.F, inst.S
    T = S if multicut else 1
    c = tuple(inst.open_cost) + (tuple(inst.prob) if multicut else (1.0,))
    rows, rhs = [], []
    for s, const, coef in opt_cuts:                           # coef.y - theta_s <= -const
        row = list(coef) + [0.0] * T
        row[F + (s if multicut else 0)] = -1.0
        rows.append(tuple(row))
        rhs.append(-const)
    for const, coef in feas_cuts:                             # coef.y <= -const
        rows.append(tuple(coef) + (0.0,) * T)
        rhs.append(-const)
    milp = MILP(c=c, A_ub=tuple(rows), b_ub=tuple(rhs), ub=(1,) * F + (INF,) * T,
                integer=(not relax,) * F + (False,) * T)
    res = highs_mip(milp, options={"mip_rel_gap": 1e-9})
    y = [float(v) for v in res.x[:F]] if relax else [int(round(v)) for v in res.x[:F]]
    return res.value, y, list(res.x[F:])


def benders(inst, multicut=True, pareto=False, lp_first=False, tol=1e-6, max_iter=500):
    """Benders decomposition. Each iteration: solve the master (a lower bound); solve every
    scenario's recourse LP at its y; add a feasibility cut for each infeasible scenario, else
    optimality cuts where the master's theta underestimates the recourse (one per scenario, or
    one probability-weighted aggregate when multicut is False). When all scenarios are feasible,
    f.y + sum_s p_s Q_s(y) is an upper bound.
    pareto=True (step 4): optimality cuts from pareto_cut, with a core point starting at 0.5 and
    moving halfway to each master solution.
    lp_first=True (step 5): first iterate with the LP relaxation of the master until its own gap
    closes (its bounds do not count towards the answer), keeping every cut; then continue with
    the integer master.
    Returns (upper bound, best y, history of (lower, upper) for the integer phase only); stops
    when upper < inf and upper - lower <= tol * max(1, |upper|)."""
    F, S = inst.F, inst.S
    opt_cuts, feas_cuts, history = [], [], []
    best, best_y = INF, None
    core = [0.5] * F
    relax = lp_first
    for _ in range(max_iter):
        lower, y, theta = solve_master(inst, opt_cuts, feas_cuts, multicut, relax)
        core = [(a + b) / 2 for a, b in zip(core, y)]
        recourse, new_cuts, feasible = [], [], True
        for s in range(S):
            q, v, alpha = second_stage(inst, s, y)
            if q == INF:
                feas_cuts.append(feasibility_cut(inst, s, y))
                feasible = False
                continue
            recourse.append(q)
            cut = pareto_cut(inst, s, y, core, q) if pareto else optimality_cut(inst, s, v, alpha)
            new_cuts.append((s, cut, q))
        ub = INF
        if feasible:
            ub = sum(f * yi for f, yi in zip(inst.open_cost, y)) + sum(p * q for p, q in zip(inst.prob, recourse))
            if multicut:
                opt_cuts += [(s, c0, cf) for s, (c0, cf), q in new_cuts if theta[s] < q - 1e-7]
            elif theta[0] < sum(p * q for p, q in zip(inst.prob, recourse)) - 1e-7:
                const = sum(inst.prob[s] * c0 for s, (c0, _), _ in new_cuts)
                coef = [sum(inst.prob[s] * cf[i] for s, (_, cf), _ in new_cuts) for i in range(F)]
                opt_cuts.append((None, const, coef))
        if relax:
            if ub < INF and ub - lower <= tol * max(1.0, abs(ub)):
                relax = False                                 # the LP master is solved: go integer
            continue
        if ub < best:
            best, best_y = ub, y
        history.append((lower, best))
        if best < INF and best - lower <= tol * max(1.0, abs(best)):
            return best, best_y, history
    return best, best_y, history


# ---------------------------------------------------------------- step 4 ---

def pareto_cut(inst, s, y, core, q):
    """A Magnanti–Wong (Pareto-optimal) optimality cut: among the dual solutions optimal at y
    (sum_j d v - sum_i u_i y_i alpha_i = q), take one maximising the cut's value at the core
    point. Dual feasibility: v_j - alpha_i <= cost_ij, 0 <= v_j <= penalty, alpha >= 0.
    Returns (const, coef)."""
    F, C = inst.F, inst.C
    d, u = inst.demand[s], inst.capacity
    nvar = C + F                                              # v_0..v_{C-1}, alpha_0..alpha_{F-1}
    A = np.zeros((F * C + 1, nvar))
    upper = np.zeros(F * C + 1)
    lower = np.full(F * C + 1, -INF)
    for i in range(F):
        for j in range(C):
            r = i * C + j
            A[r, j], A[r, C + i] = 1.0, -1.0
            upper[r] = inst.cost[i][j]
    A[-1, :C] = d
    A[-1, C:] = [-u[i] * y[i] for i in range(F)]
    lower[-1] = q - 1e-7 * max(1.0, abs(q))
    upper[-1] = INF
    obj = np.array(list(d) + [-u[i] * core[i] for i in range(F)], float)
    vub = np.array([inst.penalty] * C + [INF] * F, float)
    info = highs_lp(A, upper, obj, sense="max", lower=0.0, upper=vub, row_lower=lower)
    v, alpha = list(info.x[:C]), list(info.x[C:])
    return optimality_cut(inst, s, v, alpha)
