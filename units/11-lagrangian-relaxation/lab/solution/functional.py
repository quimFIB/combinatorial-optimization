"""Unit 11 lab — Lagrangian relaxation.  REFERENCE SOLUTION, functional.

A Lagrangian relaxation is a function from multipliers to (bound, solution,
subgradient), and subgradient ascent is an unfold over (multipliers, step
parameter, best so far). Prim's algorithm is a fold that grows the tree one
vertex at a time; the heaviest-edge-on-path table is a fold over tree layers.
"""

from __future__ import annotations

import toolz as tz

from colib.ref import unit

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def one_tree(dist, pi):
    n = len(dist)
    c = lambda i, j: dist[i][j] + pi[i] + pi[j]

    def grow(state, _):
        tree, best, edges = state                             # best[u] = (cost to tree, link)
        v = min((u for u in best if u not in tree), key=lambda u: best[u][0])
        cost, link = best[v]
        best2 = {u: min(b, (c(v, u), v)) if u not in tree | {v} else b for u, b in best.items()}
        new_edges = edges + ((min(v, link), max(v, link), cost),) if link is not None else edges
        return tree | {v}, best2, new_edges

    start = (frozenset(), {u: ((0.0, None) if u == 1 else (INF, None)) for u in range(1, n)}, ())
    _, _, tree_edges = tz.reduce(grow, range(n - 1), start)
    zero = tuple((0, u, c(0, u)) for u in sorted(range(1, n), key=lambda u: c(0, u))[:2])
    all_edges = tree_edges + zero
    degrees = [sum(1 for i, j, _ in all_edges if v in (i, j)) for v in range(n)]
    return sum(w for *_, w in all_edges) - 2 * sum(pi), degrees, [(i, j) for i, j, _ in all_edges]


# ---------------------------------------------------------------- step 2 ---

def subgradient_ascent(oracle, start, upper, iterations=500, lam=2.0, patience=20, project=None):
    project = project or (lambda v: v)

    def step(s):
        L, _, g = oracle(s["mult"])
        improved = L > s["best"] + 1e-9
        since = 0 if improved else s["since"] + 1
        lam2 = s["lam"] / 2 if (not improved and since >= patience) else s["lam"]
        since = 0 if (not improved and since >= patience) else since
        norm = sum(x * x for x in g)
        stop = norm == 0 or lam2 < 1e-6
        t = 0.0 if stop else lam2 * max(upper - L, 1e-9) / norm
        return dict(mult=s["mult"] if stop else project([m + t * x for m, x in zip(s["mult"], g)]),
                    lam=lam2, since=since, stop=stop,
                    best=L if improved else s["best"], best_mult=s["mult"] if improved else s["best_mult"],
                    history=s["history"] + [L])

    start_state = dict(mult=list(start), lam=lam, since=0, stop=False, best=-INF, best_mult=list(start), history=[])
    states = tz.drop(1, tz.iterate(step, start_state))
    final = next(s for k, s in enumerate(states, 1) if s["stop"] or k == iterations)
    return final["best"], final["best_mult"], final["history"]


def held_karp_bound(dist, upper, iterations=500):
    def oracle(pi):
        L, deg, edges = one_tree(dist, pi)
        return L, edges, [d - 2 for d in deg]
    return subgradient_ascent(oracle, [0.0] * len(dist), upper, iterations)


# ---------------------------------------------------------------- step 3 ---

def fix_edges(dist, pi, upper):
    n = len(dist)
    c = lambda i, j: dist[i][j] + pi[i] + pi[j]
    L, _, edges = one_tree(dist, pi)
    tree = frozenset(edges)
    inner = [(i, j) for i, j in edges if i != 0]
    adj = tz.groupby(0, inner + [(j, i) for i, j in inner])
    max_zero = max(c(0, j) for i, j in edges if i == 0)

    def heaviest_from(s):
        def spread(state):
            known, frontier = state
            nxt = {u: max(known[v], c(v, u)) for v in frontier for _, u in adj.get(v, []) if u not in known}
            return {**known, **nxt}, tuple(nxt)
        known, _ = next(st for st in tz.iterate(spread, ({s: 0.0}, (s,))) if not st[1])
        return known

    inner_fixed = {(s, t) for s in range(1, n) for t, h in heaviest_from(s).items()
                   if t > s and (s, t) not in tree and L + c(s, t) - h > upper + 1e-9}
    zero_fixed = {(0, u) for u in range(1, n) if (0, u) not in tree and L + c(0, u) - max_zero > upper + 1e-9}
    return inner_fixed | zero_fixed


# ---------------------------------------------------------------- step 4 ---

def gap_relax_assignment(gap, u):
    knap = unit("16").knapsack

    def agent(i):
        jobs = [j for j in range(gap.n) if u[j] - gap.cost[i][j] > 0]
        value, items = knap([u[j] - gap.cost[i][j] for j in jobs], [gap.weight[i][j] for j in jobs], gap.capacity[i])
        chosen = {jobs[k] for k in items}
        return value, [1 if j in chosen else 0 for j in range(gap.n)]

    solved = [agent(i) for i in range(gap.m)]
    x = [row for _, row in solved]
    return sum(u) - sum(v for v, _ in solved), x, [1 - sum(col) for col in zip(*x)]


def gap_relax_capacity(gap, lam):
    price = lambda i, j: gap.cost[i][j] + lam[i] * gap.weight[i][j]
    choice = [min(range(gap.m), key=lambda i: price(i, j)) for j in range(gap.n)]
    x = [[1 if choice[j] == i else 0 for j in range(gap.n)] for i in range(gap.m)]
    L = sum(price(choice[j], j) for j in range(gap.n)) - sum(l * b for l, b in zip(lam, gap.capacity))
    g = [sum(w * xi for w, xi in zip(gap.weight[i], x[i])) - gap.capacity[i] for i in range(gap.m)]
    return L, x, g


# ---------------------------------------------------------------- step 5 ---

def gap_repair(gap, x):
    m, n = gap.m, gap.n
    kept = {j: min((i for i in range(m) if x[i][j]), key=lambda i: gap.cost[i][j]) for j in range(n)
            if any(x[i][j] for i in range(m))}
    loads = lambda assigned: [sum(gap.weight[i][j] for j, a in assigned.items() if a == i) for i in range(m)]

    def place(state):
        assigned = state
        load = loads(assigned)
        options = {j: sorted((gap.cost[i][j], i) for i in range(m) if load[i] + gap.weight[i][j] <= gap.capacity[i])
                   for j in range(n) if j not in assigned}
        if any(not o for o in options.values()):
            return None
        regret = lambda j: options[j][1][0] - options[j][0][0] if len(options[j]) > 1 else INF
        j = max(options, key=regret)
        return {**assigned, j: options[j][0][1]}

    final = next(s for s in tz.iterate(lambda s: s if s is None else place(s), kept) if s is None or len(s) == n)
    if final is None:
        return None
    agent_of = [final[j] for j in range(n)]
    return gap.assignment_cost(agent_of), agent_of
