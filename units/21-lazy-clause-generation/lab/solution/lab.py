"""Unit 21 lab — lazy clause generation.  REFERENCE SOLUTION, imperative.

Integers become Booleans through the order encoding: for x in [lb, ub], literal [x <= v] for
lb <= v < ub, with [x <= v] -> [x <= v + 1]. CP propagators read bounds off the Boolean
assignment and, for every bound they tighten, hand the SAT solver an *explanation*: a clause
that is true in every solution and forces the new literal under the current assignment.
Unit 20's CDCL then learns from propagation exactly as it learns from original clauses.
"""

from __future__ import annotations

from colib.ref import unit

sat = unit("20")


# ---------------------------------------------------------------- step 1 ---

class IntVar:
    """An integer in [lb, ub] with Boolean variables for [x <= v], v = lb .. ub - 1."""

    def __init__(self, model, lb, ub, name=""):
        self.lb, self.ub, self.name = lb, ub, name
        self.first = model.nvars + 1
        model.nvars += ub - lb
        for v in range(lb, ub - 1):
            model.clauses.append([-self.le(v), self.le(v + 1)])

    def le(self, v):
        """The DIMACS literal [x <= v]. Only for lb <= v < ub."""
        assert self.lb <= v < self.ub, (self.name, v)
        return self.first + (v - self.lb)

    def ge(self, v):
        """The DIMACS literal [x >= v] = not [x <= v - 1]. Only for lb < v <= ub."""
        return -self.le(v - 1)

    def bounds(self, solver):
        """(min, max) of x under the solver's current assignment."""
        lo, hi = self.lb, self.ub
        for v in range(self.lb, self.ub):
            val = solver.value[self.first + v - self.lb]
            if val is True:
                hi = v
                break
            if val is False:
                lo = v + 1
        return lo, hi

    def value(self, solver):
        lo, hi = self.bounds(solver)
        assert lo == hi, f"{self.name} not fixed: [{lo}, {hi}]"
        return lo


class Model:
    def __init__(self):
        self.nvars = 0
        self.clauses = []
        self.propagators = []

    def int_var(self, lb, ub, name=""):
        return IntVar(self, lb, ub, name)

    def bool_var(self):
        self.nvars += 1
        return self.nvars


# ---------------------------------------------------------------- step 2 ---

def lit_true(solver, lit):
    v = solver.value[abs(lit)]
    return v is not None and v == (lit > 0)


class Precedence:
    """If literal `enabled` is true (or enabled is None): x + d <= y. Bounds propagation with explanations.
    propagate(solver) returns a list of clauses (DIMACS). A clause whose literals are all false but one
    forces that one; a clause whose literals are all false is a conflict."""

    def __init__(self, x, d, y, enabled=None):
        self.x, self.d, self.y, self.enabled = x, d, y, enabled

    def propagate(self, solver):
        if self.enabled is not None and not lit_true(solver, self.enabled):
            return []
        guard = [] if self.enabled is None else [-self.enabled]
        xlo, _ = self.x.bounds(solver)
        _, yhi = self.y.bounds(solver)
        out = []
        if xlo + self.d > self.y.lb:                              # y >= xlo + d  because  x >= xlo
            reason = [] if xlo <= self.x.lb else [-self.x.ge(xlo)]
            head = self.y.ge(xlo + self.d) if xlo + self.d <= self.y.ub else None
            clause = guard + reason + ([head] if head is not None else [])
            if head is None or not lit_true(solver, head):
                out.append(clause)
        if yhi - self.d < self.x.ub:                              # x <= yhi - d  because  y <= yhi
            reason = [] if yhi >= self.y.ub else [-self.y.le(yhi)]
            head = self.x.le(yhi - self.d) if yhi - self.d >= self.x.lb else None
            clause = guard + reason + ([head] if head is not None else [])
            if head is None or not lit_true(solver, head):
                out.append(clause)
        return out


# ---------------------------------------------------------------- step 3 ---

class Unary:
    """Tasks with start IntVars and durations on a resource of capacity 1, timetable filtering with
    explanations. If task i's compulsory part [lst_i, ect_i) is non-empty and task j (j != i) would overlap
    it when started at est_j, then s_j >= ect_i, explained by
        [s_i <= lst_i] and [s_i >= ect_i - d_i] and [s_j >= lst_i - d_j + 1]  ->  [s_j >= ect_i];
    symmetrically, if j would overlap it when started at lst_j, then s_j <= lst_i - d_j, explained by
        [s_i <= lst_i] and [s_i >= ect_i - d_i] and [s_j <= ect_i - 1]  ->  [s_j <= lst_i - d_j]."""

    def __init__(self, starts, durations):
        self.starts, self.durations = list(starts), list(durations)

    def propagate(self, solver):
        b = [s.bounds(solver) for s in self.starts]
        out = []
        for i, (si, di) in enumerate(zip(self.starts, self.durations)):
            est_i, lst_i = b[i]
            ect_i = est_i + di
            if lst_i >= ect_i:
                continue
            part = [lit for lit in (si.le(lst_i) if lst_i < si.ub else None,
                                    si.ge(est_i) if est_i > si.lb else None) if lit is not None]
            for j, (sj, dj) in enumerate(zip(self.starts, self.durations)):
                if j == i:
                    continue
                est_j, lst_j = b[j]
                if est_j < ect_i and est_j + dj > lst_i:              # j at its earliest start overlaps the part
                    trigger = sj.ge(lst_i - dj + 1) if lst_i - dj + 1 > sj.lb else None
                    head = sj.ge(ect_i) if ect_i <= sj.ub else None
                    clause = [-l for l in part] + ([-trigger] if trigger is not None else []) + \
                             ([head] if head is not None else [])
                    out.append(clause)
                elif lst_j < ect_i and lst_j + dj > lst_i:            # j at its latest start overlaps the part
                    trigger = sj.le(ect_i - 1) if ect_i - 1 < sj.ub else None
                    head = sj.le(lst_i - dj) if lst_i - dj >= sj.lb else None
                    clause = [-l for l in part] + ([-trigger] if trigger is not None else []) + \
                             ([head] if head is not None else [])
                    out.append(clause)
        return out


