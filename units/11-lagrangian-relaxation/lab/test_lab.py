"""Tests for unit 11. Run with `uv run co test 11`. You should not need to edit this."""

import itertools
import random

import networkx as nx
import pytest

from colib.colgen import GAP
from colib.mip import highs_mip, lp_relaxation
from colib.problems import TSP
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
held_karp_exact = unit("16").held_karp


def random_pi(n, seed, scale=5.0):
    r = random.Random(seed)
    return [r.uniform(-scale, scale) for _ in range(n)]


def min_one_tree(dist, pi):
    n = len(dist)
    G = nx.Graph()
    G.add_nodes_from(range(1, n))
    for i in range(1, n):
        for j in range(i + 1, n):
            G.add_edge(i, j, weight=dist[i][j] + pi[i] + pi[j])
    mst = sum(d["weight"] for *_, d in nx.minimum_spanning_tree(G).edges(data=True))
    return mst + sum(sorted(dist[0][u] + pi[0] + pi[u] for u in range(1, n))[:2]) - 2 * sum(pi)


def optimal_tour(tsp):
    length, order = held_karp_exact(tsp.dist)
    return length, {(min(a, b), max(a, b)) for a, b in zip(order, order[1:] + order[:1])}


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(30))
def test_step1_one_tree(seed):
    n = random.Random(seed).randint(3, 14)
    tsp = TSP.random(n, seed=seed)
    pi = random_pi(n, seed) if seed % 3 else [0.0] * n
    L, degrees, edges = lab.one_tree(tsp.dist, pi)
    assert L == pytest.approx(min_one_tree(tsp.dist, pi))
    assert len(edges) == n and all(i < j for i, j in edges) and len(set(edges)) == n
    assert sum(1 for i, j in edges if i == 0) == 2, "exactly two edges at vertex 0"
    assert degrees == [sum(1 for e in edges if v in e) for v in range(n)]
    G = nx.Graph([e for e in edges if 0 not in e])
    G.add_nodes_from(range(1, n))
    assert nx.is_tree(G), "edges among 1..n-1 form a spanning tree"
    weight = sum(tsp.dist[i][j] + pi[i] + pi[j] for i, j in edges)
    assert L == pytest.approx(weight - 2 * sum(pi))


@pytest.mark.parametrize("seed", range(20))
def test_step1_weak_duality(seed):
    n = random.Random(seed).randint(4, 9)
    tsp = TSP.random(n, seed=seed + 50)
    opt, _ = optimal_tour(tsp)
    for k in range(5):
        L, _, _ = lab.one_tree(tsp.dist, random_pi(n, seed * 10 + k, scale=20))
        assert L <= opt + 1e-9, "every multiplier vector gives a lower bound"


def test_step1_a_tour_that_is_a_one_tree():
    # points on a circle: the path 1-2-...-7 is the MST and vertex 0's two cheapest edges close it into
    # the optimal tour, so every degree is 2 and the bound is tight
    import math
    pts = [(math.cos(2 * math.pi * k / 8), math.sin(2 * math.pi * k / 8)) for k in range(8)]
    dist = [[round(100 * math.dist(a, b)) for b in pts] for a in pts]
    L, degrees, edges = lab.one_tree(dist, [0.0] * 8)
    assert degrees == [2] * 8 and L == 8 * dist[0][1]


# ---------------------------------------------------------------- step 2 ---

def test_step2_ascent_on_a_simple_concave_function():
    # L(m) = min(m, 10 - m): maximum 5 at m = 5; subgradient +1 left of 5, -1 right
    oracle = lambda m: (min(m[0], 10 - m[0]), None, [1.0 if m[0] < 5 else -1.0])
    best, mult, history = lab.subgradient_ascent(oracle, [0.0], upper=6.0, iterations=300)
    assert best == pytest.approx(5.0, abs=0.05) and abs(mult[0] - 5) < 0.1
    assert best == max(history)


def test_step2_stops_when_subgradient_vanishes():
    calls = []

    def oracle(m):
        calls.append(1)
        return 3.0, None, [0.0, 0.0]
    best, mult, history = lab.subgradient_ascent(oracle, [1.0, 2.0], upper=10.0, iterations=100)
    assert len(calls) == 1 and history == [3.0] and best == 3.0 and mult == [1.0, 2.0]


def test_step2_projection():
    # maximise min(-m, ...) with m >= 0: the projection must keep m at 0
    oracle = lambda m: (-m[0], None, [-1.0])
    best, mult, history = lab.subgradient_ascent(oracle, [0.0], upper=1.0, iterations=50,
                                                 project=lambda v: [max(0.0, x) for x in v])
    assert best == 0.0 and all(h <= 0 for h in history)


