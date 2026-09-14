"""Unit 18 lab — global constraints.  REFERENCE SOLUTION, imperative.

Propagators here follow unit 17's interface (.vars, .prune(dom) -> dict or None) and run
in unit 17's engine, loaded with colib.ref.unit("17"). The matching comes from unit 15.
"""

from __future__ import annotations

from colib.ref import unit

cp = unit("17")
hopcroft_karp = unit("15").hopcroft_karp


# ---------------------------------------------------------------- step 1 ---

def value_graph(dom, xs, offsets):
    """The bipartite value graph of alldifferent(x_i + offset_i): variables 0..n-1 on the left,
    distinct shifted values on the right. Returns (values, edges): values is the sorted list of
    shifted values, edges the list of (i, k) with values[k] - offsets[i] in dom[xs[i]]."""
    values = sorted({a + o for x, o in zip(xs, offsets) for a in dom[x]})
    index = {v: k for k, v in enumerate(values)}
    edges = [(i, index[a + o]) for i, (x, o) in enumerate(zip(xs, offsets)) for a in sorted(dom[x])]
    return values, edges


def maximum_matching(dom, xs, offsets):
    """A maximum matching of the value graph as {i: k}, from unit 15's Hopcroft–Karp."""
    values, edges = value_graph(dom, xs, offsets)
    return hopcroft_karp(len(xs), len(values), edges)


# ---------------------------------------------------------------- step 2 ---

def _digraph(n, values, edges, matching):
    """Nodes 0..n-1 are variables, n + k is value k. Matched edges point value -> variable,
    unmatched edges variable -> value."""
    succ = [[] for _ in range(n + len(values))]
    for i, k in edges:
        if matching.get(i) == k:
            succ[n + k].append(i)
        else:
            succ[i].append(n + k)
    return succ


def _sccs(succ):
    """Strongly connected component id per node (iterative Tarjan)."""
    N = len(succ)
    index, low, comp = [None] * N, [0] * N, [None] * N
    stack, on_stack, counter, ncomp = [], [False] * N, 0, 0
    for root in range(N):
        if index[root] is not None:
            continue
        work = [(root, 0)]
        while work:
            v, pos = work.pop()
            if pos == 0:
                index[v] = low[v] = counter
                counter += 1
                stack.append(v)
                on_stack[v] = True
            recurse = False
            for p in range(pos, len(succ[v])):
                w = succ[v][p]
                if index[w] is None:
                    work.append((v, p + 1))
                    work.append((w, 0))
                    recurse = True
                    break
                if on_stack[w]:
                    low[v] = min(low[v], index[w])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp[w] = ncomp
                    if w == v:
                        break
                ncomp += 1
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
    return comp


class AllDifferent:
    """alldifferent(x_i + offset_i), with Régin's filtering: generalised arc consistency."""

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
        succ = _digraph(n, values, edges, matching)
        pred = [[] for _ in succ]
        for u, ws in enumerate(succ):
            for w in ws:
                pred[w].append(u)
        matched_values = set(matching.values())
        reach_free = set(n + k for k in range(len(values)) if k not in matched_values)
        frontier = list(reach_free)
        while frontier:                                       # nodes that can reach a free value
            w = frontier.pop()
            for u in pred[w]:
                if u not in reach_free:
                    reach_free.add(u)
                    frontier.append(u)
        comp = _sccs(succ)
        out = {}
        for i, x in enumerate(self.xs):
            o = self.offsets[i]
            keep = frozenset(a for a in dom[x]
                             if matching[i] == (k := values.index(a + o))
                             or comp[i] == comp[n + k] or (n + k) in reach_free)
            if keep != dom[x]:
                out[x] = keep
        return out


def hall_set(dom, xs, offsets, x, a):
    """Why value a (unshifted) is not allowed for variable xs[x]: a set S of variable positions,
    not containing x, whose shifted domains together contain exactly |S| values including
    a + offsets[x]. Returns S as a sorted list, or None if a is still supported."""
    n = len(xs)
    values, edges = value_graph(dom, xs, offsets)
    matching = hopcroft_karp(n, len(values), edges)
    if len(matching) < n:
        return None
    k = values.index(a + offsets[x])
    succ = _digraph(n, values, edges, matching)
    seen, frontier = {n + k}, [n + k]
    while frontier:
        u = frontier.pop()
        for w in succ[u]:
            if w not in seen:
                seen.add(w)
                frontier.append(w)
    if x in seen or any(n + kk in seen for kk in range(len(values)) if kk not in set(matching.values())):
        return None
    return sorted(u for u in seen if u < n)


# ---------------------------------------------------------------- step 3 ---

