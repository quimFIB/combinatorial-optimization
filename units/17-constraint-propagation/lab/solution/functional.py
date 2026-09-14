"""Unit 17 lab — a small CP engine.  REFERENCE SOLUTION, functional.

The point of this version: with immutable domains, search needs no trail. A node is a
tuple of frozensets; branching makes a new tuple; backtracking is simply returning. The
Store class exists for step 1's interface (a trail over persistent snapshots), and
`fixpoint` writes its result back to a store at the boundary, but `solve` never undoes
anything. Propagators are the same pure prune functions as in the imperative version.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import toolz as tz


# ---------------------------------------------------------------- step 1 ---

class Store:
    """A trail of immutable snapshots: dom is a tuple, every change replaces it."""

    def __init__(self, domains):
        self.dom = tuple(frozenset(d) for d in domains)
        self.trail = []
        self.changed = []

    def __len__(self):
        return len(self.dom)

    def is_fixed(self, v):
        return len(self.dom[v]) == 1

    def value(self, v):
        return next(iter(self.dom[v]))

    def set_domain(self, v, new):
        new = frozenset(new)
        if new != self.dom[v]:
            self.trail.append((v, self.dom[v]))
            self.dom = self.dom[:v] + (new,) + self.dom[v + 1:]
            self.changed.append(v)
        return bool(new)

    def remove(self, v, a):
        return self.set_domain(v, self.dom[v] - {a})

    def assign(self, v, a):
        return self.set_domain(v, self.dom[v] & {a})

    def mark(self):
        return len(self.trail)

    def undo(self, mark):
        restored = tz.reduce(lambda dom, entry: dom[:entry[0]] + (entry[1],) + dom[entry[0] + 1:],
                             reversed(self.trail[mark:]), self.dom)
        self.dom, self.trail, self.changed = restored, self.trail[:mark], []


# ---------------------------------------------------------------- step 2 ---

def revise(dx, dy, allowed):
    return frozenset(a for a in dx if any(allowed(a, b) for b in dy))


def ac3(domains, constraints):
    incoming = tz.groupby(lambda arc: arc[1], constraints)

    def step(state):
        dom, queue, calls = state
        (x, y), rest = queue[0], queue[1:]
        new = revise(dom[x], dom[y], constraints[(x, y)])
        if new == dom[x]:
            return dom, rest, calls + 1
        if not new:
            return None, (), calls + 1
        again = tuple(arc for arc in incoming.get(x, ()) if arc not in rest)
        return {**dom, x: new}, rest + again, calls + 1

    start = ({v: frozenset(d) for v, d in domains.items()}, tuple(constraints), 0)
    dom, _, calls = next(s for s in tz.iterate(step, start) if s[0] is None or not s[1])
    return dom, calls


# ---------------------------------------------------------------- step 3 ---

class Binary:
    def __init__(self, x, y, allowed):
        self.vars, self.x, self.y, self.allowed = (x, y), x, y, allowed

    def prune(self, dom):
        nx = revise(dom[self.x], dom[self.y], self.allowed)
        ny = revise(dom[self.y], nx, lambda b, a: self.allowed(a, b))
        return None if not nx or not ny else {self.x: nx, self.y: ny}


class NotEqual:
    def __init__(self, x, y, offset=0):
        self.vars, self.x, self.y, self.offset = (x, y), x, y, offset

    def prune(self, dom):
        dx, dy = dom[self.x], dom[self.y]
        ny = dy - {next(iter(dx)) - self.offset} if len(dx) == 1 else dy
        nx = dx - {next(iter(ny)) + self.offset} if len(ny) == 1 else dx
        return None if not nx or not ny else {self.x: nx, self.y: ny}


class LinearLe:
    def __init__(self, xs, coefs, rhs):
        self.vars, self.xs, self.coefs, self.rhs = tuple(xs), tuple(xs), tuple(coefs), rhs

    def prune(self, dom):
        lows = [min(c * a for a in dom[x]) for x, c in zip(self.xs, self.coefs)]
        total = sum(lows)
        if total > self.rhs:
            return None
        out = {x: frozenset(a for a in dom[x] if c * a <= self.rhs - (total - low))
               for x, c, low in zip(self.xs, self.coefs, lows)}
        return None if any(not d for d in out.values()) else out


class LinearEq:
    def __init__(self, xs, coefs, rhs):
        self.vars = tuple(xs)
        self.le, self.ge = LinearLe(xs, coefs, rhs), LinearLe(xs, [-c for c in coefs], -rhs)

    def prune(self, dom):
        first = self.le.prune(dom)
        if first is None:
            return None
        second = self.ge.prune(_Overlay(dom, first))
        return None if second is None else tz.merge_with(lambda ds: ds[0] & ds[-1], first, second)


class Count:
    def __init__(self, xs, value, n_var):
        self.xs, self.value, self.n = tuple(xs), value, n_var
        self.vars = self.xs + (n_var,)

    def prune(self, dom):
        v = self.value
        sure = sum(1 for x in self.xs if dom[x] == {v})
        possible = sum(1 for x in self.xs if v in dom[x])
        dn = frozenset(k for k in dom[self.n] if sure <= k <= possible)
        if not dn:
            return None
        if max(dn) == sure:
            narrowed = {x: dom[x] - {v} for x in self.xs if v in dom[x] and dom[x] != {v}}
        elif min(dn) == possible:
            narrowed = {x: dom[x] & {v} for x in self.xs if v in dom[x]}
        else:
            narrowed = {}
        out = tz.merge_with(lambda ds: tz.reduce(frozenset.__and__, ds), {self.n: dn}, narrowed)
        return None if any(not d for d in out.values()) else out


class _Overlay:
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
    grouped = tz.groupby(0, [(v, p) for p in props for v in set(p.vars)])
    return [[p for _, p in grouped.get(v, [])] for v in range(n)]


def _fixpoint_pure(dom, props, watch, stats, queue, on_failure):
    """Returns the new domain tuple or None. queue: tuple of propagators."""
    def step(state):
        dom, queue = state
        p, rest = queue[0], queue[1:]
        stats.propagations += 1
        out = p.prune(dom)
        narrowed = None if out is None else {v: d & dom[v] for v, d in out.items() if d & dom[v] != dom[v]}
        if narrowed is None or any(not d for d in narrowed.values()):
            if on_failure:
                on_failure(p)
            return None, ()
        new_dom = tuple(narrowed.get(v, d) for v, d in enumerate(dom))
        woken = tuple(tz.unique(q for v in narrowed for q in watch[v] if q not in rest))
        return new_dom, rest + woken

    final, _ = next(s for s in tz.iterate(step, (tuple(dom), tuple(tz.unique(queue, key=id)))) if s[0] is None or not s[1])
    return final


def fixpoint(store, props, watch, stats, dirty=None, on_failure=None):
    queue = props if dirty is None else [p for v in dirty for p in watch[v]]
    result = _fixpoint_pure(store.dom, props, watch, stats, queue, on_failure)
    if result is None:
        return False
    for v, d in enumerate(result):
        store.set_domain(v, d)
    store.changed.clear()
    return True


# ---------------------------------------------------------------- step 4 ---

def first_fail(store, stats=None):
    open_vars = [(len(d), v) for v, d in enumerate(store.dom) if len(d) > 1]
    return min(open_vars)[1] if open_vars else None


class _View:
    """What a `choose` heuristic sees: .dom, like a store."""

    def __init__(self, dom):
        self.dom = dom


def solve(domains, props, choose=first_fail, all_solutions=False, node_limit=None, on_failure=None):
    t0 = time.perf_counter()
    stats = Stats()
    watch = watches(len(domains), props)
    root = _fixpoint_pure(tuple(frozenset(d) for d in domains), props, watch, stats, props, on_failure)
    budget = {"complete": True}

    def search(dom):
        """Yields solutions below this node, lazily."""
        v = choose(_View(dom), stats)
        if v is None:
            yield [next(iter(d)) for d in dom]
            return
        a = min(dom[v])
        for child in (dom[:v] + (frozenset({a}),) + dom[v + 1:], dom[:v] + (dom[v] - {a},) + dom[v + 1:]):
            if node_limit is not None and stats.nodes >= node_limit:
                budget["complete"] = False
                return
            stats.nodes += 1
            narrowed = _fixpoint_pure(child, props, watch, stats, watch[v], on_failure) if child[v] else None
            if narrowed is None:
                stats.failures += 1
            else:
                yield from search(narrowed)

    if root is None:
        stats.failures += 1
        solutions = []
    else:
        found = search(root)
        solutions = list(found) if all_solutions else list(tz.take(1, found))
    stats.solutions = len(solutions)
    stats.seconds = time.perf_counter() - t0
    stats.extra["complete"] = budget["complete"]
    return solutions, stats


# ---------------------------------------------------------------- step 5 ---

def queens(n):
    props = [p for i in range(n) for j in range(i + 1, n)
             for p in (NotEqual(i, j), NotEqual(i, j, j - i), NotEqual(i, j, i - j))]
    return [range(n)] * n, props


def sudoku(grid):
    N = len(grid)
    k = int(round(N ** 0.5))
    domains = [[grid[r][c]] if grid[r][c] else range(1, N + 1) for r in range(N) for c in range(N)]
    groups = ([[r * N + c for c in range(N)] for r in range(N)]
              + [[r * N + c for r in range(N)] for c in range(N)]
              + [[(br + r) * N + bc + c for r in range(k) for c in range(k)]
                 for br in range(0, N, k) for bc in range(0, N, k)])
    pairs = sorted({(min(a, b), max(a, b)) for g in groups for a in g for b in g if a != b})
    return domains, [NotEqual(a, b) for a, b in pairs]


def map_colouring(n, edges, k):
    return [range(k)] * n, [NotEqual(u, v) for u, v in edges]


def magic_series(n):
    return [range(n)] * n, ([Count(range(n), i, i) for i in range(n)]
                            + [LinearEq(range(n), [1] * n, n), LinearEq(range(n), list(range(n)), n)])