def test_step2_step_rule_halves():
    # a constant oracle never improves: lam halves every `patience` steps until below 1e-6
    oracle = lambda m: (0.0, None, [1.0])
    best, mult, history = lab.subgradient_ascent(oracle, [0.0], upper=1.0, iterations=10_000, lam=1.0, patience=5)
    assert 90 <= len(history) <= 110, "about 5 * log2(1e6) iterations before lam < 1e-6"


@pytest.mark.parametrize("seed", range(15))
def test_step2_held_karp_bound(seed):
    n = random.Random(seed).randint(5, 11)
    tsp = TSP.random(n, seed=seed + 100)
    opt, _ = optimal_tour(tsp)
    with time_limit(30):
        best, pi, history = lab.held_karp_bound(tsp.dist, opt)
    assert best <= opt + 1e-6
    assert best >= lab.one_tree(tsp.dist, [0.0] * n)[0] - 1e-9, "never worse than the plain 1-tree"
    assert best == pytest.approx(max(history))
    assert lab.one_tree(tsp.dist, pi)[0] == pytest.approx(best), "pi must achieve the reported bound"


@pytest.mark.parametrize("n", [20, 30])
def test_step2_close_to_the_subtour_lp(n):
    tsp = TSP.random(n, seed=n)
    subtour = unit("09").subtour_lp(tsp)[0]
    length = unit("09").tsp_exact(tsp)[0]
    with time_limit(60):
        best, _, _ = lab.held_karp_bound(tsp.dist, length, iterations=1000)
    assert best <= subtour + 1e-6, "the Lagrangian dual equals the subtour LP"
    assert best >= 0.99 * subtour


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(25))
def test_step3_never_fixes_an_optimal_edge(seed):
    n = random.Random(seed).randint(5, 10)
    tsp = TSP.random(n, seed=seed + 200)
    opt, tour = optimal_tour(tsp)
    _, pi, _ = lab.held_karp_bound(tsp.dist, opt)
    fixed = lab.fix_edges(tsp.dist, pi, opt)
    assert all(i < j for i, j in fixed)
    assert not (fixed & tour), "an edge of an optimal tour was fixed out"


@pytest.mark.parametrize("seed", range(10))
def test_step3_fixing_is_exact(seed):
    # compare with brute force: the cheapest 1-tree forced to contain e
    n = random.Random(seed).randint(5, 8)
    tsp = TSP.random(n, seed=seed + 300)
    pi = random_pi(n, seed)
    L, _, edges = lab.one_tree(tsp.dist, pi)
    for upper in (L + 5, L + 20, L + 60):
        fixed = lab.fix_edges(tsp.dist, pi, upper)
        for i, j in itertools.combinations(range(n), 2):
            forced = forced_one_tree(tsp.dist, pi, (i, j))
            assert ((i, j) in fixed) == (forced > upper + 1e-9), (i, j, forced, upper)


def forced_one_tree(dist, pi, e):
    n = len(dist)
    c = lambda a, b: dist[a][b] + pi[a] + pi[b]
    i, j = e
    if i == 0:
        rest = sorted(c(0, u) for u in range(1, n) if u != j)[0]
        G = nx.Graph()
        G.add_nodes_from(range(1, n))
        G.add_weighted_edges_from((a, b, c(a, b)) for a in range(1, n) for b in range(a + 1, n))
        return sum(d["weight"] for *_, d in nx.minimum_spanning_tree(G).edges(data=True)) + c(0, j) + rest - 2 * sum(pi)
    G = nx.Graph()
    G.add_nodes_from(range(1, n))
    G.add_weighted_edges_from((a, b, c(a, b) - (1e6 if (a, b) == e else 0)) for a in range(1, n) for b in range(a + 1, n))
    mst = sum(d["weight"] for *_, d in nx.minimum_spanning_tree(G).edges(data=True)) + 1e6
    return mst + sum(sorted(c(0, u) for u in range(1, n))[:2]) - 2 * sum(pi)


def test_step3_fixes_most_edges_near_optimum():
    tsp = TSP.random(25, seed=25)
    length = unit("09").tsp_exact(tsp)[0]
    _, pi, _ = lab.held_karp_bound(tsp.dist, length, iterations=1000)
    assert len(lab.fix_edges(tsp.dist, pi, length)) >= 0.8 * 300


# ---------------------------------------------------------------- step 4 ---

