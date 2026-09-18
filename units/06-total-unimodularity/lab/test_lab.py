"""Tests for unit 06. Run with `uv run co test 06`. You should not need to edit this."""

import random
from itertools import combinations, product

import networkx as nx
import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)


def tu_reference(A):
    A = np.array(A)
    m, n = A.shape
    return all(round(np.linalg.det(A[np.ix_(r, c)])) in (-1, 0, 1)
               for k in range(1, min(m, n) + 1) for r in combinations(range(m), k)
               for c in combinations(range(n), k))


def random_matrix(seed):
    r = random.Random(seed)
    m, n = r.randint(2, 4), r.randint(2, 5)
    return [[r.choice((-1, 0, 0, 1)) for _ in range(n)] for _ in range(m)]


def directed_incidence(n, arcs):
    return [[(1 if a[0] == v else -1 if a[1] == v else 0) for a in arcs] for v in range(n)]


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("A, want", [
    ([[1, 1, 0], [0, 1, 1], [1, 0, 1]], False),              # triangle incidence (T of the slides, transposed): det 2
    ([[1, 1], [-1, 1]], False),
    ([[2]], False),
    ([[1, 1, 0], [0, 1, 1]], True),                          # path incidence
    ([[1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]], True),     # consecutive ones
    (directed_incidence(4, [(0, 1), (1, 2), (2, 0), (2, 3)]), True),  # network matrix
])
def test_step1_known_matrices(A, want):
    assert lab.is_tu(A) is want


@pytest.mark.parametrize("seed", range(40))
def test_step1_random_matrices(seed):
    A = random_matrix(seed)
    assert lab.is_tu(A) == tu_reference(A)


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(60))
def test_step2_ghouila_houri_agrees_and_its_witness_is_real(seed):
    A = random_matrix(seed)
    w = lab.ghouila_houri(A)
    assert (w is None) == tu_reference(A)
    if w is not None:
        rows = tuple(w)
        assert rows and all(0 <= r < len(A) for r in rows)
        for sigma in product((1, -1), repeat=len(rows)):
            sums = [sum(s * A[r][j] for s, r in zip(sigma, rows)) for j in range(len(A[0]))]
            assert any(abs(v) > 1 for v in sums), f"rows {rows} do have an equitable signing {sigma}"


# ---------------------------------------------------------------- step 3 ---

def test_step3_incidence_and_interval_shapes():
    M = lab.incidence_matrix(3, [(0, 1), (1, 2)])
    assert [list(r) for r in M] == [[1, 0], [1, 1], [0, 1]]
    I = lab.interval_matrix(5, [(0, 2), (1, 5)])
    assert [list(r) for r in I] == [[1, 1, 0, 0, 0], [0, 1, 1, 1, 1]]


@pytest.mark.parametrize("seed", range(30))
def test_step3_incidence_is_tu_exactly_for_bipartite_graphs(seed):
    G = nx.gnp_random_graph(5, 0.5, seed=seed)
    edges = list(G.edges())
    if not edges:
        return
    assert tu_reference(lab.incidence_matrix(5, edges)) == nx.is_bipartite(G)


@pytest.mark.parametrize("seed", range(10))
def test_step3_interval_matrices_are_tu(seed):
    r = random.Random(seed)
    intervals = [tuple(sorted(r.sample(range(7), 2))) for _ in range(4)]
    assert tu_reference(lab.interval_matrix(6, intervals))


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(10))
def test_step4_assignment_lp_is_integral_and_optimal(seed):
    C = np.random.default_rng(seed).integers(1, 60, (6, 6))
    X = lab.assignment_lp(C.tolist())
    assert X.shape == (6, 6)
    assert np.allclose(X, np.round(X), atol=1e-7), "no integrality was imposed, yet the LP vertex is integral"
    assert np.allclose(X.sum(0), 1) and np.allclose(X.sum(1), 1)
    r, c = linear_sum_assignment(C)
    assert abs((C * X).sum() - C[r, c].sum()) < 1e-6


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(60))
def test_step5_odd_cycle(seed):
    G = nx.gnp_random_graph(8, 0.35, seed=seed)
    edges = list(G.edges())
    cyc = lab.odd_cycle(8, edges)
    if nx.is_bipartite(G):
        assert cyc is None
        return
    E = {frozenset(e) for e in edges}
    cyc = list(cyc)
    assert len(cyc) % 2 == 1 and len(set(cyc)) == len(cyc) >= 3
    assert all(frozenset((cyc[i], cyc[(i + 1) % len(cyc)])) in E for i in range(len(cyc)))


@pytest.mark.parametrize("k", [3, 5, 7])
def test_step5_half_integral_vertex_on_an_odd_cycle(k):
    edges = [(i, (i + 1) % k) for i in range(k)]
    cyc = lab.odd_cycle(k, edges)
    frac = lab.fractional_matching_on_cycle(cyc)
    A = lab.incidence_matrix(k, edges)
    res = highs_lp(A, [1] * k, [1] * len(edges), sense="max")   # max matching LP
    assert abs(res.value - k / 2) < 1e-9, "LP optimum on an odd cycle is k/2, above the integer optimum (k-1)/2"
    lp = {frozenset(e): v for e, v in zip(edges, res.x)}
    assert set(frac) == set(lp) and all(abs(frac[e] - lp[e]) < 1e-9 for e in lp)
