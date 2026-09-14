"""Unit 16 lab — dynamic programming.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 16
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Conventions. Graphs have vertices 0..n-1 and undirected edges (u, v). A tree
decomposition is a list `bags` of sets of vertices together with `tree_edges`,
pairs (i, j) of indices into `bags`.

Either style is welcome: loops and arrays, or folds over layers of a table
(see FUNCTIONAL.md at the project root).
"""

from __future__ import annotations

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def knapsack(values, weights, capacity):
    """0/1 knapsack: choose items of total weight <= capacity maximising total value.
    Weights and capacity are nonnegative integers; values may be floats.
    Returns (best value, sorted list of chosen item indices), where the best value
    equals the sum of the chosen items' values.

    best[c] after considering items 0..i = the best value within capacity c. Record
    which (item, capacity) pairs used the item, so you can walk back from `capacity`.
    It must handle capacity 100 000 with 60 items within the time limit.
    """
    raise NotImplementedError  # TODO step 1


def unbounded_knapsack(values, weights, capacity):
    """Knapsack where each item may be used any number of times (unit 10's pricer).
    Returns (best value, counts) with counts[i] = copies of item i used.
    """
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def held_karp(dist):
    """Exact TSP by dynamic programming over subsets, O(n^2 2^n) time.
    `dist` is an n x n matrix, not necessarily symmetric. Returns (length, order), where
    order is a permutation of range(n) with order[0] == 0 and length is the length of
    the closed tour order[0] -> order[1] -> ... -> order[-1] -> order[0].

    D[S, k] = the shortest path that starts at 0, visits exactly the cities in S
    (a subset of 1..n-1), and ends at k in S.
    """
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def tree_vertex_cover(n, edges, weights):
    """Minimum-weight vertex cover of a forest (a graph with no cycles).
    Returns (weight, set of vertices).

    Root each component, then compute two numbers per vertex, children first: the
    best cover of v's subtree with v in the cover, and with v out. It must not hit
    Python's recursion limit on a path of 5 000 vertices.
    """
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def width(bags):
    """The width of a decomposition: the largest bag size minus one."""
    raise NotImplementedError  # TODO step 4


def is_tree_decomposition(n, edges, bags, tree_edges):
    """True iff all of:
      * tree_edges form a tree on the bag indices 0..len(bags)-1;
      * every vertex is in some bag;
      * both ends of every edge are together in some bag;
      * for every vertex, the bags containing it form a connected subtree.
    """
    raise NotImplementedError  # TODO step 4


def elimination_decomposition(n, edges, order=None):
    """A tree decomposition from an elimination ordering. Returns (bags, tree_edges).

    Eliminate the vertices one at a time (in `order`, or when order is None, by picking
    the vertex of minimum current degree, smallest index on ties). Eliminating v: its
    bag is v plus its current neighbours; join those neighbours into a clique; delete v.
    The bag of v hangs off the bag of whichever of its neighbours is eliminated next.
    Bags with no neighbours left start a new component; link those in a chain so the
    result is a single tree.
    """
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def td_vertex_cover(n, edges, weights, bags, tree_edges):
    """Minimum-weight vertex cover by DP over a tree decomposition.
    Returns (weight, set of vertices).

    Root the decomposition at bag 0. For each bag, and each subset S of it that covers
    every graph edge inside the bag, table[bag][S] = the least weight of a cover of the
    vertices in this bag's subtree that meets the bag in exactly S. Combine children by
    agreement on the vertices shared with each child, without counting a shared
    vertex's weight twice. Time O(len(bags) * 2^(width+1)), times small factors.
    """
    raise NotImplementedError  # TODO step 5
