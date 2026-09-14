"""Unit 23 lab — combinatorial approximation algorithms.  REFERENCE SOLUTION, imperative.

Every algorithm here returns, next to its solution, the quantity its proof compares against: prices for
greedy set cover, a matching or a far-apart point set for the packing bounds, the tree and matching weights
for the TSP heuristics. The tests check the proofs' inequalities, not just the final ratio.

Distances are symmetric integer matrices satisfying the triangle inequality (colib.approx.metric_tsp).
Tours are vertex orders starting at 0.
"""

from __future__ import annotations

from fractions import Fraction
from math import lcm

from colib.approx import min_weight_perfect_matching
from colib.problems import SetCover


# ---------------------------------------------------------------- step 1 ---

def greedy_set_cover(sc):
    """Repeatedly buy the set minimising cost / (number of still-uncovered elements it covers); ties go to
    the lowest index. Returns (x, price): x a 0/1 list over the sets, and price[e] the cost of the set that
    first covered e divided by how many elements it newly covered then (a Fraction). sum(price) == cost."""
    uncovered = set(range(sc.universe))
    x = [0] * sc.n
    price = [Fraction(0)] * sc.universe
    while uncovered:
        best, best_new = None, None
        for i, s in enumerate(sc.sets):
            new = len(s & uncovered)
            if new and (best is None or sc.costs[i] * best_new < sc.costs[best] * new):
                best, best_new = i, new
        if best is None:
            raise ValueError("instance cannot be covered")
        for e in sc.sets[best] & uncovered:
            price[e] = Fraction(sc.costs[best], best_new)
        uncovered -= sc.sets[best]
        x[best] = 1
    return x, price


def harmonic(k):
    """H_k = 1 + 1/2 + ... + 1/k as a Fraction (H_0 = 0)."""
    return sum((Fraction(1, i) for i in range(1, k + 1)), Fraction(0))


def greedy_tight_instance(n):
    """Universe range(n). Set i (i = 0 .. n-1) is {i} with cost L / (i + 1), where L = lcm(1..n); set n is
    the whole universe with cost L + 1. Greedy pays L * H_n; the optimum pays L + 1."""
    L = lcm(*range(1, n + 1))
    sets = tuple(frozenset({i}) for i in range(n)) + (frozenset(range(n)),)
    return SetCover(n, sets, tuple(L // (i + 1) for i in range(n)) + (L + 1,))


# ---------------------------------------------------------------- step 2 ---

def matching_vertex_cover(vc):
    """Scan the edges in order, keeping each edge whose endpoints are both unmatched: a maximal matching.
    Returns (cover, matching): cover the 0/1 list of matched vertices, matching the kept edges in order."""
    matched = [0] * vc.n
    matching = []
    for u, v in vc.edges:
        if not matched[u] and not matched[v]:
            matched[u] = matched[v] = 1
            matching.append((u, v))
    return matched, matching


def k_center(dist, k, first=0):
    """Farthest-first traversal (Gonzalez 1985): start from `first`, then repeatedly add the point farthest
    from the chosen centres (ties to the lowest index). Returns (centres, radius, witness): radius is the
    largest distance from a point to its nearest centre, and witness is the farthest point at the end,
    whose distance to every centre is >= radius (so centres + [witness] are k + 1 points pairwise >= radius
    apart). If radius is 0, witness is None."""
    n = len(dist)
    centres = [first]
    near = list(dist[first])
    while len(centres) < k:
        far = max(range(n), key=lambda v: (near[v], -v))
        if near[far] == 0:
            break
        centres.append(far)
        near = [min(near[v], dist[far][v]) for v in range(n)]
    far = max(range(n), key=lambda v: (near[v], -v))
    radius = near[far]
    return centres, radius, (far if radius > 0 else None)


# ---------------------------------------------------------------- step 3 ---

def prim(dist):
    """A minimum spanning tree of the complete graph, O(n^2). Returns its n - 1 edges as sorted pairs."""
    n = len(dist)
    if n <= 1:
        return []
    in_tree = [False] * n
    in_tree[0] = True
    best = list(dist[0])
    parent = [0] * n
    edges = []
    for _ in range(n - 1):
        v = min((u for u in range(n) if not in_tree[u]), key=lambda u: best[u])
        in_tree[v] = True
        edges.append(tuple(sorted((parent[v], v))))
        for u in range(n):
            if not in_tree[u] and dist[v][u] < best[u]:
                best[u], parent[u] = dist[v][u], v
    return sorted(edges)


def shortcut(walk):
    """The order of first visits along a closed walk: a Hamiltonian tour when the walk visits every vertex."""
    seen = set()
    tour = []
    for v in walk:
        if v not in seen:
            seen.add(v)
            tour.append(v)
    return tour


def double_tree(dist):
    """The 2-approximation: a depth-first walk around the MST (every tree edge traversed twice), shortcut.
    Children are visited in increasing vertex order from root 0. Returns (tour, tree weight)."""
    tree = prim(dist)
    adj = {v: [] for v in range(len(dist))}
    for u, v in tree:
        adj[u].append(v)
        adj[v].append(u)
    walk, stack, seen = [], [0], set()
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        walk.append(v)
        stack.extend(sorted(adj[v], reverse=True))
    return shortcut(walk), sum(dist[u][v] for u, v in tree)


# ---------------------------------------------------------------- step 4 ---

def odd_vertices(n, edges):
    """Vertices of odd degree in the multigraph on range(n) with the given edge list, sorted."""
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    return [v for v in range(n) if degree[v] % 2]


def euler_circuit(n, edges, start=0):
    """A closed walk from `start` using every edge of a connected multigraph with all degrees even exactly
    once (Hierholzer). Returns the vertex sequence, beginning and ending at start (len(edges) + 1 entries)."""
    adj = {v: [] for v in range(n)}
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k))
        adj[v].append((u, k))
    used = [False] * len(edges)
    stack, circuit = [start], []
    while stack:
        v = stack[-1]
        while adj[v] and used[adj[v][-1][1]]:
            adj[v].pop()
        if adj[v]:
            u, k = adj[v].pop()
            used[k] = True
            stack.append(u)
        else:
            circuit.append(stack.pop())
    return circuit[::-1]


