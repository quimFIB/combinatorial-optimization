"""Unit 13's recorded matroid runs, for units/13-matroids/explore.html.

Greedy is a logged copy of the reference `greedy`, run with the reference oracles: `graphic` on
the deck's five-vertex graph (Kruskal), and matchings of the 2-3-2 path written as the
intersection of two reference `partition` oracles (a matching uses each vertex at most once).
Each run's result is checked against the reference `greedy`, its optimum found by brute force,
and `matroid_witness` says whether the system is a matroid. Intersection is a logged copy of the
reference `intersection`, started from the deck's stuck set {e1}; its final size is checked
against the reference.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations

from colib import ref

L = ref.unit("13")

# ---------------------------------------------------------------- greedy
FOREST_N = 5
FOREST_EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 4), (2, 4)]
FOREST_W = [4, 1, 3, 2, 5, 6, 2]

PATH_N = 4
PATH_EDGES = [(0, 1), (1, 2), (2, 3)]
PATH_W = [2, 3, 2]


def name(edges, e):
    return f"{edges[e][0]}{edges[e][1]}"


def matching_oracle(edges):
    """Matchings of a bipartite graph: at most one edge at each even and at each odd vertex."""
    even = L.partition([u if u % 2 == 0 else v for u, v in edges], {v: 1 for v in range(0, 2 * len(edges) + 2, 2)})
    odd = L.partition([u if u % 2 == 1 else v for u, v in edges], {v: 1 for v in range(1, 2 * len(edges) + 2, 2)})
    return lambda S: even(S) and odd(S)


def forest_path(n, edges, chosen, a, b):
    """The chosen edges joining a to b (the cycle a new edge would close)."""
    adj = {v: [] for v in range(n)}
    for e in chosen:
        u, v = edges[e]
        adj[u].append((v, e))
        adj[v].append((u, e))
    parent = {a: None}
    queue = deque([a])
    while queue:
        u = queue.popleft()
        for v, e in adj[u]:
            if v not in parent:
                parent[v] = (u, e)
                queue.append(v)
    path, v = [], b
    while parent[v] is not None:
        u, e = parent[v]
        path.append(e)
        v = u
    return sorted(path)


def greedy_states(kind):
    if kind == "forest":
        n_v, edges, weight = FOREST_N, FOREST_EDGES, FOREST_W
        independent = L.graphic(n_v, edges)
    else:
        n_v, edges, weight = PATH_N, PATH_EDGES, PATH_W
        independent = matching_oracle(edges)
    n = len(edges)
    chosen, states = [], []

    def snap(note, consider=None, verdict=None, blocking=(), best=None, explain=""):
        states.append({"chosen": sorted(chosen), "consider": consider, "verdict": verdict, "blocking": sorted(blocking),
                       "value": sum(weight[e] for e in chosen), "best": best, "note": note, "explain": explain})

    what = "a forest" if kind == "forest" else "a matching"
    snap("sort the edges by weight, heaviest first",
         explain=f"Take each edge if the chosen edges stay {what}; the oracle is the only thing that knows the graph's rules.")
    for e in sorted(range(n), key=lambda e: (-weight[e], e)):
        if weight[e] <= 0:
            break
        if independent(chosen + [e]):
            chosen.append(e)
            snap(f"edge {name(edges, e)} (weight {weight[e]}): still {what}, take it", consider=e, verdict="take",
                 explain=f"Chosen weight so far {sum(weight[x] for x in chosen)}.")
        else:
            u, v = edges[e]
            if kind == "forest":
                block = forest_path(n_v, edges, chosen, u, v)
                why = f"it would close a cycle with {', '.join(name(edges, x) for x in block)}"
            else:
                block = [x for x in chosen if set(edges[x]) & {u, v}]
                why = f"it shares a vertex with {', '.join(name(edges, x) for x in block)}"
            snap(f"edge {name(edges, e)} (weight {weight[e]}): skip, {why}", consider=e, verdict="skip", blocking=block,
                 explain="Once skipped, an edge is never reconsidered.")
    assert sorted(chosen) == L.greedy(n, weight, independent), "greedy trace disagrees with the reference"
    best = max((S for k in range(n + 1) for S in combinations(range(n), k) if independent(list(S))),
               key=lambda S: sum(weight[e] for e in S))
    best_value = sum(weight[e] for e in best)
    value = sum(weight[e] for e in chosen)
    witness = L.matroid_witness(n, independent)
    if witness is None:
        assert value == best_value
        explain = (f"Brute force over all {2 ** n} edge sets agrees: {best_value} is the best. "
                   "Forests form a matroid, and on a matroid greedy is always optimal.")
        snap(f"greedy weight {value}: optimal", best=list(best), explain=explain)
    else:
        kind_w, A, B = witness
        assert kind_w == "exchange" and value < best_value
        explain = (f"The best matching is {', '.join(name(edges, e) for e in best)}, weight {best_value}. "
                   f"Matchings are not a matroid: {{{', '.join(name(edges, e) for e in A)}}} is smaller than "
                   f"{{{', '.join(name(edges, e) for e in B)}}}, yet no edge of the second can be added to the first. "
                   "That failed exchange is exactly where greedy goes wrong.")
        snap(f"greedy weight {value}, but {best_value} is possible", best=list(best), explain=explain)
    return states


# ---------------------------------------------------------------- intersection
# e0 = l0 r0, e1 = l1 r0, e2 = l1 r1; M1: one edge per left vertex, M2: one per right vertex
BI_EDGES = [(0, 0), (1, 0), (1, 1)]
START = {1}


def intersection_states():
    n = len(BI_EDGES)
    m1 = L.partition([l for l, _ in BI_EDGES], {0: 1, 1: 1})
    m2 = L.partition([r for _, r in BI_EDGES], {0: 1, 1: 1})
    I = set(START)
    states = []

    def snap(note, sources=(), sinks=(), arcs=(), path=(), explain=""):
        states.append({"I": sorted(I), "sources": sorted(sources), "sinks": sorted(sinks),
                       "arcs": [list(a) for a in arcs], "path": list(path), "note": note, "explain": explain})

    snap("I = {e1}: nothing more fits",
         explain="e0 clashes with e1 at r0, and e2 clashes with it at ℓ1. Adding edges one at a time is stuck at size 1.")
    while True:
        out = sorted(set(range(n)) - I)
        sources = [y for y in out if m1(sorted(I | {y}))]
        sinks = {y for y in out if m2(sorted(I | {y}))}
        if not sources:
            snap("no source: I is a largest common independent set", sources, sinks,
                 explain=f"No edge can be added to I keeping one edge per left vertex, so no path can even start. "
                         f"Size {len(I)}: a perfect matching on 2 + 2 vertices, as large as possible.")
            break
        snap(f"sources {{{', '.join(f'e{y}' for y in sources)}}}, sinks {{{', '.join(f'e{y}' for y in sorted(sinks))}}}",
             sources, sinks,
             explain="A source can be added keeping one edge per left vertex (M1); a sink can be added keeping one edge per right vertex (M2).")
        adj, arcs = {v: [] for v in range(n)}, []
        for x in sorted(I):
            for y in out:
                J = sorted((I - {x}) | {y})
                if m1(J):
                    adj[x].append(y)
                    arcs.append((x, y, 1))
                if m2(J):
                    adj[y].append(x)
                    arcs.append((y, x, 2))
        parent = {s: None for s in sources}
        queue = deque(sources)
        end = None
        while queue:
            v = queue.popleft()
            if v in sinks:
                end = v
                break
            for w in adj[v]:
                if w not in parent:
                    parent[w] = v
                    queue.append(w)
        snap("exchange graph: swap x out and y in", sources, sinks, arcs,
             explain="Arc x → y (M1 side) if I − x + y still has one edge per left vertex; arc y → x (M2 side) if it still has one edge per right vertex.")
        if end is None:
            snap("no path from a source to a sink: I is maximum", sources, sinks, arcs,
                 explain="No exchange sequence grows I; the matroid intersection theorem says I is then as large as possible.")
            break
        path = []
        while end is not None:
            path.append(end)
            end = parent[end]
        path.reverse()
        snap(f"shortest path {' → '.join(f'e{v}' for v in path)}", sources, sinks, arcs, path,
             explain="Breadth-first search from the sources. Alternately it adds an edge, removes one, adds one: the augmenting path of bipartite matching.")
        I ^= set(path)
        snap(f"flip along the path: I = {{{', '.join(f'e{v}' for v in sorted(I))}}}", path=path,
             explain="Edges on the path outside I go in, the ones inside come out. I grows by one and stays independent in both matroids.")
    assert len(I) == len(L.intersection(n, m1, m2)), "intersection trace disagrees with the reference size"
    assert m1(sorted(I)) and m2(sorted(I))
    return states


def data():
    return {
        "forest": {"title": "forests: Kruskal", "n": FOREST_N, "edges": FOREST_EDGES, "weights": FOREST_W,
                   "states": greedy_states("forest")},
        "path": {"title": "matchings on a path", "n": PATH_N, "edges": PATH_EDGES, "weights": PATH_W,
                 "states": greedy_states("path")},
        "intersection": {"title": "matroid intersection, from I = {e1}", "edges": BI_EDGES, "states": intersection_states()},
    }
