"""Unit 18 lab — global constraints.  REFERENCE SOLUTION, functional.

Régin's filter is graph reachability and strongly connected components, both written
here as fixpoints over sets (Kosaraju's two passes become two reachability folds, which
is quadratic but clear). Timetable filtering is a pure function of the domains.
Search uses unit 17's engine; `minimise` is an unfold over incumbents.
"""

from __future__ import annotations

import toolz as tz

from colib.ref import unit

cp = unit("17")
hopcroft_karp = unit("15").hopcroft_karp


# ---------------------------------------------------------------- step 1 ---

def value_graph(dom, xs, offsets):
    values = sorted({a + o for x, o in zip(xs, offsets) for a in dom[x]})
    index = {v: k for k, v in enumerate(values)}
    return values, [(i, index[a + o]) for i, (x, o) in enumerate(zip(xs, offsets)) for a in sorted(dom[x])]


def maximum_matching(dom, xs, offsets):
    values, edges = value_graph(dom, xs, offsets)
    return hopcroft_karp(len(xs), len(values), edges)


# ---------------------------------------------------------------- step 2 ---

def _arcs(n, edges, matching):
    return [((n + k, i) if matching.get(i) == k else (i, n + k)) for i, k in edges]


def _closure(start, adjacency):
    grow = lambda seen: seen | {w for u in seen for w in adjacency.get(u, ())}
    return next(b for a, b in tz.sliding_window(2, tz.iterate(grow, frozenset(start))) if a == b)


def _adjacency(arcs, reverse=False):
    return tz.valmap(lambda pairs: [p[0 if reverse else 1] for p in pairs],
                     tz.groupby(1 if reverse else 0, arcs))


class AllDifferent:
    def __init__(self, xs, offsets=None):
        self.xs = list(xs)
        self.offsets = list(offsets) if offsets is not None else [0] * len(self.xs)
        self.vars = tuple(self.xs)

    def prune(self, dom):
        n = len(self.xs)
        values, edges = value_graph(dom, self.xs, self.offsets)
        matching = hopcroft_karp(n, len(values), edges)
        if len(matching) < n:
            return None
        arcs = _arcs(n, edges, matching)
        forward, backward = _adjacency(arcs), _adjacency(arcs, reverse=True)
        free = {n + k for k in range(len(values))} - {n + k for k in matching.values()}
        reach_free = _closure(free, backward)

        def same_scc(u, w):
            return w in _closure({u}, forward) and u in _closure({w}, forward)

        def supported(i, a):
            k = values.index(a + self.offsets[i])
            return matching[i] == k or (n + k) in reach_free or same_scc(i, n + k)

        out = {x: frozenset(a for a in dom[x] if supported(i, a)) for i, x in enumerate(self.xs)}
        return {x: d for x, d in out.items() if d != dom[x]}


def hall_set(dom, xs, offsets, x, a):
    n = len(xs)
    values, edges = value_graph(dom, xs, offsets)
    matching = hopcroft_karp(n, len(values), edges)
    if len(matching) < n:
        return None
    k = values.index(a + offsets[x])
    seen = _closure({n + k}, _adjacency(_arcs(n, edges, matching)))
    free = {n + kk for kk in range(len(values))} - {n + kk for kk in matching.values()}
    return None if x in seen or seen & free else sorted(u for u in seen if u < n)


# ---------------------------------------------------------------- step 3 ---

