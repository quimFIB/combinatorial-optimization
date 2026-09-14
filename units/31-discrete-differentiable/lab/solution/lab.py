"""Unit 31 lab — where discrete meets differentiable.  REFERENCE SOLUTION, imperative.

Assignment costs are n x n arrays. JAX is used where gradients are the point (steps 2 and 3); everything else
is numpy. Branch and bound is unit 07's (colib.ref), whose branching rules have the signature
rule(milp, node, stats) -> variable index, with node = (lb, ub, lp) and lp.x the LP solution.
"""

from __future__ import annotations

import math

import jax
import jax.numpy as jnp
import numpy as np
from scipy.special import logsumexp

from colib.bb import INT_TOL, solve_node
from colib.ref import unit

jax.config.update("jax_enable_x64", True)


# ---------------------------------------------------------------- step 1 ---

def sinkhorn(C, eps, iterations):
    """Entropic assignment: the doubly stochastic P = exp((f_i + g_j - C_ij) / eps) whose row and column sums are
    all 1, by log-domain Sinkhorn. Start from g = 0; each iteration sets f_i = -eps logsumexp_j((g_j - C_ij)/eps)
    and then g_j = -eps logsumexp_i((f_i - C_ij)/eps). Returns P."""
    C = np.asarray(C, float)
    g = np.zeros(C.shape[1])
    for _ in range(iterations):
        f = -eps * logsumexp((g[None, :] - C) / eps, axis=1)
        g = -eps * logsumexp((f[:, None] - C) / eps, axis=0)
    return np.exp((f[:, None] + g[None, :] - C) / eps)


def round_to_permutation(P):
    """Greedy rounding: repeatedly take the largest remaining entry (ties: lowest row, then column), assign that
    row to that column, and remove both. Returns perm with perm[i] = the column of row i."""
    n = P.shape[0]
    order = sorted(((-P[i, j], i, j) for i in range(n) for j in range(n)))
    perm = [None] * n
    used = set()
    for _, i, j in order:
        if perm[i] is None and j not in used:
            perm[i] = j
            used.add(j)
    return perm


def assignment_cost(C, perm):
    """The total cost of assigning row i to column perm[i]."""
    return float(sum(C[i][j] for i, j in enumerate(perm)))


# ---------------------------------------------------------------- step 2 ---

def entropic_cost(C, eps, iterations):
    """JAX-differentiable entropic assignment cost <C, P> + eps * sum P (log P - 1), with P from `iterations` of
    the same log-domain Sinkhorn updates as step 1 (use jax.scipy.special.logsumexp)."""
    from jax.scipy.special import logsumexp as jlse
    C = jnp.asarray(C)
    g = jnp.zeros(C.shape[1])
    for _ in range(iterations):
        f = -eps * jlse((g[None, :] - C) / eps, axis=1)
        g = -eps * jlse((f[:, None] - C) / eps, axis=0)
    logP = (f[:, None] + g[None, :] - C) / eps
    P = jnp.exp(logP)
    return jnp.sum(C * P) + eps * jnp.sum(P * (logP - 1))


def entropic_gradient(C, eps, iterations):
    """d entropic_cost / d C by jax.grad, as a numpy array. At convergence it equals the Sinkhorn plan P
    (the envelope theorem), which a hard assignment's cost can't give you: its gradient is a permutation
    matrix that jumps."""
    return np.asarray(jax.grad(lambda c: entropic_cost(c, eps, iterations))(jnp.asarray(C, dtype=float)))


# ---------------------------------------------------------------- step 3 ---

def gumbel_max_sample(logits, rng):
    """One sample from softmax(logits) by the Gumbel-max trick: argmax(logits + G), G_k = -log(-log U_k) with U
    from rng.random(len(logits))."""
    u = rng.random(len(logits))
    return int(np.argmax(np.asarray(logits) - np.log(-np.log(u))))


def gumbel_softmax(logits, tau, key):
    """softmax((logits + G) / tau) with G = -log(-log U), U = jax.random.uniform(key, logits.shape). JAX in, JAX out."""
    u = jax.random.uniform(key, logits.shape, minval=1e-12, maxval=1.0)
    return jax.nn.softmax((logits - jnp.log(-jnp.log(u))) / tau)


def straight_through(logits, tau, key):
    """Straight-through Gumbel-softmax: the forward value is the one-hot argmax of gumbel_softmax(logits, tau, key),
    and the gradient is that of the soft sample: hard + soft - stop_gradient(soft)."""
    soft = gumbel_softmax(logits, tau, key)
    hard = jax.nn.one_hot(jnp.argmax(soft), logits.shape[0])
    return hard + soft - jax.lax.stop_gradient(soft)


