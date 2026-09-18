"""Tests for unit 31. Run with `uv run co test 31`. You should not need to edit this."""

import itertools
import math
import random

import cvxpy as cp
import jax
import jax.numpy as jnp
import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from colib.bb import NodeLP, multi_knapsack, solve_node
from colib.mip import MILP
from colib.ref import unit
from colib.testing import load_lab, time_limit

jax.config.update("jax_enable_x64", True)
lab = load_lab(__file__)


def optimal_cost(C):
    r, c = linear_sum_assignment(C)
    return float(C[r, c].sum())


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(8))
def test_step1_sinkhorn_is_doubly_stochastic(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(3, 12))
    C = rng.uniform(0, 1, (n, n))
    P = lab.sinkhorn(C, 0.1, 400)
    assert P.shape == (n, n) and P.min() > 0
    assert np.allclose(P.sum(axis=0), 1, atol=1e-9), "columns exact after the last update"
    assert np.allclose(P.sum(axis=1), 1, atol=1e-6)
    logratio = np.log(P) + C / 0.1                     # (f_i + g_j) / eps: every row a shift of the first
    assert np.allclose(logratio - logratio[:, [0]], (logratio - logratio[:, [0]])[0], atol=1e-8)


def test_step1_one_iteration_by_hand():
    C = np.array([[0.0, 1.0], [2.0, 0.0]])
    eps = 1.0
    f = -eps * np.log(np.exp(-C / eps).sum(axis=1))
    g = -eps * np.log(np.exp((f[:, None] - C) / eps).sum(axis=0))
    assert np.allclose(lab.sinkhorn(C, eps, 1), np.exp((f[:, None] + g[None, :] - C) / eps))


@pytest.mark.parametrize("seed", range(8))
def test_step1_small_eps_recovers_the_assignment(seed):
    rng = np.random.default_rng(seed + 20)
    n = int(rng.integers(3, 9))
    C = rng.integers(0, 50, (n, n)).astype(float) + rng.uniform(0, 1e-3, (n, n))
    perm = lab.round_to_permutation(lab.sinkhorn(C, 0.02, 3000))
    assert sorted(perm) == list(range(n))
    assert lab.assignment_cost(C, perm) == pytest.approx(optimal_cost(C))


def test_step1_rounding_is_greedy_on_largest_entries():
    P = np.array([[0.5, 0.4, 0.1], [0.45, 0.1, 0.45], [0.05, 0.5, 0.45]])
    assert lab.round_to_permutation(P) == [0, 2, 1]
    assert lab.round_to_permutation(np.full((3, 3), 1 / 3)) == [0, 1, 2]


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(4))
def test_step2_entropic_cost_value(seed):
    rng = np.random.default_rng(seed + 40)
    C = rng.uniform(0, 1, (5, 5))
    P = lab.sinkhorn(C, 0.2, 200)
    expected = float((C * P).sum() + 0.2 * (P * (np.log(P) - 1)).sum())
    assert float(lab.entropic_cost(jnp.asarray(C), 0.2, 200)) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize("seed", range(5))
def test_step2_gradient_is_the_plan(seed):
    rng = np.random.default_rng(seed + 50)
    n = int(rng.integers(3, 8))
    C = rng.uniform(0, 1, (n, n))
    G = lab.entropic_gradient(C, 0.1, 400)
    assert isinstance(G, np.ndarray) and G.shape == (n, n)
    assert np.allclose(G, lab.sinkhorn(C, 0.1, 400), atol=1e-6), "envelope theorem: the gradient is P"
    h = 1e-6
    i, j = int(rng.integers(n)), int(rng.integers(n))
    up, dn = C.copy(), C.copy()
    up[i, j] += h
    dn[i, j] -= h
    numeric = (float(lab.entropic_cost(up, 0.1, 400)) - float(lab.entropic_cost(dn, 0.1, 400))) / (2 * h)
    assert G[i, j] == pytest.approx(numeric, rel=1e-5, abs=1e-8)


# ---------------------------------------------------------------- step 3 ---

def test_step3_gumbel_max_matches_softmax():
    logits = np.array([1.0, 0.0, -1.0, 2.0])
    p = np.exp(logits) / np.exp(logits).sum()
    rng = np.random.default_rng(0)
    counts = np.bincount([lab.gumbel_max_sample(logits, rng) for _ in range(20000)], minlength=4) / 20000
    assert np.all(np.abs(counts - p) < 5 * np.sqrt(p * (1 - p) / 20000))


