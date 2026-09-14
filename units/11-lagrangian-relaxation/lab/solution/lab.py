"""Unit 11 lab — Lagrangian relaxation.  REFERENCE SOLUTION, imperative.

TSP: a symmetric distance matrix `dist` (n >= 3). Multipliers pi[v], one per vertex;
the modified cost of edge {i, j} is dist[i][j] + pi[i] + pi[j].

GAP: colib.colgen.GAP. An assignment is `agent_of`, a list with agent_of[j] = the agent
of job j.
"""

from __future__ import annotations

from colib.ref import unit

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def one_tree(dist, pi):
    """The minimum 1-tree under modified costs: a spanning tree on vertices 1..n-1 plus the
    two cheapest edges at vertex 0. Returns (L, degrees, edges) where
    L = modified weight - 2 * sum(pi) is the Lagrangian bound, and edges are (i, j), i < j."""
    n = len(dist)
    c = lambda i, j: dist[i][j] + pi[i] + pi[j]
    in_tree = [False] * n
    best = [INF] * n
    link = [-1] * n
    best[1] = 0.0
    edges, weight = [], 0.0
    for _ in range(n - 1):                                    # Prim on 1..n-1
        v = min((u for u in range(1, n) if not in_tree[u]), key=lambda u: best[u])
        in_tree[v] = True
        if link[v] != -1:
            edges.append((min(v, link[v]), max(v, link[v])))
            weight += best[v]
        for u in range(1, n):
            if not in_tree[u] and c(v, u) < best[u]:
                best[u], link[u] = c(v, u), v
    two = sorted(range(1, n), key=lambda u: c(0, u))[:2]
    for u in two:
        edges.append((0, u))
        weight += c(0, u)
    degrees = [0] * n
    for i, j in edges:
        degrees[i] += 1
        degrees[j] += 1
    return weight - 2 * sum(pi), degrees, edges


# ---------------------------------------------------------------- step 2 ---

def subgradient_ascent(oracle, start, upper, iterations=500, lam=2.0, patience=20, project=None):
    """Maximise a concave Lagrangian by subgradient steps with the Polyak-type rule
    t = lam * (upper - L) / |g|^2, halving lam after `patience` iterations without a new
    best. oracle(mult) -> (L, solution, g). project(mult) -> mult, or None.
    Stops early when g == 0 (the relaxed solution is feasible and complementary) or lam < 1e-6.
    Returns (best L, best multipliers, history of L per iteration)."""
    mult = list(start)
    best, best_mult, history, since = -INF, list(mult), [], 0
    for _ in range(iterations):
        L, _, g = oracle(mult)
        history.append(L)
        if L > best + 1e-9:
            best, best_mult, since = L, list(mult), 0
        else:
            since += 1
            if since >= patience:
                lam, since = lam / 2, 0
        norm = sum(x * x for x in g)
        if norm == 0 or lam < 1e-6:
            break
        t = lam * max(upper - L, 1e-9) / norm
        mult = [m + t * x for m, x in zip(mult, g)]
        if project is not None:
            mult = project(mult)
    return best, best_mult, history


def held_karp_bound(dist, upper, iterations=500):
    """The Held–Karp bound by subgradient ascent on one_tree. The subgradient is
    degree - 2 at every vertex. Returns (best bound, pi, history)."""
    def oracle(pi):
        L, deg, edges = one_tree(dist, pi)
        return L, edges, [d - 2 for d in deg]
    return subgradient_ascent(oracle, [0.0] * len(dist), upper, iterations)


# ---------------------------------------------------------------- step 3 ---