def christofides(dist):
    """Christofides' 3/2-approximation: MST, plus a minimum-weight perfect matching on its odd-degree
    vertices (colib.approx.min_weight_perfect_matching), then an Euler circuit of the union from 0,
    shortcut. Returns (tour, tree weight, matching weight)."""
    n = len(dist)
    tree = prim(dist)
    matching = min_weight_perfect_matching(odd_vertices(n, tree), dist)
    tour = shortcut(euler_circuit(n, tree + matching, 0)) if n > 1 else [0]
    return tour, sum(dist[u][v] for u, v in tree), sum(dist[u][v] for u, v in matching)


# ---------------------------------------------------------------- step 5 ---

def list_scheduling(p, m):
    """Graham's list scheduling: jobs in the given order, each to a currently least-loaded machine (lowest
    index on ties). Returns (makespan, machine), machine[j] the machine of job j."""
    load = [0] * m
    machine = [0] * len(p)
    for j, pj in enumerate(p):
        i = min(range(m), key=lambda i: (load[i], i))
        machine[j] = i
        load[i] += pj
    return max(load), machine


def lpt(p, m):
    """Longest processing time first: list scheduling on the jobs sorted by decreasing time (stable).
    Returns (makespan, machine) indexed by the original job numbers."""
    order = sorted(range(len(p)), key=lambda j: -p[j])
    makespan, sorted_machine = list_scheduling([p[j] for j in order], m)
    machine = [0] * len(p)
    for pos, j in enumerate(order):
        machine[j] = sorted_machine[pos]
    return makespan, machine


def list_scheduling_tight(m):
    """m(m - 1) jobs of length 1, then one of length m: list scheduling gives 2m - 1, the optimum m."""
    return [1] * (m * (m - 1)) + [m]


def lpt_tight(m):
    """2m + 1 jobs: two each of 2m - 1, 2m - 2, ..., m + 1, then three of m. LPT gives 4m - 1, the optimum 3m."""
    return [t for t in range(2 * m - 1, m, -1) for _ in range(2)] + [m] * 3
