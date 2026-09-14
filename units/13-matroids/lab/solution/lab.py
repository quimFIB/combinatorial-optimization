"""Unit 13 lab — matroids and the exact reach of greedy.  REFERENCE SOLUTION, imperative.

An independence system is given by an oracle: independent(S) -> bool for a
subset S (any iterable) of the ground set range(n).
"""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from itertools import combinations

from colib.polyhedra import rank


# ---------------------------------------------------------------- step 1 ---

def graphic(n_vertices, edges):
    """Independence oracle of the graphic matroid: a set of edge indices is
    independent iff those edges form a forest."""
    def independent(S):
        parent = list(range(n_vertices))

        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        for e in S:
            u, v = edges[e]
            ru, rv = find(u), find(v)
            if ru == rv:
                return False
            parent[ru] = rv
        return True
    return independent


def uniform(k):
    return lambda S: len(set(S)) <= k


def partition(block_of, capacity):
    """block_of[e] is e's block; at most capacity[b] elements from block b."""
    def independent(S):
        count = {}
        for e in S:
            b = block_of[e]
            count[b] = count.get(b, 0) + 1
            if count[b] > capacity[b]:
                return False
        return True
    return independent


def linear(vectors):
    """Independent iff the chosen vectors are linearly independent over the rationals."""
    return lambda S: rank([vectors[e] for e in S]) == len(set(S)) if S else True


# ---------------------------------------------------------------- step 2 ---

def greedy(n, weight, independent):
    """Max-weight independent set by the greedy algorithm: consider elements in
    decreasing weight, skip non-positive weights, add when still independent."""
    chosen = []
    for e in sorted(range(n), key=lambda e: (-weight[e], e)):
        if weight[e] <= 0:
            break
        if independent(chosen + [e]):
            chosen.append(e)
    return sorted(chosen)


# ---------------------------------------------------------------- step 3 ---

def matroid_witness(n, independent):
    """None if (range(n), independent) is a matroid; otherwise a witness:
    ("empty",) if the empty set is dependent,
    ("hereditary", S, T) with T a subset of an independent S that is dependent,
    ("exchange", A, B) with A, B independent, |A| < |B|, and no b in B - A
    making A + b independent."""
    if not independent([]):
        return ("empty",)
    indep = [frozenset(S) for k in range(n + 1) for S in combinations(range(n), k) if independent(S)]
    indep_set = set(indep)
    for S in indep:
        for e in S:
            if S - {e} not in indep_set:
                return ("hereditary", tuple(sorted(S)), tuple(sorted(S - {e})))
    for A in indep:
        for B in indep:
            if len(A) < len(B) and not any((A | {b}) in indep_set for b in B - A):
                return ("exchange", tuple(sorted(A)), tuple(sorted(B)))
    return None


# ---------------------------------------------------------------- step 4 ---

def intersection(n, indep1, indep2):
    """A maximum-cardinality set independent in both matroids (augmenting paths
    in the exchange graph)."""
    I = set()
    while True:
        out = sorted(set(range(n)) - I)
        sources = [y for y in out if indep1(sorted(I | {y}))]
        sinks = {y for y in out if indep2(sorted(I | {y}))}
        # exchange graph: x in I -> y outside if I - x + y independent in M1;
        #                 y outside -> x in I if I - x + y independent in M2
        adj = {v: [] for v in range(n)}
        for x in I:
            for y in out:
                J = sorted((I - {x}) | {y})
                if indep1(J):
                    adj[x].append(y)
                if indep2(J):
                    adj[y].append(x)
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
        if end is None:
            return sorted(I)
        path = []
        while end is not None:
            path.append(end)
            end = parent[end]
        I ^= set(path)


# ---------------------------------------------------------------- step 5 ---

def greedy_coverage(sets, k):
    """Pick k sets greedily, each time the one covering the most new elements
    (ties: lowest index). Returns the list of chosen indices, in order."""
    covered, chosen = set(), []
    for _ in range(k):
        best = max((i for i in range(len(sets)) if i not in chosen),
                   key=lambda i: (len(set(sets[i]) - covered), -i), default=None)
        if best is None:
            break
        chosen.append(best)
        covered |= set(sets[best])
    return chosen