class Cumulative:
    """Tasks i with start variable starts[i], fixed durations[i] and demands[i] never use more
    than `capacity` at any time. Timetable filtering: build the profile of compulsory parts,
    fail if it exceeds capacity, and remove every start value of a task that would overload
    some time point together with the others' compulsory parts."""

    def __init__(self, starts, durations, demands, capacity):
        self.starts, self.durations, self.demands = list(starts), list(durations), list(demands)
        self.capacity = capacity
        self.vars = tuple(self.starts)

    def compulsory(self, dom, i):
        lst = max(dom[self.starts[i]])
        ect = min(dom[self.starts[i]]) + self.durations[i]
        return range(lst, ect) if lst < ect else range(0)

    def prune(self, dom):
        profile = {}
        parts = []
        for i in range(len(self.starts)):
            part = self.compulsory(dom, i)
            parts.append(part)
            for t in part:
                profile[t] = profile.get(t, 0) + self.demands[i]
                if profile[t] > self.capacity:
                    return None
        out = {}
        for i, s in enumerate(self.starts):
            d, r, part = self.durations[i], self.demands[i], parts[i]
            keep = frozenset(t for t in dom[s]
                             if all(profile.get(u, 0) - (r if u in part else 0) + r <= self.capacity
                                    for u in range(t, t + d)))
            if keep != dom[s]:
                if not keep:
                    return None
                out[s] = keep
        return out


# ---------------------------------------------------------------- step 4 ---

def queens_global(n):
    """Three AllDifferent over the same variables: rows, and the two diagonals via offsets."""
    return [range(n)] * n, [AllDifferent(range(n)), AllDifferent(range(n), list(range(n))),
                            AllDifferent(range(n), [-i for i in range(n)])]


def sudoku_global(grid):
    N = len(grid)
    k = int(round(N ** 0.5))
    domains = [[grid[r][c]] if grid[r][c] else range(1, N + 1) for r in range(N) for c in range(N)]
    groups = [[r * N + c for c in range(N)] for r in range(N)]
    groups += [[r * N + c for r in range(N)] for c in range(N)]
    groups += [[(br + r) * N + bc + c for r in range(k) for c in range(k)]
               for br in range(0, N, k) for bc in range(0, N, k)]
    return domains, [AllDifferent(g) for g in groups]


def pigeonhole(n, use_global):
    """n + 1 pigeons in n holes: unsatisfiable."""
    if use_global:
        return [range(n)] * (n + 1), [AllDifferent(range(n + 1))]
    return [range(n)] * (n + 1), [cp.NotEqual(i, j) for i in range(n + 1) for j in range(i + 1, n + 1)]


def jobshop(shop, horizon, use_global):
    """Start-time variables for operation (j, k), numbered job by job, then a makespan variable
    last. Precedences inside each job; makespan >= every job's last end. Machines: a Cumulative
    of capacity 1 (use_global) or, for every pair of operations on a machine, a Binary
    'one before the other'. Returns (domains, props, makespan variable)."""
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    var = {op: v for v, op in enumerate(ops)}
    dur = {op: shop.jobs[op[0]][op[1]][1] for op in ops}
    mk = len(ops)
    domains = [range(0, horizon - dur[op] + 1) for op in ops] + [range(0, horizon + 1)]
    props = []
    for j, job in enumerate(shop.jobs):
        for k in range(len(job) - 1):
            props.append(cp.LinearLe([var[(j, k)], var[(j, k + 1)]], [1, -1], -dur[(j, k)]))
        last = (j, len(job) - 1)
        props.append(cp.LinearLe([var[last], mk], [1, -1], -dur[last]))
    for m in range(shop.machines):
        on = [op for op in ops if shop.jobs[op[0]][op[1]][0] == m]
        if use_global:
            props.append(Cumulative([var[op] for op in on], [dur[op] for op in on], [1] * len(on), 1))
        else:
            for a in range(len(on)):
                for b in range(a + 1, len(on)):
                    da, db = dur[on[a]], dur[on[b]]
                    props.append(cp.Binary(var[on[a]], var[on[b]],
                                           lambda s, t, da=da, db=db: s + da <= t or t + db <= s))
    return domains, props, mk


def minimise(domains, props, objective, choose=None, node_limit=None):
    """Branch and bound by repeated search: find a solution, require objective <= value - 1,
    search again, until infeasible. Returns (best value, best solution, total stats, trace of
    (value, nodes so far)); best value is None if there is no solution. If node_limit is hit,
    the best found so far is returned and stats.extra['complete'] is False."""
    choose = choose or cp.first_fail
    total = cp.Stats()
    best, best_sol, trace = None, None, []
    extra = []
    complete = True
    while True:
        remaining = None if node_limit is None else max(0, node_limit - total.nodes)
        sols, st = cp.solve(domains, props + extra, choose=choose, node_limit=remaining)
        total.nodes += st.nodes
        total.failures += st.failures
        total.propagations += st.propagations
        total.seconds += st.seconds
        if not sols:
            complete = st.extra["complete"]
            break
        best_sol = sols[0]
        best = best_sol[objective]
        trace.append((best, total.nodes))
        extra = [cp.LinearLe([objective], [1], best - 1)]
    total.extra["complete"] = complete
    return best, best_sol, total, trace
