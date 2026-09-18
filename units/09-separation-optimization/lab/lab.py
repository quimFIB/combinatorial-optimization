"""Unit 09 lab — separation and optimization: subtour elimination for the TSP.

    uv run co test 09

The TSP as an edge-variable program: x_e for each edge of the complete graph,
indexed in the order of colib.tsp.edges(n) (itertools.combinations order).
colib.tsp.degree_milp(tsp, integer) gives

    min sum c_e x_e   s.t.  sum_{e at v} x_e = 2 for every v,  0 <= x_e <= 1

and you add subtour elimination inequalities, one per vertex set S:

    sum_{e crossing S} x_e >= 2,    as an A_ub row:  -sum x_e <= -2.

There are 2^(n-1) - 1 of them. You never write them all down.

Also available: colib.mip.lp_relaxation, colib.mip.highs_mip,
colib.tsp.tour_from_edges(n, x).
"""

from __future__ import annotations

from collections import deque
from dataclasses import replace

from colib.mip import highs_mip, lp_relaxation
from colib.problems import TSP
from colib.tsp import degree_milp, edges, tour_from_edges


# ---------------------------------------------------------------- step 1 ---

def subtour_row(n, S):
    """(row, rhs) for S in <= form: -1 on every edge with exactly one endpoint in S, rhs -2."""
    raise NotImplementedError("step 1: subtour_row")


def components(n, x, eps=1e-6):
    """Connected components of the support graph (edges with x_e > eps), as a
    list of sorted tuples of vertices. Isolated vertices are components too."""
    raise NotImplementedError("step 1: components")


# ---------------------------------------------------------------- step 2 ---

def min_cut(n, x):
    """A global minimum cut of the complete graph weighted by x (Stoer–Wagner).
    Return (value, S), with S a tuple of vertices (0 < |S| < n) whose crossing
    weight equals value."""
    raise NotImplementedError("step 2: min_cut")


# ---------------------------------------------------------------- step 3 ---

def separate_subtours(n, x, eps=1e-6):
    """Vertex sets whose subtour inequality x violates:
    if the support graph is disconnected, every component;
    otherwise one side S of a minimum cut, if its value is below 2 - eps;
    otherwise []."""
    raise NotImplementedError("step 3: separate_subtours")


# ---------------------------------------------------------------- step 4 ---

def subtour_lp(tsp: TSP):
    """The subtour elimination LP bound by lazy constraints: solve the LP with
    the subtour constraints found so far (degree_milp(tsp, integer=False) plus A_ub
    rows), separate at its solution, add one per violated set, repeat until none is
    found. Return (value, x, number_of_constraints_added, number_of_LP_solves)."""
    raise NotImplementedError("step 4: subtour_lp")


# ---------------------------------------------------------------- step 5 ---

def tsp_exact(tsp: TSP):
    """An optimal tour by lazy constraints on the integer program: solve
    degree_milp(tsp, integer=True) with the subtour constraints found so far using
    highs_mip (pass options={"mip_rel_gap": 0.0}); if the chosen edges form more than
    one cycle, add a subtour constraint for every cycle's vertex set and repeat.
    Return (length, order, number_of_constraints_added, number_of_MIP_solves), where
    order is the list of vertices along the tour."""
    raise NotImplementedError("step 5: tsp_exact")
