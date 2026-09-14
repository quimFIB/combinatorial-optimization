"""Unit 21 lab — lazy clause generation.  REFERENCE SOLUTION, functional where it clarifies.

Explanations are the natural functional part: a propagator is a pure function from the current
bounds to a list of clauses. The solver that consumes them is unit 20's CDCL, whose trail and
watches are mutable by design, so LCGSolver is inherited from the imperative reference (the
lab sheet says so). The order encoding, both propagators and the job-shop model are rewritten.
"""

from __future__ import annotations

import importlib.util
import sys
from itertools import combinations
from pathlib import Path

import toolz as tz


def _imperative():
    name = "_unit21_imperative_reference"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name("lab.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


_imp = _imperative()
sat = _imp.sat


# ---------------------------------------------------------------- step 1 ---

class IntVar:
    def __init__(self, model, lb, ub, name=""):
        self.lb, self.ub, self.name = lb, ub, name
        self.first = model.nvars + 1
        model.nvars += ub - lb
        model.clauses.extend([-self.le(v), self.le(v + 1)] for v in range(lb, ub - 1))

    def le(self, v):
        assert self.lb <= v < self.ub, (self.name, v)
        return self.first + (v - self.lb)

    def ge(self, v):
        return -self.le(v - 1)

    def bounds(self, solver):
        values = [solver.value[self.first + k] for k in range(self.ub - self.lb)]
        hi = next((self.lb + k for k, val in enumerate(values) if val is True), self.ub)
        lo = max((self.lb + k + 1 for k, val in enumerate(values) if val is False), default=self.lb)
        return lo, hi

    def value(self, solver):
        lo, hi = self.bounds(solver)
        assert lo == hi, f"{self.name} not fixed: [{lo}, {hi}]"
        return lo


class Model(_imp.Model):
    def int_var(self, lb, ub, name=""):
        return IntVar(self, lb, ub, name)


# ---------------------------------------------------------------- step 2 ---

def lit_true(solver, lit):
    v = solver.value[abs(lit)]
    return v is not None and v == (lit > 0)


def _clause(*parts):
    return [lit for part in parts for lit in part if lit is not None]


class Precedence:
    def __init__(self, x, d, y, enabled=None):
        self.x, self.d, self.y, self.enabled = x, d, y, enabled

    def propagate(self, solver):
        if self.enabled is not None and not lit_true(solver, self.enabled):
            return []
        guard = [] if self.enabled is None else [-self.enabled]
        (xlo, _), (_, yhi) = self.x.bounds(solver), self.y.bounds(solver)

        def push_y():                                        # y >= xlo + d because x >= xlo
            head = self.y.ge(xlo + self.d) if xlo + self.d <= self.y.ub else None
            return head, [None if xlo <= self.x.lb else -self.x.ge(xlo)]

        def pull_x():                                        # x <= yhi - d because y <= yhi
            head = self.x.le(yhi - self.d) if yhi - self.d >= self.x.lb else None
            return head, [None if yhi >= self.y.ub else -self.y.le(yhi)]

        rules = [rule() for fires, rule in ((xlo + self.d > self.y.lb, push_y), (yhi - self.d < self.x.ub, pull_x)) if fires]
        return [_clause(guard, reason, [head]) for head, reason in rules if head is None or not lit_true(solver, head)]


# ---------------------------------------------------------------- step 3 ---

class Unary:
    def __init__(self, starts, durations):
        self.starts, self.durations = list(starts), list(durations)

    def propagate(self, solver):
        b = [s.bounds(solver) for s in self.starts]
        tasks = list(zip(self.starts, self.durations, b))

        def explain(i, j):
            si, di, (est_i, lst_i) = tasks[i]
            sj, dj, (est_j, lst_j) = tasks[j]
            ect_i = est_i + di
            part = [si.le(lst_i) if lst_i < si.ub else None, si.ge(est_i) if est_i > si.lb else None]
            negated_part = [-l for l in part if l is not None]
            if est_j < ect_i and est_j + dj > lst_i:
                trigger = sj.ge(lst_i - dj + 1) if lst_i - dj + 1 > sj.lb else None
                head = sj.ge(ect_i) if ect_i <= sj.ub else None
                return [_clause(negated_part, [None if trigger is None else -trigger], [head])]
            if lst_j < ect_i and lst_j + dj > lst_i:
                trigger = sj.le(ect_i - 1) if ect_i - 1 < sj.ub else None
                head = sj.le(lst_i - dj) if lst_i - dj >= sj.lb else None
                return [_clause(negated_part, [None if trigger is None else -trigger], [head])]
            return []

        with_part = [i for i, (_, di, (est, lst)) in enumerate(tasks) if lst < est + di]
        return [c for i in with_part for j in range(len(tasks)) if j != i for c in explain(i, j)]


# ---------------------------------------------------------------- step 4 ---

LCGSolver = _imp.LCGSolver


# ---------------------------------------------------------------- step 5 ---

def jobshop_model(shop, horizon):
    m = Model()
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    dur = {op: shop.jobs[op[0]][op[1]][1] for op in ops}
    starts = {op: m.int_var(0, horizon - dur[op], f"s{op[0]},{op[1]}") for op in ops}
    mk = m.int_var(0, horizon, "makespan")
    chains = [Precedence(starts[(j, k)], dur[(j, k)], starts[(j, k + 1)])
              for j, job in enumerate(shop.jobs) for k in range(len(job) - 1)]
    ends = [Precedence(starts[(j, len(job) - 1)], dur[(j, len(job) - 1)], mk) for j, job in enumerate(shop.jobs)]
    by_machine = tz.groupby(lambda op: shop.jobs[op[0]][op[1]][0], ops)

    def machine_props(group):
        unary = Unary([starts[op] for op in group], [dur[op] for op in group])
        pairs = [(a, c, m.bool_var()) for a, c in combinations(group, 2)]
        return [unary] + [p for a, c, b in pairs for p in (Precedence(starts[a], dur[a], starts[c], enabled=b),
                                                           Precedence(starts[c], dur[c], starts[a], enabled=-b))]

    m.propagators = chains + ends + [p for mach in range(shop.machines) for p in machine_props(by_machine.get(mach, []))]
    return m, starts, mk


def minimise_makespan(shop, horizon, conflict_limit=None, **kw):
    model, starts, mk = jobshop_model(shop, horizon)
    solver = LCGSolver(model, **kw)

    def step(state):
        best, trace, _ = state
        result = solver.solve(conflict_limit=conflict_limit)
        if result is None:
            return best, trace, ("stopped", False)
        if result is False:
            return best, trace, ("done", True)
        value = mk.value(solver)
        solver.cancel_until(0)
        proven_now = value == 0 or not solver.add_clause([mk.le(value - 1)])
        return value, trace + [(value, solver.stats["conflicts"])], (("done", True) if proven_now else None)

    best, trace, (_, proven) = next(s for s in tz.iterate(step, (None, [], None)) if s[2] is not None)
    return best, proven, solver.stats, trace
