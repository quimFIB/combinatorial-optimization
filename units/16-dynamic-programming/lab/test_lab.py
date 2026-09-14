"""Tests for unit 16. Run with `uv run co test 16`. You should not need to edit this."""

import itertools
import random

import pytest

from colib.graphs import ktree, partial_ktree, random_tree
from colib.mip import MILP, highs_mip
from colib.problems import TSP
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


# ---------------------------------------------------------------- step 1 ---

def brute_knapsack(values, weights, capacity):
    n = len(values)
    return max(sum(values[i] for i in S) for k in range(n + 1) for S in itertools.combinations(range(n), k)
               if sum(weights[i] for i in S) <= capacity)


def knapsack_instance(seed, n=None, C=None):
    r = random.Random(seed)
    n = n if n is not None else r.randint(0, 11)
    C = C if C is not None else r.randint(0, 40)
    return [r.randint(1, 30) for _ in range(n)], [r.randint(1, 15) for _ in range(n)], C


def test_step1_textbook():
    value, items = lab.knapsack([60, 100, 120], [10, 20, 30], 50)
    assert value == 220 and items == [1, 2]


def test_step1_nothing_fits():
    assert lab.knapsack([5, 6], [10, 11], 9) == (0, [])
    assert lab.knapsack([], [], 10) == (0, [])


@pytest.mark.parametrize("seed", range(40))
def test_step1_knapsack_brute_force(seed):
    values, weights, C = knapsack_instance(seed)
    value, items = lab.knapsack(values, weights, C)
    assert items == sorted(set(items)), "items: sorted, no repeats"
    assert sum(weights[i] for i in items) <= C, "over capacity"
    assert value == sum(values[i] for i in items), "value must match the items"
    assert value == brute_knapsack(values, weights, C)


@pytest.mark.parametrize("seed", range(10))
def test_step1_fractional_values(seed):
    r = random.Random(seed + 70)
    n = r.randint(1, 10)
    values = [round(r.uniform(0.01, 1.0), 3) for _ in range(n)]
    weights = [r.randint(1, 12) for _ in range(n)]
    value, items = lab.knapsack(values, weights, 25)
    assert value == pytest.approx(brute_knapsack(values, weights, 25))


def test_step1_large_capacity_fast():
    values, weights, _ = knapsack_instance(5, n=60)
    weights = [w * 400 for w in weights]
    with time_limit(20):
        value, items = lab.knapsack(values, weights, 100_000)
    assert sum(weights[i] for i in items) <= 100_000 and value == sum(values[i] for i in items)


def brute_unbounded(values, weights, C):
    best = [0] * (C + 1)
    for c in range(1, C + 1):
        best[c] = max([best[c - 1]] + [best[c - w] + v for v, w in zip(values, weights) if w <= c])
    return best[C]


def test_step1_unbounded_textbook():
    value, counts = lab.unbounded_knapsack([10, 40, 50, 70], [1, 3, 4, 5], 8)
    assert value == 110 and sum(k * w for k, w in zip(counts, [1, 3, 4, 5])) <= 8


@pytest.mark.parametrize("seed", range(30))
def test_step1_unbounded(seed):
    values, weights, C = knapsack_instance(seed + 100)
    value, counts = lab.unbounded_knapsack(values, weights, C)
    assert len(counts) == len(values) and all(k >= 0 for k in counts)
    assert sum(k * w for k, w in zip(counts, weights)) <= C, "over capacity"
    assert value == sum(k * v for k, v in zip(counts, values))
    assert value == brute_unbounded(values, weights, C)


@pytest.mark.parametrize("seed", range(10))
def test_step1_unbounded_dual_prices(seed):
    # unit 10's pricing problem: float values (dual prices), integer widths, a roll of width 100
    r = random.Random(seed + 900)
    widths = [r.randint(10, 45) for _ in range(r.randint(1, 6))]
    duals = [round(r.uniform(0.1, 0.6), 4) for _ in widths]
    value, counts = lab.unbounded_knapsack(duals, widths, 100)
    assert value == pytest.approx(brute_unbounded(duals, widths, 100))
    assert sum(k * w for k, w in zip(counts, widths)) <= 100


# ---------------------------------------------------------------- step 2 ---

def tour_len(D, order):
    n = len(order)
    return sum(D[order[i]][order[(i + 1) % n]] for i in range(n))


def brute_tsp(D):
    n = len(D)
    return min(tour_len(D, (0,) + p) for p in itertools.permutations(range(1, n)))


def test_step2_tiny():
    assert lab.held_karp([[0]]) == (0, [0])
    length, order = lab.held_karp([[0, 3], [4, 0]])
    assert length == 7 and order == [0, 1]
    length, order = lab.held_karp([[0, 1, 9], [1, 0, 2], [9, 2, 0]])
    assert length == 12 and sorted(order) == [0, 1, 2]


@pytest.mark.parametrize("seed", range(25))
def test_step2_euclidean_brute_force(seed):
    n = random.Random(seed).randint(3, 9)
    tsp = TSP.random(n, seed=seed)
    length, order = lab.held_karp(tsp.dist)
    assert order[0] == 0 and sorted(order) == list(range(n)), "order: a permutation starting at 0"
    assert length == tour_len(tsp.dist, order), "length must be the length of the returned tour"
    assert length == brute_tsp(tsp.dist)


