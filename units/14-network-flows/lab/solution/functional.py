"""Unit 14 lab — network flows.  REFERENCE SOLUTION, functional.

Residual capacities live in an immutable tuple indexed like the imperative
version (arc k = edges 2k forward, 2k+1 backward); every augmentation returns a
new tuple. Each algorithm is an unfold over its state. This costs O(m) per push,
which is fine at lab sizes and makes the invariants easy to read.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, replace
from functools import reduce
from itertools import takewhile

import toolz as tz


@dataclass(frozen=True)
class Net:
    n: int
    to: tuple
    cost: tuple
    adj: tuple                     # adj[u] = edge ids leaving u
    original: tuple


def build(n, arcs):
    to = tuple(x for u, v, *_ in arcs for x in (v, u))
    cost = tuple(x for _, _, _, *rest in arcs for w in [rest[0] if rest else 0] for x in (w, -w))
    tail = tuple(x for u, v, *_ in arcs for x in (u, v))
    adj = tuple(tuple(e for e in range(len(to)) if tail[e] == u) for u in range(n))
    caps = tuple(x for _, _, c, *_ in arcs for x in (c, 0))
    return Net(n, to, cost, adj, tuple(c for _, _, c, *_ in arcs)), caps


def push(caps, e, amount):
    return tuple(c - amount if i == e else c + amount if i == e ^ 1 else c for i, c in enumerate(caps))


def flows(net, caps):
    return [net.original[k] - caps[2 * k] for k in range(len(net.original))]


def bfs_parents(net, caps, s):
    """{node: edge used to reach it} for everything reachable from s in the residual graph."""
    def grow(state):
        parent, frontier = state
        new = {net.to[e]: e for u in frontier for e in net.adj[u]
               if caps[e] > 0 and net.to[e] not in parent}
        nxt = tuple(dict.fromkeys(new))
        return {**parent, **{v: new[v] for v in nxt}}, nxt

    layers = takewhile(lambda st: st[1], tz.iterate(grow, ({s: None}, (s,))))
    return tz.last(layers)[0]


def path_edges(net, parent, t):
    return list(takewhile(lambda e: e is not None,
                          tz.iterate(lambda e: parent[net.to[e ^ 1]], parent[t])))


# ---------------------------------------------------------------- step 1 ---

def edmonds_karp(n, arcs, s, t):
    net, caps0 = build(n, arcs)

    def augment(state):
        caps, value, done = state
        parent = bfs_parents(net, caps, s)
        if t not in parent:
            return caps, value, True
        path = path_edges(net, parent, t)
        amount = min(caps[e] for e in path)
        return reduce(lambda c, e: push(c, e, amount), path, caps), value + amount, False

    caps, value, _ = next(st for st in tz.iterate(augment, (caps0, 0, False)) if st[2])
    return value, flows(net, caps)


def min_cut(n, arcs, flow, s):
    edges = [(u, v) for (u, v, c, *_), f in zip(arcs, flow) if f < c] + \
            [(v, u) for (u, v, c, *_), f in zip(arcs, flow) if f > 0]
    adj = tz.groupby(0, edges)

    def grow(state):
        seen, frontier = state
        new = tuple(dict.fromkeys(v for u in frontier for _, v in adj.get(u, ()) if v not in seen))
        return seen | set(new), new

    return tz.last(takewhile(lambda st: st[1], tz.iterate(grow, ({s}, (s,)))))[0]


# ---------------------------------------------------------------- step 2 ---

def dinic(n, arcs, s, t):
    net, caps0 = build(n, arcs)

    def levels(caps):
        parent = bfs_parents(net, caps, s)
        depth = {s: 0}
        for v in parent:                                   # parents precede children in BFS order
            if v != s:
                depth[v] = depth[net.to[parent[v] ^ 1]] + 1
        return depth

    def blocking_path(caps, depth):
        """One s-t path along level-increasing residual edges (DFS), or None."""
        def search(u, visited):
            if u == t:
                return []
            for e in net.adj[u]:
                v = net.to[e]
                if caps[e] > 0 and depth.get(v) == depth[u] + 1 and v not in visited:
                    rest = search(v, visited | {v})
                    if rest is not None:
                        return [e] + rest
            return None

        return search(s, frozenset({s}))

    def phase(state):
        caps, value, done = state
        depth = levels(caps)
        if t not in depth:
            return caps, value, True

        def saturate(st):
            c, v, stop = st
            path = blocking_path(c, depth)
            if path is None:
                return c, v, True
            amount = min(c[e] for e in path)
            return reduce(lambda cc, e: push(cc, e, amount), path, c), v + amount, False

        caps2, value2, _ = next(st for st in tz.iterate(saturate, (caps, value, False)) if st[2])
        return caps2, value2, False

    caps, value, _ = next(st for st in tz.iterate(phase, (caps0, 0, False)) if st[2])
    return value, flows(net, caps)


# ---------------------------------------------------------------- step 3 ---

@dataclass(frozen=True)
class PR:
    caps: tuple
    height: tuple
    excess: tuple
    active: tuple


def push_relabel(n, arcs, s, t):
    net, caps0 = build(n, arcs)
    source_edges = [e for e in net.adj[s] if caps0[e] > 0]
    caps1 = reduce(lambda c, e: push(c, e, caps0[e]), source_edges, caps0)
    excess1 = tuple(sum(caps0[e] for e in source_edges if net.to[e] == v) - (sum(caps0[e] for e in source_edges) if v == s else 0)
                    for v in range(n))
    active1 = tuple(dict.fromkeys(net.to[e] for e in source_edges if net.to[e] not in (s, t)))
    start = PR(caps1, tuple(n if v == s else 0 for v in range(n)), excess1, active1)

    def discharge(st: PR) -> PR:
        u, rest = st.active[0], st.active[1:]
        admissible = next((e for e in net.adj[u]
                           if st.caps[e] > 0 and st.height[u] == st.height[net.to[e]] + 1), None)
        if admissible is None:
            h = 1 + min(st.height[net.to[e]] for e in net.adj[u] if st.caps[e] > 0)
            return replace(st, height=tuple(h if i == u else x for i, x in enumerate(st.height)))
        v = net.to[admissible]
        amount = min(st.excess[u], st.caps[admissible])
        excess = tuple(x - amount if i == u else x + amount if i == v else x for i, x in enumerate(st.excess))
        joins = (v,) if v not in (s, t) and st.excess[v] == 0 else ()
        still = (u,) if excess[u] > 0 else ()
        return PR(push(st.caps, admissible, amount), st.height, excess, still + rest + joins)

    final = next(st for st in tz.iterate(discharge, start) if not st.active)
    return final.excess[t], flows(net, final.caps)


# ---------------------------------------------------------------- step 4 ---

def min_cost_flow(n, arcs, s, t, demand):
    net, caps0 = build(n, arcs)
    INF = float("inf")

    def relax(pot, _):
        return tuple(min([pot[v]] + [pot[net.to[e ^ 1]] + net.cost[e] for e in range(len(net.to))
                                     if net.to[e] == v and caps0[e] > 0 and pot[net.to[e ^ 1]] < INF])
                     for v in range(n))

    pot0 = reduce(relax, range(n - 1), tuple(0 if v == s else INF for v in range(n)))
    pot0 = tuple(p if p < INF else 0 for p in pot0)

    def dijkstra(caps, pot):
        def pop(state):
            dist, prev, heap, _ = state
            if not heap:
                return dist, prev, heap, True
            (d, u), heap = heap[0], heap[1:]
            if d > dist[u]:
                return dist, prev, heap, False
            better = [(d + net.cost[e] + pot[u] - pot[net.to[e]], net.to[e], e) for e in net.adj[u]
                      if caps[e] > 0 and d + net.cost[e] + pot[u] - pot[net.to[e]] < dist[net.to[e]]]
            dist = reduce(lambda dd, b: {**dd, b[1]: min(dd[b[1]], b[0])}, better, dist)
            prev = reduce(lambda pp, b: {**pp, b[1]: b[2]} if dist[b[1]] == b[0] else pp, better, prev)
            return dist, prev, tuple(sorted(heap + tuple((b[0], b[1]) for b in better))), False

        start = ({v: (0 if v == s else INF) for v in range(n)}, {}, ((0, s),), False)
        dist, prev, _, _ = next(st for st in tz.iterate(pop, start) if st[3])
        return dist, prev

    def step(state):
        caps, pot, sent, cost, status = state
        if sent >= demand:
            return caps, pot, sent, cost, "done"
        dist, prev = dijkstra(caps, pot)
        if dist[t] == INF:
            return caps, pot, sent, cost, "infeasible"
        pot = tuple(p + dist[v] if dist[v] < INF else p for v, p in enumerate(pot))
        path = path_edges(net, {**prev, s: None}, t)
        amount = min([demand - sent] + [caps[e] for e in path])
        caps = reduce(lambda c, e: push(c, e, amount), path, caps)
        return caps, pot, sent + amount, cost + amount * sum(net.cost[e] for e in path), None

    caps, _, _, cost, status = next(st for st in tz.iterate(step, (caps0, pot0, 0, 0, None)) if st[4])
    return None if status == "infeasible" else (cost, flows(net, caps))


# ---------------------------------------------------------------- step 5 ---

def project_selection(profit, requires, max_flow=dinic):
    k = len(profit)
    s, t = k, k + 1
    INF = sum(abs(p) for p in profit) + 1
    arcs = ([(s, p, w) for p, w in enumerate(profit) if w > 0]
            + [(p, t, -w) for p, w in enumerate(profit) if w < 0]
            + [(p, q, INF) for p, q in requires])
    value, flow = max_flow(k + 2, arcs, s, t)
    side = min_cut(k + 2, arcs, flow, s)
    return sum(w for w in profit if w > 0) - value, {p for p in range(k) if p in side}
