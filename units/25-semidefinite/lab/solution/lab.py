"""Unit 25 lab — semidefinite relaxations.  REFERENCE SOLUTION, imperative.

Max-Cut instances are unit 00's MaxCut(n, edges, weights) with positive weights; a cut is a 0/1 list.
SDPs are solved with cvxpy (the CLARABEL interior-point solver), LPs with colib.solvers.highs_lp.
"""

from __future__ import annotations

import math
from itertools import combinations

import cvxpy as cp
import numpy as np

from colib.solvers import highs_lp


# ---------------------------------------------------------------- step 1 ---

def weight_matrix(mc):
    """The symmetric n x n numpy array W with W[u, v] = W[v, u] = weight of edge uv (0 if absent)."""
    W = np.zeros((mc.n, mc.n))
    for (u, v), w in zip(mc.edges, mc.weights):
        W[u, v] += w
        W[v, u] += w
    return W


def maxcut_sdp(mc):
    """The Goemans-Williamson relaxation: maximise sum over edges w_uv (1 - X_uv) / 2 over PSD X with unit
    diagonal. Returns (value, X) with X a numpy array."""
    X = cp.Variable((mc.n, mc.n), PSD=True)
    W = weight_matrix(mc)
    problem = cp.Problem(cp.Maximize(cp.sum(cp.multiply(W, 1 - X)) / 4), [cp.diag(X) == 1])
    problem.solve(solver="CLARABEL")
    return float(problem.value), np.array(X.value)


def vectors_from_gram(X):
    """Unit vectors v_1 .. v_n (the rows of the returned n x n array) with v_i . v_j ~= X_ij: eigendecompose,
    clip negative eigenvalues (solver noise) to zero, scale, and renormalise each row to length 1."""
    vals, vecs = np.linalg.eigh((X + X.T) / 2)
    V = vecs * np.sqrt(np.clip(vals, 0, None))
    return V / np.linalg.norm(V, axis=1, keepdims=True)


# ---------------------------------------------------------------- step 2 ---

def hyperplane_round(V, rng):
    """A uniformly random hyperplane through the origin: r with independent standard normal entries
    (rng.standard_normal), and x_i = 1 iff v_i . r >= 0."""
    r = rng.standard_normal(V.shape[1])
    return [1 if float(V[i] @ r) >= 0 else 0 for i in range(V.shape[0])]


def expected_cut(mc, V):
    """The exact expected weight of hyperplane_round's cut: sum over edges w_uv * angle(v_u, v_v) / pi."""
    total = 0.0
    for (u, v), w in zip(mc.edges, mc.weights):
        c = float(np.clip(V[u] @ V[v], -1.0, 1.0))
        total += w * math.acos(c) / math.pi
    return total


def gw_constant(grid=100_000):
    """alpha_GW = min over theta in (0, pi] of (theta / pi) / ((1 - cos theta) / 2), by evaluating on a fine grid
    and refining around the best point by golden-section search. Returns (alpha, theta)."""
    ratio = lambda t: (t / math.pi) / ((1 - math.cos(t)) / 2)
    best = min((ratio(math.pi * k / grid), math.pi * k / grid) for k in range(1, grid + 1))
    lo, hi = best[1] - math.pi / grid, min(math.pi, best[1] + math.pi / grid)
    g = (math.sqrt(5) - 1) / 2
    for _ in range(60):
        a, b = hi - g * (hi - lo), lo + g * (hi - lo)
        if ratio(a) < ratio(b):
            hi = b
        else:
            lo = a
    t = (lo + hi) / 2
    return ratio(t), t


# ---------------------------------------------------------------- step 3 ---

def maxcut_edge_lp(mc):
    """The naive LP: variables x_v in [0, 1] and z_e in [0, 1] per edge, z_uv <= x_u + x_v and
    z_uv <= 2 - x_u - x_v, maximise sum w z. Returns its value."""
    n, m = mc.n, len(mc.edges)
    A, b = [], []
    for k, (u, v) in enumerate(mc.edges):
        row = [0.0] * (n + m)
        row[n + k], row[u], row[v] = 1, -1, -1
        A.append(row)
        b.append(0)
        row = [0.0] * (n + m)
        row[n + k], row[u], row[v] = 1, 1, 1
        A.append(row)
        b.append(2)
    c = [0.0] * n + list(mc.weights)
    return highs_lp(A, b, c, sense="max", upper=1.0).value


def maxcut_triangle_lp(mc):
    """The metric (triangle) LP over the complete graph: z_ij in [0, 1] for every pair i < j, and for every
    triple the four inequalities z_ij + z_jk + z_ik <= 2 and z_ij <= z_ik + z_jk (and its two rotations).
    Maximise sum over edges w z. Returns its value."""
    n = mc.n
    pairs = list(combinations(range(n), 2))
    index = {p: k for k, p in enumerate(pairs)}
    A, b = [], []
    for i, j, k in combinations(range(n), 3):
        a, bb, cc = index[(i, j)], index[(j, k)], index[(i, k)]
        for coeffs, rhs in (((1, 1, 1), 2), ((1, -1, -1), 0), ((-1, 1, -1), 0), ((-1, -1, 1), 0)):
            row = [0.0] * len(pairs)
            row[a], row[bb], row[cc] = coeffs
            A.append(row)
            b.append(rhs)
    c = [0.0] * len(pairs)
    for (u, v), w in zip(mc.edges, mc.weights):
        c[index[(min(u, v), max(u, v))]] += w
    if not A:
        return float(sum(mc.weights))
    return highs_lp(A, b, c, sense="max", upper=1.0).value


# ---------------------------------------------------------------- step 4 ---

def lovasz_theta(n, edges):
    """theta(G) = max sum_ij X_ij over PSD X with trace 1 and X_uv = 0 for every edge uv."""
    X = cp.Variable((n, n), PSD=True)
    constraints = [cp.trace(X) == 1] + [X[u, v] == 0 for u, v in edges]
    problem = cp.Problem(cp.Maximize(cp.sum(X)), constraints)
    problem.solve(solver="CLARABEL")
    return float(problem.value)


def complement(n, edges):
    """The complement graph's edges, as sorted pairs in lexicographic order."""
    present = {tuple(sorted(e)) for e in edges}
    return [(u, v) for u, v in combinations(range(n), 2) if (u, v) not in present]


# ---------------------------------------------------------------- step 5 ---

def local_search(mc, x):
    """One-flip local search: repeatedly scan vertices in index order and flip the first one whose flip
    strictly increases the cut, until no flip helps. Returns the new cut (x itself is not modified)."""
    x = list(x)
    adj = [[] for _ in range(mc.n)]
    for (u, v), w in zip(mc.edges, mc.weights):
        adj[u].append((v, w))
        adj[v].append((u, w))
    improved = True
    while improved:
        improved = False
        for v in range(mc.n):
            gain = sum(w if x[u] == x[v] else -w for u, w in adj[v])
            if gain > 0:
                x[v] = 1 - x[v]
                improved = True
                break
    return x


def goemans_williamson(mc, rounds, rng):
    """Solve the SDP once, round `rounds` times, and return (best cut, its weight, the SDP value)."""
    value, X = maxcut_sdp(mc)
    V = vectors_from_gram(X)
    best, best_w = None, -1
    for _ in range(rounds):
        x = hyperplane_round(V, rng)
        w = mc.objective(x)
        if w > best_w:
            best, best_w = x, w
    return best, best_w, value
