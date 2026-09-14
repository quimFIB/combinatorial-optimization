"""Unit 23's recorded data, for units/23-approximation/explore.html.

Greedy set cover on the deck's five-element instance, step by step: the loop of the
reference `greedy_set_cover` copied here so each step's cost-per-new-element can be
recorded, and checked against the reference's own result. Metric TSP: the deck's six
points and an eight-point instance, through the reference `prim`, `double_tree`,
`odd_vertices`, `min_weight_perfect_matching`, `euler_circuit`, `shortcut` and
`christofides`, with the optimum by brute force. `co viz 23` writes the data file.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from itertools import combinations, permutations

from colib import ref
from colib.approx import metric_closure, min_weight_perfect_matching
from colib.problems import SetCover

L = ref.unit("23")


def fr(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


# ---------------------------------------------------------------- set cover
def set_cover():
    sc = SetCover(5, (frozenset({2}), frozenset({0}), frozenset({1, 2, 3, 4}), frozenset({0, 1, 3, 4})), (5, 1, 6, 4))
    uncovered = set(range(sc.universe))
    x = [0] * sc.n
    price = [None] * sc.universe
    states = [{"bought": [], "uncovered": sorted(uncovered), "price": [None] * sc.universe,
               "ratios": [fr(Fraction(c, len(s))) for c, s in zip(sc.costs, sc.sets)], "pick": None, "paid": 0,
               "note": "Nothing bought yet. Each set's cost per element it would newly cover is shown."}]
    paid = 0
    while uncovered:
        best, best_new = None, None
        ratios = []
        for i, s in enumerate(sc.sets):
            new = len(s & uncovered)
            ratios.append(fr(Fraction(sc.costs[i], new)) if new else None)
            if new and (best is None or sc.costs[i] * best_new < sc.costs[best] * new):
                best, best_new = i, new
        for e in sc.sets[best] & uncovered:
            price[e] = Fraction(sc.costs[best], best_new)
        newly = sorted(sc.sets[best] & uncovered)
        uncovered -= sc.sets[best]
        x[best] = 1
        paid += sc.costs[best]
        states.append({"bought": [i for i in range(sc.n) if x[i]], "uncovered": sorted(uncovered),
                       "price": [None if p is None else fr(p) for p in price], "ratios": ratios, "pick": best,
                       "paid": paid, "newly": newly,
                       "note": f"Buy S{best}: cost {sc.costs[best]} over {best_new} new element(s), price {fr(Fraction(sc.costs[best], best_new))} each."})
    rx, rprice = L.greedy_set_cover(sc)
    assert rx == x and rprice == price
    best_cost = min(sum(sc.costs[i] for i in S) for k in range(1, sc.n + 1) for S in combinations(range(sc.n), k)
                    if set().union(*(sc.sets[i] for i in S)) == set(range(sc.universe)))
    return {"universe": sc.universe, "sets": [sorted(s) for s in sc.sets], "costs": list(sc.costs),
            "states": states, "opt": best_cost, "harmonic": [fr(L.harmonic(len(s))) for s in sc.sets]}


# ---------------------------------------------------------------- TSP
def six_points():
    pts = [(6, 6), (14, 4), (22, 7), (10, 15), (20, 16), (28, 14)]   # the deck's figure, one unit = 10 px
    dist = [[int(math.dist(a, b) + 0.5) for b in pts] for a in pts]
    return pts, [list(r) for r in metric_closure(dist)]


def random_points(n, seed):
    r = random.Random(seed)
    pts = [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(n)]      # as colib.approx.metric_tsp draws them
    dist = [[int(math.dist(a, b) + 0.5) for b in pts] for a in pts]
    return pts, [list(r) for r in metric_closure(dist)]


def length(tour, dist):
    return sum(dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def tsp_run(title, pts, dist):
    n = len(dist)
    tree = L.prim(dist)
    w_tree = sum(dist[u][v] for u, v in tree)
    # double tree: the depth-first walk with returns, as the deck draws it
    adj = {v: sorted(u for e in tree for u in e if v in e and u != v) for v in range(n)}
    walk, seen = [], set()

    def dfs(v):
        seen.add(v)
        walk.append(v)
        for u in adj[v]:
            if u not in seen:
                dfs(u)
                walk.append(v)
    dfs(0)
    dt_tour, _ = L.double_tree(dist)
    assert L.shortcut(walk) == dt_tour
    odd = L.odd_vertices(n, tree)
    matching = min_weight_perfect_matching(odd, dist)
    circuit = L.euler_circuit(n, tree + matching, 0)
    ch_tour, wt, wm = L.christofides(dist)
    assert L.shortcut(circuit) == ch_tour and wt == w_tree
    opt = min(length([0, *p], dist) for p in permutations(range(1, n)))
    common = {"points": [list(p) for p in pts], "dist": dist, "tree": [list(e) for e in tree], "w_tree": w_tree,
              "opt": opt}
    dt_states = [
        {"show": "points", "note": "The points. Distances are rounded and metric (triangle inequality holds)."},
        {"show": "tree", "note": f"Minimum spanning tree, weight {w_tree}: a lower bound, since deleting a tour edge leaves a spanning path."},
        {"show": "walk", "note": f"Walk around the tree, every edge twice: length {2 * w_tree}."},
        {"show": "tour", "note": f"Shortcut repeated vertices: tour {' '.join(map(str, dt_tour))}, length {length(dt_tour, dist)} ≤ 2·{w_tree} = {2 * w_tree}. Optimum {opt}."},
    ]
    ch_states = [
        {"show": "tree", "note": f"Minimum spanning tree, weight {w_tree}."},
        {"show": "odd", "note": f"Odd-degree vertices of the tree: {', '.join(map(str, odd))}. Always an even number."},
        {"show": "matching", "note": f"Minimum-weight perfect matching on them, weight {wm} ≤ OPT/2 = {opt / 2:g}."},
        {"show": "circuit", "note": f"Tree + matching has all degrees even: Euler circuit {' '.join(map(str, circuit))}, length {w_tree + wm}."},
        {"show": "tour", "note": f"Shortcut: tour {' '.join(map(str, ch_tour))}, length {length(ch_tour, dist)} ≤ {w_tree} + {wm} = {w_tree + wm}. Optimum {opt}."},
    ]
    return [
        {"title": f"{title}: double tree", **common, "walk": walk, "tourlist": dt_tour, "algo": "double tree", "states": dt_states},
        {"title": f"{title}: Christofides", **common, "odd": odd, "matching": [list(e) for e in matching], "w_matching": wm,
         "circuit": circuit, "tourlist": ch_tour, "algo": "Christofides", "states": ch_states},
    ]


def pick_eight():
    """An eight-point instance where Christofides beats the double tree and the matching has choices."""
    for seed in range(200):
        pts, dist = random_points(8, seed)
        dt, _ = L.double_tree(dist)
        ch, _, _ = L.christofides(dist)
        if len(L.odd_vertices(8, L.prim(dist))) >= 4 and length(ch, dist) < length(dt, dist) - 15:
            return seed, pts, dist
    raise RuntimeError("no instance found")


def data():
    pts6, d6 = six_points()
    seed, pts8, d8 = pick_eight()
    return {"setcover": set_cover(),
            "tsp": tsp_run("six points (the deck's)", pts6, d6) + tsp_run(f"eight random points (seed {seed})", pts8, d8)}
