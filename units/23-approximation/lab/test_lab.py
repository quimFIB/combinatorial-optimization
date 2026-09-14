"""Tests for unit 23. Run with `uv run co test 23`. You should not need to edit this."""

import itertools
import random
from collections import Counter
from fractions import Fraction

import networkx as nx
import pytest

from colib.approx import metric_tsp, min_weight_perfect_matching
from colib.mip import MILP, highs_mip
from colib.oracle import brute_force
from colib.problems import SetCover, VertexCover
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def tour_length(dist, tour):
    return sum(dist[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def tsp_optimum(dist):
    return unit("16").held_karp(dist)[0]


def mst_weight(dist):
    g = nx.Graph()
    g.add_weighted_edges_from((i, j, dist[i][j]) for i in range(len(dist)) for j in range(i + 1, len(dist)))
    return sum(d["weight"] for _, _, d in nx.minimum_spanning_edges(g, data=True))


def vc_optimum(vc):
    milp = MILP(c=(1,) * vc.n, A_ub=tuple(tuple(-1 if v in e else 0 for v in range(vc.n)) for e in vc.edges),
                b_ub=(-1,) * len(vc.edges), ub=(1,) * vc.n, integer=(True,) * vc.n)
    return round(highs_mip(milp, options={"mip_rel_gap": 0.0}).value)


def makespan_optimum(p, m):
    best = sum(p)
    for rest in itertools.product(range(m), repeat=len(p) - 1):
        load = [0] * m
        for j, i in enumerate((0,) + rest):
            load[i] += p[j]
        best = min(best, max(load))
    return best


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(25))
def test_step1_greedy_is_a_cover_paid_for_by_prices(seed):
    sc = SetCover.random(random.Random(seed).randint(2, 12), seed=seed)
    x, price = lab.greedy_set_cover(sc)
    assert sc.is_feasible(x)
    assert len(price) == sc.universe and all(pr > 0 for pr in price)
    assert sum(Fraction(pr) for pr in price) == sc.objective(x), "prices sum to the cost paid"


@pytest.mark.parametrize("seed", range(25))
def test_step1_price_lemma_and_Hd_bound(seed):
    sc = SetCover.random(random.Random(seed + 40).randint(2, 11), seed=seed + 40)
    x, price = lab.greedy_set_cover(sc)
    for s, c in zip(sc.sets, sc.costs):
        # the heart of the proof: prices / H_|S| are a feasible dual, so every set is "paid" at most H_|S| c_S
        assert sum(Fraction(price[e]) for e in s) <= lab.harmonic(len(s)) * c
    d = max(len(s) for s in sc.sets)
    assert sc.objective(x) <= lab.harmonic(d) * brute_force(sc).value


def test_step1_uses_cost_per_new_element():
    # set 0 covers most but is expensive per element; set 1 is cheapest per element
    sc = SetCover(4, (frozenset({0, 1, 2, 3}), frozenset({0, 1}), frozenset({2, 3})), (10, 2, 3))
    x, price = lab.greedy_set_cover(sc)
    assert x == [0, 1, 1] and [Fraction(p) for p in price] == [1, 1, Fraction(3, 2), Fraction(3, 2)]


def test_step1_ratio_counts_only_uncovered_elements_and_ties_go_low():
    sc = SetCover(4, (frozenset({0, 1, 2}), frozenset({0, 1, 3}), frozenset({3})), (3, 3, 1))
    x, price = lab.greedy_set_cover(sc)
    # 0 and 1 tie at 1 per element: take 0. Then set 1 covers only {3} at 3, set 2 at 1.
    assert x == [1, 0, 1]
    sc = SetCover(2, (frozenset({1}), frozenset({0})), (1, 1))
    assert lab.greedy_set_cover(sc)[0] == [1, 1]
    sc = SetCover(3, (frozenset({0, 1}), frozenset({1, 2}), frozenset({0, 1, 2})), (2, 2, 4))
    assert lab.greedy_set_cover(sc)[0] == [1, 1, 0]
    sc = SetCover(2, (frozenset({1}), frozenset({0, 1}), frozenset({0, 1})), (2, 2, 2))
    assert lab.greedy_set_cover(sc)[0] == [0, 1, 0], "ties at equal ratio go to the lowest index"


def test_step1_harmonic():
    assert lab.harmonic(0) == 0 and lab.harmonic(1) == 1
    assert Fraction(lab.harmonic(4)) == Fraction(25, 12)


@pytest.mark.parametrize("n", [2, 3, 5, 7, 8])
def test_step1_tight_instance(n):
    sc = lab.greedy_tight_instance(n)
    assert sc.universe == n and sc.n == n + 1 and sc.sets[-1] == frozenset(range(n))
    assert all(sc.sets[i] == frozenset({i}) for i in range(n))
    x, _ = lab.greedy_set_cover(sc)
    opt = brute_force(sc).value
    L = sc.costs[-1] - 1
    assert opt == L + 1
    assert sc.objective(x) == lab.harmonic(n) * L, "greedy pays L * H_n"


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(20))
def test_step2_matching_cover(seed):
    vc = VertexCover.random(random.Random(seed).randint(4, 30), seed=seed, p=0.25)
    cover, matching = lab.matching_vertex_cover(vc)
    ends = [v for e in matching for v in e]
    assert len(ends) == len(set(ends)), "a matching: no shared endpoints"
    assert set(matching) <= set(vc.edges)
    assert all(u in ends or v in ends for u, v in vc.edges), "maximal: every edge touches the matching"
    assert cover == [1 if v in ends else 0 for v in range(vc.n)]
    assert vc.is_feasible(cover)
    opt = vc_optimum(vc)
    assert len(matching) <= opt <= sum(cover) <= 2 * opt


