"""Unit 17 lab — a small CP engine.  REFERENCE SOLUTION, imperative.

Variables are 0..n-1 with finite integer domains (frozensets). A propagator is an
object with `.vars` (the variables it watches) and `.prune(dom)`, a *pure* function of
the current domains that returns either None (the constraint cannot be satisfied) or
a dict {var: narrower domain} for the variables it narrows. Only the engine changes the
store, and the store trails every change so search can undo it.

Units 18, 19 and 21 build on this file through colib.ref.unit("17").
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


# ---------------------------------------------------------------- step 1 ---

class Store:
    """Domains with a trail. `dom[v]` is a frozenset; every change pushes (v, old domain)."""

    def __init__(self, domains):
        self.dom = [frozenset(d) for d in domains]
        self.trail = []
        self.changed = []                                     # variables changed since the engine last looked

    def __len__(self):
        return len(self.dom)

    def is_fixed(self, v):
        return len(self.dom[v]) == 1

    def value(self, v):
        (a,) = self.dom[v]
        return a

    def set_domain(self, v, new):
        """Narrow dom[v] to `new` (a subset). Returns False if it becomes empty."""
        new = frozenset(new)
        old = self.dom[v]
        if new != old:
            self.trail.append((v, old))
            self.dom[v] = new
            self.changed.append(v)
        return bool(new)

    def remove(self, v, a):
        return self.set_domain(v, self.dom[v] - {a})

    def assign(self, v, a):
        return self.set_domain(v, self.dom[v] & {a})

    def mark(self):
        return len(self.trail)

    def undo(self, mark):
        while len(self.trail) > mark:
            v, old = self.trail.pop()
            self.dom[v] = old
        self.changed.clear()


# ---------------------------------------------------------------- step 2 ---

def revise(dx, dy, allowed):
    """The values of dx with at least one support in dy under allowed(a, b)."""
    return frozenset(a for a in dx if any(allowed(a, b) for b in dy))


def ac3(domains, constraints):
    """AC-3. domains: dict var -> set; constraints: dict (x, y) -> allowed(a, b), one entry
    per direction you want enforced (give both (x, y) and (y, x) for a symmetric constraint).
    Returns (domains as a dict of frozensets, number of revise calls), or (None, calls) on a wipeout."""
    dom = {v: frozenset(d) for v, d in domains.items()}
    incoming = {}
    for z, x in constraints:
        incoming.setdefault(x, []).append(z)                  # arcs (z, x) are rechecked when x shrinks
    queue = deque(constraints)
    queued = set(constraints)
    calls = 0
    while queue:
        arc = queue.popleft()
        queued.discard(arc)
        x, y = arc
        calls += 1
        new = revise(dom[x], dom[y], constraints[arc])
        if new != dom[x]:
            if not new:
                return None, calls
            dom[x] = new
            for z in incoming.get(x, ()):
                if (z, x) not in queued:
                    queue.append((z, x))
                    queued.add((z, x))
    return dom, calls


# ---------------------------------------------------------------- step 3 ---

class Binary:
    """Arc consistency on one binary constraint allowed(a, b) between x and y."""

    def __init__(self, x, y, allowed):
        self.vars = (x, y)
        self.x, self.y, self.allowed = x, y, allowed

    def prune(self, dom):
        nx = revise(dom[self.x], dom[self.y], self.allowed)
        ny = revise(dom[self.y], nx, lambda b, a: self.allowed(a, b))
        if not nx or not ny:
            return None
        return {self.x: nx, self.y: ny}


class NotEqual:
    """x != y + offset. Prunes only when one side is fixed (this is arc consistency for !=)."""

    def __init__(self, x, y, offset=0):
        self.vars = (x, y)
        self.x, self.y, self.offset = x, y, offset

    def prune(self, dom):
        dx, dy = dom[self.x], dom[self.y]
        out = {}
        if len(dx) == 1:
            (a,) = dx
            dy = dy - {a - self.offset}
            out[self.y] = dy
        if len(dy) == 1:
            (b,) = dy
            dx = dx - {b + self.offset}
            out[self.x] = dx
        if not dx or not dy:
            return None
        return out


class LinearLe:
    """sum_i coef_i * x_i <= rhs, bounds consistency (integer coefficients, any signs)."""

    def __init__(self, xs, coefs, rhs):
        self.vars = tuple(xs)
        self.xs, self.coefs, self.rhs = list(xs), list(coefs), rhs

    def prune(self, dom):
        lows = [c * min(dom[x]) if c > 0 else c * max(dom[x]) for x, c in zip(self.xs, self.coefs)]
        total = sum(lows)
        if total > self.rhs:
            return None
        out = {}
        for x, c, low in zip(self.xs, self.coefs, lows):
            slack = self.rhs - (total - low)                  # c * x <= slack
            keep = frozenset(a for a in dom[x] if c * a <= slack)
            if keep != dom[x]:
                if not keep:
                    return None
                out[x] = keep
        return out


class LinearEq:
    """sum_i coef_i * x_i == rhs, as two LinearLe."""

    def __init__(self, xs, coefs, rhs):
        self.vars = tuple(xs)
        self.le = LinearLe(xs, coefs, rhs)
        self.ge = LinearLe(xs, [-c for c in coefs], -rhs)

    def prune(self, dom):
        out = self.le.prune(dom)
        if out is None:
            return None
        view = _Overlay(dom, out)
        more = self.ge.prune(view)
        if more is None:
            return None
        out.update(more)
        return out


class Count:
    """count(x_i == value) == n_var, where n_var is itself a variable."""

    def __init__(self, xs, value, n_var):
        self.xs, self.value, self.n = list(xs), value, n_var
        self.vars = tuple(self.xs) + (n_var,)

    def prune(self, dom):
        sure = sum(1 for x in self.xs if dom[x] == {self.value})
        possible = sum(1 for x in self.xs if self.value in dom[x])
        dn = frozenset(k for k in dom[self.n] if sure <= k <= possible)
        if not dn:
            return None
        out = {self.n: dn}
        if max(dn) == sure:                                   # no more may take the value
            for x in self.xs:
                if dom[x] != {self.value} and self.value in dom[x]:
                    out[x] = out.get(x, dom[x]) - {self.value}
        elif min(dn) == possible:                             # every candidate must take it
            for x in self.xs:
                if self.value in dom[x]:
                    out[x] = out.get(x, dom[x]) & {self.value}
        if any(not d for d in out.values()):
            return None
        return out


class _Overlay:
    """dom with some entries replaced, without copying."""

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
    w = [[] for _ in range(n)]
    for p in props:
        for v in set(p.vars):
            w[v].append(p)
    return w


def fixpoint(store, props, watch, stats, dirty=None, on_failure=None):
    """Run propagators to a fixpoint. With dirty=None every propagator runs once to start;
    otherwise only those watching a variable in `dirty`. A propagator is re-queued whenever a
    variable it watches changes (including by itself). Returns False on failure."""
    if dirty is None:
        queue = deque(props)
    else:
        queue = deque(dict.fromkeys(p for v in dirty for p in watch[v]))
    queued = set(map(id, queue))
    while queue:
        p = queue.popleft()
        queued.discard(id(p))
        stats.propagations += 1
        out = p.prune(store.dom)
        if out is None:
            if on_failure:
                on_failure(p)
            return False
        store.changed.clear()
        for v, d in out.items():
            if not store.set_domain(v, d & store.dom[v]):
                if on_failure:
                    on_failure(p)
                return False
        for v in store.changed:
            for q in watch[v]:
                if id(q) not in queued:
                    queue.append(q)
                    queued.add(id(q))
        store.changed.clear()
    return True


# ---------------------------------------------------------------- step 4 ---

def first_fail(store, stats=None):
    """The unfixed variable with the smallest domain (lowest index on ties), or None."""
    best = None
    for v, d in enumerate(store.dom):
        if len(d) > 1 and (best is None or len(d) < len(store.dom[best])):
            best = v
    return best


def solve(domains, props, choose=first_fail, all_solutions=False, node_limit=None, on_failure=None):
    """Depth-first search with propagation. At each node pick a variable with `choose` and
    branch on its smallest value a: first x = a, then x != a. Counts a node per branch taken.
    Returns (solutions, stats): a list of solutions (each a list of values), stopping after the
    first unless all_solutions. stats.extra['complete'] says whether the search finished."""
    t0 = time.perf_counter()
    store = Store(domains)
    watch = watches(len(store), props)
    stats = Stats()
    solutions = []
    complete = True

    if not fixpoint(store, props, watch, stats, on_failure=on_failure):
        stats.failures += 1
        stats.seconds = time.perf_counter() - t0
        stats.extra["complete"] = True
        return solutions, stats

    def dfs():
        nonlocal complete
        v = choose(store, stats)
        if v is None:
            solutions.append([store.value(u) for u in range(len(store))])
            stats.solutions += 1
            return not all_solutions                          # True = stop
        a = min(store.dom[v])
        for branch in ("eq", "ne"):
            if node_limit is not None and stats.nodes >= node_limit:
                complete = False
                return True
            stats.nodes += 1
            m = store.mark()
            ok = store.assign(v, a) if branch == "eq" else store.remove(v, a)
            if ok and fixpoint(store, props, watch, stats, dirty=[v], on_failure=on_failure):
                if dfs():
                    store.undo(m)
                    return True
            else:
                stats.failures += 1
            store.undo(m)
        return False

    dfs()
    stats.seconds = time.perf_counter() - t0
    stats.extra["complete"] = complete
    return solutions, stats


# ---------------------------------------------------------------- step 5 ---

def queens(n):
    """Variable i = the row of the queen in column i. Returns (domains, propagators)."""
    props = []
    for i in range(n):
        for j in range(i + 1, n):
            props += [NotEqual(i, j), NotEqual(i, j, j - i), NotEqual(i, j, i - j)]
    return [range(n)] * n, props


def sudoku(grid):
    """grid: a k^2 x k^2 list of lists, 0 for blank. Variable r * N + c. Pairwise != on rows,
    columns and boxes."""
    N = len(grid)
    k = int(round(N ** 0.5))
    domains = [[grid[r][c]] if grid[r][c] else range(1, N + 1) for r in range(N) for c in range(N)]
    groups = [[r * N + c for c in range(N)] for r in range(N)]
    groups += [[r * N + c for r in range(N)] for c in range(N)]
    groups += [[(br + r) * N + bc + c for r in range(k) for c in range(k)]
               for br in range(0, N, k) for bc in range(0, N, k)]
    pairs = {(min(a, b), max(a, b)) for g in groups for a in g for b in g if a != b}
    return domains, [NotEqual(a, b) for a, b in sorted(pairs)]


def map_colouring(n, edges, k):
    return [range(k)] * n, [NotEqual(u, v) for u, v in edges]


def magic_series(n):
    """s_i = the number of occurrences of i in (s_0, ..., s_{n-1}), with the two classic
    redundant constraints sum s_i = n and sum i * s_i = n."""
    props = [Count(range(n), i, i) for i in range(n)]
    props.append(LinearEq(range(n), [1] * n, n))
    props.append(LinearEq(range(n), list(range(n)), n))
    return [range(n)] * n, props
