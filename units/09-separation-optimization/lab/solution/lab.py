"""Unit 09 lab — separation and optimization: subtour elimination.  REFERENCE SOLUTION, imperative.

Edge variables x_e for the complete graph, indexed as colib.tsp.edges(n).
Subtour elimination: for every S with 1 <= |S| <= n-1,
    sum_{e in delta(S)} x_e >= 2,     written for colib.mip as  -sum x_e <= -2.
"""

from __future__ import annotations

from collections import deque
from dataclasses import replace

from colib.mip import highs_mip, lp_relaxation
from colib.tsp import degree_milp, edges, tour_from_edges


# ---------------------------------------------------------------- step 1 ---

def subtour_row(n, S):
    """The subtour elimination inequality for S as (row, rhs) in <= form."""
    S = set(S)
    return tuple(-1 if (i in S) != (j in S) else 0 for i, j in edges(n)), -2


def components(n, x, eps=1e-6):
    """Connected components of the support graph {e : x_e > eps}, as a list of sorted tuples."""
    adj = {v: [] for v in range(n)}
    for (i, j), v in zip(edges(n), x):
        if v > eps:
            adj[i].append(j)
            adj[j].append(i)
    seen, comps = set(), []
    for s in range(n):
        if s in seen:
            continue
        comp, queue = [], deque([s])
        seen.add(s)
        while queue:
            u = queue.popleft()
            comp.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
        comps.append(tuple(sorted(comp)))
    return comps


# ---------------------------------------------------------------- step 2 ---

def min_cut(n, x):
    """Stoer–Wagner global minimum cut of the graph with edge weights x.
    Returns (cut_value, S) with S one side of a minimum cut."""
    w = [[0.0] * n for _ in range(n)]
    for (i, j), v in zip(edges(n), x):
        w[i][j] = w[j][i] = v
    groups = [[v] for v in range(n)]            # merged vertices
    active = list(range(n))
    best_val, best_set = float("inf"), None
    while len(active) > 1:
        # maximum adjacency ordering
        weights = {v: 0.0 for v in active}
        order = []
        remaining = set(active)
        while remaining:
            u = max(remaining, key=lambda v: (weights[v], -v))
            order.append(u)
            remaining.remove(u)
            for v in remaining:
                weights[v] += w[u][v]
        s, t = order[-2], order[-1]
        cut_of_phase = weights[t]
        if cut_of_phase < best_val:
            best_val, best_set = cut_of_phase, tuple(sorted(groups[t]))
        # merge t into s
        groups[s] += groups[t]
        for v in active:
            w[s][v] += w[t][v]
            w[v][s] = w[s][v]
        w[s][s] = 0.0
        active.remove(t)
    return best_val, best_set


# ---------------------------------------------------------------- step 3 ---

def separate_subtours(n, x, eps=1e-6):
    """Violated subtour sets for x: every component if the support graph is
    disconnected; otherwise the min cut's side if its value is below 2 - eps;
    otherwise an empty list."""
    comps = components(n, x, eps)
    if len(comps) > 1:
        return comps
    value, S = min_cut(n, x)
    return [S] if value < 2 - eps else []


# ---------------------------------------------------------------- step 4 ---

def subtour_lp(tsp):
    """The subtour elimination LP bound by lazy constraints.
    Returns (value, x, cuts_added, lp_solves)."""
    n = tsp.n
    milp = degree_milp(tsp, integer=False)
    rows, rhs, solves = [], [], 0
    while True:
        lp = lp_relaxation(replace(milp, A_ub=tuple(rows), b_ub=tuple(rhs)))
        solves += 1
        found = separate_subtours(n, lp.x)
        if not found:
            return lp.value, lp.x, len(rows), solves
        for S in found:
            r, b = subtour_row(n, S)
            rows.append(r)
            rhs.append(b)


# ---------------------------------------------------------------- step 5 ---

def tsp_exact(tsp):
    """Optimal tour by lazy subtour elimination on the integer program: solve the
    MILP with the cuts so far; if the solution's edges form subtours, add a cut
    for each component and repeat. Returns (length, order, cuts_added, mip_solves)."""
    n = tsp.n
    milp = degree_milp(tsp, integer=True)
    rows, rhs, solves = [], [], 0
    while True:
        sol = highs_mip(replace(milp, A_ub=tuple(rows), b_ub=tuple(rhs)), options={"mip_rel_gap": 0.0})
        solves += 1
        comps = components(n, sol.x, eps=0.5)
        if len(comps) == 1:
            order = tour_from_edges(n, sol.x)
            return round(sol.value), order, len(rows), solves
        for S in comps:
            r, b = subtour_row(n, S)
            rows.append(r)
            rhs.append(b)
