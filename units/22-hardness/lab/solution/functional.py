"""Unit 22 lab — reductions and an FPTAS.  REFERENCE SOLUTION, functional.

A reduction is a pure function between instance types, and each solution map is another. The
clause-splitting reduction is a fold that threads the next fresh variable; the value DP is a fold
over items producing a table per item, and reconstruction is an unfold back through the tables.
"""

from __future__ import annotations

import math
from itertools import accumulate, chain

import toolz as tz

from colib.problems import SetCover, VertexCover


# ---------------------------------------------------------------- step 1 ---

def literal_vertex(lit):
    return 2 * (abs(lit) - 1) + (lit < 0)


def sat_to_vertex_cover(nvars, clauses):
    assert all(len(c) == 3 for c in clauses), "3-CNF only"
    corner = lambda j, t: 2 * nvars + 3 * j + t
    variable_edges = [(literal_vertex(v), literal_vertex(-v)) for v in range(1, nvars + 1)]
    triangles = [(corner(j, a), corner(j, b)) for j in range(len(clauses)) for a, b in ((0, 1), (0, 2), (1, 2))]
    links = [tuple(sorted((corner(j, t), literal_vertex(lit)))) for j, c in enumerate(clauses) for t, lit in enumerate(c)]
    return VertexCover(2 * nvars + 3 * len(clauses), tuple(sorted(set(variable_edges + triangles + links)))), \
        nvars + 2 * len(clauses)


def cover_from_assignment(nvars, clauses, assignment):
    true_lit = lambda lit: assignment[abs(lit) - 1] == (lit > 0)
    literals = {literal_vertex(v if assignment[v - 1] else -v) for v in range(1, nvars + 1)}
    corners = {2 * nvars + 3 * j + t for j, c in enumerate(clauses)
               for keep in [next(t for t, lit in enumerate(c) if true_lit(lit))] for t in range(3) if t != keep}
    return [1 if u in literals | corners else 0 for u in range(2 * nvars + 3 * len(clauses))]


def assignment_from_cover(nvars, clauses, cover):
    return [bool(cover[literal_vertex(v)]) for v in range(1, nvars + 1)]


# ---------------------------------------------------------------- step 2 ---

def _split(c, top):
    """(new clauses, number of fresh variables used) for one clause, fresh variables numbered from top + 1."""
    k = len(c)
    if k == 1:
        y, z = top + 1, top + 2
        return [[c[0], sy, sz] for sy in (y, -y) for sz in (z, -z)], 2
    if k == 2:
        return [[c[0], c[1], top + 1], [c[0], c[1], -(top + 1)]], 1
    if k == 3:
        return [list(c)], 0
    ys = list(range(top + 1, top + k - 2))
    middle = [[-ys[i - 1], c[i + 1], ys[i]] for i in range(1, len(ys))]
    return [[c[0], c[1], ys[0]]] + middle + [[-ys[-1], c[-2], c[-1]]], k - 3


def cnf_to_3cnf(nvars, clauses):
    def step(state, c):
        top, out = state
        new, used = _split(c, top)
        return top + used, out + new
    return tz.reduce(step, clauses, (nvars, []))


def extend_assignment(nvars, clauses, assignment):
    def fresh_values(c):
        if len(c) in (1, 2):
            return [False] * (3 - len(c))
        truth = [assignment[abs(l) - 1] == (l > 0) for l in c]
        return [not any(truth[:i + 2]) for i in range(len(c) - 3)]
    return list(assignment) + list(chain.from_iterable(fresh_values(c) for c in clauses))


def satisfies(assignment, clauses):
    return all(any(assignment[abs(l) - 1] == (l > 0) for l in c) for c in clauses)


# ---------------------------------------------------------------- step 3 ---

def vertex_cover_to_set_cover(vc):
    incident = tz.groupby(0, [(v, e) for e, (a, b) in enumerate(vc.edges) for v in (a, b)])
    return SetCover(len(vc.edges), tuple(frozenset(e for _, e in incident.get(v, [])) for v in range(vc.n)), (1,) * vc.n)


def sat_to_set_cover(nvars, clauses):
    vc, k = sat_to_vertex_cover(nvars, clauses)
    return vertex_cover_to_set_cover(vc), k


# ---------------------------------------------------------------- step 4 ---

def knapsack_by_value(values, weights, capacity):
    total = sum(values)

    def add_item(table, item):
        v, w = item
        return tuple(min(table[p], table[p - v] + w) if p >= v else table[p] for p in range(total + 1))

    tables = list(accumulate(zip(values, weights), add_item, initial=(0,) + (math.inf,) * total))
    best = max(p for p in range(total + 1) if tables[-1][p] <= capacity)

    def back(state):
        i, p, items = state
        taken = tables[i][p] != tables[i - 1][p]
        return i - 1, p - values[i - 1] if taken else p, items + (i - 1,) if taken else items

    _, _, items = next(s for s in tz.iterate(back, (len(values), best, ())) if s[0] == 0)
    return best, sorted(items)


def knapsack_fptas(values, weights, capacity, eps):
    usable = [i for i in range(len(values)) if weights[i] <= capacity and values[i] > 0]
    if not usable:
        return 0, []
    K = eps * max(values[i] for i in usable) / len(usable)
    _, picked = knapsack_by_value([int(values[i] // K) for i in usable], [weights[i] for i in usable], capacity)
    items = sorted(usable[k] for k in picked)
    return sum(values[i] for i in items), items
