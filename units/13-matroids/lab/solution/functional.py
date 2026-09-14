"""Unit 13 lab — matroids.  REFERENCE SOLUTION, functional.

Oracles are closures. Greedy is a fold over the sorted ground set. The axiom
checker is `next` over generators of violations. Intersection is an unfold over
common independent sets, each step a BFS for a shortest augmenting path.
"""

from __future__ import annotations

from collections import Counter
from functools import reduce
from itertools import chain, combinations, takewhile

import toolz as tz

from colib.polyhedra import rank


# ---------------------------------------------------------------- step 1 ---

def graphic(n_vertices, edges):
    def independent(S):
        chosen = [edges[e] for e in S]

        def union(labels, edge):
            if labels is None:
                return None
            u, v = edge
            if labels[u] == labels[v]:
                return None                                  # a cycle
            old, new = labels[u], labels[v]
            return tuple(new if lab == old else lab for lab in labels)

        return reduce(union, chosen, tuple(range(n_vertices))) is not None
    return independent


def uniform(k):
    return lambda S: len(set(S)) <= k


def partition(block_of, capacity):
    return lambda S: all(c <= capacity[b] for b, c in Counter(block_of[e] for e in S).items())


def linear(vectors):
    return lambda S: (not S) or rank([vectors[e] for e in S]) == len(set(S))


# ---------------------------------------------------------------- step 2 ---

def greedy(n, weight, independent):
    order = sorted(range(n), key=lambda e: (-weight[e], e))
    positive = takewhile(lambda e: weight[e] > 0, order)
    return sorted(reduce(lambda chosen, e: chosen + [e] if independent(chosen + [e]) else chosen, positive, []))


# ---------------------------------------------------------------- step 3 ---

def matroid_witness(n, independent):
    if not independent([]):
        return ("empty",)
    indep = [frozenset(S) for k in range(n + 1) for S in combinations(range(n), k) if independent(S)]
    family = set(indep)
    hereditary = (("hereditary", tuple(sorted(S)), tuple(sorted(S - {e})))
                  for S in indep for e in S if S - {e} not in family)
    exchange = (("exchange", tuple(sorted(A)), tuple(sorted(B)))
                for A in indep for B in indep
                if len(A) < len(B) and not any((A | {b}) in family for b in B - A))
    return next(chain(hereditary, exchange), None)


# ---------------------------------------------------------------- step 4 ---

def shortest_augmenting_path(n, I, indep1, indep2):
    out = [y for y in range(n) if y not in I]
    sources = [y for y in out if indep1(sorted(I | {y}))]
    sinks = {y for y in out if indep2(sorted(I | {y}))}
    arcs = [(x, y) for x in I for y in out if indep1(sorted((I - {x}) | {y}))] + \
           [(y, x) for x in I for y in out if indep2(sorted((I - {x}) | {y}))]
    adj = tz.groupby(0, arcs)

    def layer(state):
        parent, frontier = state
        nxt = {w: v for v in frontier for _, w in adj.get(v, ()) if w not in parent}
        return {**parent, **nxt}, tuple(dict.fromkeys(nxt))

    start = ({s: None for s in sources}, tuple(sources))
    layers = list(takewhile(lambda st: st[1], tz.iterate(layer, start)))
    reached = next(((v, st[0]) for st in layers for v in st[1] if v in sinks), None)
    if reached is None:
        return None
    end, parent = reached
    return list(takewhile(lambda v: v is not None, tz.iterate(lambda v: parent[v], end)))


def intersection(n, indep1, indep2):
    def step(I):
        path = shortest_augmenting_path(n, I, indep1, indep2)
        return None if path is None else I ^ frozenset(path)

    states = list(takewhile(lambda I: I is not None, tz.iterate(lambda I: step(I) if I is not None else None,
                                                               frozenset())))
    return sorted(states[-1])


# ---------------------------------------------------------------- step 5 ---

def greedy_coverage(sets, k):
    def pick(state, _):
        chosen, covered = state
        candidates = [i for i in range(len(sets)) if i not in chosen]
        if not candidates:
            return state
        best = max(candidates, key=lambda i: (len(set(sets[i]) - covered), -i))
        return chosen + [best], covered | set(sets[best])

    return reduce(pick, range(k), ([], set()))[0]
