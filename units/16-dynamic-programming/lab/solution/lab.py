"""Unit 16 lab — dynamic programming.  REFERENCE SOLUTION, imperative.

Graphs have vertices 0..n-1 and undirected edges (u, v). A tree decomposition is
a list `bags` of sets of vertices plus `tree_edges`, pairs (i, j) of bag indices.
"""

from __future__ import annotations

import numpy as np

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def knapsack(values, weights, capacity):
    """0/1 knapsack by DP over capacities. Returns (best value, sorted list of items)."""
    n = len(values)
    best = np.zeros(capacity + 1)
    take = np.zeros((n, capacity + 1), dtype=bool)          # take[i, c]: item i used at capacity c
    for i in range(n):
        w = weights[i]
        if w > capacity:
            continue
        with_i = best[:capacity + 1 - w] + values[i]           # candidate for capacities w..C
        better = with_i > best[w:]
        take[i, w:] = better
        best[w:] = np.where(better, with_i, best[w:])
    items, c = [], capacity
    for i in reversed(range(n)):                              # walk the decisions back
        if take[i, c]:
            items.append(i)
            c -= weights[i]
    items.sort()
    return sum(values[i] for i in items), items


def unbounded_knapsack(values, weights, capacity):
    """Each item may be used any number of times. Returns (best value, counts list)."""
    n = len(values)
    best = [0] * (capacity + 1)
    choice = [-1] * (capacity + 1)                            # last item added at capacity c, or -1
    for c in range(1, capacity + 1):
        best[c], choice[c] = best[c - 1], -1                  # leave one unit of capacity unused
        for i in range(n):
            w = weights[i]
            if w <= c and best[c - w] + values[i] > best[c]:
                best[c], choice[c] = best[c - w] + values[i], i
    counts, c = [0] * n, capacity
    while c > 0:
        if choice[c] == -1:
            c -= 1
        else:
            counts[choice[c]] += 1
            c -= weights[choice[c]]
    return sum(k * v for k, v in zip(counts, values)), counts


# ---------------------------------------------------------------- step 2 ---

def held_karp(dist):
    """Exact TSP by DP over subsets, O(n^2 2^n). Returns (length, order) with order[0] == 0.

    dp[S][k] = shortest path from 0 through exactly the cities in S (a subset of 1..n-1),
    ending at k in S. Vectorised by subset size: every dp entry of size s is
    computed from entries of size s - 1 in one numpy operation per end city.
    """
    n = len(dist)
    if n <= 2:
        return (dist[0][1] + dist[1][0] if n == 2 else 0), list(range(n))
    m = n - 1                                                 # cities 1..n-1 are bits 0..m-1
    D = np.array(dist, dtype=float)
    d = D[1:, 1:]
    size = 1 << m
    dp = np.full((size, m), INF)
    parent = np.full((size, m), -1, dtype=np.int8 if m < 127 else np.int16)
    for k in range(m):
        dp[1 << k, k] = D[0, k + 1]
    popcount = np.zeros(size, dtype=np.int8)
    for b in range(m):
        popcount[(np.arange(size) >> b) & 1 == 1] += 1
    for s in range(2, m + 1):
        masks = np.nonzero(popcount == s)[0]
        for k in range(m):
            sel = masks[(masks >> k) & 1 == 1]
            prev = sel ^ (1 << k)
            cand = dp[prev] + d[:, k]                         # cand[., j] = path to j, then j -> k
            j = cand.argmin(axis=1)
            dp[sel, k] = cand[np.arange(len(sel)), j]
            parent[sel, k] = j
    full = size - 1
    last = int(np.argmin(dp[full] + D[1:, 0]))
    order, mask, k = [], full, last
    while k != -1:
        order.append(k + 1)
        mask, k = mask ^ (1 << k), int(parent[mask, k])
    order.append(0)
    order.reverse()
    return sum(dist[order[i]][order[(i + 1) % n]] for i in range(n)), order


# ---------------------------------------------------------------- step 3 ---

