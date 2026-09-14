"""Mixed-integer linear programs, facility-location instances, and solver wrappers.

A MILP here is always a *minimization*:

    min  c.x   s.t.  A_ub x <= b_ub,   A_eq x = b_eq,   lb <= x <= ub,
                     x_j integer for j with integer[j] True

Rows are plain lists; solvers get them as numpy/sparse arrays. Units 05, 07, 08,
10, 12 and 27 build on this.
"""

from __future__ import annotations

import math
import random as _random
import time
from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class MILP:
    c: tuple
    A_ub: tuple = ()
    b_ub: tuple = ()
    A_eq: tuple = ()
    b_eq: tuple = ()
    lb: tuple | None = None          # default 0
    ub: tuple | None = None          # default +inf
    integer: tuple | None = None     # default all continuous
    names: tuple | None = None

    @property
    def n(self):
        return len(self.c)

    def bounds(self):
        lb = self.lb if self.lb is not None else (0.0,) * self.n
        ub = self.ub if self.ub is not None else (math.inf,) * self.n
        return lb, ub

    def is_feasible(self, x, tol=1e-6) -> bool:
        x = np.asarray(x, float)
        lb, ub = self.bounds()
        if np.any(x < np.asarray(lb) - tol) or np.any(x > np.asarray(ub) + tol):
            return False
        if self.integer is not None and any(i and abs(v - round(v)) > tol for i, v in zip(self.integer, x)):
            return False
        if self.A_ub and np.any(np.asarray(self.A_ub, float) @ x > np.asarray(self.b_ub, float) + tol):
            return False
        if self.A_eq and np.any(np.abs(np.asarray(self.A_eq, float) @ x - np.asarray(self.b_eq, float)) > tol):
            return False
        return True

    def objective(self, x) -> float:
        return float(np.asarray(self.c, float) @ np.asarray(x, float))


@dataclass
class MIPInfo:
    status: str
    value: float | None = None
    x: np.ndarray | None = None
    nodes: int = 0
    seconds: float = 0.0
    bound: float | None = None        # best dual bound at termination
    root_bound: float | None = None   # dual bound after the root node (solver cuts included)
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- solvers

def _highs_model(milp: MILP, relax: bool):
    import highspy
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    n = milp.n
    lb, ub = milp.bounds()
    h.addVars(n, np.array([max(-inf, v) if v != -math.inf else -inf for v in lb], float),
              np.array([inf if v == math.inf else v for v in ub], float))
    h.changeColsCost(n, np.arange(n, dtype=np.int32), np.asarray(milp.c, float))

    def add(rows, lo, up):
        if not rows:
            return
        M = np.asarray(rows, float)
        starts, idx, vals = [], [], []
        for r in M:
            starts.append(len(idx))
            nz = np.nonzero(r)[0]
            idx.extend(nz.tolist())
            vals.extend(r[nz].tolist())
        h.addRows(len(M), np.asarray(lo, float), np.asarray(up, float), len(idx),
                  np.asarray(starts, np.int32), np.asarray(idx, np.int32), np.asarray(vals, float))

    add(milp.A_ub, [-inf] * len(milp.A_ub), milp.b_ub)
    add(milp.A_eq, milp.b_eq, milp.b_eq)
    if not relax and milp.integer is not None and any(milp.integer):
        idx = np.array([j for j, i in enumerate(milp.integer) if i], np.int32)
        h.changeColsIntegrality(len(idx), idx, np.array([highspy.HighsVarType.kInteger] * len(idx)))
    return h


def lp_relaxation(milp: MILP) -> MIPInfo:
    """Optimal value of the LP relaxation (integrality dropped), via HiGHS."""
    import highspy
    h = _highs_model(milp, relax=True)
    t = time.perf_counter()
    h.run()
    dt = time.perf_counter() - t
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        return MIPInfo(str(h.getModelStatus()), seconds=dt)
    return MIPInfo("optimal", h.getInfo().objective_function_value,
                   np.array(h.getSolution().col_value), 0, dt)


