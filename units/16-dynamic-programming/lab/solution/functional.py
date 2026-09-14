"""Unit 16 lab — dynamic programming.  REFERENCE SOLUTION, functional.

Dynamic programming is the functional programmer's home ground: a table is a
dictionary comprehension over states, each defined from states already built.
Every DP here is a fold over *layers* — items, capacities, subset sizes, tree
depths, decomposition bags — and a reconstruction is an unfold back through
the choices. Subsets are frozensets rather than bitmasks, which is slower (the
imperative reference vectorises Held–Karp with numpy) but reads as the recurrence.
"""

from __future__ import annotations

from itertools import combinations

import toolz as tz

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def knapsack(values, weights, capacity):
    n = len(values)

    def add_item(row, i):
        w, v = weights[i], values[i]
        return tuple(max(row[c], row[c - w] + v) if w <= c else row[c] for c in range(capacity + 1))

    rows = list(tz.accumulate(add_item, range(n), (0,) * (capacity + 1)))    # rows[i]: items < i

    def back(state):
        i, c, items = state
        took = rows[i][c] != rows[i - 1][c]
        return i - 1, c - weights[i - 1] if took else c, items + (i - 1,) if took else items

    _, _, items = next(s for s in tz.iterate(back, (n, capacity, ())) if s[0] == 0)
    return sum(values[i] for i in items), sorted(items)


def unbounded_knapsack(values, weights, capacity):
    n = len(values)

    def extend(row, c):
        options = [(row[c - 1][0], -1)] + [(row[c - weights[i]][0] + values[i], i)
                                           for i in range(n) if weights[i] <= c]
        best = max(o[0] for o in options)
        return row + (next(o for o in options if o[0] == best),)

    row = tz.reduce(extend, range(1, capacity + 1), ((0, -1),))

    def back(state):
        c, counts = state
        i = row[c][1]
        return (c - 1, counts) if i == -1 else (c - weights[i], tz.assoc(counts, i, counts[i] + 1))

    _, counts = next(s for s in tz.iterate(back, (capacity, {i: 0 for i in range(n)})) if s[0] <= 0)
    counts = [counts[i] for i in range(n)]
    return sum(k * v for k, v in zip(counts, values)), counts


# ---------------------------------------------------------------- step 2 ---

def held_karp(dist):
    n = len(dist)
    if n <= 2:
        order = list(range(n))
        return (dist[0][1] + dist[1][0] if n == 2 else 0), order
    cities = range(1, n)
    first = {(frozenset([k]), k): (dist[0][k], None) for k in cities}

    def layer(table, size):
        return {(S, k): min((table[(S - {k}, j)][0] + dist[j][k], j) for j in S if j != k)
                for S in map(frozenset, combinations(cities, size)) for k in S}

    tables = list(tz.accumulate(layer, range(2, n), first))
    full = frozenset(cities)
    _, last = min((tables[-1][(full, k)][0] + dist[k][0], k) for k in cities)

    def back(state):
        S, k, path = state
        prev = tables[len(S) - 1][(S, k)][1]
        return S - {k}, prev, path + (k,)

    _, _, path = next(s for s in tz.iterate(back, (full, last, ())) if s[1] is None)
    order = [0] + list(reversed(path))
    return sum(dist[order[i]][order[(i + 1) % n]] for i in range(n)), order


# ---------------------------------------------------------------- step 3 ---

def _neighbours(n, edges):
    arcs = tz.groupby(0, list(edges) + [(v, u) for u, v in edges])
    return {v: [b for _, b in arcs.get(v, [])] for v in range(n)}


def _rooted_layers(n, adj):
    """BFS layers of a rooted spanning forest: (list of layers, parent dict)."""
    def grow(state):
        seen, parent, layers = state
        frontier = layers[-1]
        nxt = {u: v for v in frontier for u in adj[v] if u not in seen}
        if nxt:
            return seen | set(nxt), {**parent, **nxt}, layers + (tuple(sorted(nxt)),)
        fresh = next((v for v in range(n) if v not in seen), None)
        return (seen, parent, layers + ((),)) if fresh is None else \
            (seen | {fresh}, {**parent, fresh: -1}, layers + ((fresh,),))

    start = (frozenset({0}), {0: -1}, ((0,),)) if n else (frozenset(), {}, ((),))
    seen, parent, layers = next(s for s in tz.iterate(grow, start) if not s[2][-1])
    return [l for l in layers if l], parent