@pytest.mark.parametrize("seed", range(15))
def test_step2_asymmetric(seed):
    r = random.Random(seed + 40)
    n = r.randint(3, 8)
    D = [[0 if i == j else r.randint(1, 60) for j in range(n)] for i in range(n)]
    length, order = lab.held_karp(D)
    assert length == tour_len(D, order) == brute_tsp(D)


def test_step2_n12_agrees_with_mip():
    unit09 = unit("09")
    tsp = TSP.random(12, seed=3)
    with time_limit(60):
        length, order = lab.held_karp(tsp.dist)
    assert length == unit09.tsp_exact(tsp)[0]


# ---------------------------------------------------------------- step 3 ---

def brute_vc(n, edges, weights):
    return min(sum(weights[i] for i in range(n) if m >> i & 1) for m in range(1 << n)
               if all(m >> a & 1 or m >> b & 1 for a, b in edges))


def assert_cover(n, edges, weights, value, cover):
    assert all(0 <= v < n for v in cover)
    assert all(a in cover or b in cover for a, b in edges), "not a vertex cover"
    assert value == sum(weights[v] for v in cover), "weight must match the cover"


def test_step3_star_and_path():
    star = [(0, i) for i in range(1, 6)]
    assert lab.tree_vertex_cover(6, star, [1] * 6)[0] == 1
    assert lab.tree_vertex_cover(6, star, [10, 1, 1, 1, 1, 1])[0] == 5
    path = [(i, i + 1) for i in range(4)]
    assert lab.tree_vertex_cover(5, path, [1] * 5)[0] == 2


@pytest.mark.parametrize("seed", range(40))
def test_step3_random_forests(seed):
    r = random.Random(seed)
    n = r.randint(1, 13)
    edges = [(r.randrange(i), i) for i in range(1, n) if r.random() < 0.85]     # a forest
    weights = [r.randint(1, 9) for _ in range(n)]
    value, cover = lab.tree_vertex_cover(n, edges, weights)
    assert_cover(n, edges, weights, value, cover)
    assert value == brute_vc(n, edges, weights)


def test_step3_long_path_no_recursion_limit():
    n = 5000
    edges = [(i, i + 1) for i in range(n - 1)]
    with time_limit(30):
        value, cover = lab.tree_vertex_cover(n, edges, [1] * n)
    assert value == n // 2
    assert_cover(n, edges, [1] * n, value, cover)


def test_step3_big_tree_against_lp():
    # trees are bipartite, so the vertex cover LP is integral (unit 06)
    n, edges = random_tree(300, seed=4)
    r = random.Random(4)
    weights = [r.randint(1, 20) for _ in range(n)]
    milp = MILP(c=tuple(weights), A_ub=tuple(tuple(-1 if v in e else 0 for v in range(n)) for e in edges),
                b_ub=(-1,) * len(edges), ub=(1,) * n, integer=(True,) * n)
    value, cover = lab.tree_vertex_cover(n, edges, weights)
    assert_cover(n, edges, weights, value, cover)
    assert value == round(highs_mip(milp).value)


# ---------------------------------------------------------------- step 4 ---

def test_step4_width():
    assert lab.width([{0, 1}, {1, 2, 3}]) == 2
    assert lab.width([{0}]) == 0


def test_step4_accepts_trivial_and_path_decomposition():
    edges = [(0, 1), (1, 2), (2, 3)]
    assert lab.is_tree_decomposition(4, edges, [{0, 1, 2, 3}], [])
    assert lab.is_tree_decomposition(4, edges, [{0, 1}, {1, 2}, {2, 3}], [(0, 1), (1, 2)])


def test_step4_rejects_each_violation():
    edges = [(0, 1), (1, 2), (2, 3)]
    bags = [{0, 1}, {1, 2}, {2, 3}]
    assert not lab.is_tree_decomposition(4, edges, [{0, 1}, {2, 3}], [(0, 1)]), "edge (1, 2) in no bag"
    assert not lab.is_tree_decomposition(5, edges, bags, [(0, 1), (1, 2)]), "vertex 4 in no bag"
    assert not lab.is_tree_decomposition(4, edges, [{0, 1}, {2, 3}, {1, 2}], [(0, 1), (1, 2)]), \
        "bags holding 1 are not connected"
    assert not lab.is_tree_decomposition(4, edges, bags, [(0, 1)]), "not a tree: disconnected"
    assert not lab.is_tree_decomposition(4, edges, bags + [{3}], [(0, 1), (1, 2), (2, 0)]), \
        "not a tree: a cycle and a stray bag"


def test_step4_rejects_cycles_that_pass_everything_else():
    edges = [(0, 1), (1, 2), (2, 3)]
    bags = [{0, 1}, {1, 2}, {2, 3}]
    # connected, every vertex's bags connected, but three tree edges on three bags
    assert not lab.is_tree_decomposition(4, edges, bags, [(0, 1), (1, 2), (2, 0)])
    # the right number of edges (3 on 4 bags), but a cycle plus an isolated empty bag
    assert not lab.is_tree_decomposition(4, edges, bags + [set()], [(0, 1), (1, 2), (2, 0)])