def tree_vertex_cover(n, edges, weights):
    """Minimum-weight vertex cover of a forest. Returns (weight, set of vertices).

    For each vertex v with children C: inc[v] = w[v] + sum min(inc[c], exc[c]),
    exc[v] = sum inc[c]. Iterative, so a path of 10^5 vertices does not recurse.
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order, seen = [], [False] * n
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        stack = [root]
        while stack:
            v = stack.pop()
            order.append(v)
            for u in adj[v]:
                if not seen[u]:
                    seen[u], parent[u] = True, v
                    stack.append(u)
    inc = list(weights)
    exc = [0] * n
    for v in reversed(order):                                 # children before parents
        p = parent[v]
        if p != -1:
            inc[p] += min(inc[v], exc[v])
            exc[p] += inc[v]
    cover = set()
    for v in order:                                           # parents before children
        p = parent[v]
        if p == -1:
            chosen = inc[v] <= exc[v]
        else:
            chosen = True if p not in cover else inc[v] <= exc[v]
        if chosen:
            cover.add(v)
    return sum(weights[v] for v in cover), cover


# ---------------------------------------------------------------- step 4 ---

def width(bags):
    return max((len(b) for b in bags), default=0) - 1


def is_tree_decomposition(n, edges, bags, tree_edges):
    """True iff (bags, tree_edges) is a tree decomposition of the graph."""
    B = len(bags)
    if B == 0:
        return n == 0
    if len(tree_edges) != B - 1:
        return False
    adj = [[] for _ in range(B)]
    for i, j in tree_edges:
        adj[i].append(j)
        adj[j].append(i)
    seen, stack = {0}, [0]
    while stack:
        for j in adj[stack.pop()]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    if len(seen) != B:                                        # B - 1 edges and connected: a tree
        return False
    if any(not any(v in b for b in bags) for v in range(n)):
        return False
    if any(not any(u in b and v in b for b in bags) for u, v in edges):
        return False
    for v in range(n):                                        # bags holding v form a subtree
        holding = [i for i in range(B) if v in bags[i]]
        reach, stack = {holding[0]}, [holding[0]]
        while stack:
            for j in adj[stack.pop()]:
                if j not in reach and v in bags[j]:
                    reach.add(j)
                    stack.append(j)
        if len(reach) != len(holding):
            return False
    return True


def elimination_decomposition(n, edges, order=None):
    """A tree decomposition from an elimination ordering; with order=None, choose the
    next vertex greedily by minimum current degree (ties: smallest index).
    Returns (bags, tree_edges)."""
    nbrs = [set() for _ in range(n)]
    for u, v in edges:
        nbrs[u].add(v)
        nbrs[v].add(u)
    alive = set(range(n))
    position, bags, eliminated = {}, [], []
    for step in range(n):
        v = order[step] if order is not None else min(alive, key=lambda x: (len(nbrs[x]), x))
        bag = {v} | nbrs[v]
        for a in nbrs[v]:                                     # make the neighbourhood a clique
            nbrs[a] |= nbrs[v] - {a}
            nbrs[a].discard(v)
        alive.discard(v)
        position[v] = step
        bags.append(bag)
        eliminated.append(v)
    tree_edges, roots = [], []
    for i, v in enumerate(eliminated):
        later = bags[i] - {v}
        if later:
            u = min(later, key=position.get)                  # the earliest-eliminated neighbour
            tree_edges.append((i, position[u]))
        else:
            roots.append(i)
    tree_edges += list(zip(roots, roots[1:]))                 # join components into one tree
    return bags, tree_edges


# ---------------------------------------------------------------- step 5 ---

def td_vertex_cover(n, edges, weights, bags, tree_edges):
    """Minimum-weight vertex cover by DP over a tree decomposition, O(bags * 2^(width+1)).
    Returns (weight, set of vertices)."""
    if not bags:
        return 0, set()
    B = len(bags)
    adj = [[] for _ in range(B)]
    for i, j in tree_edges:
        adj[i].append(j)
        adj[j].append(i)
    parent, order, stack = [-1] * B, [], [0]
    seen = [False] * B
    seen[0] = True
    while stack:
        b = stack.pop()
        order.append(b)
        for c in adj[b]:
            if not seen[c]:
                seen[c], parent[c] = True, b
                stack.append(c)
    edge_set = {frozenset(e) for e in edges}
    lists = [sorted(b) for b in bags]
    table, back = [None] * B, [dict() for _ in range(B)]      # back[b][c][key] = best child subset

    def weight(bag, S):
        return sum(weights[bag[i]] for i in range(len(bag)) if S >> i & 1)

    for b in reversed(order):
        bag = lists[b]
        k = len(bag)
        pairs = [(1 << i) | (1 << j) for i in range(k) for j in range(i + 1, k)
                 if frozenset((bag[i], bag[j])) in edge_set]
        t = [INF] * (1 << k)
        for S in range(1 << k):
            if all(S & p for p in pairs):
                t[S] = weight(bag, S)
        for c in adj[b]:
            if c == parent[b]:
                continue
            child, cbag = table[c], lists[c]
            shared = [v for v in cbag if v in bags[b]]
            cbit = [cbag.index(v) for v in shared]
            bbit = [bag.index(v) for v in shared]
            best, arg = {}, {}
            for Sc, val in enumerate(child):
                if val == INF:
                    continue
                key = sum(1 << q for q, i in enumerate(cbit) if Sc >> i & 1)
                val -= sum(weights[shared[q]] for q in range(len(shared)) if key >> q & 1)
                if val < best.get(key, INF):
                    best[key], arg[key] = val, Sc
            back[b][c] = arg
            for S in range(1 << k):
                if t[S] < INF:
                    key = sum(1 << q for q, i in enumerate(bbit) if S >> i & 1)
                    t[S] += best[key]                         # every key exists: "all in" is always valid
        table[b] = t
    root = min(range(len(table[0])), key=table[0].__getitem__)
    chosen, cover = {0: root}, set()
    for b in order:                                           # parents before children
        S, bag = chosen[b], lists[b]
        cover |= {bag[i] for i in range(len(bag)) if S >> i & 1}
        for c in adj[b]:
            if c != parent[b]:
                shared = [v for v in lists[c] if v in bags[b]]
                key = sum(1 << q for q, v in enumerate(shared) if S >> bag.index(v) & 1)
                chosen[c] = back[b][c][key]
    return sum(weights[v] for v in cover), cover