def tree_vertex_cover(n, edges, weights):
    if n == 0:
        return 0, set()
    adj = _neighbours(n, edges)
    layers, parent = _rooted_layers(n, adj)
    children = tz.groupby(lambda v: parent[v], [v for v in range(n) if parent[v] != -1])

    def solve_layer(dp, layer):                                # dp[v] = (include v, exclude v)
        return {**dp, **{v: (weights[v] + sum(min(dp[c]) for c in children.get(v, [])),
                             sum(dp[c][0] for c in children.get(v, []))) for v in layer}}

    dp = tz.reduce(solve_layer, reversed(layers), {})

    def choose(cover, layer):
        return cover | {v for v in layer
                        if (parent[v] != -1 and parent[v] not in cover) or dp[v][0] <= dp[v][1]}

    cover = tz.reduce(choose, layers, frozenset())
    return sum(weights[v] for v in cover), set(cover)


# ---------------------------------------------------------------- step 4 ---

def width(bags):
    return max((len(b) for b in bags), default=0) - 1


def _connected(nodes, adj):
    nodes = frozenset(nodes)
    if not nodes:
        return True
    start = frozenset([min(nodes)])
    grow = lambda R: R | {j for i in R for j in adj.get(i, ()) if j in nodes}
    fix = next(b for a, b in tz.sliding_window(2, tz.iterate(grow, start)) if a == b)
    return fix == nodes


def is_tree_decomposition(n, edges, bags, tree_edges):
    B = len(bags)
    if B == 0:
        return n == 0
    adj = tz.merge_with(lambda xs: [y for x in xs for y in x],
                        *({i: [j]} for i, j in tree_edges), *({j: [i]} for i, j in tree_edges))
    return (len(tree_edges) == B - 1
            and _connected(range(B), adj)
            and all(any(v in b for b in bags) for v in range(n))
            and all(any(u in b and v in b for b in bags) for u, v in edges)
            and all(_connected([i for i in range(B) if v in bags[i]], adj) for v in range(n)))


def elimination_decomposition(n, edges, order=None):
    nbrs0 = tz.valmap(frozenset, _neighbours(n, edges))

    def eliminate(state):
        nbrs, step, out = state
        v = order[step] if order is not None else min(nbrs, key=lambda x: (len(nbrs[x]), x))
        N = nbrs[v]
        rest = {a: (nbrs[a] | N) - {a, v} if a in N else nbrs[a] for a in nbrs if a != v}
        return rest, step + 1, out + ((v, frozenset(N | {v})),)

    *_, out = next(s for s in tz.iterate(eliminate, (nbrs0, 0, ())) if s[1] == n)
    position = {v: i for i, (v, _) in enumerate(out)}
    bags = [set(b) for _, b in out]
    links = [(i, min(b - {v}, key=position.get)) for i, (v, b) in enumerate(out) if b - {v}]
    roots = [i for i, (v, b) in enumerate(out) if not b - {v}]
    return bags, [(i, position[u]) for i, u in links] + list(zip(roots, roots[1:]))


# ---------------------------------------------------------------- step 5 ---

def _subsets(xs):
    xs = list(xs)
    return (frozenset(c) for k in range(len(xs) + 1) for c in combinations(xs, k))


def td_vertex_cover(n, edges, weights, bags, tree_edges):
    if not bags:
        return 0, set()
    bags = [frozenset(b) for b in bags]
    adj = tz.merge_with(lambda xs: [y for x in xs for y in x],
                        {i: [] for i in range(len(bags))},
                        *({i: [j]} for i, j in tree_edges), *({j: [i]} for i, j in tree_edges))
    layers, parent = _rooted_layers(len(bags), adj)
    children = tz.groupby(lambda b: parent[b], [b for b in range(len(bags)) if parent[b] != -1])
    edge_set = {frozenset(e) for e in edges}
    w = lambda S: sum(weights[v] for v in S)

    def valid(bag, S):
        return all(u in S or v in S for u, v in map(tuple, edge_set) if u in bag and v in bag)

    def table_for(tables, b):
        def child_best(c, P):                                    # best child subset agreeing with P on the overlap
            shared = bags[b] & bags[c]
            return min(((tables[c][Sc] - w(Sc & shared), Sc) for Sc in tables[c] if Sc & shared == P),
                       default=(INF, None), key=lambda t: t[0])
        rows = {S: w(S) + sum(child_best(c, S & bags[c])[0] for c in children.get(b, []))
                for S in _subsets(bags[b]) if valid(bags[b], S)}
        return {**tables, b: {S: val for S, val in rows.items() if val < INF}}

    tables = tz.reduce(lambda t, layer: tz.reduce(table_for, layer, t), reversed(layers), {})

    def pick(chosen, layer):
        def best_child(c):
            shared = bags[parent[c]] & bags[c]
            P = chosen[parent[c]] & shared
            return min((Sc for Sc in tables[c] if Sc & shared == P),
                       key=lambda Sc: tables[c][Sc] - w(Sc & shared))
        return {**chosen, **{b: (min(tables[b], key=tables[b].get) if parent[b] == -1 else best_child(b))
                             for b in layer}}

    chosen = tz.reduce(pick, layers, {})
    cover = frozenset().union(*chosen.values())
    return w(cover), set(cover)