@pytest.mark.parametrize("seed", range(30))
def test_step4_elimination_is_valid(seed):
    r = random.Random(seed)
    n = r.randint(1, 16)
    p = r.uniform(0.05, 0.6)
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < p]
    bags, tree_edges = lab.elimination_decomposition(n, edges)
    assert lab.is_tree_decomposition(n, edges, bags, tree_edges)


@pytest.mark.parametrize("seed", range(10))
def test_step4_given_order(seed):
    r = random.Random(seed + 30)
    n = r.randint(2, 12)
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < 0.4]
    order = r.sample(range(n), n)
    bags, tree_edges = lab.elimination_decomposition(n, edges, order)
    assert lab.is_tree_decomposition(n, edges, bags, tree_edges)
    # with the identity order on a path 0-1-...-n-1, every bag has at most two vertices
    path = [(i, i + 1) for i in range(n - 1)]
    assert lab.width(lab.elimination_decomposition(n, path, list(range(n)))[0]) == 1


@pytest.mark.parametrize("k", range(1, 6))
def test_step4_min_degree_is_exact_on_ktrees(k):
    n, edges = ktree(30, k, seed=k)
    bags, tree_edges = lab.elimination_decomposition(n, edges)
    assert lab.is_tree_decomposition(n, edges, bags, tree_edges)
    assert lab.width(bags) == k


def test_step4_cycle_and_clique():
    cycle = [(i, (i + 1) % 8) for i in range(8)]
    assert lab.width(lab.elimination_decomposition(8, cycle)[0]) == 2
    clique = [(a, b) for a in range(6) for b in range(a + 1, 6)]
    assert lab.width(lab.elimination_decomposition(6, clique)[0]) == 5


def test_step4_bad_order_is_wider():
    # a star eliminated centre-first becomes a clique on the leaves
    star = [(0, i) for i in range(1, 7)]
    assert lab.width(lab.elimination_decomposition(7, star, list(range(7)))[0]) == 6
    assert lab.width(lab.elimination_decomposition(7, star)[0]) == 1


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(30))
def test_step5_random_graphs(seed):
    r = random.Random(seed)
    n = r.randint(1, 13)
    p = r.uniform(0.1, 0.5)
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < p]
    weights = [r.randint(1, 9) for _ in range(n)]
    bags, tree_edges = lab.elimination_decomposition(n, edges)
    with time_limit(20):
        value, cover = lab.td_vertex_cover(n, edges, weights, bags, tree_edges)
    assert_cover(n, edges, weights, value, cover)
    assert value == brute_vc(n, edges, weights)


def test_step5_hand_decompositions():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]                  # a 4-cycle
    weights = [1, 5, 1, 5]
    for bags, te in [([{0, 1, 2, 3}], []),
                     ([{0, 1, 2}, {0, 2, 3}], [(0, 1)]),
                     ([{0, 2, 3}, {0, 1, 2}], [(1, 0)])]:
        value, cover = lab.td_vertex_cover(4, edges, weights, bags, te)
        assert value == 2 and cover == {0, 2}


def test_step5_root_choice_does_not_matter():
    # a path decomposition listed so that bag 0 is in the middle of the tree
    edges = [(i, i + 1) for i in range(5)]
    bags = [{2, 3}, {0, 1}, {1, 2}, {3, 4}, {4, 5}]
    te = [(1, 2), (2, 0), (0, 3), (3, 4)]
    weights = [3, 1, 3, 1, 3, 1]
    value, cover = lab.td_vertex_cover(6, edges, weights, bags, te)
    assert value == 3 and cover == {1, 3, 5}


@pytest.mark.parametrize("seed", range(10))
def test_step5_random_orders(seed):
    r = random.Random(seed + 500)
    n = r.randint(2, 11)
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < 0.35]
    weights = [r.randint(1, 9) for _ in range(n)]
    bags, te = lab.elimination_decomposition(n, edges, r.sample(range(n), n))
    value, cover = lab.td_vertex_cover(n, edges, weights, bags, te)
    assert_cover(n, edges, weights, value, cover)
    assert value == brute_vc(n, edges, weights)


@pytest.mark.parametrize("k", [2, 3, 4])
def test_step5_partial_ktree_against_mip(k):
    n, edges = partial_ktree(80, k, seed=k)
    r = random.Random(k)
    weights = [r.randint(1, 20) for _ in range(n)]
    bags, te = lab.elimination_decomposition(n, edges)
    with time_limit(60):
        value, cover = lab.td_vertex_cover(n, edges, weights, bags, te)
    assert_cover(n, edges, weights, value, cover)
    milp = MILP(c=tuple(weights), A_ub=tuple(tuple(-1 if v in e else 0 for v in range(n)) for e in edges),
                b_ub=(-1,) * len(edges), ub=(1,) * n, integer=(True,) * n)
    assert value == round(highs_mip(milp, options={"mip_rel_gap": 0.0}).value)
