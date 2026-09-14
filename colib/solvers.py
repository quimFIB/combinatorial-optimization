"""Thin, careful wrappers around the industrial solvers, for tests and "then" steps.

Careful means: statuses are normalised to "optimal" / "infeasible" /
"unbounded", and the known ways a solver's status can mislead are handled
(HiGHS's presolve reports some unbounded LPs as infeasible; the wrapper
re-checks).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SolveInfo:
    status: str
    value: float | None = None
    x: np.ndarray | None = None
    iterations: int = 0
    seconds: float = 0.0
    row_duals: np.ndarray | None = None
    col_duals: np.ndarray | None = None      # reduced costs
    extra: dict[str, Any] = field(default_factory=dict)


def highs_lp(A, b, c, *, sense="max", method="simplex", presolve=True, lower=0.0, upper=None,
             row_lower=None, warm=None) -> SolveInfo:
    """Solve  max/min c.x  s.t.  row_lower <= A x <= b,  lower <= x <= upper  with highspy.

    method: "simplex" (dual simplex), "primal" (primal simplex) or "ipm".
    """
    import highspy

    A = np.asarray(A, dtype=float)
    m, n = A.shape
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("presolve", "on" if presolve else "off")
    if method == "ipm":
        h.setOptionValue("solver", "ipm")
        h.setOptionValue("run_crossover", "on")
    else:
        h.setOptionValue("solver", "simplex")
        h.setOptionValue("simplex_strategy", 4 if method == "primal" else 1)
    inf = highspy.kHighsInf
    lo = np.broadcast_to(np.asarray(-inf if lower is None else lower, float), (n,))
    up = np.broadcast_to(np.asarray(inf if upper is None else upper, float), (n,))
    h.addVars(n, lo.copy(), up.copy())
    h.changeColsCost(n, np.arange(n, dtype=np.int32), np.asarray(c, dtype=float))
    rl = np.full(m, -inf) if row_lower is None else np.asarray(row_lower, float)
    starts, idx, vals = [], [], []
    for i in range(m):
        starts.append(len(idx))
        nz = np.nonzero(A[i])[0]
        idx.extend(nz.tolist())
        vals.extend(A[i, nz].tolist())
    h.addRows(m, rl, np.asarray(b, float), len(idx), np.asarray(starts, np.int32),
              np.asarray(idx, np.int32), np.asarray(vals, float))
    h.changeObjectiveSense(highspy.ObjSense.kMaximize if sense == "max" else highspy.ObjSense.kMinimize)
    t = time.perf_counter()
    h.run()
    dt = time.perf_counter() - t
    ms = h.getModelStatus()
    info = h.getInfo()
    iters = int(info.ipm_iteration_count if method == "ipm" else 0) + int(info.simplex_iteration_count)
    S = highspy.HighsModelStatus
    if ms == S.kOptimal:
        sol = h.getSolution()
        return SolveInfo("optimal", float(info.objective_function_value), np.array(sol.col_value),
                         iters, dt, np.array(sol.row_dual), np.array(sol.col_dual), {"highs": h})
    if ms == S.kUnbounded:
        return SolveInfo("unbounded", iterations=iters, seconds=dt)
    if ms in (S.kInfeasible, S.kUnboundedOrInfeasible) and presolve:
        # presolve can mislabel: re-run without it to get the true status
        again = highs_lp(A, b, c, sense=sense, method=method, presolve=False, lower=lower,
                         upper=upper, row_lower=row_lower)
        again.iterations += iters
        again.seconds += dt
        return again
    if ms == S.kInfeasible:
        return SolveInfo("infeasible", iterations=iters, seconds=dt)
    return SolveInfo(str(ms), iterations=iters, seconds=dt)


def lp_status(A, b, c, sense="max") -> SolveInfo:
    """HiGHS's verdict on  max c.x, A x <= b, x >= 0  with presolve pitfalls handled."""
    return highs_lp(A, b, c, sense=sense)


def highs_general(lp) -> SolveInfo:
    """Solve a colib.lp.GeneralLP with HiGHS. Row duals are HiGHS's own convention."""
    import highspy
    inf = highspy.kHighsInf
    lo_row = [b if s in (">=", "=") else -inf for s, b in zip(lp.senses, lp.b)]
    up_row = [b if s in ("<=", "=") else inf for s, b in zip(lp.senses, lp.b)]
    lo = [0.0 if s == ">=0" else -inf for s in lp.signs]
    up = [0.0 if s == "<=0" else inf for s in lp.signs]
    A = lp.A if lp.m else [[0.0] * lp.n]
    return highs_lp(A, up_row if lp.m else [inf], lp.c, sense=lp.sense, lower=lo, upper=up,
                    row_lower=lo_row if lp.m else [-inf])
