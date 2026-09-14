"""Unit 00 lab — models, instances, and an oracle you trust.  REFERENCE SOLUTION.

Look here only after the hint ladder in HINTS.org has run out.
"""

from __future__ import annotations

from colib import Result, VertexCover


# ---------------------------------------------------------------- step 1 ---
# Model two problems as (predicate, objective) over their spaces.

def vertex_cover_feasible(inst, x) -> bool:
    return all(x[u] == 1 or x[v] == 1 for u, v in inst.edges)


def vertex_cover_objective(inst, x) -> int:
    return sum(x)


def bin_packing_feasible(inst, x) -> bool:
    load: dict[int, int] = {}
    for item, b in enumerate(x):
        load[b] = load.get(b, 0) + inst.sizes[item]
    return all(total <= inst.capacity for total in load.values())


def bin_packing_objective(inst, x) -> int:
    return len(set(x))


# ---------------------------------------------------------------- step 2 ---

def set_partitions(n: int):
    if n == 0:
        yield ()
        return
    a = [0] * n

    def extend(i, top):
        if i == n:
            yield tuple(a)
            return
        for block in range(top + 2):      # an existing block, or open block top+1
            a[i] = block
            yield from extend(i + 1, max(top, block))

    yield from extend(1, 0)


# ---------------------------------------------------------------- step 3 ---

def brute_force(problem) -> Result:
    best_val = best_sol = None
    feasible = examined = 0
    for x in problem.space():
        examined += 1
        if not problem.is_feasible(x):
            continue
        feasible += 1
        v = problem.objective(x)
        if (best_val is None
                or (problem.sense == "min" and v < best_val)
                or (problem.sense == "max" and v > best_val)):
            best_val, best_sol = v, x
    return Result(best_val, best_sol, feasible, examined)


# ---------------------------------------------------------------- step 4 ---

def matching_lower_bound(inst: VertexCover, matching) -> int:
    edges = {frozenset(e) for e in inst.edges}
    used = set()
    for u, v in matching:
        if frozenset((u, v)) not in edges:
            raise ValueError(f"({u}, {v}) is not an edge of the graph")
        if u in used or v in used:
            raise ValueError(f"({u}, {v}) shares an endpoint with an earlier edge")
        used |= {u, v}
    return len(matching)


def certify_vertex_cover(inst: VertexCover, cover, matching) -> bool:
    try:
        lb = matching_lower_bound(inst, matching)
    except ValueError:
        return False
    return inst.is_feasible(cover) and sum(cover) == lb


# ---------------------------------------------------------------- step 5 ---

def plausible_vertex_cover(inst: VertexCover):
    """Repeatedly take a vertex of maximum remaining degree."""
    remaining = set(inst.edges)
    x = [0] * inst.n
    while remaining:
        deg = [0] * inst.n
        for u, v in remaining:
            deg[u] += 1
            deg[v] += 1
        best = max(range(inst.n), key=deg.__getitem__)
        x[best] = 1
        remaining = {(u, v) for u, v in remaining if best not in (u, v)}
    return tuple(x)
