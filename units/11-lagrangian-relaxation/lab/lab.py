"""Unit 11 lab — Lagrangian relaxation.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 11
after each. Read README.md first; HINTS.org has a ladder of hints per step.

TSP: a symmetric distance matrix `dist` (n >= 3). Multipliers pi[v], one per vertex;
the modified cost of edge {i, j} is dist[i][j] + pi[i] + pi[j].

GAP: colib.colgen.GAP with .m agents, .n jobs, .cost[i][j], .weight[i][j],
.capacity[i]. An assignment is `agent_of`, with agent_of[j] = the agent of job j.

Given: colib.ref.unit("16").knapsack (0/1 knapsack returning (value, items)).
"""

from __future__ import annotations

from colib.colgen import GAP
from colib.ref import unit

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def one_tree(dist, pi):
    """The minimum 1-tree under modified costs: a minimum spanning tree on vertices 1..n-1,
    plus the two cheapest edges at vertex 0.
    Returns (L, degrees, edges): L = (modified weight of the 1-tree) - 2 * sum(pi), the
    Lagrangian bound; degrees[v] in the 1-tree; edges as (i, j) with i < j."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def subgradient_ascent(oracle, start, upper, iterations=500, lam=2.0, patience=20, project=None):
    """Maximise a Lagrangian function by subgradient steps.

    oracle(mult) -> (L, solution, g): the bound at `mult` and a subgradient g.
    Each iteration: call the oracle and append L to the history. Track the best L and the
    multipliers that gave it; if L doesn't beat the best by 1e-9, count it, and after
    `patience` such iterations in a row halve lam and reset the count. Stop if g is all
    zeros or lam < 1e-6. Otherwise step  mult += t * g  with  t = lam * (upper - L) / |g|^2
    (use max(upper - L, 1e-9)), then apply project(mult) if given.
    Returns (best L, best multipliers, history).
    """
    raise NotImplementedError  # TODO step 2


def held_karp_bound(dist, upper, iterations=500):
    """The Held–Karp bound: subgradient_ascent on one_tree from pi = 0, where the subgradient
    at each vertex is its degree minus 2. Returns (best bound, pi, history)."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def fix_edges(dist, pi, upper):
    """Edges that no tour of length <= upper can contain, by 1-tree reduced costs.

    For an edge e not in the minimum 1-tree, the cheapest 1-tree containing e costs
      L + c(e) - (the heaviest modified edge on the tree path between e's ends)  if 0 is not in e,
      L + c(e) - (the dearer of vertex 0's two chosen edges)                     if 0 is in e.
    An edge is fixed out when that cost exceeds upper + 1e-9. Tree edges are never fixed.
    Returns a set of (i, j) with i < j."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def gap_relax_assignment(gap: GAP, u):
    """Dualise 'each job is assigned exactly once' with multipliers u[j]:
      L(u) = sum_j u[j] + sum_i min { sum_j (cost[i][j] - u[j]) x[i][j] : agent i's capacity }.
    Each agent's problem is a 0/1 knapsack over the jobs with u[j] - cost[i][j] > 0.
    Returns (L, x, g) with x an m x n 0/1 matrix and g[j] = 1 - sum_i x[i][j]."""
    raise NotImplementedError  # TODO step 4


def gap_relax_capacity(gap: GAP, lam):
    """Dualise the capacities with lam[i] >= 0:
      L(lam) = -sum_i lam[i] * capacity[i] + sum_j min_i (cost[i][j] + lam[i] * weight[i][j]).
    Returns (L, x, g) with g[i] = (agent i's load under x) - capacity[i]."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def gap_repair(gap: GAP, x):
    """A Lagrangian heuristic from the assignment relaxation's x (each agent's jobs fit its
    capacity, but a job may be taken by several agents or by none).

    Keep each multiply-assigned job with its cheapest agent among those that took it. Then, while jobs
    remain unassigned: for each, list the agents that still have room for it, sorted by cost;
    if some job has none, return None. Otherwise place the job with the largest regret
    (second-cheapest cost minus cheapest; infinite if it has only one option) on its cheapest
    agent. Returns (cost, agent_of)."""
    raise NotImplementedError  # TODO step 5
