"""Unit 18 lab — global constraints.

Fill in the parts marked TODO, one step at a time, and run
    uv run co test 18
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Propagators follow unit 17's interface (.vars, .prune(dom) -> dict or None) and run in unit
17's engine: `cp` below is colib.ref.unit("17"), the reference engine, or yours with
CO_MINE=17. The maximum matching is unit 15's Hopcroft–Karp (yours with CO_MINE=15).
"""

from __future__ import annotations

from colib.problems import JobShop
from colib.ref import unit

cp = unit("17")
hopcroft_karp = unit("15").hopcroft_karp          # hopcroft_karp(nl, nr, edges) -> {left: right}


# ---------------------------------------------------------------- step 1 ---

def value_graph(dom, xs, offsets):
    """The value graph of alldifferent(x_i + offsets[i]). Returns (values, edges): `values` is
    the sorted list of distinct shifted values a + offsets[i] over all a in dom[xs[i]], and
    `edges` the list of pairs (i, k) with values[k] - offsets[i] in dom[xs[i]]. Variables are
    numbered by their position i in xs."""
    raise NotImplementedError  # TODO step 1


def maximum_matching(dom, xs, offsets):
    """A maximum matching of the value graph, {i: k}."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

class AllDifferent:
    """alldifferent(x_i + offset_i) with Régin's filtering (generalised arc consistency).

    Fail if the maximum matching doesn't cover every variable. Otherwise direct the value graph:
    matched edges value -> variable, unmatched edges variable -> value. A value a stays in x's
    domain iff its edge is matched, or its two ends lie in the same strongly connected
    component, or the value node can reach a free (unmatched) value."""

    def __init__(self, xs, offsets=None):
        self.xs = list(xs)
        self.offsets = list(offsets) if offsets is not None else [0] * len(self.xs)
        self.vars = tuple(self.xs)

    def prune(self, dom):
        raise NotImplementedError  # TODO step 2


def hall_set(dom, xs, offsets, x, a):
    """Why value a (unshifted) can't be taken by variable xs[x]: a sorted list S of variable
    positions, x not in S, whose shifted domains together contain exactly len(S) values,
    including a + offsets[x]. None if a is still supported (or no matching exists).

    Hint: in the directed graph above, the variables reachable from a's value node."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

class Cumulative:
    """Tasks i start at variable starts[i], last durations[i] and use demands[i]; the total use
    never exceeds `capacity`. Timetable filtering:
      * compulsory part of task i: [max start, min start + duration), when non-empty;
      * profile(u) = total demand of compulsory parts covering time u; fail if above capacity;
      * a start value t of task i survives iff for every u in [t, t + d_i):
        profile(u) - (demand_i if u is in i's own compulsory part) + demand_i <= capacity.
    """

    def __init__(self, starts, durations, demands, capacity):
        self.starts, self.durations, self.demands = list(starts), list(durations), list(demands)
        self.capacity = capacity
        self.vars = tuple(self.starts)

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def queens_global(n):
    """n-queens with three AllDifferent: rows, and the diagonals through offsets +i and -i."""
    raise NotImplementedError  # TODO step 4


def sudoku_global(grid):
    """One AllDifferent per row, column and box (variables r * N + c, as in unit 17)."""
    raise NotImplementedError  # TODO step 4


def pigeonhole(n, use_global):
    """n + 1 variables over range(n), all different: one AllDifferent, or pairwise cp.NotEqual."""
    raise NotImplementedError  # TODO step 4


def jobshop(shop: JobShop, horizon, use_global):
    """A job-shop model. Variables: the start of each operation (j, k), numbered job by job in
    order, over range(0, horizon - duration + 1); then a makespan variable over
    range(0, horizon + 1). Constraints: start(j, k) + duration <= start(j, k + 1) and
    start(j, last) + duration <= makespan, as cp.LinearLe; per machine, one Cumulative of
    capacity 1 (use_global) or, for every pair of operations on it, a cp.Binary saying one ends
    before the other starts. Returns (domains, props, makespan variable)."""
    raise NotImplementedError  # TODO step 4


def minimise(domains, props, objective, choose=None, node_limit=None):
    """Minimise a variable by repeated search: solve; if a solution has objective value v, add
    cp.LinearLe([objective], [1], v - 1) and solve again from scratch; stop when none is found.
    node_limit bounds the total nodes over all searches.
    Returns (best value or None, best solution or None, total cp.Stats, trace), where trace lists
    (value, total nodes so far) per improvement and stats.extra['complete'] says whether the
    last search finished (so the best value is proven optimal)."""
    raise NotImplementedError  # TODO step 4
