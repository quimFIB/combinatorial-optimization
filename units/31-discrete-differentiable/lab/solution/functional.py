"""Unit 31 lab — where discrete meets differentiable.  REFERENCE SOLUTION, functional.

Sinkhorn is a fold over iterations on the potential g; rounding is a fold over entries sorted by size; the
estimators are single expressions; the ranker is a fold over epochs. The one stateful piece is the
strong-branching recorder, which has to observe unit 07's tree as it runs: it appends to a local list.
"""

from __future__ import annotations

import math
from functools import reduce

import jax
import jax.numpy as jnp
import numpy as np
from scipy.special import logsumexp

from colib.bb import INT_TOL
from colib.ref import unit

jax.config.update("jax_enable_x64", True)


# ---------------------------------------------------------------- step 1 ---

def _potentials(C, eps, iterations, lse, xp):
    def update(fg, _):
        _, g = fg
        f = -eps * lse((g[None, :] - C) / eps, axis=1)
        return f, -eps * lse((f[:, None] - C) / eps, axis=0)
    return reduce(update, range(iterations), (None, xp.zeros(C.shape[1])))


def sinkhorn(C, eps, iterations):
    C = np.asarray(C, float)
    f, g = _potentials(C, eps, iterations, logsumexp, np)
    return np.exp((f[:, None] + g[None, :] - C) / eps)


def round_to_permutation(P):
    n = P.shape[0]
    entries = sorted((-P[i, j], i, j) for i in range(n) for j in range(n))

    def take(state, entry):
        perm, used = state
        _, i, j = entry
        return (perm | {i: j}, used | {j}) if i not in perm and j not in used else state

    perm, _ = reduce(take, entries, ({}, frozenset()))
    return [perm[i] for i in range(n)]


def assignment_cost(C, perm):
    return float(sum(C[i][j] for i, j in enumerate(perm)))


# ---------------------------------------------------------------- step 2 ---

def entropic_cost(C, eps, iterations):
    from jax.scipy.special import logsumexp as jlse
    C = jnp.asarray(C)
    f, g = _potentials(C, eps, iterations, jlse, jnp)
    logP = (f[:, None] + g[None, :] - C) / eps
    P = jnp.exp(logP)
    return jnp.sum(C * P) + eps * jnp.sum(P * (logP - 1))


def entropic_gradient(C, eps, iterations):
    return np.asarray(jax.grad(lambda c: entropic_cost(c, eps, iterations))(jnp.asarray(C, dtype=float)))


# ---------------------------------------------------------------- step 3 ---

def gumbel_max_sample(logits, rng):
    return int(np.argmax(np.asarray(logits) - np.log(-np.log(rng.random(len(logits))))))


def gumbel_softmax(logits, tau, key):
    u = jax.random.uniform(key, logits.shape, minval=1e-12, maxval=1.0)
    return jax.nn.softmax((logits - jnp.log(-jnp.log(u))) / tau)


def straight_through(logits, tau, key):
    soft = gumbel_softmax(logits, tau, key)
    return jax.nn.one_hot(jnp.argmax(soft), logits.shape[0]) + soft - jax.lax.stop_gradient(soft)


def _probabilities(logits):
    return np.exp(np.asarray(logits, float) - logsumexp(logits))


def expectation_gradient(logits, values):
    p, v = _probabilities(logits), np.asarray(values, float)
    return p * (v - p @ v)


def reinforce_gradient(logits, values, samples):
    p = _probabilities(logits)
    return sum((values[k] * (np.eye(len(p))[k] - p) for k in samples), np.zeros_like(p)) / len(samples)


# ---------------------------------------------------------------- step 4 ---

def active_constraints(A, b, x, lam, tol=1e-7):
    slack = np.asarray(b, float) - np.asarray(A, float) @ np.asarray(x, float)
    return [i for i, (s, l) in enumerate(zip(slack, lam)) if s <= tol and l > tol]


def qp_argmin_jacobian(Q, A, b, x, lam, tol=1e-7):
    Q, A = np.asarray(Q, float), np.asarray(A, float)
    n = Q.shape[0]
    AS = A[active_constraints(A, b, x, lam, tol)].reshape(-1, n)
    k = AS.shape[0]
    K = np.block([[Q, AS.T], [AS, np.zeros((k, k))]])
    rhs = np.vstack([-np.eye(n), np.zeros((k, n))])
    return np.linalg.solve(K, rhs)[:n, :]


# ---------------------------------------------------------------- step 5 ---

def candidate_features(milp, node):
    _, _, lp = node
    c = np.abs(np.asarray(milp.c, float))
    colsum = np.abs(np.asarray(milp.A_ub, float)).sum(axis=0) if milp.A_ub else np.zeros(len(milp.c))
    cmax, amax = (c.max() or 1.0), (colsum.max() or 1.0)
    frac = lambda v: min(v - math.floor(v), math.ceil(v) - v)
    idx = [j for j, (flag, v) in enumerate(zip(milp.integer, lp.x)) if flag and frac(v) > INT_TOL]
    rows = [[frac(lp.x[j]), c[j] / cmax, colsum[j] / amax, lp.x[j] - math.floor(lp.x[j]),
             1 - (lp.x[j] - math.floor(lp.x[j]))] for j in idx]
    return idx, np.array(rows, float).reshape(len(rows), 5)


def collect_strong_branching(milp, node_limit=2000):
    bb = unit("07")
    samples = []                        # the recorder has to observe the tree while it runs

    def recording_rule(m, node, stats):
        j = bb.strong_branching(m, node, stats)
        idx, feats = candidate_features(m, node)
        samples.append((feats, idx.index(j)))
        return j

    bb.branch_and_bound(milp, recording_rule, "best", node_limit=node_limit)
    return samples


def train_ranker(samples, epochs=300, lr=0.5):
    def grad(w):
        def one(F, chosen):
            s = F @ w
            return F.T @ (np.exp(s - logsumexp(s)) - np.eye(len(s))[chosen])
        return sum((one(F, c) for F, c in samples), np.zeros(5)) / len(samples)
    return reduce(lambda w, _: w - lr * grad(w), range(epochs), np.zeros(5))


def imitation_accuracy(w, samples):
    return sum(int(np.argmax(F @ w)) == chosen for F, chosen in samples) / len(samples)


def learned_rule(w):
    def rule(milp, node, stats):
        idx, F = candidate_features(milp, node)
        return idx[int(np.argmax(F @ w))]
    return rule
