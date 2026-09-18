"""Unit 13 lab — matroids and the exact reach of greedy.

    uv run co test 13

An independence system on the ground set range(n) is given by an ORACLE:
a function independent(S) -> bool for any list/iterable S of elements. Step 1
builds oracles; the rest only ever call them.

Any style passes; the tests only check results. Oracles are naturally closures.
"""

from __future__ import annotations

from collections import deque
from itertools import combinations

from colib.polyhedra import rank          # exact rank of a list of vectors


# ---------------------------------------------------------------- step 1 ---

def graphic(n_vertices, edges):
    """Return the oracle of the graphic matroid of a graph with vertices
    range(n_vertices) and edge list `edges`: a set of edge INDICES is independent
    iff those edges contain no cycle."""
    raise NotImplementedError("step 1: graphic")


def uniform(k):
    """The uniform matroid U_{k,n}: independent iff at most k elements."""
    raise NotImplementedError("step 1: uniform")


def partition(block_of, capacity):
    """The partition matroid: element e lies in block block_of[e]; independent iff
    no block b contributes more than capacity[b] elements."""
    raise NotImplementedError("step 1: partition")


def linear(vectors):
    """The linear matroid: independent iff the vectors indexed by S are linearly
    independent over the rationals (use colib.polyhedra.rank). The empty set is
    independent."""
    raise NotImplementedError("step 1: linear")


# ---------------------------------------------------------------- step 2 ---

def greedy(n, weight, independent):
    """The greedy algorithm: go through the elements by decreasing weight (ties:
    lower index first), stop at the first non-positive weight, and add each
    element if the chosen set stays independent. Return the chosen set sorted."""
    raise NotImplementedError("step 2: greedy")


# ---------------------------------------------------------------- step 3 ---

def matroid_witness(n, independent):
    """Decide by brute force whether (range(n), independent) is a matroid.
    Return None if it is. Otherwise return the first violated axiom found, checking
    in this order:
      ("empty",)                  the empty set is not independent
      ("hereditary", S, T)        S independent, T = S minus one element, T dependent
      ("exchange", A, B)          A, B independent, |A| < |B|, and no b in B - A with
                                  A + {b} independent
    with S, T, A, B as sorted tuples."""
    raise NotImplementedError("step 3: matroid_witness")


# ---------------------------------------------------------------- step 4 ---

def intersection(n, indep1, indep2):
    """A maximum-cardinality set independent in both matroids, by augmenting paths.

    Start from I = empty. Build the exchange graph on the ground set:
      sources: y not in I with I + y independent in M1
      sinks:   y not in I with I + y independent in M2
      arc x -> y (x in I, y not in I) if I - x + y is independent in M1
      arc y -> x (y not in I, x in I) if I - x + y is independent in M2
    Find a SHORTEST path from a source to a sink (BFS). If none exists, I is
    maximum; otherwise flip membership of every vertex on the path and repeat.
    Return I sorted.
    """
    raise NotImplementedError("step 4: intersection")


# ---------------------------------------------------------------- step 5 ---

def greedy_coverage(sets, k):
    """Maximum coverage, greedily: k times, pick the not-yet-chosen set covering the
    most elements not covered so far (ties: lowest index). Return the list of chosen
    indices in the order picked."""
    raise NotImplementedError("step 5: greedy_coverage")