def highs_mip(milp: MILP, time_limit: float = 60.0, presolve: bool = True, options: dict | None = None) -> MIPInfo:
    """Solve with HiGHS's branch-and-cut; reports nodes and bounds."""
    import highspy
    h = _highs_model(milp, relax=False)
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("presolve", "on" if presolve else "off")
    for k, v in (options or {}).items():
        h.setOptionValue(k, v)
    t = time.perf_counter()
    h.run()
    dt = time.perf_counter() - t
    info = h.getInfo()
    ms = h.getModelStatus()
    S = highspy.HighsModelStatus
    status = {S.kOptimal: "optimal", S.kInfeasible: "infeasible", S.kTimeLimit: "time_limit"}.get(ms, str(ms))
    x = np.array(h.getSolution().col_value) if status in ("optimal", "time_limit") else None
    return MIPInfo(status, info.objective_function_value if x is not None else None, x,
                   int(info.mip_node_count), dt, info.mip_dual_bound)


def scip_mip(milp: MILP, time_limit: float = 60.0, settings: dict | None = None) -> MIPInfo:
    """Solve with SCIP; reports nodes, root dual bound and final bound."""
    from pyscipopt import Model, quicksum
    m = Model()
    m.hideOutput()
    m.setParam("limits/time", float(time_limit))
    for k, v in (settings or {}).items():
        m.setParam(k, v)
    lb, ub = milp.bounds()
    xs = []
    for j in range(milp.n):
        vt = "I" if milp.integer is not None and milp.integer[j] else "C"
        xs.append(m.addVar(vtype=vt, lb=None if lb[j] == -math.inf else lb[j],
                           ub=None if ub[j] == math.inf else ub[j], obj=float(milp.c[j])))
    for row, rhs in zip(milp.A_ub, milp.b_ub):
        m.addCons(quicksum(float(a) * xs[j] for j, a in enumerate(row) if a) <= float(rhs))
    for row, rhs in zip(milp.A_eq, milp.b_eq):
        m.addCons(quicksum(float(a) * xs[j] for j, a in enumerate(row) if a) == float(rhs))
    m.setMinimize()
    t = time.perf_counter()
    m.optimize()
    dt = time.perf_counter() - t
    st = m.getStatus()
    status = {"optimal": "optimal", "infeasible": "infeasible", "timelimit": "time_limit"}.get(st, st)
    x = np.array([m.getVal(v) for v in xs]) if m.getNSols() > 0 else None
    return MIPInfo(status, m.getObjVal() if x is not None else None, x, int(m.getNTotalNodes()), dt,
                   m.getDualbound(), m.getDualboundRoot())


# ---------------------------------------------------------------- facility location

@dataclass(frozen=True)
class FacilityLocation:
    """F facilities, C customers. open_cost[i]; serve_cost[i][j] = cost of serving
    all of customer j's demand from facility i. For the capacitated variant,
    demand[j] and capacity[i] are also used."""
    open_cost: tuple
    serve_cost: tuple
    demand: tuple
    capacity: tuple

    @property
    def F(self):
        return len(self.open_cost)

    @property
    def C(self):
        return len(self.demand)

    @classmethod
    def random(cls, F: int, C: int, seed=0, capacity_ratio: float = 3.0):
        """Points in the unit square; serving cost = distance x demand x 10.
        Total capacity is about capacity_ratio times total demand."""
        r = _random.Random(seed)
        fac = [(r.random(), r.random()) for _ in range(F)]
        cus = [(r.random(), r.random()) for _ in range(C)]
        demand = tuple(r.randint(5, 35) for _ in range(C))
        total = sum(demand)
        capacity = tuple(max(1, int(capacity_ratio * total / F * r.uniform(0.6, 1.4))) for _ in range(F))
        open_cost = tuple(r.randint(80, 200) for _ in range(F))
        serve = tuple(tuple(int(round(10 * math.dist(fac[i], cus[j]) * demand[j])) for j in range(C))
                      for i in range(F))
        return cls(open_cost, serve, demand, capacity)


def facility_names(F: int, C: int):
    """Variable order used by every facility-location formulation in the course:
    y_0..y_{F-1}, then x_00, x_01, ..., x_{F-1,C-1} (row-major)."""
    return tuple([f"y{i}" for i in range(F)] + [f"x{i}_{j}" for i in range(F) for j in range(C)])
