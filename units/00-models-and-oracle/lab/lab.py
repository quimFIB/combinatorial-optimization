"""Unit 00 lab — models, instances, and an oracle you trust.

Fill in the functions marked TODO, one step at a time. Run

    uv run co test 00

after each; a step's tests go from "not started" to ✓. Everything you need
from the library is imported below. Stuck? HINTS.org, one rung at a time.

Any style passes: the tests call your functions and check what they return,
never how. Loops, comprehensions, recursion, `functools.reduce` (a foldl) —
use whichever fits the step. The lab sheet notes which shape each step has,
and FUNCTIONAL.md at the project root maps Haskell names to Python and toolz.
"""

from __future__ import annotations

from colib import BinPacking, Result, VertexCover


# ---------------------------------------------------------------- step 1 ---
# Model two problems as (predicate, objective) over their spaces.
#
# A VertexCover instance has `inst.n` vertices and `inst.edges`, a tuple of
# (u, v) pairs. A candidate x is a 0/1 tuple of length n: x[v] == 1 means v is
# in the cover.
#
# A BinPacking instance has `inst.sizes` and `inst.capacity`. A candidate x is
# a restricted growth string: x[i] is the bin that item i goes in (step 2
# explains why the space is these and not all maps item -> bin).

def vertex_cover_feasible(inst: VertexCover, x) -> bool:
    """True iff every edge has at least one endpoint in the cover."""
    cover_feasible = True
    for u, v in inst.edges:
        cover_feasible = cover_feasible and (x[u] == 1 or x[v] == 1)
    return cover_feasible


def vertex_cover_objective(inst: VertexCover, x) -> int:
    """The number of vertices in the cover."""
    return sum(x)


def bin_packing_feasible(inst: BinPacking, x) -> bool:
    """True iff no bin's total size exceeds the capacity."""
    load = {}
    for item, b in enumerate(x):
        load[b] = load.get(b, 0) + inst.sizes[item]
    return all(total <= inst.capacity for total in load.values())


def bin_packing_objective(inst: BinPacking, x) -> int:
    """The number of bins used."""
    return len(set(x))


# ---------------------------------------------------------------- step 2 ---

def set_partitions(n: int):
    """Every partition of range(n) exactly once, as tuples a of length n.

    Return any iterable: a generator, a list, a lazy `itertools.chain`.

    Use restricted growth strings: a[0] == 0 and a[i] <= 1 + max(a[:i]).
    For n = 3 that is (0,0,0) (0,0,1) (0,1,0) (0,1,1) (0,1,2) — five, the
    Bell number B(3). For n = 0: a single empty tuple.
    """
    if n == 0:
        yield ()
        return
    # Element n-1 either joins one of the existing blocks 0..max(a) of a
    # partition of the first n-1 elements, or opens block max(a)+1 by itself.
    for a in set_partitions(n - 1):
        new_block = max(a) + 1 if a else 0
        for label in range(new_block + 1):
            yield a + (label,)


# ---------------------------------------------------------------- step 3 ---

def brute_force(problem) -> Result:
    """Solve any colib problem exactly by walking problem.space().

    Return Result(value, solution, feasible, examined):
      value     the best objective (respecting problem.sense), or None if no
                candidate is feasible
      solution  a candidate achieving it (the first one found), or None
      feasible  how many candidates were feasible
      examined  how many candidates you looked at
    """
    if problem.sense == "min":
        better = lambda a, b: a < b
    else:
        better = lambda a, b: a > b

    value, solution = None, None
    feasible = examined = 0
    for x in problem.space():
        examined += 1
        if not problem.is_feasible(x):
            continue
        feasible += 1
        v = problem.objective(x)
        # Strict comparison keeps the first optimum found.
        if value is None or better(v, value):
            value, solution = v, x
    return Result(value, solution, feasible, examined)


# ---------------------------------------------------------------- step 4 ---
# "Here is a cover of size k" is a claim anyone can check. "Nothing smaller
# exists" needs a different kind of object. For vertex cover, a matching is one:
# every cover must contain a distinct vertex from each matched edge.

def matching_lower_bound(inst: VertexCover, matching) -> int:
    """Validate `matching` (a list of (u, v) edges) and return its size.

    Raise ValueError if some pair is not an edge of the graph (in either
    orientation) or two pairs share an endpoint.
    """
    edges = {frozenset(e) for e in inst.edges}
    used = set()
    for u, v in matching:
        if frozenset((u, v)) not in edges:
            raise ValueError(f"({u}, {v}) is not an edge")
        if u in used or v in used:
            raise ValueError(f"({u}, {v}) shares an endpoint with an earlier pair")
        used.update((u, v))
    return len(matching)


def certify_vertex_cover(inst: VertexCover, cover, matching) -> bool:
    """True iff `cover` is a feasible cover AND `matching` is a valid matching
    of the same size — which together prove the cover optimal. False otherwise
    (including when the matching is invalid)."""
    try:
        size = matching_lower_bound(inst, matching)
    except ValueError:
        return False
    return vertex_cover_feasible(inst, cover) and vertex_cover_objective(inst, cover) == size


# ---------------------------------------------------------------- step 5 ---

def plausible_vertex_cover(inst: VertexCover):
    """Write a vertex cover heuristic you would *believe* is optimal.

    It must always return a feasible cover (a 0/1 tuple). It must not be
    optimal — the test runs the harness and passes only if the harness finds
    the instance where it is wrong. The classic trap: keep taking the vertex
    that covers the most uncovered edges.
    """
    # Greedy by degree: take the vertex touching the most uncovered edges,
    # drop those edges, repeat until none are left.
    x = [0] * inst.n
    remaining = list(inst.edges)
    while remaining:
        degree = [0] * inst.n
        for u, v in remaining:
            degree[u] += 1
            degree[v] += 1
        best = max(range(inst.n), key=lambda w: degree[w])
        x[best] = 1
        remaining = [(u, v) for u, v in remaining if best not in (u, v)]
    return tuple(x)