def gap_instances():
    out = []
    for seed in range(40):
        g = GAP.random(3, 10, seed=seed, tightness=0.9)
        opt = highs_mip(g.milp(), options={"mip_rel_gap": 0.0})
        if opt.status == "optimal":
            out.append((seed, g, opt.value, lp_relaxation(g.milp()).value))
        if len(out) == 12:
            break
    return out


GAPS = gap_instances()


@pytest.mark.parametrize("case", GAPS, ids=lambda c: f"seed{c[0]}")
def test_step4_relaxations_are_lower_bounds(case):
    _, g, opt, lp = case
    r = random.Random(case[0])
    for _ in range(5):
        u = [r.uniform(0, 60) for _ in range(g.n)]
        L, x, grad = lab.gap_relax_assignment(g, u)
        assert L <= opt + 1e-6
        assert all(sum(g.weight[i][j] * x[i][j] for j in range(g.n)) <= g.capacity[i] for i in range(g.m)), \
            "each agent's knapsack respects its capacity"
        assert grad == [1 - sum(x[i][j] for i in range(g.m)) for j in range(g.n)]
        assert L == pytest.approx(sum(u) + sum((g.cost[i][j] - u[j]) * x[i][j] for i in range(g.m) for j in range(g.n)))
        lam = [r.uniform(0, 3) for _ in range(g.m)]
        L2, x2, grad2 = lab.gap_relax_capacity(g, lam)
        assert L2 <= lp + 1e-6, "dualising capacities can never beat the LP"
        assert all(sum(x2[i][j] for i in range(g.m)) == 1 for j in range(g.n))
        assert grad2 == [sum(g.weight[i][j] * x2[i][j] for j in range(g.n)) - g.capacity[i] for i in range(g.m)]


def test_step4_assignment_relaxation_beats_the_lp():
    gains = []
    with time_limit(120):
        for _, g, opt, lp in GAPS:
            best, _, _ = lab.subgradient_ascent(lambda u: lab.gap_relax_assignment(g, u), [0.0] * g.n, opt, 300)
            cap, _, _ = lab.subgradient_ascent(lambda l: lab.gap_relax_capacity(g, l), [0.0] * g.m, opt, 300,
                                               project=lambda v: [max(0.0, x) for x in v])
            assert best <= opt + 1e-6 and cap <= lp + 1e-6
            assert cap >= lp - 0.01 * abs(lp), "the capacity dual converges to the LP bound"
            gains.append(best - lp)
    assert sum(1 for gain in gains if gain > 1.0) >= len(gains) // 2, \
        "knapsack subproblems lack the integrality property: their bound should beat the LP"


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("case", GAPS, ids=lambda c: f"seed{c[0]}")
def test_step5_repair(case):
    _, g, opt, _ = case
    _, u, _ = lab.subgradient_ascent(lambda u: lab.gap_relax_assignment(g, u), [0.0] * g.n, opt, 300)
    _, x, _ = lab.gap_relax_assignment(g, u)
    result = lab.gap_repair(g, x)
    if result is not None:
        cost, agent_of = result
        assert g.is_feasible(agent_of) and cost == g.assignment_cost(agent_of) and cost >= opt - 1e-6


def test_step5_repair_usually_succeeds():
    ok = near = 0
    for _, g, opt, _ in GAPS:
        _, u, _ = lab.subgradient_ascent(lambda u: lab.gap_relax_assignment(g, u), [0.0] * g.n, opt, 300)
        result = lab.gap_repair(g, lab.gap_relax_assignment(g, u)[1])
        if result is not None:
            ok += 1
            near += result[0] <= 1.05 * opt
    assert ok >= 0.75 * len(GAPS) and near >= 0.6 * len(GAPS)


def test_step5_repair_keeps_the_cheapest_duplicate():
    g = GAP(cost=((5, 9), (3, 9)), weight=((1, 1), (1, 1)), capacity=(2, 2))
    cost, agent_of = lab.gap_repair(g, [[1, 0], [1, 0]])
    assert agent_of[0] == 1 and cost == 3 + 9


def test_step5_repair_by_regret():
    # job 1 has a large regret (agent 0 is much cheaper) and must be placed first
    g = GAP(cost=((1, 1), (2, 50)), weight=((5, 5), (5, 5)), capacity=(5, 10))
    cost, agent_of = lab.gap_repair(g, [[0, 0], [0, 0]])
    assert agent_of == [1, 0] and cost == 3


def test_step5_repair_can_fail():
    g = GAP(cost=((1, 1),), weight=((6, 6),), capacity=(10,))
    assert lab.gap_repair(g, [[0, 0]]) is None
