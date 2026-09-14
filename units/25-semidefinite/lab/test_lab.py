"""Tests for unit 25. Run with `uv run co test 25`. You should not need to edit this."""

import itertools
import math
import random

import networkx as nx
import numpy as np
import pytest

from colib.oracle import brute_force
from colib.problems import MaxCut
from colib.testing import load_lab

lab = load_lab(__file__)


def cycle(n):
    return MaxCut(n, tuple((i, (i + 1) % n) if i + 1 < n else (0, n - 1) for i in range(n)), (1,) * n)


def small_maxcut(seed, low=4, high=11):
    r = random.Random(seed)
    mc = MaxCut.random(r.randint(low, high), seed=seed, p=r.choice([0.3, 0.5, 0.8]))
    return mc if mc.edges else MaxCut(2, ((0, 1),), (3,))


def alpha_brute(n, edges):
    E = {tuple(sorted(e)) for e in edges}
    return max(len(S) for k in range(n + 1) for S in itertools.combinations(range(n), k)
               if all((a, b) not in E for a, b in itertools.combinations(S, 2)))


def chromatic_brute(n, edges):
    for k in range(1, n + 1):
        for col in itertools.product(range(k), repeat=n - 1):
            col = (0,) + col
            if all(col[u] != col[v] for u, v in edges):
                return k
    return n


# ---------------------------------------------------------------- step 1 ---

def test_step1_weight_matrix():
    mc = MaxCut(3, ((0, 1), (1, 2)), (4, 7))
    W = lab.weight_matrix(mc)
    assert np.array_equal(np.asarray(W), np.array([[0, 4, 0], [4, 0, 7], [0, 7, 0]]))


@pytest.mark.parametrize("seed", range(12))
def test_step1_sdp_is_a_relaxation(seed):
    mc = small_maxcut(seed)
    value, X = lab.maxcut_sdp(mc)
    X = np.asarray(X)
    assert X.shape == (mc.n, mc.n)
    assert np.allclose(np.diag(X), 1, atol=1e-5)
    assert np.linalg.eigvalsh((X + X.T) / 2).min() >= -1e-5
    recomputed = sum(w * (1 - X[u, v]) / 2 for (u, v), w in zip(mc.edges, mc.weights))
    assert abs(value - recomputed) <= 1e-4 * max(1, value)
    opt = brute_force(mc).value
    assert opt - 1e-4 <= value <= sum(mc.weights) + 1e-4


def test_step1_known_values():
    assert lab.maxcut_sdp(cycle(5))[0] == pytest.approx(5 * (1 - math.cos(4 * math.pi / 5)) / 2, abs=1e-4)
    assert lab.maxcut_sdp(cycle(6))[0] == pytest.approx(6, abs=1e-4), "bipartite: the SDP is exact"
    k3 = MaxCut(3, ((0, 1), (1, 2), (0, 2)), (1, 1, 1))
    assert lab.maxcut_sdp(k3)[0] == pytest.approx(2.25, abs=1e-4)


@pytest.mark.parametrize("seed", range(8))
def test_step1_vectors_reproduce_the_gram_matrix(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(3, 12))
    B = rng.standard_normal((n, n))
    G = B @ B.T
    d = np.sqrt(np.diag(G))
    X = G / np.outer(d, d)
    X = X - 1e-9 * np.eye(n)             # a tiny negative perturbation, as a solver might return
    V = np.asarray(lab.vectors_from_gram(X))
    assert V.shape[0] == n
    assert np.allclose(np.linalg.norm(V, axis=1), 1, atol=1e-9)
    assert np.allclose(V @ V.T, X, atol=1e-5)


def test_step1_vectors_repair_a_slightly_indefinite_matrix():
    # unit diagonal but one negative eigenvalue: clip it, rebuild, and renormalise the rows
    X = np.array([[1.0, 0.9, 0.9], [0.9, 1.0, -0.2], [0.9, -0.2, 1.0]])
    vals, vecs = np.linalg.eigh(X)
    assert vals.min() < -0.05
    P = vecs @ np.diag(np.clip(vals, 0, None)) @ vecs.T
    d = 1 / np.sqrt(np.diag(P))
    V = np.asarray(lab.vectors_from_gram(X))
    assert np.allclose(np.linalg.norm(V, axis=1), 1, atol=1e-9)
    assert np.allclose(V @ V.T, P * np.outer(d, d), atol=1e-9)