def expectation_gradient(logits, values):
    """The exact gradient of E_{k ~ softmax(logits)} values[k] with respect to logits: p * (values - p . values)."""
    p = np.exp(np.asarray(logits, float) - logsumexp(logits))
    v = np.asarray(values, float)
    return p * (v - p @ v)


def reinforce_gradient(logits, values, samples):
    """The score-function (REINFORCE) estimate from sampled indices: mean over samples k of values[k] * (e_k - p)."""
    p = np.exp(np.asarray(logits, float) - logsumexp(logits))
    total = np.zeros_like(p)
    for k in samples:
        e = np.zeros_like(p)
        e[k] = 1.0
        total += values[k] * (e - p)
    return total / len(samples)


# ---------------------------------------------------------------- step 4 ---

def active_constraints(A, b, x, lam, tol=1e-7):
    """Indices i with b_i - (A x)_i <= tol and lam_i > tol (active and strictly complementary)."""
    slack = np.asarray(b, float) - np.asarray(A, float) @ np.asarray(x, float)
    return [i for i in range(len(b)) if slack[i] <= tol and lam[i] > tol]


def qp_argmin_jacobian(Q, A, b, x, lam, tol=1e-7):
    """For x*(q) = argmin 1/2 x^T Q x + q^T x subject to A x <= b, the Jacobian dx*/dq at a solution with
    multipliers lam. With the active set fixed, the KKT system [[Q, A_S^T], [A_S, 0]] [x; lam_S] = [-q; b_S] is
    linear in q, so differentiate it: solve [[Q, A_S^T], [A_S, 0]] [X; L] = [-I; 0] and return X (n x n)."""
    Q = np.asarray(Q, float)
    A = np.asarray(A, float)
    n = Q.shape[0]
    S = active_constraints(A, b, x, lam, tol)
    k = len(S)
    K = np.zeros((n + k, n + k))
    K[:n, :n] = Q
    if k:
        K[:n, n:] = A[S].T
        K[n:, :n] = A[S]
    rhs = np.zeros((n + k, n))
    rhs[:n, :] = -np.eye(n)
    return np.linalg.solve(K, rhs)[:n, :]


# ---------------------------------------------------------------- step 5 ---

def candidate_features(milp, node):
    """For each integer variable j with fractional LP value (fractionality > INT_TOL), the vector
    [fractionality (distance to the nearest integer), |c_j| / max |c|, sum_i |A_ij| / max over columns,
    the fractional part f, 1 - f]. Returns (list of candidate indices in increasing order, 2-D numpy array)."""
    _, _, lp = node
    c = np.abs(np.asarray(milp.c, float))
    A = np.abs(np.asarray(milp.A_ub, float)) if milp.A_ub else np.zeros((0, len(milp.c)))
    colsum = A.sum(axis=0) if A.size else np.zeros(len(milp.c))
    cmax = c.max() or 1.0
    amax = colsum.max() or 1.0
    idx, rows = [], []
    for j, (flag, v) in enumerate(zip(milp.integer, lp.x)):
        f = v - math.floor(v)
        frac = min(f, 1 - f)
        if flag and frac > INT_TOL:
            idx.append(j)
            rows.append([frac, c[j] / cmax, colsum[j] / amax, f, 1 - f])
    return idx, np.array(rows, float).reshape(len(rows), 5)


def collect_strong_branching(milp, node_limit=2000):
    """Run unit 07's branch_and_bound with strong branching, recording at every branching node the candidate
    features and the position (within the candidate list) of the variable strong branching chose. Returns a
    list of (features array, chosen position) pairs."""
    bb = unit("07")
    samples = []

    def recording_rule(m, node, stats):
        j = bb.strong_branching(m, node, stats)
        idx, feats = candidate_features(m, node)
        samples.append((feats, idx.index(j)))
        return j

    bb.branch_and_bound(milp, recording_rule, "best", node_limit=node_limit)
    return samples


def train_ranker(samples, epochs=300, lr=0.5):
    """A linear scorer w (5 numbers, starting at 0) trained by full-batch gradient descent on the mean over samples
    of the softmax cross-entropy of scores F w against the chosen position. Returns w."""
    w = np.zeros(5)
    for _ in range(epochs):
        grad = np.zeros(5)
        for F, chosen in samples:
            s = F @ w
            p = np.exp(s - logsumexp(s))
            grad += F.T @ (p - np.eye(len(p))[chosen])
        w -= lr * grad / len(samples)
    return w


def imitation_accuracy(w, samples):
    """Fraction of samples where argmax(F w) (ties: first) is the chosen position."""
    return sum(int(np.argmax(F @ w)) == chosen for F, chosen in samples) / len(samples)


def learned_rule(w):
    """A unit 07 branching rule that branches on the candidate with the highest score w . features (ties: lowest
    index)."""
    def rule(milp, node, stats):
        idx, F = candidate_features(milp, node)
        return idx[int(np.argmax(F @ w))]
    return rule
