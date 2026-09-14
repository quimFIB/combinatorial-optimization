"""Unit 00 lab — models, instances, and an oracle you trust.  REFERENCE SOLUTION, functional.

The same functions as `lab.py`, written without mutation: predicates,
comprehensions, recursion, and `reduce` where the imperative version keeps a
running state, and toolz for grouping and counting (see FUNCTIONAL.md at the
project root). Checked by the same tests:  uv run co test 00 --solution functional

Look here only after the hint ladder in HINTS.org has run out.
"""

from __future__ import annotations

from dataclasses import replace
from functools import reduce
from itertools import chain

import toolz as tz

from colib import Result, VertexCover


# ---------------------------------------------------------------- step 1 ---

def vertex_cover_feasible(inst, x) -> bool:
    return all(x[u] or x[v] for u, v in inst.edges)


def vertex_cover_objective(inst, x) -> int:
    return sum(x)


def bin_loads(inst, x) -> dict:
    """Total size in each bin: fold the (bin, size) pairs by bin."""
    return tz.reduceby(lambda pair: pair[0], lambda load, pair: load + pair[1],
                       zip(x, inst.sizes), 0)


def bin_packing_feasible(inst, x) -> bool:
    return all(load <= inst.capacity for load in bin_loads(inst, x).values())


def bin_packing_objective(inst, x) -> int:
    return len(set(x))


# ---------------------------------------------------------------- step 2 ---

def set_partitions(n: int):
    """A restricted growth string is a prefix plus one more label: an existing
    block 0..top, or the new block top+1. Recursion on that, lazily chained."""
    def extend(prefix: tuple, top: int):
        if len(prefix) == n:
            return iter((prefix,))
        return chain.from_iterable(extend(prefix + (b,), max(top, b)) for b in range(top + 2))

    return iter(((),)) if n == 0 else extend((0,), 0)


# ---------------------------------------------------------------- step 3 ---

def brute_force(problem) -> Result:
    """One fold over the space. The accumulator is the whole Result."""
    better = (lambda v, best: v < best) if problem.sense == "min" else (lambda v, best: v > best)

    def visit(acc: Result, x) -> Result:
        if not problem.is_feasible(x):
            return replace(acc, examined=acc.examined + 1)
        v = problem.objective(x)
        if acc.value is None or better(v, acc.value):
            return Result(v, x, acc.feasible + 1, acc.examined + 1)
        return replace(acc, feasible=acc.feasible + 1, examined=acc.examined + 1)

    return reduce(visit, problem.space(), Result(None, None, 0, 0))


# ---------------------------------------------------------------- step 4 ---

def is_matching(inst: VertexCover, matching) -> bool:
    edges = frozenset(map(frozenset, inst.edges))
    endpoints = [v for pair in matching for v in pair]
    return (all(frozenset(pair) in edges for pair in matching)
            and len(set(endpoints)) == len(endpoints))


def matching_lower_bound(inst: VertexCover, matching) -> int:
    if not is_matching(inst, matching):
        raise ValueError(f"not a matching of this graph: {matching!r}")
    return len(matching)


def certify_vertex_cover(inst: VertexCover, cover, matching) -> bool:
    return (is_matching(inst, matching)
            and inst.is_feasible(cover)
            and sum(cover) == len(matching))


# ---------------------------------------------------------------- step 5 ---

def plausible_vertex_cover(inst: VertexCover):
    """Take a vertex of maximum remaining degree, recurse on the edges it leaves."""
    def go(remaining: frozenset, chosen: frozenset) -> frozenset:
        if not remaining:
            return chosen
        degree = tz.frequencies(tz.concat(remaining))
        best = max(range(inst.n), key=lambda v: degree.get(v, 0))
        return go(frozenset(e for e in remaining if best not in e), chosen | {best})

    cover = go(frozenset(inst.edges), frozenset())
    return tuple(int(v in cover) for v in range(inst.n))