def fix_edges(dist, pi, upper):
    """Edges that no tour shorter than or equal to `upper` can use, by 1-tree reduced
    costs: the cheapest 1-tree forced to contain edge e costs L + c(e) - (the most expensive
    edge it must displace). Returns a set of (i, j), i < j."""
    n = len(dist)
    c = lambda i, j: dist[i][j] + pi[i] + pi[j]
    L, _, edges = one_tree(dist, pi)
    tree = set(edges)
    adj = [[] for _ in range(n)]
    zero = []
    for i, j in edges:
        if i == 0:
            zero.append(j)
        else:
            adj[i].append(j)
            adj[j].append(i)
    max_zero = max(c(0, u) for u in zero)
    fixed = set()
    for s in range(1, n):                                     # heaviest edge on each tree path from s
        heaviest = [-INF] * n
        heaviest[s] = 0.0
        stack = [s]
        while stack:
            v = stack.pop()
            for u in adj[v]:
                if heaviest[u] == -INF:
                    heaviest[u] = max(heaviest[v], c(v, u))
                    stack.append(u)
        for t in range(s + 1, n):
            if (s, t) not in tree and L + c(s, t) - heaviest[t] > upper + 1e-9:
                fixed.add((s, t))
    for u in range(1, n):
        if (0, u) not in tree and L + c(0, u) - max_zero > upper + 1e-9:
            fixed.add((0, u))
    return fixed


# ---------------------------------------------------------------- step 4 ---

def gap_relax_assignment(gap, u):
    """Dualise 'each job assigned once' with free multipliers u[j]. What remains is one
    0/1 knapsack per agent. Returns (L, x, g): x[i][j] in {0, 1}, g[j] = 1 - sum_i x[i][j]."""
    m, n = gap.m, gap.n
    knap = unit("16").knapsack
    L = sum(u)
    x = [[0] * n for _ in range(m)]
    for i in range(m):
        jobs = [j for j in range(n) if u[j] - gap.cost[i][j] > 0]
        value, items = knap([u[j] - gap.cost[i][j] for j in jobs], [gap.weight[i][j] for j in jobs],
                            gap.capacity[i])
        L -= value
        for k in items:
            x[i][jobs[k]] = 1
    g = [1 - sum(x[i][j] for i in range(m)) for j in range(n)]
    return L, x, g


def gap_relax_capacity(gap, lam):
    """Dualise the capacities with multipliers lam[i] >= 0. Each job independently takes the
    agent minimising cost + lam * weight. Returns (L, x, g), g[i] = load_i - capacity_i."""
    m, n = gap.m, gap.n
    L = -sum(lam[i] * gap.capacity[i] for i in range(m))
    x = [[0] * n for _ in range(m)]
    for j in range(n):
        i = min(range(m), key=lambda a: gap.cost[a][j] + lam[a] * gap.weight[a][j])
        x[i][j] = 1
        L += gap.cost[i][j] + lam[i] * gap.weight[i][j]
    g = [sum(gap.weight[i][j] * x[i][j] for j in range(n)) - gap.capacity[i] for i in range(m)]
    return L, x, g


# ---------------------------------------------------------------- step 5 ---

def gap_repair(gap, x):
    """A Lagrangian heuristic from the assignment relaxation's x, whose agents already
    respect their capacities. A job taken by several agents stays with the cheapest of them;
    then each unassigned job, largest regret first (the gap between its cheapest and
    second-cheapest agent with room), goes to the cheapest agent with room.
    Returns (cost, agent_of), or None if some job fits nowhere."""
    m, n = gap.m, gap.n
    agent_of = [min((i for i in range(m) if x[i][j]), key=lambda i: gap.cost[i][j], default=None)
                for j in range(n)]
    load = [0] * m
    for j, i in enumerate(agent_of):
        if i is not None:
            load[i] += gap.weight[i][j]
    pending = [j for j in range(n) if agent_of[j] is None]
    while pending:
        def room(j):
            return sorted((gap.cost[i][j], i) for i in range(m) if load[i] + gap.weight[i][j] <= gap.capacity[i])
        options = {j: room(j) for j in pending}
        if any(not o for o in options.values()):
            return None
        regret = lambda j: options[j][1][0] - options[j][0][0] if len(options[j]) > 1 else INF
        j = max(pending, key=regret)
        i = options[j][0][1]
        agent_of[j] = i
        load[i] += gap.weight[i][j]
        pending.remove(j)
    return gap.assignment_cost(agent_of), agent_of