def test_step3_gumbel_softmax_and_straight_through():
    logits = jnp.array([0.5, 1.5, -0.3])
    key = jax.random.PRNGKey(3)
    soft = lab.gumbel_softmax(logits, 0.5, key)
    assert float(soft.sum()) == pytest.approx(1.0) and float(soft.min()) > 0
    u = jax.random.uniform(key, logits.shape, minval=1e-12, maxval=1.0)
    assert np.allclose(soft, jax.nn.softmax((logits - jnp.log(-jnp.log(u))) / 0.5))
    cold = lab.gumbel_softmax(logits, 1e-3, key)
    assert float(cold.max()) > 0.999, "tau -> 0 approaches one-hot"
    hard = lab.straight_through(logits, 0.5, key)
    assert sorted(np.asarray(hard).tolist()) == [0.0, 0.0, 1.0] and int(jnp.argmax(hard)) == int(jnp.argmax(soft))
    w = jnp.array([1.0, -2.0, 0.5])
    g_st = jax.grad(lambda l: jnp.dot(w, lab.straight_through(l, 0.5, key)))(logits)
    g_soft = jax.grad(lambda l: jnp.dot(w, lab.gumbel_softmax(l, 0.5, key)))(logits)
    assert np.allclose(g_st, g_soft), "straight-through: the soft sample's gradient"


@pytest.mark.parametrize("seed", range(5))
def test_step3_exact_expectation_gradient(seed):
    rng = np.random.default_rng(seed)
    logits = rng.standard_normal(5)
    values = rng.standard_normal(5)
    g = lab.expectation_gradient(logits, values)
    ref = jax.grad(lambda l: jnp.dot(jax.nn.softmax(l), jnp.asarray(values)))(jnp.asarray(logits))
    assert np.allclose(g, ref)


def test_step3_reinforce_is_unbiased():
    logits = np.array([0.3, -0.7, 1.1, 0.0])
    values = np.array([2.0, -1.0, 0.5, 4.0])
    p = np.exp(logits) / np.exp(logits).sum()
    rng = np.random.default_rng(1)
    samples = rng.choice(4, size=40000, p=p)
    estimate = lab.reinforce_gradient(logits, values, samples)
    exact = lab.expectation_gradient(logits, values)
    assert np.allclose(estimate, exact, atol=0.02)
    single = lab.reinforce_gradient(logits, values, [2])
    assert np.allclose(single, values[2] * (np.eye(4)[2] - p))


# ---------------------------------------------------------------- step 4 ---

def solve_qp(Q, q, A, b):
    x = cp.Variable(len(q))
    con = [A @ x <= b]
    cp.Problem(cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) + q @ x), con).solve(solver="CLARABEL",
                                                                                       tol_gap_abs=1e-12, tol_gap_rel=1e-12, tol_feas=1e-12)
    return x.value, con[0].dual_value


def random_qp(seed, n=5, m=6):
    rng = np.random.default_rng(seed)
    B = rng.standard_normal((n, n))
    Q = B @ B.T + np.eye(n)
    return Q, rng.standard_normal(n) * 3, rng.standard_normal((m, n)), rng.uniform(0.1, 1.0, m)


def test_step4_active_constraints():
    A = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    b = np.array([1.0, 2.0, 5.0])
    assert lab.active_constraints(A, b, [1.0, 2.0], [0.5, 0.0, 0.0]) == [0], "constraint 1 is tight but not strictly complementary"
    assert lab.active_constraints(A, b, [1.0, 2.0], [0.5, 0.2, 0.1]) == [0, 1]


@pytest.mark.parametrize("seed", range(8))
def test_step4_jacobian_matches_finite_differences(seed):
    Q, q, A, b = random_qp(seed)
    x, lam = solve_qp(Q, q, A, b)
    S = lab.active_constraints(A, b, x, lam, tol=1e-6)
    J = lab.qp_argmin_jacobian(Q, A, b, x, lam, tol=1e-6)
    assert J.shape == (5, 5)
    h = 1e-5
    for k in range(5):
        e = np.zeros(5)
        e[k] = h
        xp, _ = solve_qp(Q, q + e, A, b)
        xm, _ = solve_qp(Q, q - e, A, b)
        assert np.allclose(J[:, k], (xp - xm) / (2 * h), atol=1e-4), f"column {k}, active set {S}"


