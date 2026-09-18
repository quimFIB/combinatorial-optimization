"""Unit 06 lab — total unimodularity.

    uv run co test 06

Matrices are lists of lists of small integers. Graphs are (n, edges) with
vertices 0..n-1 and edges a list of (u, v) pairs. Everything except step 4 is
exact integer arithmetic.

Any style passes; the tests only check results. Steps 1 and 2 are quantifiers
over finite sets: all(...) / any(...) over itertools.combinations and product.
"""

from __future__ import annotations

from itertools import combinations, product

import numpy as np

from colib.solvers import highs_lp


# ---------------------------------------------------------------- step 1 ---

def is_tu(A) -> bool:
    """True iff every square submatrix of A has determinant -1, 0 or 1.
    (So every entry, a 1x1 submatrix, must be -1, 0 or 1.) Compute determinants
    exactly: integers or Fractions, not floats."""
    raise NotImplementedError("step 1: is_tu")


# ---------------------------------------------------------------- step 2 ---

def ghouila_houri(A):
    """Ghouila-Houri's criterion. A is TU iff every nonempty subset R of rows can
    be signed (a +1 or -1 per row) so that the signed sum of those rows has every
    entry in {-1, 0, 1}.

    Return None if A is TU; otherwise return a subset of rows (a tuple of row
    indices) that has no such signing.
    """
    raise NotImplementedError("step 2: ghouila_houri")


# ---------------------------------------------------------------- step 3 ---

def incidence_matrix(n, edges):
    """The n x len(edges) vertex-edge incidence matrix of an undirected graph:
    entry [v][e] is 1 if v is an endpoint of edge e, else 0."""
    raise NotImplementedError("step 3: incidence_matrix")


def interval_matrix(n, intervals):
    """One row per interval (a, b), meaning the columns a <= j < b: a row of
    consecutive ones among n columns."""
    raise NotImplementedError("step 3: interval_matrix")


# ---------------------------------------------------------------- step 4 ---

def assignment_lp(cost):
    """The assignment problem as a plain LP with no integrality: variables
    x_ij >= 0 (row-major), sum_j x_ij = 1 for each i, sum_i x_ij = 1 for each j,
    minimize sum c_ij x_ij. Solve it with colib.solvers.highs_lp (use
    row_lower=b to make the constraints equalities, sense="min") and return the
    n x n numpy array of x."""
    raise NotImplementedError("step 4: assignment_lp")


# ---------------------------------------------------------------- step 5 ---

def odd_cycle(n, edges):
    """An odd cycle of the graph as a list of distinct vertices [v0, ..., vk-1]
    (k odd; consecutive vertices adjacent, and vk-1 adjacent to v0), or None if
    the graph is bipartite. Any odd cycle will do."""
    raise NotImplementedError("step 5: odd_cycle")


def fractional_matching_on_cycle(cycle):
    """The matching LP's optimal vertex on an odd cycle: 1/2 on every cycle
    edge. Return a dict {frozenset({u, v}): 0.5} with one entry per cycle edge."""
    raise NotImplementedError("step 5: fractional_matching_on_cycle")
