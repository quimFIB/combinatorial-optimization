"""Instances and compact models for decomposition methods (units 10, 11, 12, 27).

Cutting stock: rolls of width W; item i has width widths[i] and must be produced
demands[i] times. A pattern is a count vector a with sum a_i * widths[i] <= W.

CVRP: vertex 0 is the depot, 1..n are customers with demands; vehicles of a given
capacity leave and return to the depot; unlimited fleet; minimise total distance.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from colib.mip import MILP


@dataclass(frozen=True)
class CuttingStock:
    W: int
    widths: tuple[int, ...]
    demands: tuple[int, ...]

    @property
    def m(self):
        return len(self.widths)

    @classmethod
    def random(cls, m: int, seed=0, W: int = 1000, low: float = 0.1, high: float = 0.45, demand=(5, 50)):
        r = random.Random(seed)
        widths = sorted({r.randint(int(low * W), int(high * W)) for _ in range(4 * m)}, reverse=True)
        widths = tuple(sorted(r.sample(widths, min(m, len(widths))), reverse=True))
        return cls(W, widths, tuple(r.randint(*demand) for _ in widths))

    def first_fit_decreasing(self):
        """Number of rolls used by first-fit decreasing: an upper bound."""
        free = []
        for i in sorted(range(self.m), key=lambda i: -self.widths[i]):
            for _ in range(self.demands[i]):
                for k, f in enumerate(free):
                    if f >= self.widths[i]:
                        free[k] -= self.widths[i]
                        break
                else:
                    free.append(self.W - self.widths[i])
        return len(free)

    def kantorovich(self, rolls: int | None = None) -> MILP:
        """The compact model: y_k = roll k used, x_ik = copies of item i cut from roll k.
        Variables ordered y_0..y_{K-1}, then x row-major by roll."""
        K = rolls if rolls is not None else self.first_fit_decreasing()
        m, nv = self.m, K + K * self.m
        x = lambda k, i: K + k * m + i
        A_ub, b_ub = [], []
        for k in range(K):                                    # sum_i w_i x_ik <= W y_k
            row = [0] * nv
            row[k] = -self.W
            for i in range(m):
                row[x(k, i)] = self.widths[i]
            A_ub.append(tuple(row))
            b_ub.append(0)
        for i in range(m):                                    # sum_k x_ik >= d_i
            row = [0] * nv
            for k in range(K):
                row[x(k, i)] = -1
            A_ub.append(tuple(row))
            b_ub.append(-self.demands[i])
        for k in range(K - 1):                                # symmetry: y_k >= y_{k+1}
            row = [0] * nv
            row[k], row[k + 1] = -1, 1
            A_ub.append(tuple(row))
            b_ub.append(0)
        ub = (1,) * K + tuple(self.W // self.widths[i] for _ in range(K) for i in range(m))
        return MILP(c=(1,) * K + (0,) * (K * m), A_ub=tuple(A_ub), b_ub=tuple(b_ub),
                    ub=ub, integer=(True,) * nv)


@dataclass(frozen=True)
class CVRP:
    dist: tuple[tuple[int, ...], ...]      # (n+1) x (n+1), vertex 0 the depot
    demand: tuple[int, ...]                # demand[0] == 0
    capacity: int

    @property
    def n(self):
        return len(self.dist) - 1

    @classmethod
    def random(cls, n: int, seed=0, capacity: int = 20, max_demand: int = 9):
        r = random.Random(seed)
        pts = [(50.0, 50.0)] + [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(n)]
        dist = tuple(tuple(int(math.dist(a, b) + 0.5) for b in pts) for a in pts)
        return cls(dist, (0,) + tuple(r.randint(1, max_demand) for _ in range(n)), capacity)

    def route_cost(self, route):
        path = [0, *route, 0]
        return sum(self.dist[a][b] for a, b in zip(path, path[1:]))

    def route_load(self, route):
        return sum(self.demand[v] for v in route)


@dataclass(frozen=True)
class GAP:
    """Generalised assignment (minimisation): each job j goes to exactly one agent i,
    costing cost[i][j] and using weight[i][j] of agent i's capacity[i]."""
    cost: tuple[tuple[int, ...], ...]
    weight: tuple[tuple[int, ...], ...]
    capacity: tuple[int, ...]

    @property
    def m(self):
        return len(self.cost)

    @property
    def n(self):
        return len(self.cost[0])

    @classmethod
    def random(cls, m: int, n: int, seed=0, tightness: float = 0.8):
        """Chu–Beasley type C: costs 10–50, weights 5–25, capacity = tightness * sum_j w_ij / m."""
        r = random.Random(seed)
        cost = tuple(tuple(r.randint(10, 50) for _ in range(n)) for _ in range(m))
        weight = tuple(tuple(r.randint(5, 25) for _ in range(n)) for _ in range(m))
        cap = tuple(int(tightness * sum(weight[i]) / m) for i in range(m))
        return cls(cost, weight, cap)

    def milp(self) -> MILP:
        """x_ij row-major by agent."""
        m, n = self.m, self.n
        A_eq = tuple(tuple(1 if v % n == j else 0 for v in range(m * n)) for j in range(n))
        A_ub = tuple(tuple(self.weight[i][v % n] if v // n == i else 0 for v in range(m * n)) for i in range(m))
        return MILP(c=tuple(self.cost[v // n][v % n] for v in range(m * n)), A_ub=A_ub, b_ub=self.capacity,
                    A_eq=A_eq, b_eq=(1,) * n, ub=(1,) * (m * n), integer=(True,) * (m * n))

    def assignment_cost(self, agent_of):
        return sum(self.cost[agent_of[j]][j] for j in range(self.n))

    def is_feasible(self, agent_of):
        load = [0] * self.m
        for j, i in enumerate(agent_of):
            load[i] += self.weight[i][j]
        return len(agent_of) == self.n and all(load[i] <= self.capacity[i] for i in range(self.m))


@dataclass(frozen=True)
class StochasticFacility:
    """Two-stage stochastic capacitated facility location (unit 12).

    First stage: open facilities (open_cost[i], capacity[i]). Then a demand scenario s
    (probability prob[s], demand[s][j]) is revealed and customers are served at cost[i][j]
    per unit, with unmet demand at `penalty` per unit (None: all demand must be met).
    """
    open_cost: tuple[int, ...]
    capacity: tuple[int, ...]
    cost: tuple[tuple[float, ...], ...]
    demand: tuple[tuple[int, ...], ...]
    prob: tuple[float, ...]
    penalty: float | None

    @property
    def F(self):
        return len(self.open_cost)

    @property
    def C(self):
        return len(self.cost[0])

    @property
    def S(self):
        return len(self.prob)

    @classmethod
    def random(cls, F: int, C: int, S: int, seed=0, penalty: float | None = 50.0, capacity_ratio: float = 1.6):
        r = random.Random(seed)
        fac = [(r.random(), r.random()) for _ in range(F)]
        cus = [(r.random(), r.random()) for _ in range(C)]
        base = [r.randint(5, 35) for _ in range(C)]
        demand = tuple(tuple(max(0, int(round(b * r.lognormvariate(0, 0.35)))) for b in base) for _ in range(S))
        cap = tuple(max(1, int(capacity_ratio * sum(base) / F * r.uniform(0.7, 1.3))) for _ in range(F))
        cost = tuple(tuple(round(10 * math.dist(fac[i], cus[j]), 3) for j in range(C)) for i in range(F))
        open_cost = tuple(r.randint(150, 400) for _ in range(F))
        return cls(open_cost, cap, cost, demand, tuple(1.0 / S for _ in range(S)), penalty)

    def deterministic_equivalent(self, time_limit: float = 60.0):
        """Solve the extensive form with HiGHS (sparse). Returns (status, value, y, seconds, bound).
        Variables: y (F), then x_ijs for s, i, j, then z_js for s, j when penalty is set."""
        import highspy
        import numpy as np
        F, C, S = self.F, self.C, self.S
        pen = self.penalty is not None
        nx_ = F * C * S
        nz = C * S if pen else 0
        n = F + nx_ + nz
        xi = lambda s, i, j: F + s * F * C + i * C + j
        zi = lambda s, j: F + nx_ + s * C + j
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("time_limit", float(time_limit))
        inf = highspy.kHighsInf
        cost = np.zeros(n)
        cost[:F] = self.open_cost
        for s in range(S):
            for i in range(F):
                for j in range(C):
                    cost[xi(s, i, j)] = self.prob[s] * self.cost[i][j]
            if pen:
                for j in range(C):
                    cost[zi(s, j)] = self.prob[s] * self.penalty
        ub = np.full(n, inf)
        ub[:F] = 1
        h.addVars(n, np.zeros(n), ub)
        h.changeColsCost(n, np.arange(n, dtype=np.int32), cost)
        lo, up, starts, idx, val = [], [], [], [], []
        for s in range(S):
            for j in range(C):                                # sum_i x_ijs + z_js >= d_js
                starts.append(len(idx))
                idx += [xi(s, i, j) for i in range(F)] + ([zi(s, j)] if pen else [])
                val += [1.0] * (F + (1 if pen else 0))
                lo.append(self.demand[s][j])
                up.append(inf)
            for i in range(F):                                # sum_j x_ijs - u_i y_i <= 0
                starts.append(len(idx))
                idx += [xi(s, i, j) for j in range(C)] + [i]
                val += [1.0] * C + [-float(self.capacity[i])]
                lo.append(-inf)
                up.append(0.0)
        h.addRows(len(lo), np.array(lo), np.array(up), len(idx), np.array(starts, np.int32),
                  np.array(idx, np.int32), np.array(val))
        h.changeColsIntegrality(F, np.arange(F, dtype=np.int32), np.array([highspy.HighsVarType.kInteger] * F))
        h.setOptionValue("mip_rel_gap", 1e-6)
        t = time.perf_counter()
        h.run()
        dt = time.perf_counter() - t
        info = h.getInfo()
        S_ = highspy.HighsModelStatus
        status = {S_.kOptimal: "optimal", S_.kInfeasible: "infeasible", S_.kTimeLimit: "time_limit"}.get(
            h.getModelStatus(), str(h.getModelStatus()))
        y = [int(round(v)) for v in h.getSolution().col_value[:F]] if status in ("optimal", "time_limit") else None
        value = info.objective_function_value if y is not None else None
        return status, value, y, dt, info.mip_dual_bound
