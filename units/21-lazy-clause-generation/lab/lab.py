"""Unit 21 lab — lazy clause generation.

Fill in the parts marked TODO, one step at a time, and run
    uv run co test 21
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Integers become Booleans through the order encoding: for x in [lb, ub], literal [x <= v] for
lb <= v < ub, with clauses [x <= v] -> [x <= v + 1]. CP propagators read bounds off the Boolean
assignment and, for every bound they tighten, return an *explanation*: a clause, true in every
solution of the constraint, that forces the new literal under the current assignment. Unit 20's
CDCL (`sat`, the reference or yours with CO_MINE=20) learns from those clauses like any other.

All literals here are DIMACS ints.
"""

from __future__ import annotations

from colib.problems import JobShop
from colib.ref import unit

sat = unit("20")


# ---------------------------------------------------------------- step 1 ---

class IntVar:
    """An integer in [lb, ub]: Boolean variables first .. first + (ub - lb) - 1 stand for [x <= lb], ...,
    [x <= ub - 1]."""

    def __init__(self, model, lb, ub, name=""):
        """Take the next ub - lb variable numbers from the model and add the chain clauses
        (not [x <= v]) or [x <= v + 1] for lb <= v < ub - 1."""
        raise NotImplementedError  # TODO step 1

    def le(self, v):
        """The literal [x <= v], for lb <= v < ub."""
        raise NotImplementedError  # TODO step 1

    def ge(self, v):
        """The literal [x >= v] = not [x <= v - 1], for lb < v <= ub."""
        raise NotImplementedError  # TODO step 1

    def bounds(self, solver):
        """(min, max) of x under solver.value (index by Boolean variable number): the largest v + 1 with
        [x <= v] false, and the smallest v with [x <= v] true (ub if none)."""
        raise NotImplementedError  # TODO step 1

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


def lit_true(solver, lit):
    v = solver.value[abs(lit)]
    return v is not None and v == (lit > 0)


# ---------------------------------------------------------------- step 2 ---

class Precedence:
    """x + d <= y, when literal `enabled` is true (always, if enabled is None).

    propagate(solver) returns a list of explanation clauses (nothing if disabled):
      * if min(x) + d > y.lb:  (not enabled) or (not [x >= min x]) or [y >= min x + d]
      * if max(y) - d < x.ub:  (not enabled) or (not [y <= max y]) or [x <= max y - d]
    Leave out a reason literal that would be trivially true (x's min is still x.lb, y's max is still y.ub)
    and a head that lies outside the variable's range (then the clause is a conflict explanation). Skip a
    clause whose head is already true."""

    def __init__(self, x, d, y, enabled=None):
        self.x, self.d, self.y, self.enabled = x, d, y, enabled

    def propagate(self, solver):
        raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

class Unary:
    """Tasks with start IntVars and durations on a machine of capacity 1: timetable filtering, explained.

    For each task i with a compulsory part [lst_i, ect_i) (lst_i = max s_i, ect_i = min s_i + d_i, lst_i < ect_i),
    whose literals are [s_i <= lst_i] and [s_i >= est_i] (leave out either if trivially true), and each other
    task j with bounds [est_j, lst_j]:
      * if est_j < ect_i and est_j + d_j > lst_i (j at its earliest start overlaps the part):
            not part  or  not [s_j >= lst_i - d_j + 1]  or  [s_j >= ect_i]
      * else if lst_j < ect_i and lst_j + d_j > lst_i (j at its latest start overlaps it):
            not part  or  not [s_j <= ect_i - 1]  or  [s_j <= lst_i - d_j]
    (Trigger literals that are trivially true, and heads outside s_j's range, are left out.)
    Returns the list of clauses."""

    def __init__(self, starts, durations):
        self.starts, self.durations = list(starts), list(durations)

    def propagate(self, solver):
        raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

class LCGSolver(sat.Solver):
    """Unit 20's CDCL plus propagators.

    propagate(): loop { unit-propagate (return a conflict if there is one); run the propagators, turning each
    explanation into a clause through _add_explanation; stop at a conflict; if some propagator implied a
    new literal, go back to unit propagation; if none did, return None }.

    _add_explanation(clause) must: ignore it if some literal is already true, or if two or more are
    unassigned; otherwise count stats['explanations'], store it as a learned clause (the unassigned literal
    first; the remaining literals ordered by decreasing decision level) and log it to the proof, then
    either enqueue the unassigned literal with it as reason, or, if every literal is false, remember it as
    the conflict. Unit explanations at level 0 are enqueued without a reason."""

    def __init__(self, model, proof=None, **kw):
        raise NotImplementedError  # TODO step 4

    def propagate(self):
        raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def jobshop_model(shop: JobShop, horizon):
    """Start IntVars s[(j, k)] in [0, horizon - d_jk] (created job by job), then a makespan IntVar in [0, horizon].
    Propagators: Precedence(s[j, k], d, s[j, k + 1]) inside each job; Precedence(s[j, last], d, makespan); per
    machine a Unary over its operations and, for every pair (a, c) of them, a Boolean b with
    Precedence(a, d_a, c, enabled=b) and Precedence(c, d_c, a, enabled=-b).
    Returns (model, starts dict, makespan IntVar)."""
    raise NotImplementedError  # TODO step 5


def minimise_makespan(shop: JobShop, horizon, conflict_limit=None, **kw):
    """Build the model and one LCGSolver (kw passed on). Loop: solve (conflict_limit bounds the total
    conflicts). None: return (best, False, stats, trace). False: return (best, True, ...). True: record the
    makespan in trace as (value, conflicts so far), backjump to level 0 and add_clause([makespan <= value - 1]);
    if that makes the solver inconsistent (or value is 0), the value is proven optimal.
    Returns (best or None, proven, solver.stats, trace)."""
    raise NotImplementedError  # TODO step 5