# ---------------------------------------------------------------- step 4 ---

class LCGSolver(sat.Solver):
    """Unit 20's CDCL with propagators. After unit propagation reaches a fixpoint, every propagator runs;
    each explanation clause that is unit or falsified under the current assignment is added as a learned
    clause (with its implied literal first) and either enqueued or reported as the conflict."""

    def __init__(self, model, proof=None, **kw):
        super().__init__(model.nvars, model.clauses, proof=proof, **kw)
        self.propagators = list(model.propagators)
        self.stats["explanations"] = 0

    def propagate(self):
        while True:
            confl = super().propagate()
            if confl is not None:
                return confl
            added = False
            for p in self.propagators:
                for clause in p.propagate(self):
                    result = self._add_explanation(clause)
                    if result == "conflict":
                        return self._last_conflict
                    added = added or result == "implied"
                if added:
                    break                                          # unit-propagate the new literals first
            if not added:
                return None

    def _add_explanation(self, clause):
        lits = [sat.to_internal(l) for l in dict.fromkeys(clause)]
        values = [self.lit_value(i) for i in lits]
        if any(v is True for v in values):
            return "satisfied"
        free = [i for i, v in zip(lits, values) if v is None]
        if len(free) > 1:
            return "not unit"
        self.stats["explanations"] += 1
        if not lits:
            self._last_conflict = self._attach_any([])
            return "conflict"
        if not free:
            lits.sort(key=lambda i: -self.level[i >> 1])
            self._last_conflict = self._attach_any(lits)
            return "conflict"
        rest = [i for i in lits if i != free[0]]
        rest.sort(key=lambda i: -self.level[i >> 1])
        c = [free[0]] + rest
        if len(c) == 1:
            if self.decision_level() == 0:
                self.enqueue(c[0], None)
            else:
                ci = self._attach_any(c)
                self.enqueue(c[0], ci)
            return "implied"
        ci = self._attach_any(c)
        self.enqueue(c[0], ci)
        return "implied"

    def _attach_any(self, c):
        """Store an explanation as a learned clause; unit clauses are stored without watches (they are only
        ever used as reasons)."""
        ci = len(self.clauses)
        self.clauses.append(c)
        self.learnt.append(True)
        self.lbd.append(len({self.level[i >> 1] for i in c}))
        self.deleted.append(False)
        if len(c) >= 2:
            self.watches[c[0]].append(ci)
            self.watches[c[1]].append(ci)
        if self.proof is not None:
            self.proof.append(" ".join(str(sat.to_dimacs(i)) for i in c) + (" 0" if c else "0"))
        return ci

    def locked(self, ci):
        c = self.clauses[ci]
        return bool(c) and self.reason[c[0] >> 1] == ci and self.lit_value(c[0]) is True


# ---------------------------------------------------------------- step 5 ---

def jobshop_model(shop, horizon):
    """Start IntVars s[(j, k)] in [0, horizon - d], a makespan IntVar in [0, horizon]; precedences inside jobs
    and to the makespan; per machine one Unary, plus for every pair of its operations a Boolean b with
    b -> (a before c) and not b -> (c before a) as enabled Precedence propagators. Returns
    (model, starts dict, makespan var)."""
    m = Model()
    starts = {}
    for j, job in enumerate(shop.jobs):
        for k, (_, d) in enumerate(job):
            starts[(j, k)] = m.int_var(0, horizon - d, f"s{j},{k}")
    mk = m.int_var(0, horizon, "makespan")
    for j, job in enumerate(shop.jobs):
        for k in range(len(job) - 1):
            m.propagators.append(Precedence(starts[(j, k)], job[k][1], starts[(j, k + 1)]))
        m.propagators.append(Precedence(starts[(j, len(job) - 1)], job[-1][1], mk))
    for mach in range(shop.machines):
        ops = [(j, k) for j, job in enumerate(shop.jobs) for k, (mm, _) in enumerate(job) if mm == mach]
        dur = [shop.jobs[j][k][1] for j, k in ops]
        m.propagators.append(Unary([starts[op] for op in ops], dur))
        for a in range(len(ops)):
            for c in range(a + 1, len(ops)):
                b = m.bool_var()
                m.propagators.append(Precedence(starts[ops[a]], dur[a], starts[ops[c]], enabled=b))
                m.propagators.append(Precedence(starts[ops[c]], dur[c], starts[ops[a]], enabled=-b))
    return m, starts, mk


def minimise_makespan(shop, horizon, conflict_limit=None, **kw):
    """Solve, then repeatedly add the unit clause [makespan <= best - 1] at level 0 and solve again, keeping
    every learned clause. Returns (best makespan or None, proven optimal?, stats, trace of (makespan,
    conflicts so far))."""
    model, starts, mk = jobshop_model(shop, horizon)
    solver = LCGSolver(model, **kw)
    best, trace = None, []
    while True:
        result = solver.solve(conflict_limit=conflict_limit)        # a limit on the total conflicts
        if result is None:
            return best, False, solver.stats, trace
        if result is False:
            return best, True, solver.stats, trace
        best = mk.value(solver)
        trace.append((best, solver.stats["conflicts"]))
        solver.cancel_until(0)
        if best == 0 or not solver.add_clause([mk.le(best - 1)]):
            return best, True, solver.stats, trace