class Cumulative:
    def __init__(self, starts, durations, demands, capacity):
        self.starts, self.durations, self.demands = list(starts), list(durations), list(demands)
        self.capacity = capacity
        self.vars = tuple(self.starts)

    def compulsory(self, dom, i):
        lst, ect = max(dom[self.starts[i]]), min(dom[self.starts[i]]) + self.durations[i]
        return range(lst, ect) if lst < ect else range(0)

    def prune(self, dom):
        parts = [self.compulsory(dom, i) for i in range(len(self.starts))]
        profile = tz.merge_with(sum, *({t: self.demands[i]} for i, part in enumerate(parts) for t in part))
        if any(load > self.capacity for load in profile.values()):
            return None

        def fits(i, t):
            return all(profile.get(u, 0) - (self.demands[i] if u in parts[i] else 0) + self.demands[i] <= self.capacity
                       for u in range(t, t + self.durations[i]))

        out = {s: frozenset(t for t in dom[s] if fits(i, t)) for i, s in enumerate(self.starts)}
        return None if any(not d for d in out.values()) else {s: d for s, d in out.items() if d != dom[s]}


# ---------------------------------------------------------------- step 4 ---

def queens_global(n):
    return [range(n)] * n, [AllDifferent(range(n)), AllDifferent(range(n), list(range(n))),
                            AllDifferent(range(n), [-i for i in range(n)])]


def sudoku_global(grid):
    N = len(grid)
    k = int(round(N ** 0.5))
    domains = [[grid[r][c]] if grid[r][c] else range(1, N + 1) for r in range(N) for c in range(N)]
    groups = ([[r * N + c for c in range(N)] for r in range(N)]
              + [[r * N + c for r in range(N)] for c in range(N)]
              + [[(br + r) * N + bc + c for r in range(k) for c in range(k)]
                 for br in range(0, N, k) for bc in range(0, N, k)])
    return domains, [AllDifferent(g) for g in groups]


def pigeonhole(n, use_global):
    domains = [range(n)] * (n + 1)
    if use_global:
        return domains, [AllDifferent(range(n + 1))]
    return domains, [cp.NotEqual(i, j) for i in range(n + 1) for j in range(i + 1, n + 1)]


def jobshop(shop, horizon, use_global):
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    var = {op: v for v, op in enumerate(ops)}
    dur = {op: shop.jobs[op[0]][op[1]][1] for op in ops}
    machine = {op: shop.jobs[op[0]][op[1]][0] for op in ops}
    mk = len(ops)
    domains = [range(0, horizon - dur[op] + 1) for op in ops] + [range(0, horizon + 1)]
    chains = [cp.LinearLe([var[(j, k)], var[(j, k + 1)]], [1, -1], -dur[(j, k)])
              for j, job in enumerate(shop.jobs) for k in range(len(job) - 1)]
    ends = [cp.LinearLe([var[(j, len(job) - 1)], mk], [1, -1], -dur[(j, len(job) - 1)])
            for j, job in enumerate(shop.jobs)]
    on = tz.groupby(lambda op: machine[op], ops)

    def machine_props(m):
        group = on.get(m, [])
        if use_global:
            return [Cumulative([var[op] for op in group], [dur[op] for op in group], [1] * len(group), 1)]
        return [cp.Binary(var[a], var[b], lambda s, t, da=dur[a], db=dur[b]: s + da <= t or t + db <= s)
                for a, b in ((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))]

    return domains, chains + ends + [p for m in range(shop.machines) for p in machine_props(m)], mk


def minimise(domains, props, objective, choose=None, node_limit=None):
    choose = choose or cp.first_fail

    def step(state):
        best, best_sol, trace, total, _ = state
        extra = [] if best is None else [cp.LinearLe([objective], [1], best - 1)]
        remaining = None if node_limit is None else max(0, node_limit - total.nodes)
        sols, st = cp.solve(domains, props + extra, choose=choose, node_limit=remaining)
        total = cp.Stats(nodes=total.nodes + st.nodes, failures=total.failures + st.failures,
                         propagations=total.propagations + st.propagations, seconds=total.seconds + st.seconds,
                         extra={"complete": st.extra["complete"]})
        if not sols:
            return best, best_sol, trace, total, True
        value = sols[0][objective]
        return value, sols[0], trace + [(value, total.nodes)], total, False

    best, best_sol, trace, total, _ = next(s for s in tz.iterate(step, (None, None, [], cp.Stats(), False)) if s[4])
    return best, best_sol, total, trace
