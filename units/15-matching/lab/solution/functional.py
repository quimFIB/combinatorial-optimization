"""Unit 15 lab — matching.  REFERENCE SOLUTION, functional.

Hopcroft–Karp and Gale–Shapley are unfolds over immutable matchings. König's
cover is a reachability fixpoint. (This Hopcroft–Karp augments one shortest
path per round rather than a maximal set per phase: the same answer, O(VE)
instead of O(E√V).) The Hungarian method is a fold over rows; each row is an
unfold growing a shortest-path tree with the potentials u, v as immutable tuples.

Step 6 (blossom) is the one place the functional reference reuses the
imperative code: the contraction bookkeeping of Edmonds' algorithm is
inherently a mutable union-find over bases, and a persistent rewrite would
obscure rather than clarify it. The lab sheet says so.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import toolz as tz
from itertools import takewhile

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def augmenting_path(nl, adj, match_l, match_r):
    """A shortest augmenting path as a list of (l, r) edges, or None (BFS over layers)."""
    free = tuple(l for l in range(nl) if l not in match_l)

    def grow(state):
        parent, frontier, found = state
        if found is not None or not frontier:
            return state
        steps = [(l, r) for l in frontier for r in adj[l]]
        end = next(((l, r) for l, r in steps if r not in match_r), None)
        if end is not None:
            return parent, frontier, end
        nxt = {match_r[r]: (l, r) for l, r in steps if match_r[r] not in parent}
        return {**parent, **nxt}, tuple(dict.fromkeys(nxt)), None

    parent, _, end = next(st for st in tz.iterate(grow, ({l: None for l in free}, free, None))
                         if st[2] is not None or not st[1])
    if end is None:
        return None
    back = takewhile(lambda e: e is not None, tz.iterate(lambda e: parent[e[0]], end))
    return list(back)


def hopcroft_karp(nl, nr, edges):
    adj = tz.groupby(0, edges)
    adj = {l: [r for _, r in adj.get(l, [])] for l in range(nl)}

    def step(state):
        match_l, done = state
        match_r = {r: l for l, r in match_l.items()}
        path = augmenting_path(nl, adj, match_l, match_r)
        if path is None:
            return match_l, True
        # path edges (l, r) alternate: each r becomes matched to its l
        updated = {**match_l, **dict(path)}
        return updated, False

    return next(st for st in tz.iterate(step, ({}, False)) if st[1])[0]


# ---------------------------------------------------------------- step 2 ---

def konig_cover(nl, nr, edges, matching):
    match_r = {r: l for l, r in matching.items()}

    def grow(state):
        reach_l, reach_r = state
        new_r = {r for l, r in edges if l in reach_l and matching.get(l) != r}
        new_l = {match_r[r] for r in new_r if r in match_r}
        return reach_l | new_l, reach_r | new_r

    start = (frozenset(l for l in range(nl) if l not in matching), frozenset())
    fixpoint = next(b for a, b in tz.sliding_window(2, tz.iterate(grow, start)) if a == b)
    return set(range(nl)) - set(fixpoint[0]), set(fixpoint[1])


# ---------------------------------------------------------------- step 3 ---

def hungarian(cost):
    """The O(n^3) Hungarian method with immutable state: a fold over rows; each row
    runs an unfold that grows a shortest-path tree over columns (updating the
    potentials u, v by the minimum reduced cost delta), then an unfold that flips
    the alternating path back to the root. Columns and rows are 1-based inside,
    with index 0 as the virtual root."""
    n = len(cost)
    idx = range(n + 1)

    def add_row(state, i):
        u, v, p = state
        start = dict(u=u, v=v, p=tuple(i if j == 0 else p[j] for j in idx), way=(0,) * (n + 1),
                     minv=(INF,) * (n + 1), used=(False,) * (n + 1), j0=0, done=False)

        def grow(st):
            used = tuple(True if j == st["j0"] else x for j, x in enumerate(st["used"]))
            i0 = st["p"][st["j0"]]
            cand = {j: cost[i0 - 1][j - 1] - st["u"][i0] - st["v"][j] for j in range(1, n + 1) if not used[j]}
            improve = {j: c for j, c in cand.items() if c < st["minv"][j]}
            minv = tuple(improve.get(j, x) for j, x in enumerate(st["minv"]))
            way = tuple(st["j0"] if j in improve else x for j, x in enumerate(st["way"]))
            delta, j1 = min((minv[j], j) for j in range(1, n + 1) if not used[j])
            u2 = tuple(x + sum(delta for j in idx if used[j] and st["p"][j] == r) for r, x in enumerate(st["u"]))
            v2 = tuple(x - delta if used[j] else x for j, x in enumerate(st["v"]))
            minv2 = tuple(x if used[j] else x - delta for j, x in enumerate(minv))
            return dict(st, u=u2, v=v2, minv=minv2, way=way, used=used, j0=j1, done=st["p"][j1] == 0)

        tree = next(st for st in tz.iterate(grow, start) if st["done"])

        def flip(fs):
            p, j0 = fs
            j1 = tree["way"][j0]
            return tuple(p[j1] if j == j0 else x for j, x in enumerate(p)), j1

        p_final = next(fs for fs in tz.iterate(flip, (tree["p"], tree["j0"])) if fs[1] == 0)[0]
        return tree["u"], tree["v"], p_final

    u, v, p = tz.reduce(add_row, range(1, n + 1), ((0,) * (n + 1), (0,) * (n + 1), (0,) * (n + 1)))
    assign = [next(j - 1 for j in range(1, n + 1) if p[j] == i) for i in range(1, n + 1)]
    return assign, sum(cost[i][assign[i]] for i in range(n)), list(u[1:]), list(v[1:])


# ---------------------------------------------------------------- step 4 ---

def certify_assignment(cost, assign, u, v, tol=1e-9):
    n = len(cost)
    return (sorted(assign) == list(range(n))
            and all(u[i] + v[j] <= cost[i][j] + tol for i in range(n) for j in range(n))
            and all(abs(u[i] + v[assign[i]] - cost[i][assign[i]]) <= tol for i in range(n)))


# ---------------------------------------------------------------- step 5 ---

def gale_shapley(proposer_prefs, receiver_prefs):
    n = len(proposer_prefs)
    rank = [{p: k for k, p in enumerate(prefs)} for prefs in receiver_prefs]

    def step(state):
        holder, next_choice, free = state
        p, rest = free[0], free[1:]
        r = proposer_prefs[p][next_choice[p]]
        nc = tuple(k + 1 if q == p else k for q, k in enumerate(next_choice))
        current = holder.get(r)
        if current is None:
            return {**holder, r: p}, nc, rest
        if rank[r][p] < rank[r][current]:
            return {**holder, r: p}, nc, rest + (current,)
        return holder, nc, rest + (p,)

    holder, _, _ = next(st for st in tz.iterate(step, ({}, (0,) * n, tuple(range(n)))) if not st[2])
    return {p: r for r, p in holder.items()}


def is_stable(proposer_prefs, receiver_prefs, matching):
    partner_of_r = {r: p for p, r in matching.items()}
    prefers = lambda r, a, b: receiver_prefs[r].index(a) < receiver_prefs[r].index(b)
    blocking = ((p, r) for p, prefs in enumerate(proposer_prefs)
                for r in takewhile(lambda r, p=p: r != matching[p], prefs)
                if prefers(r, p, partner_of_r[r]))
    return next(blocking, None) is None


# ---------------------------------------------------------------- step 6 (stretch) ---

def _imperative():
    path = Path(__file__).with_name("lab.py")
    name = "_unit15_imperative_reference"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


def blossom(n, edges):
    return _imperative().blossom(n, edges)
