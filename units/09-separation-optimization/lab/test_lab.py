"""Tests for unit 09. Run with `uv run co test 09`. You should not need to edit this."""

import itertools
from dataclasses import replace
from functools import lru_cache

import networkx as nx
import numpy as np
import pytest

from colib import TSP, brute_force
from colib.mip import lp_relaxation
from colib.testing import load_lab, time_limit
from colib.tsp import degree_milp, edges, tour_length

lab = load_lab(__file__)


def cut_weight(n, x, S):
    S = set(S)
    return sum(v for (i, j), v in zip(edges(n), x) if (i in S) != (j in S))


@lru_cache(maxsize=None)
def full_subtour_lp(seed, n):
    t = TSP.random(n, seed=seed)
    rows, rhs = [], []
    for k in range(1, n):
        for S in itertools.combinations(range(n), k):
            if 0 in S:
                r = tuple(-1 if (i in S) != (j in S) else 0 for i, j in edges(n))
                rows.append(r)
                rhs.append(-2)
    return lp_relaxation(replace(degree_milp(t, False), A_ub=tuple(rows), b_ub=tuple(rhs))).value


# ---------------------------------------------------------------- step 1 ---

def test_step1_subtour_row():
    n = 4
    row, rhs = lab.subtour_row(n, (0, 1))
    assert rhs == -2
    crossing = {e for e, v in zip(edges(n), row) if v == -1}
    assert crossing == {(0, 2), (0, 3), (1, 2), (1, 3)} and all(v in (0, -1) for v in row)


@pytest.mark.parametrize("seed", range(20))
def test_step1_components(seed):
    n = 9
    rng = np.random.default_rng(seed)
    x = rng.random(len(edges(n))) * (rng.random(len(edges(n))) < 0.25)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(e for e, v in zip(edges(n), x) if v > 1e-6)
    want = sorted(tuple(sorted(c)) for c in nx.connected_components(G))
    assert sorted(tuple(sorted(c)) for c in lab.components(n, x)) == want


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(30))
def test_step2_min_cut_matches_networkx(seed):
    n = 8
    rng = np.random.default_rng(seed)
    x = np.round(rng.random(len(edges(n))) * (rng.random(len(edges(n))) < 0.6), 3)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_weighted_edges_from((i, j, float(v)) for (i, j), v in zip(edges(n), x) if v > 0)
    value, S = lab.min_cut(n, x)
    want = nx.stoer_wagner(G)[0] if nx.is_connected(G) else 0.0      # a disconnected support has a cut of weight 0
    assert abs(value - want) < 1e-9
    assert 0 < len(S) < n and abs(cut_weight(n, x, S) - value) < 1e-9, "S must realize the reported value"


# ---------------------------------------------------------------- step 3 ---

def test_step3_disconnected_support_gives_every_component():
    n = 6
    x = [0.0] * len(edges(n))
    idx = {e: k for k, e in enumerate(edges(n))}
    for e in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]:
        x[idx[e]] = 1.0                                   # two triangles
    found = sorted(tuple(sorted(S)) for S in lab.separate_subtours(n, x))
    assert found == [(0, 1, 2), (3, 4, 5)]


def test_step3_connected_but_violated_and_satisfied():
    n = 6
    idx = {e: k for k, e in enumerate(edges(n))}
    x = [0.0] * len(edges(n))
    for e in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]:
        x[idx[e]] = 1.0
    x[idx[(2, 3)]] = 0.5                                  # a thin bridge: connected, cut value 0.5
    S = lab.separate_subtours(n, x)
    assert len(S) == 1 and cut_weight(n, x, S[0]) < 2
    tour = [0.0] * len(edges(n))
    for k in range(n):
        tour[idx[tuple(sorted((k, (k + 1) % n)))]] = 1.0
    assert lab.separate_subtours(n, tour) == []


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(6))
def test_step4_lazy_lp_equals_the_full_lp(seed):
    n = 8
    t = TSP.random(n, seed=seed)
    with time_limit(60):
        value, x, cuts, solves = lab.subtour_lp(t)
    assert abs(value - full_subtour_lp(seed, n)) < 1e-6, "lazily generated constraints must reach the same bound"
    assert cuts < 2 ** (n - 1) - 1, "the point of lazy generation: far fewer constraints than exist"
    assert all(cut_weight(n, x, S) >= 2 - 1e-6 for k in range(1, n) for S in itertools.combinations(range(n), k))
    assert value <= brute_force(t).value + 1e-6


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(6))
def test_step5_exact_tour(seed):
    t = TSP.random(9, seed=100 + seed)
    with time_limit(120):
        length, order, cuts, solves = lab.tsp_exact(t)
    assert sorted(order) == list(range(9))
    assert tour_length(t, order) == length == brute_force(t).value


def test_step3_cut_value_between_one_and_two_is_still_violated():
    n = 6
    idx = {e: k for k, e in enumerate(edges(n))}
    x = [0.0] * len(edges(n))
    for e in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]:
        x[idx[e]] = 1.0
    x[idx[(2, 3)]] = 0.75
    x[idx[(0, 5)]] = 0.75                                  # cut {0,1,2} has value 1.5 < 2
    S = lab.separate_subtours(n, x)
    assert len(S) == 1 and abs(cut_weight(n, x, S[0]) - 1.5) < 1e-9
