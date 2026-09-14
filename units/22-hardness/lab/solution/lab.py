"""Unit 22 lab — reductions and an FPTAS.  REFERENCE SOLUTION, imperative.

Formulas are DIMACS-style: variables 1..n, clauses as lists of nonzero ints. Assignments are lists
of booleans, index 0 for variable 1. Vertex cover and set cover instances are unit 00's classes in
colib.problems; their solutions are 0/1 lists.
"""

from __future__ import annotations

import math

from colib.problems import SetCover, VertexCover


# ---------------------------------------------------------------- step 1 ---

def literal_vertex(lit):
    """Vertex of literal x_v (2(v-1)) or not x_v (2(v-1) + 1)."""
    return 2 * (abs(lit) - 1) + (lit < 0)


def sat_to_vertex_cover(nvars, clauses):
    """The textbook reduction from 3-CNF (every clause exactly 3 literals) to vertex cover.
    A variable gadget is an edge between x_v and not x_v; a clause gadget is a triangle whose t-th corner
    (vertex 2n + 3j + t) is joined to the vertex of the clause's t-th literal.
    Returns (VertexCover, k): the formula is satisfiable iff a cover of size <= k = n + 2m exists."""
    m = len(clauses)
    edges = set()
    for v in range(1, nvars + 1):
        edges.add((literal_vertex(v), literal_vertex(-v)))
    for j, clause in enumerate(clauses):
        assert len(clause) == 3, "3-CNF only"
        corners = [2 * nvars + 3 * j + t for t in range(3)]
        edges |= {(corners[0], corners[1]), (corners[0], corners[2]), (corners[1], corners[2])}
        for t, lit in enumerate(clause):
            a, b = sorted((corners[t], literal_vertex(lit)))
            edges.add((a, b))
    return VertexCover(2 * nvars + 3 * m, tuple(sorted(edges))), nvars + 2 * m


def cover_from_assignment(nvars, clauses, assignment):
    """A cover of size exactly n + 2m from a satisfying assignment: the true literal of every variable,
    and in each triangle every corner except one whose literal is true."""
    m = len(clauses)
    cover = [0] * (2 * nvars + 3 * m)
    for v in range(1, nvars + 1):
        cover[literal_vertex(v if assignment[v - 1] else -v)] = 1
    for j, clause in enumerate(clauses):
        keep = next(t for t, lit in enumerate(clause) if assignment[abs(lit) - 1] == (lit > 0))
        for t in range(3):
            if t != keep:
                cover[2 * nvars + 3 * j + t] = 1
    return cover


def assignment_from_cover(nvars, clauses, cover):
    """A satisfying assignment from a cover of size <= n + 2m: x_v is true iff the vertex of x_v is in the cover.
    (Such a cover holds exactly one vertex per variable edge and two per triangle, so the uncovered corner of
    each triangle forces its literal's vertex into the cover.)"""
    return [bool(cover[literal_vertex(v)]) for v in range(1, nvars + 1)]


# ---------------------------------------------------------------- step 2 ---

def cnf_to_3cnf(nvars, clauses):
    """An equisatisfiable 3-CNF, every clause with exactly 3 literals over distinct variables where possible.
    Width 1: (l) -> four clauses with two fresh variables. Width 2: (a or b) -> two clauses with one fresh
    variable. Width k > 3: the chain (l1 or l2 or y1), (not y1 or l3 or y2), ..., (not y_{k-3} or l_{k-1} or l_k).
    Returns (new nvars, new clauses)."""
    top = nvars
    out = []
    for c in clauses:
        c = list(c)
        if len(c) == 1:
            y, z = top + 1, top + 2
            top += 2
            out += [[c[0], y, z], [c[0], y, -z], [c[0], -y, z], [c[0], -y, -z]]
        elif len(c) == 2:
            y = top + 1
            top += 1
            out += [[c[0], c[1], y], [c[0], c[1], -y]]
        elif len(c) == 3:
            out.append(c)
        else:
            ys = list(range(top + 1, top + len(c) - 2))
            top += len(c) - 3
            out.append([c[0], c[1], ys[0]])
            for i in range(1, len(ys)):
                out.append([-ys[i - 1], c[i + 1], ys[i]])
            out.append([-ys[-1], c[-2], c[-1]])
    return top, out


def extend_assignment(nvars, clauses, assignment):
    """Extend a satisfying assignment of the original formula to one of cnf_to_3cnf's output.
    Fresh variables of width-1 and width-2 clauses can be anything (False); in a chain, y_i is true iff none of
    l_1 .. l_{i+1} is true."""
    out = list(assignment)
    for c in clauses:
        if len(c) == 1:
            out += [False, False]
        elif len(c) == 2:
            out.append(False)
        elif len(c) > 3:
            truth = [assignment[abs(l) - 1] == (l > 0) for l in c]
            for i in range(len(c) - 3):
                out.append(not any(truth[:i + 2]))
    return out


def satisfies(assignment, clauses):
    return all(any(assignment[abs(l) - 1] == (l > 0) for l in c) for c in clauses)


# ---------------------------------------------------------------- step 3 ---

def vertex_cover_to_set_cover(vc):
    """Elements are the edges (in vc.edges order); vertex v's set is its incident edges, at cost 1.
    Solutions are the same 0/1 vector on both sides, with the same objective."""
    sets = tuple(frozenset(e for e, (a, b) in enumerate(vc.edges) if v in (a, b)) for v in range(vc.n))
    return SetCover(len(vc.edges), sets, (1,) * vc.n)


def sat_to_set_cover(nvars, clauses):
    """3-CNF -> vertex cover -> set cover, composed. Returns (SetCover, k)."""
    vc, k = sat_to_vertex_cover(nvars, clauses)
    return vertex_cover_to_set_cover(vc), k


# ---------------------------------------------------------------- step 4 ---

def knapsack_by_value(values, weights, capacity):
    """Exact 0/1 knapsack by DP over total value: W[p] = least weight achieving value exactly p.
    Integer values. Returns (best value, sorted items)."""
    n = len(values)
    total = sum(values)
    INF = math.inf
    W = [0] + [INF] * total
    choice = [[False] * (total + 1) for _ in range(n)]
    for i in range(n):
        v, w = values[i], weights[i]
        for p in range(total, v - 1, -1):
            if W[p - v] + w < W[p]:
                W[p] = W[p - v] + w
                choice[i][p] = True
    best = max(p for p in range(total + 1) if W[p] <= capacity)
    items, p = [], best
    for i in reversed(range(n)):
        if choice[i][p]:
            items.append(i)
            p -= values[i]
    return best, sorted(items)


def knapsack_fptas(values, weights, capacity, eps):
    """(1 - eps)-approximate knapsack in O(n^3 / eps): drop items heavier than the capacity, scale values by
    K = eps * vmax / n rounding down, solve the scaled problem exactly by value, and return
    (true value of the chosen items, sorted items)."""
    usable = [i for i in range(len(values)) if weights[i] <= capacity and values[i] > 0]
    if not usable:
        return 0, []
    vmax = max(values[i] for i in usable)
    K = eps * vmax / len(usable)
    scaled = [int(values[i] // K) for i in usable]
    _, picked = knapsack_by_value(scaled, [weights[i] for i in usable], capacity)
    items = sorted(usable[k] for k in picked)
    return sum(values[i] for i in items), items