def test_step4_unconstrained_and_fully_constrained():
    Q = np.array([[2.0, 0.0], [0.0, 4.0]])
    A = np.array([[1.0, 0.0]])
    J = lab.qp_argmin_jacobian(Q, A, [10.0], [0.0, 0.0], [0.0])
    assert np.allclose(J, -np.linalg.inv(Q)), "no active constraint: dx/dq = -Q^-1"
    J = lab.qp_argmin_jacobian(Q, A, [1.0], [1.0, 0.0], [3.0])
    assert np.allclose(J, [[0.0, 0.0], [0.0, -0.25]]), "x_1 pinned by the active constraint"


# ---------------------------------------------------------------- step 5 ---

def test_step5_candidate_features():
    milp = MILP(c=(-4.0, -2.0, -1.0), A_ub=((1.0, 2.0, 3.0), (2.0, 0.0, 2.0)), b_ub=(4.0, 3.0),
                ub=(1, 1, 1), integer=(True, False, True))
    node = ((0, 0, 0), (1, 1, 1), NodeLP("optimal", 0.0, (0.25, 0.5, 0.9)))
    idx, F = lab.candidate_features(milp, node)
    assert idx == [0, 2], "only fractional integer variables"
    assert np.allclose(F[0], [0.25, 1.0, 3 / 5, 0.25, 0.75]), "column sums 3, 2, 5 are scaled by their own maximum"
    assert np.allclose(F[1], [0.1, 0.25, 1.0, 0.9, 0.1])


def test_step5_collection_records_strong_branching_choices():
    bb = unit("07")
    milp = multi_knapsack(12, 3, 4)
    samples = lab.collect_strong_branching(milp, node_limit=300)
    assert samples
    choices = []

    def spy(m, node, stats):
        j = bb.strong_branching(m, node, stats)
        idx, _ = lab.candidate_features(m, node)
        choices.append(idx.index(j))
        return j
    bb.branch_and_bound(milp, spy, "best", node_limit=300)
    assert [c for _, c in samples] == choices
    assert all(F.shape[1] == 5 and 0 <= c < F.shape[0] for F, c in samples)


def test_step5_ranker_learns_the_informative_feature():
    rng = np.random.default_rng(0)
    samples = []
    for _ in range(200):
        k = int(rng.integers(2, 8))
        F = rng.uniform(0, 1, (k, 5))
        samples.append((F, int(np.argmax(F[:, 2]))))       # the choice is the candidate with the largest feature 2
    w = lab.train_ranker(samples, epochs=300, lr=0.5)
    assert w[2] == max(w) and w[2] > 1
    assert lab.imitation_accuracy(w, samples) >= 0.8
    assert lab.imitation_accuracy(np.zeros(5), samples) < 0.4, "ties go to the first candidate"


def test_step5_ranker_gradient_step():
    F = np.array([[1.0, 0, 0, 0, 0], [0, 1.0, 0, 0, 0]])
    w = lab.train_ranker([(F, 1)], epochs=1, lr=1.0)
    assert np.allclose(w, [-0.5, 0.5, 0, 0, 0]), "one step from zero: -(p - onehot) with p uniform"
    w = lab.train_ranker([(F, 1), (F, 0), (F, 1)], epochs=1, lr=1.0)
    assert np.allclose(w, [-1 / 6, 1 / 6, 0, 0, 0]), "the gradient is averaged over samples"


@pytest.mark.parametrize("seed", range(3))
def test_step5_learned_rule_is_a_valid_rule(seed):
    bb = unit("07")
    milp = multi_knapsack(12, 3, seed + 10)
    w = np.array([1.0, 0.3, 0.2, 0.0, 0.0])
    rule = lab.learned_rule(w)
    lb, ub = (tuple(float(v) for v in bounds) for bounds in milp.bounds())
    root = solve_node(milp, lb, ub)
    j = rule(milp, (lb, ub, root), {"lp_solves": 0, "pseudo": {}})
    idx, F = lab.candidate_features(milp, (lb, ub, root))
    assert j == idx[int(np.argmax(F @ w))]
    with time_limit(60):
        result = bb.branch_and_bound(milp, rule, "best")
        reference = bb.branch_and_bound(milp, bb.most_fractional, "best")
    assert result.status == "optimal" and result.value == pytest.approx(reference.value)
