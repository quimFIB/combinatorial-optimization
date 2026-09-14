"""Unit 23 lab — combinatorial approximation algorithms.  REFERENCE SOLUTION, functional.

Greedy algorithms are unfolds: a state (what is covered, which centres are chosen, which vertices are in the
tree) and a step that makes one greedy choice. Each is written as tz.iterate over immutable states, taken
until the stopping condition. Hierholzer's algorithm keeps its stack and edge set as persistent values too.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import chain
from math import lcm

import toolz as tz

from colib.approx import min_weight_perfect_matching
from colib.problems import SetCover


def _until(pred, step, state):
    return next(s for s in tz.iterate(step, state) if pred(s))


# ---------------------------------------------------------------- step 1 ---

def greedy_set_cover(sc):
    def ratio_key(i, uncovered):
        new = len(sc.sets[i] & uncovered)
        return (Fraction(sc.costs[i], new), i)

    def step(state):
        uncovered, chosen, price = state
        candidates = [i for i in range(sc.n) if sc.sets[i] & uncovered]
        if not candidates:
            raise ValueError("instance cannot be covered")
        best = min(candidates, key=lambda i: ratio_key(i, uncovered))
        paid = Fraction(sc.costs[best], len(sc.sets[best] & uncovered))
        return (uncovered - sc.sets[best], chosen | {best},
                tz.merge(price, {e: paid for e in sc.sets[best] & uncovered}))

    _, chosen, price = _until(lambda s: not s[0], step, (frozenset(range(sc.universe)), frozenset(), {}))
    return [int(i in chosen) for i in range(sc.n)], [price[e] for e in range(sc.universe)]


def harmonic(k):
    return sum((Fraction(1, i) for i in range(1, k + 1)), Fraction(0))


def greedy_tight_instance(n):
    L = lcm(*range(1, n + 1))
    return SetCover(n, tuple(frozenset({i}) for i in range(n)) + (frozenset(range(n)),),
                    tuple(L // (i + 1) for i in range(n)) + (L + 1,))


# ---------------------------------------------------------------- step 2 ---

def matching_vertex_cover(vc):
    def keep(state, edge):
        matched, matching = state
        u, v = edge
        return (matched, matching) if u in matched or v in matched else (matched | {u, v}, matching + (edge,))

    matched, matching = tz.reduce(keep, vc.edges, (frozenset(), ()))
    return [int(v in matched) for v in range(vc.n)], list(matching)


def k_center(dist, k, first=0):
    n = len(dist)
    nearest = lambda centres: tuple(min(dist[c][v] for c in centres) for v in range(n))
    farthest = lambda near: max(range(n), key=lambda v: (near[v], -v))

    def step(centres):
        return centres + (farthest(nearest(centres)),)

    def done(centres):
        near = nearest(centres)
        return len(centres) == k or near[farthest(near)] == 0

    centres = _until(done, step, (first,))
    near = nearest(centres)
    far = farthest(near)
    return list(centres), near[far], (far if near[far] > 0 else None)


# ---------------------------------------------------------------- step 3 ---

def prim(dist):
    n = len(dist)

    def step(state):
        tree, edges = state
        u, v = min(((u, v) for u in tree for v in range(n) if v not in tree), key=lambda e: dist[e[0]][e[1]])
        return tree | {v}, edges + (tuple(sorted((u, v))),)

    if n <= 1:
        return []
    return sorted(_until(lambda s: len(s[0]) == n, step, (frozenset({0}), ()))[1])


def shortcut(walk):
    return list(tz.unique(walk))


def double_tree(dist):
    tree = prim(dist)
    children = tz.groupby(0, chain(tree, ((v, u) for u, v in tree)))

    def preorder(v, parent):
        kids = sorted(w for _, w in children.get(v, []) if w != parent)
        return [v] + list(chain.from_iterable(preorder(w, v) for w in kids))

    return shortcut(preorder(0, None)), sum(dist[u][v] for u, v in tree)


# ---------------------------------------------------------------- step 4 ---

def odd_vertices(n, edges):
    degree = tz.frequencies(chain.from_iterable(edges))
    return [v for v in range(n) if degree.get(v, 0) % 2]


def euler_circuit(n, edges, start=0):
    incident = tz.groupby(0, [(u, (v, k)) for k, (u, v) in enumerate(edges)] + [(v, (u, k)) for k, (u, v) in enumerate(edges)])

    def step(state):
        stack, unused, circuit = state
        v = stack[-1]
        nxt = next(((u, k) for _, (u, k) in incident.get(v, []) if k in unused), None)
        if nxt is None:
            return stack[:-1], unused, circuit + (v,)
        return stack + (nxt[0],), unused - {nxt[1]}, circuit

    _, _, circuit = _until(lambda s: not s[0], step, ((start,), frozenset(range(len(edges))), ()))
    return list(reversed(circuit))


def christofides(dist):
    n = len(dist)
    tree = prim(dist)
    matching = min_weight_perfect_matching(odd_vertices(n, tree), dist)
    tour = shortcut(euler_circuit(n, tree + matching, 0)) if n > 1 else [0]
    return tour, sum(dist[u][v] for u, v in tree), sum(dist[u][v] for u, v in matching)


# ---------------------------------------------------------------- step 5 ---

def list_scheduling(p, m):
    def assign(state, pj):
        load, machine = state
        i = min(range(m), key=lambda i: (load[i], i))
        return load[:i] + (load[i] + pj,) + load[i + 1:], machine + (i,)

    load, machine = tz.reduce(assign, p, ((0,) * m, ()))
    return max(load), list(machine)


def lpt(p, m):
    order = sorted(range(len(p)), key=lambda j: -p[j])
    makespan, sorted_machine = list_scheduling([p[j] for j in order], m)
    machine_of = dict(zip(order, sorted_machine))
    return makespan, [machine_of[j] for j in range(len(p))]


def list_scheduling_tight(m):
    return [1] * (m * (m - 1)) + [m]


def lpt_tight(m):
    return [t for t in range(2 * m - 1, m, -1) for _ in (0, 1)] + [m] * 3
