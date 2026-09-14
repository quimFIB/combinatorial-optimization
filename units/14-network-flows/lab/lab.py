"""Unit 14 lab — network flows.

    uv run co test 14

A network is (n, arcs): nodes 0..n-1 and a list of directed arcs (u, v, capacity),
or (u, v, capacity, cost) for min-cost flow. Parallel arcs are allowed and are
separate arcs. A flow is a list with one integer per arc, in arc order.

Residual graphs: the standard trick is to store arc k as two edges, 2k (forward,
residual capacity c - f) and 2k+1 (backward, residual capacity f), so that the
reverse of edge e is e ^ 1. The reference solutions both use it.

Any style passes; the tests check the flow is valid and optimal.
"""

from __future__ import annotations

import heapq
from collections import deque


# ---------------------------------------------------------------- step 1 ---

def edmonds_karp(n, arcs, s, t):
    """Maximum s-t flow by shortest (BFS) augmenting paths. Return (value, flow)."""
    raise NotImplementedError("step 1: edmonds_karp")


def min_cut(n, arcs, flow, s):
    """The set of nodes reachable from s in the residual graph of `flow` (forward
    residual where flow < capacity, backward where flow > 0). For a maximum flow
    this is the source side of a minimum cut. Return a set."""
    raise NotImplementedError("step 1: min_cut")


# ---------------------------------------------------------------- step 2 ---

def dinic(n, arcs, s, t):
    """Maximum flow by Dinic's algorithm: repeat { BFS levels from s in the
    residual graph; find a blocking flow using only edges from level i to i+1
    (DFS with a per-node "current edge" pointer) } until t is unreachable.
    Return (value, flow)."""
    raise NotImplementedError("step 2: dinic")


# ---------------------------------------------------------------- step 3 ---

def push_relabel(n, arcs, s, t):
    """Maximum flow by FIFO push-relabel. Start with height[s] = n, every arc out
    of s saturated, and every node other than s and t that received excess in a
    queue. While the queue is non-empty, discharge its front node u: push along
    admissible residual edges (height[u] == height[v] + 1), relabel u to
    1 + min height of its residual neighbours when none is admissible, and
    enqueue nodes (other than s, t) that gain excess from zero.
    Return (excess at t, flow)."""
    raise NotImplementedError("step 3: push_relabel")


# ---------------------------------------------------------------- step 4 ---

def min_cost_flow(n, arcs, s, t, demand):
    """Send `demand` units from s to t at minimum total cost. Arcs are
    (u, v, capacity, cost); costs may be negative but there is no negative cycle.

    Successive shortest paths with potentials: initialise potentials by
    Bellman-Ford from s; then repeatedly run Dijkstra on reduced costs
    cost(e) + pot[u] - pot[v] (nonnegative on residual edges), add the distances
    to the potentials, and augment along the shortest path by as much as it and
    the remaining demand allow. Return (cost, flow), or None if the demand
    cannot be met."""
    raise NotImplementedError("step 4: min_cost_flow")


# ---------------------------------------------------------------- step 5 ---

def project_selection(profit, requires, max_flow=None):
    """Project selection by minimum cut. profit[p] may be negative (a cost).
    requires is a list of (p, q): choosing p forces choosing q. Return
    (best_total_profit, chosen_set) with chosen_set closed under requires.

    Build: source -> p with capacity profit[p] if positive; p -> sink with
    capacity -profit[p] if negative; p -> q with infinite capacity for each
    requirement. The source side of a minimum cut is an optimal selection, and
    the best profit is (sum of positive profits) - (cut value). Use your dinic
    (or edmonds_karp) and min_cut."""
    raise NotImplementedError("step 5: project_selection")
