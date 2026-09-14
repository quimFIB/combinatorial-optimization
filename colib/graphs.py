"""Random graph families with controlled structure (units 16, 22, 28).

Graphs are (n, edges) with vertices 0..n-1 and edges as sorted pairs (u, v), u < v.
"""

from __future__ import annotations

import random


def random_tree(n: int, seed=0):
    """A uniformly-attached random tree: vertex i joins a random earlier vertex."""
    r = random.Random(seed)
    return n, [(r.randrange(i), i) for i in range(1, n)]


def ktree(n: int, k: int, seed=0):
    """A random k-tree on n >= k + 1 vertices: start from a (k+1)-clique, then each new
    vertex joins all of a random existing k-clique. Treewidth exactly k."""
    r = random.Random(seed)
    base = list(range(min(n, k + 1)))
    edges = {(u, v) for u in base for v in base if u < v}
    cliques = [tuple(c for c in base if c != x) for x in base] if n > k else []
    for v in range(k + 1, n):
        c = r.choice(cliques)
        edges |= {(u, v) for u in c}
        cliques += [tuple(sorted(set(c) - {x} | {v})) for x in c]
    return n, sorted(edges)


def partial_ktree(n: int, k: int, keep: float = 0.7, seed=0):
    """A k-tree with each edge kept independently with probability `keep`: treewidth <= k."""
    r = random.Random(seed + 1_000_003)
    n, edges = ktree(n, k, seed)
    return n, [e for e in edges if r.random() < keep]
