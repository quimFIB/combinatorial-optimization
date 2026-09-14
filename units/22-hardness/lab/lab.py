"""Unit 22 lab — reductions and an FPTAS.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 22
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Formulas are DIMACS-style: variables 1..n, clauses as lists of nonzero ints. Assignments are lists of
booleans, index 0 for variable 1. Vertex cover and set cover instances are unit 00's classes in
colib.problems (VertexCover(n, edges), SetCover(universe, sets, costs)); their solutions are 0/1 lists.
"""

from __future__ import annotations

import math

from colib.problems import SetCover, VertexCover


# ---------------------------------------------------------------- step 1 ---

def satisfies(assignment, clauses):
    """True iff every clause has a literal made true by the assignment."""
    raise NotImplementedError  # TODO step 1


def literal_vertex(lit):
    """The vertex of literal x_v is 2(v - 1); the vertex of not x_v is 2(v - 1) + 1."""
    raise NotImplementedError  # TODO step 1


def sat_to_vertex_cover(nvars, clauses):
    """The textbook reduction from 3-CNF (every clause exactly 3 literals) to vertex cover.
    Vertices: the 2n literal vertices, then for clause j a triangle with corners 2n + 3j + t, t = 0, 1, 2.
    Edges (each as (smaller, larger), sorted, no duplicates): x_v -- not x_v; the three triangle edges;
    corner t of clause j -- the vertex of the clause's t-th literal.
    Returns (VertexCover, k) with k = n + 2m."""
    raise NotImplementedError  # TODO step 1


def cover_from_assignment(nvars, clauses, assignment):
    """A cover of size exactly k from a satisfying assignment (a 0/1 list over all vertices)."""
    raise NotImplementedError  # TODO step 1


def assignment_from_cover(nvars, clauses, cover):
    """A satisfying assignment from any cover of size <= k."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def cnf_to_3cnf(nvars, clauses):
    """An equisatisfiable formula whose clauses have exactly 3 literals. Fresh variables are numbered from
    nvars + 1 upwards, in clause order. Width 1: (l) becomes (l, ±y, ±z), four clauses. Width 2: (a, b)
    becomes (a, b, y) and (a, b, -y). Width 3: unchanged. Width k > 3: the chain
    (l1, l2, y1), (-y1, l3, y2), ..., (-y_{k-3}, l_{k-1}, l_k). Returns (new nvars, new clauses)."""
    raise NotImplementedError  # TODO step 2


def extend_assignment(nvars, clauses, assignment):
    """Extend a satisfying assignment of `clauses` to one of cnf_to_3cnf's output: fresh variables of width-1 and
    width-2 clauses are False; chain variable y_i (i = 1 .. k-3) is True iff none of l_1 .. l_{i+1} is true."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def vertex_cover_to_set_cover(vc: VertexCover):
    """Elements: the edges, numbered in vc.edges order. Sets: for each vertex, the frozenset of its incident edges,
    cost 1. The same 0/1 vector is a solution of both, with the same cost."""
    raise NotImplementedError  # TODO step 3


def sat_to_set_cover(nvars, clauses):
    """The composition of the two reductions. Returns (SetCover, k)."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def knapsack_by_value(values, weights, capacity):
    """Exact 0/1 knapsack by DP over total value (integer values): W[p] = least weight achieving exactly value p.
    Returns (best value, sorted list of items)."""
    raise NotImplementedError  # TODO step 4


def knapsack_fptas(values, weights, capacity, eps):
    """The FPTAS: keep the items that fit on their own and have positive value; if none, return (0, []).
    With vmax their largest value and n their number, K = eps * vmax / n; solve knapsack_by_value on the values
    floor(v / K). Returns (the true total value of the chosen items, sorted items); guaranteed >= (1 - eps) OPT."""
    raise NotImplementedError  # TODO step 4