def test_step1_vectors_from_a_rank_deficient_solution():
    X = np.array([[1, -1, 1], [-1, 1, -1], [1, -1, 1]], float) + np.diag([-1e-10, 2e-10, 0])
    V = np.asarray(lab.vectors_from_gram(X))
    assert np.allclose(V @ V.T, np.round(X), atol=1e-4)


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(6))
def test_step2_rounding_matches_its_expectation(seed):
    mc = small_maxcut(seed + 30, 6, 11)
    _, X = lab.maxcut_sdp(mc)
    V = np.asarray(lab.vectors_from_gram(X))
    rng = np.random.default_rng(seed)
    samples = [mc.objective(lab.hyperplane_round(V, rng)) for _ in range(3000)]
    for _ in range(3):
        x = lab.hyperplane_round(V, rng)
        assert len(x) == mc.n and set(x) <= {0, 1}
    mean, sd = np.mean(samples), np.std(samples) / math.sqrt(len(samples))
    expected = lab.expected_cut(mc, V)
    assert abs(mean - expected) <= 5 * sd + 1e-3 * max(1.0, expected)   # solver precision when the SDP is integral


def test_step2_rounding_uses_a_uniform_direction():
    # three vectors 120 degrees apart in the plane: every pair is cut with probability 2/3
    V = np.array([[1, 0], [-0.5, math.sqrt(3) / 2], [-0.5, -math.sqrt(3) / 2]])
    mc = MaxCut(3, ((0, 1), (1, 2), (0, 2)), (1, 1, 1))
    rng = np.random.default_rng(1)
    cut01 = sum(len(set(x[:2])) == 2 for x in (lab.hyperplane_round(V, rng) for _ in range(6000))) / 6000
    assert abs(cut01 - 2 / 3) < 0.03
    assert lab.expected_cut(mc, V) == pytest.approx(2.0)


def test_step2_ties_at_zero_go_to_side_one():
    class Fixed:
        def standard_normal(self, size):
            return np.array([1.0, 0.0])[:size]
    V = np.array([[0.0, 1.0], [1.0, 0.0], [-1.0, 0.0]])
    assert lab.hyperplane_round(V, Fixed()) == [1, 1, 0]


def test_step2_gw_constant():
    alpha, theta = lab.gw_constant()
    assert alpha == pytest.approx(0.8785672, abs=2e-6)
    assert theta == pytest.approx(2.3311223, abs=1e-4)


@pytest.mark.parametrize("seed", range(10))
def test_step2_expected_cut_beats_alpha_times_sdp(seed):
    mc = small_maxcut(seed + 50)
    value, X = lab.maxcut_sdp(mc)
    V = np.asarray(lab.vectors_from_gram(X))
    alpha, _ = lab.gw_constant()
    assert lab.expected_cut(mc, V) >= alpha * value - 1e-3


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(10))
def test_step3_edge_lp_is_useless(seed):
    mc = small_maxcut(seed + 70)
    assert lab.maxcut_edge_lp(mc) == pytest.approx(sum(mc.weights), abs=1e-6)


def test_step3_triangle_lp_on_cycles_and_k4():
    assert lab.maxcut_triangle_lp(cycle(5)) == pytest.approx(4, abs=1e-6)
    assert lab.maxcut_triangle_lp(cycle(7)) == pytest.approx(6, abs=1e-6)
    k4 = MaxCut(4, tuple(itertools.combinations(range(4), 2)), (1,) * 6)
    assert lab.maxcut_triangle_lp(k4) == pytest.approx(4, abs=1e-6)
    k5 = MaxCut(5, tuple(itertools.combinations(range(5), 2)), (1,) * 10)
    assert lab.maxcut_triangle_lp(k5) == pytest.approx(20 / 3, abs=1e-6), "K5: all z = 2/3"