def test_step2_scans_edges_in_order():
    vc = VertexCover(4, ((1, 2), (0, 1), (2, 3), (0, 3)))
    assert lab.matching_vertex_cover(vc)[1] == [(1, 2), (0, 3)]


@pytest.mark.parametrize("n", [1, 3, 6])
def test_step2_matching_cover_is_tight_on_complete_bipartite(n):
    vc = VertexCover(2 * n, tuple((i, n + j) for i in range(n) for j in range(n)))
    cover, _ = lab.matching_vertex_cover(vc)
    assert sum(cover) == 2 * n and vc_optimum(vc) == n


def k_center_optimum(dist, k):
    n = len(dist)
    return min(max(min(dist[v][c] for c in C) for v in range(n)) for C in itertools.combinations(range(n), k))


@pytest.mark.parametrize("seed", range(20))
def test_step2_k_center(seed):
    r = random.Random(seed)
    n, k = r.randint(4, 12), r.randint(1, 4)
    dist = metric_tsp(n, seed).dist
    first = r.randrange(n)
    centres, radius, witness = lab.k_center(dist, k, first)
    assert centres[0] == first and len(centres) <= k and len(set(centres)) == len(centres)
    assert radius == max(min(dist[v][c] for c in centres) for v in range(n))
    for i, c in enumerate(centres[1:], start=1):
        assert min(dist[c][d] for d in centres[:i]) == max(min(dist[v][d] for d in centres[:i]) for v in range(n)), \
            "each new centre is a farthest point from the earlier ones"
    if radius > 0:
        pts = centres + [witness]
        assert all(dist[a][b] >= radius for a, b in itertools.combinations(pts, 2)), "k + 1 points pairwise >= radius"
    assert radius <= 2 * k_center_optimum(dist, k)


def test_step2_k_center_ties_go_to_the_lowest_index():
    # points at 0, -5, +5 on a line
    dist = ((0, 5, 5), (5, 0, 10), (5, 10, 0))
    assert lab.k_center(dist, 2, 0) == ([0, 1], 5, 2)
    assert lab.k_center(dist, 1, 0) == ([0], 5, 1)


def test_step2_k_center_stops_at_zero_radius():
    dist = ((0, 0, 5), (0, 0, 5), (5, 5, 0))
    centres, radius, witness = lab.k_center(dist, 3, 0)
    assert radius == 0 and witness is None and len(centres) == 2


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(15))
def test_step3_prim(seed):
    n = random.Random(seed).randint(1, 25)
    dist = metric_tsp(n, seed).dist
    tree = lab.prim(dist)
    assert len(tree) == max(0, n - 1) and all(u < v for u, v in tree)
    g = nx.Graph(tree)
    g.add_nodes_from(range(n))
    assert n == 0 or nx.is_connected(g)
    assert sum(dist[u][v] for u, v in tree) == (mst_weight(dist) if n > 1 else 0)


def test_step3_shortcut():
    assert lab.shortcut([0, 2, 1, 2, 3, 2, 0]) == [0, 2, 1, 3]
    assert lab.shortcut([0]) == [0]


def test_step3_double_tree_walks_children_in_order():
    # a star centred on 0 whose leaves are nearer in reverse order: preorder must still be 0, 1, 2, 3
    dist = ((0, 5, 4, 3), (5, 0, 9, 8), (4, 9, 0, 7), (3, 8, 7, 0))
    assert lab.double_tree(dist) == ([0, 1, 2, 3], 12)
    # a path 0 - 2 - 1 - 3
    dist = ((0, 2, 1, 3), (2, 0, 1, 1), (1, 1, 0, 2), (3, 1, 2, 0))
    assert lab.double_tree(dist)[0] == [0, 2, 1, 3]


