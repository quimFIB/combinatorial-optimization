"""Unit 12 lab — Benders decomposition.  REFERENCE SOLUTION, functional.

Benders is an unfold over an immutable record: the cut sets, the best incumbent, the
phase (LP master or integer master) and the history. Each step is a pure function of
that record: solve the master, map the scenarios to recourse results, derive cuts.
The LP solves are HiGHS calls, pure functions of their data.
"""

from __future__ import annotations

import numpy as np
import toolz as tz

from colib.mip import MILP, highs_mip
from colib.solvers import highs_lp

INF = float("inf")


def _recourse_lp(inst, s, y, phase_one=False):
    F, C = inst.F, inst.C
    with_z = phase_one or inst.penalty is not None
    x_cols = [[1.0 if (col % C == j) else 0.0 for col in range(F * C)] for j in range(C)]
    z_cols = [[1.0 if k == j else 0.0 for k in range(C)] if with_z else [] for j in range(C)]
    demand_rows = [x_cols[j] + z_cols[j] for j in range(C)]
    cap_rows = [[1.0 if col // C == i else 0.0 for col in range(F * C)] + ([0.0] * C if with_z else [])
                for i in range(F)]
    A = np.array(demand_rows + cap_rows)
    unit = [inst.cost[i][j] for i in range(F) for j in range(C)]
    c = [0.0] * (F * C) + [1.0] * C if phase_one else unit + ([inst.penalty] * C if with_z else [])
    lower = list(inst.demand[s]) + [-INF] * F
    upper = [INF] * C + [inst.capacity[i] * y[i] for i in range(F)]
    return highs_lp(A, np.array(upper, float), np.array(c, float), sense="min", row_lower=np.array(lower, float))


def _split_duals(inst, duals):
    return [max(0.0, float(d)) for d in duals[:inst.C]], [max(0.0, -float(d)) for d in duals[inst.C:]]


# ---------------------------------------------------------------- step 1 ---

def second_stage(inst, s, y):
    info = _recourse_lp(inst, s, y)
    if info.status != "optimal":
        return INF, None, None
    v, alpha = _split_duals(inst, info.row_duals)
    return info.value, v, alpha


# ---------------------------------------------------------------- step 2 ---

def optimality_cut(inst, s, v, alpha):
    return (sum(d * vj for d, vj in zip(inst.demand[s], v)),
            [-u * a for u, a in zip(inst.capacity, alpha)])


def feasibility_cut(inst, s, y):
    info = _recourse_lp(inst, s, y, phase_one=True)
    return None if info.value <= 1e-7 else optimality_cut(inst, s, *_split_duals(inst, info.row_duals))


# ---------------------------------------------------------------- step 3 ---

def solve_master(inst, opt_cuts, feas_cuts, multicut=True, relax=False):
    F, S = inst.F, inst.S
    T = S if multicut else 1
    theta_col = lambda s: F + (s if multicut else 0)
    opt_rows = [tuple(coef) + tuple(-1.0 if F + t == theta_col(s) else 0.0 for t in range(T))
                for s, _, coef in opt_cuts]
    feas_rows = [tuple(coef) + (0.0,) * T for _, coef in feas_cuts]
    milp = MILP(c=tuple(inst.open_cost) + (tuple(inst.prob) if multicut else (1.0,)),
                A_ub=tuple(opt_rows + feas_rows),
                b_ub=tuple(-const for _, const, _ in opt_cuts) + tuple(-const for const, _ in feas_cuts),
                ub=(1,) * F + (INF,) * T, integer=(not relax,) * F + (False,) * T)
    res = highs_mip(milp, options={"mip_rel_gap": 1e-9})
    y = [float(v) if relax else int(round(v)) for v in res.x[:F]]
    return res.value, y, list(res.x[F:])


def benders(inst, multicut=True, pareto=False, lp_first=False, tol=1e-6, max_iter=500):
    F, S = inst.F, inst.S
    closed = lambda ub, lb: ub < INF and ub - lb <= tol * max(1.0, abs(ub))

    def step(st):
        lower, y, theta = solve_master(inst, st["opt"], st["feas"], multicut, st["relax"])
        core = [(a + b) / 2 for a, b in zip(st["core"], y)]
        results = [(s, *second_stage(inst, s, y)) for s in range(S)]
        infeasible = [s for s, q, _, _ in results if q == INF]
        feas = st["feas"] + [feasibility_cut(inst, s, y) for s in infeasible]
        feasible = not infeasible
        cuts = [(s, pareto_cut(inst, s, y, core, q) if pareto else optimality_cut(inst, s, v, a), q)
                for s, q, v, a in results if q < INF]
        expected = sum(inst.prob[s] * q for s, _, q in cuts)
        ub = sum(f * yi for f, yi in zip(inst.open_cost, y)) + expected if feasible else INF
        if not feasible:
            new_opt = []
        elif multicut:
            new_opt = [(s, c0, cf) for s, (c0, cf), q in cuts if theta[s] < q - 1e-7]
        else:
            new_opt = [(None, sum(inst.prob[s] * c0 for s, (c0, _), _ in cuts),
                        [sum(inst.prob[s] * cf[i] for s, (_, cf), _ in cuts) for i in range(F)])] \
                if theta[0] < expected - 1e-7 else []
        base = dict(st, opt=st["opt"] + new_opt, feas=feas, core=core)
        if st["relax"]:
            return dict(base, relax=not closed(ub, lower), done=False)
        best, best_y = (ub, y) if ub < st["best"] else (st["best"], st["best_y"])
        return dict(base, best=best, best_y=best_y, history=st["history"] + [(lower, best)], done=closed(best, lower))

    start = dict(opt=[], feas=[], core=[0.5] * F, relax=lp_first, best=INF, best_y=None, history=[], done=False)
    states = tz.take(max_iter, tz.drop(1, tz.iterate(step, start)))
    final = tz.last(tz.concat([[start], _until_done(states)]))
    return final["best"], final["best_y"], final["history"]


def _until_done(states):
    for st in states:
        yield st
        if st["done"]:
            return


# ---------------------------------------------------------------- step 4 ---

def pareto_cut(inst, s, y, core, q):
    F, C = inst.F, inst.C
    d, u = inst.demand[s], inst.capacity
    pair_rows = [[1.0 if k == j else 0.0 for k in range(C)] + [-1.0 if k == i else 0.0 for k in range(F)]
                 for i in range(F) for j in range(C)]
    optimal_row = [list(map(float, d)) + [-u[i] * y[i] for i in range(F)]]
    A = np.array(pair_rows + optimal_row)
    upper = np.array([inst.cost[i][j] for i in range(F) for j in range(C)] + [INF])
    lower = np.array([-INF] * (F * C) + [q - 1e-7 * max(1.0, abs(q))])
    obj = np.array(list(map(float, d)) + [-u[i] * core[i] for i in range(F)])
    info = highs_lp(A, upper, obj, sense="max", lower=0.0,
                    upper=np.array([inst.penalty] * C + [INF] * F, float), row_lower=lower)
    return optimality_cut(inst, s, list(info.x[:C]), list(info.x[C:]))