@pytest.mark.parametrize("seed", range(10))
def test_step3_triangle_lp_sits_between(seed):
    mc = small_maxcut(seed + 90, 5, 10)
    tri = lab.maxcut_triangle_lp(mc)
    assert brute_force(mc).value - 1e-6 <= tri <= lab.maxcut_edge_lp(mc) + 1e-6


def test_step3_triangle_lp_rotations():
    # with negative weights the LP wants some z small, and each of the three rotated inequalities
    # z_ij <= z_ik + z_jk is what stops a different one: every triangle cut has exactly 0 or 2 edges
    triangle = ((0, 1), (1, 2), (0, 2))
    for weights, value in (((5, -3, -1), 4), ((-3, 4, -4), 1), ((-1, -1, 5), 4)):
        assert lab.maxcut_triangle_lp(MaxCut(3, triangle, weights)) == pytest.approx(value, abs=1e-6)


# ---------------------------------------------------------------- step 4 ---

def test_step4_theta_known_values():
    c5 = [(i, (i + 1) % 5) for i in range(5)]
    assert lab.lovasz_theta(5, c5) == pytest.approx(math.sqrt(5), abs=1e-4)
    assert lab.lovasz_theta(10, list(nx.petersen_graph().edges())) == pytest.approx(4, abs=1e-4)
    assert lab.lovasz_theta(4, []) == pytest.approx(4, abs=1e-4), "empty graph: theta = n"
    assert lab.lovasz_theta(4, list(itertools.combinations(range(4), 2))) == pytest.approx(1, abs=1e-4)


def test_step4_complement():
    assert lab.complement(4, [(1, 0), (2, 3)]) == [(0, 2), (0, 3), (1, 2), (1, 3)]


@pytest.mark.parametrize("seed", range(10))
def test_step4_sandwich(seed):
    r = random.Random(seed)
    n = r.randint(4, 8)
    edges = [(u, v) for u, v in itertools.combinations(range(n), 2) if r.random() < 0.45]
    theta = lab.lovasz_theta(n, edges)
    assert alpha_brute(n, edges) - 1e-4 <= theta <= chromatic_brute(n, lab.complement(n, edges)) + 1e-4


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(15))
def test_step5_local_search(seed):
    mc = small_maxcut(seed + 120, 5, 14)
    r = random.Random(seed)
    x0 = [r.randint(0, 1) for _ in range(mc.n)]
    x = lab.local_search(mc, x0)
    assert len(x) == mc.n and set(x) <= {0, 1}
    assert mc.objective(x) >= mc.objective(x0)
    for v in range(mc.n):
        y = list(x)
        y[v] = 1 - y[v]
        assert mc.objective(y) <= mc.objective(x), "no single flip improves"
    assert 2 * mc.objective(x) >= sum(mc.weights), "a local optimum cuts at least half the weight"


def test_step5_local_search_takes_the_first_improving_flip():
    mc = MaxCut(3, ((0, 1), (1, 2)), (1, 5))
    x0 = [0, 0, 0]
    # flip 0 (gain 1), then 1 (gain 5 - 1), then 0 again (gain 1): the scan restarts after every flip
    assert lab.local_search(mc, x0) == [0, 1, 0]
    assert x0 == [0, 0, 0], "the input is not modified"
    mc = MaxCut(4, ((0, 1), (2, 3), (1, 2)), (1, 1, 1))
    assert lab.local_search(mc, [0, 0, 0, 0]) == [1, 0, 1, 0]
    mc = MaxCut(5, ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (2, 4)), (4, 3, 3, 3, 4, 2))
    assert lab.local_search(mc, [0] * 5) == [0, 1, 1, 0, 0], "restart the scan from vertex 0 after each flip"


@pytest.mark.parametrize("seed", range(6))
def test_step5_goemans_williamson(seed):
    mc = small_maxcut(seed + 150, 6, 12)
    rng = np.random.default_rng(seed)
    x, w, value = lab.goemans_williamson(mc, 30, rng)
    assert mc.objective(x) == w
    assert value == pytest.approx(lab.maxcut_sdp(mc)[0], abs=1e-4)
    alpha, _ = lab.gw_constant()
    assert w >= alpha * brute_force(mc).value - 1e-6   # best of 30 rounds, fixed seeds
