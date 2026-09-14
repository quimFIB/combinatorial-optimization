"""Unit 17 lab — a small CP engine.

Fill in the parts marked TODO, one step at a time, and run
    uv run co test 17
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Variables are 0..n-1 with finite integer domains (frozensets). A propagator is an object
with `.vars` (the variables it watches) and `.prune(dom)`: a *pure* function of the current
domains (anything indexable by variable) returning either None, meaning the constraint
can't be satisfied, or a dict {var: narrower domain} for the variables it narrows. Only the
engine changes the store, and the store trails every change so search can undo it.

Units 18, 19 and 21 build on this engine (the reference one, or yours with CO_MINE=17).
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


# ---------------------------------------------------------------- step 1 ---

class Store:
    """Domains with a trail."""

    def __init__(self, domains):
        """dom: a list of frozensets, one per variable. trail: a list of (var, old domain).
        changed: variables whose domain changed since the engine last cleared it."""
        raise NotImplementedError  # TODO step 1

    def __len__(self):
        return len(self.dom)

    def is_fixed(self, v):
        return len(self.dom[v]) == 1

    def value(self, v):
        """The single value of a fixed variable."""
        raise NotImplementedError  # TODO step 1

    def set_domain(self, v, new):
        """Replace dom[v] by `new` (a subset of it). If it actually changes, push (v, old) on the
        trail and append v to `changed`. Return False if the new domain is empty, else True."""
        raise NotImplementedError  # TODO step 1

    def remove(self, v, a):
        raise NotImplementedError  # TODO step 1

    def assign(self, v, a):
        raise NotImplementedError  # TODO step 1

    def mark(self):
        """A position on the trail to undo back to."""
        raise NotImplementedError  # TODO step 1

    def undo(self, mark):
        """Restore every domain changed since `mark`, and clear `changed`."""
        raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def revise(dx, dy, allowed):
    """The values a in dx with some b in dy such that allowed(a, b)."""
    raise NotImplementedError  # TODO step 2


def ac3(domains, constraints):
    """AC-3. domains: dict var -> set of values. constraints: dict (x, y) -> allowed(a, b); each
    entry is one directed arc, revising x against y. Put every arc on a queue; when revising
    (x, y) shrinks x, re-queue every arc (z, x). Returns (dict var -> frozenset, number of
    revise calls), or (None, calls) as soon as a domain becomes empty."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

class Binary:
    """Arc consistency on one binary constraint allowed(a, b) between x and y."""

    def __init__(self, x, y, allowed):
        self.vars = (x, y)
        self.x, self.y, self.allowed = x, y, allowed

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


class NotEqual:
    """x != y + offset."""

    def __init__(self, x, y, offset=0):
        self.vars = (x, y)
        self.x, self.y, self.offset = x, y, offset

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


class LinearLe:
    """sum_i coef_i * x_i <= rhs (integer coefficients of any sign). Remove every value that
    exceeds what the others' most favourable values leave room for."""

    def __init__(self, xs, coefs, rhs):
        self.vars = tuple(xs)
        self.xs, self.coefs, self.rhs = list(xs), list(coefs), rhs

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


class LinearEq:
    """sum_i coef_i * x_i == rhs. Suggestion: two LinearLe, the second applied to the first's
    result (the _Overlay helper below shows domains with some entries replaced)."""

    def __init__(self, xs, coefs, rhs):
        self.vars = tuple(xs)
        self.xs, self.coefs, self.rhs = list(xs), list(coefs), rhs

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


class Count:
    """The number of x_i equal to `value` is the value of variable n_var (which may itself be
    one of the x_i). Bound n_var by (surely equal, possibly equal); if n_var's max equals the
    sure count, remove `value` elsewhere; if its min equals the possible count, fix every
    candidate to `value`."""

    def __init__(self, xs, value, n_var):
        self.xs, self.value, self.n = list(xs), value, n_var
        self.vars = tuple(self.xs) + (n_var,)

    def prune(self, dom):
        raise NotImplementedError  # TODO step 3


class _Overlay:
    """dom with some entries replaced, without copying: _Overlay(dom, {3: frozenset({1})})[3]."""

    def __init__(self, base, over):
        self.base, self.over = base, over

    def __getitem__(self, v):
        return self.over.get(v, self.base[v])


@dataclass
class Stats:
    nodes: int = 0
    failures: int = 0
    propagations: int = 0
    solutions: int = 0
    seconds: float = 0.0
    extra: dict = field(default_factory=dict)


def watches(n, props):
    """watches(n, props)[v] = the propagators watching variable v."""
    w = [[] for _ in range(n)]
    for p in props:
        for v in set(p.vars):
            w[v].append(p)
    return w


def fixpoint(store: Store, props, watch, stats: Stats, dirty=None, on_failure=None):
    """Run propagators until none changes anything. The queue starts with every propagator
    (dirty=None) or with those watching a variable in `dirty`. For each propagator taken from
    the queue: count a propagation in stats, call prune(store.dom), apply its narrowings through
    store.set_domain, and queue every propagator watching a changed variable that isn't queued
    already, including the one that just ran. On failure (None, or an emptied domain) call
    on_failure(propagator) if given and return False. Return True at the fixpoint."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def first_fail(store: Store, stats: Stats | None = None):
    """The unfixed variable with the smallest domain, lowest index on ties; None if all fixed."""
    raise NotImplementedError  # TODO step 4


def solve(domains, props, choose=first_fail, all_solutions=False, node_limit=None, on_failure=None):
    """Depth-first search with propagation.

    Propagate at the root. At each node let v = choose(store, stats) (None: every variable is
    fixed, so record a solution) and a = min(dom[v]); try the branch v = a, then v != a. Each
    branch taken counts as a node (stop branching once stats.nodes reaches node_limit); a
    branch whose propagation fails counts a failure. Undo to a mark after each branch.
    Stop after the first solution unless all_solutions.
    Returns (solutions, stats): solutions as lists of values; stats.solutions and
    stats.seconds filled in, and stats.extra["complete"] False if the node limit cut the search."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def queens(n):
    """Variable i is the row of the queen in column i. Rows differ, and so do both diagonals,
    as three NotEqual per pair of columns. Returns (domains, propagators)."""
    raise NotImplementedError  # TODO step 5


def sudoku(grid):
    """grid: an N x N list of lists (N = k^2), 0 for a blank. Variable r * N + c. One NotEqual
    per distinct pair of cells sharing a row, column or box. Returns (domains, propagators)."""
    raise NotImplementedError  # TODO step 5


def map_colouring(n, edges, k):
    raise NotImplementedError  # TODO step 5


def magic_series(n):
    """s_i = the number of occurrences of i in s. One Count per i, plus the redundant
    constraints sum_i s_i = n and sum_i i * s_i = n."""
    raise NotImplementedError  # TODO step 5