@pytest.mark.parametrize("seed", range(20))
def test_step3_double_tree_bound(seed):
    n = random.Random(seed).randint(2, 11)
    dist = metric_tsp(n, seed + 10).dist
    tour, w = lab.double_tree(dist)
    assert sorted(tour) == list(range(n)) and tour[0] == 0
    assert w == mst_weight(dist)
    opt = tsp_optimum(dist)
    assert w <= opt and tour_length(dist, tour) <= 2 * w


# ---------------------------------------------------------------- step 4 ---

def test_step4_odd_vertices():
    assert lab.odd_vertices(5, [(0, 1), (1, 2), (1, 3)]) == [0, 1, 2, 3]
    assert lab.odd_vertices(3, [(0, 1), (0, 1), (1, 2)]) == [1, 2]
    for seed in range(10):
        tree = lab.prim(metric_tsp(12, seed).dist)
        odd = lab.odd_vertices(12, tree)
        assert len(odd) % 2 == 0 and odd == sorted(odd)


def random_eulerian(n, seed):
    r = random.Random(seed)
    edges = []
    for _ in range(r.randint(1, 4)):
        walk = [0] + [r.randrange(n) for _ in range(r.randint(1, 8))] + [0]
        edges += [(a, b) for a, b in zip(walk, walk[1:]) if a != b]
    return edges


@pytest.mark.parametrize("seed", range(25))
def test_step4_euler_circuit(seed):
    n = 6
    edges = random_eulerian(n, seed)
    if not edges:
        edges = [(0, 1), (1, 0)]
    start = edges[len(edges) // 2][0]
    with time_limit(5):
        circuit = lab.euler_circuit(n, edges, start)
    assert circuit[0] == circuit[-1] == start and len(circuit) == len(edges) + 1
    used = Counter(tuple(sorted(e)) for e in zip(circuit, circuit[1:]))
    assert used == Counter(tuple(sorted(e)) for e in edges), "every edge exactly once"


@pytest.mark.parametrize("seed", range(30))
def test_step4_christofides(seed):
    n = random.Random(seed).randint(3, 11)
    dist = metric_tsp(n, seed + 500).dist
    tour, w, mw = lab.christofides(dist)
    assert sorted(tour) == list(range(n)) and tour[0] == 0
    opt = tsp_optimum(dist)
    assert w == mst_weight(dist)
    assert 2 * mw <= opt, "the matching costs at most half the optimal tour"
    assert tour_length(dist, tour) <= w + mw <= Fraction(3, 2) * opt


def test_step4_christofides_matches_odd_vertices_optimally():
    dist = metric_tsp(14, 3).dist
    tour, w, mw = lab.christofides(dist)
    odd = lab.odd_vertices(14, lab.prim(dist))   # christofides is expected to build on your own prim
    assert mw == sum(dist[u][v] for u, v in min_weight_perfect_matching(odd, dist))


# ---------------------------------------------------------------- step 5 ---

def loads(p, m, machine):
    load = [0] * m
    for j, i in enumerate(machine):
        load[i] += p[j]
    return load


def test_step5_list_scheduling_follows_the_order():
    assert lab.list_scheduling([3, 3, 2, 2, 2], 2) == (7, [0, 1, 0, 1, 0])
    assert lab.lpt([2, 3, 2, 3, 2], 2) == (7, [0, 0, 1, 1, 0])   # the optimum is 6: 3 + 3 and 2 + 2 + 2


@pytest.mark.parametrize("seed", range(30))
def test_step5_bounds_against_brute_force(seed):
    r = random.Random(seed)
    m = r.randint(2, 3)
    p = [r.randint(1, 20) for _ in range(r.randint(m + 1, 8))]
    opt = makespan_optimum(p, m)
    for f, bound in ((lab.list_scheduling, Fraction(2) - Fraction(1, m)),
                     (lab.lpt, Fraction(4, 3) - Fraction(1, 3 * m))):
        makespan, machine = f(p, m)
        assert len(machine) == len(p) and all(0 <= i < m for i in machine)
        assert max(loads(p, m, machine)) == makespan
        assert makespan <= bound * opt


@pytest.mark.parametrize("m", [2, 3, 4, 6])
def test_step5_list_scheduling_tight(m):
    p = lab.list_scheduling_tight(m)
    assert len(p) == m * (m - 1) + 1 and sum(p) == m * m and max(p) == m   # so the optimum is m
    assert lab.list_scheduling(p, m)[0] == 2 * m - 1


@pytest.mark.parametrize("m", [2, 3, 4, 6])
def test_step5_lpt_tight(m):
    p = lab.lpt_tight(m)
    assert len(p) == 2 * m + 1 and sum(p) == 3 * m * m
    assert lab.lpt(p, m)[0] == 4 * m - 1
    if m <= 3:
        assert makespan_optimum(p, m) == 3 * m
