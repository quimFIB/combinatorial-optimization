"""Tests for unit 15. Run with `uv run co test 15`. You should not need to edit this."""

import itertools
import random

import networkx as nx
import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def bipartite(seed, nl=None, nr=None, p=None):
    r = random.Random(seed)
    nl = nl or r.randint(1, 12)
    nr = nr or r.randint(1, 12)
    p = p if p is not None else r.uniform(0.1, 0.5)
    return nl, nr, [(l, rr) for l in range(nl) for rr in range(nr) if r.random() < p]


def nx_matching_size(nl, nr, edges):
    G = nx.Graph()
    G.add_nodes_from(("L", l) for l in range(nl))
    G.add_nodes_from(("R", r) for r in range(nr))
    G.add_edges_from((("L", l), ("R", r)) for l, r in edges)
    return len(nx.max_weight_matching(G, maxcardinality=True))


def assert_bipartite_matching(nl, nr, edges, m):
    assert all(0 <= l < nl for l in m), "left vertex out of range"
    assert all((l, r) in set(edges) for l, r in m.items()), "matched pair is not an edge"
    assert len(set(m.values())) == len(m), "a right vertex is matched twice"


def random_cost(seed, n=None, high=50):
    r = random.Random(seed)
    n = n or r.randint(1, 9)
    return [[r.randint(0, high) for _ in range(n)] for _ in range(n)]


def scipy_optimum(cost):
    C = np.array(cost)
    rows, cols = linear_sum_assignment(C)
    return int(C[rows, cols].sum())


def random_prefs(seed, n):
    r = random.Random(seed)
    return ([r.sample(range(n), n) for _ in range(n)], [r.sample(range(n), n) for _ in range(n)])


# ---------------------------------------------------------------- step 1 ---

def test_step1_small():
    edges = [(0, 0), (0, 1), (1, 0), (2, 1), (2, 2)]
    m = lab.hopcroft_karp(3, 3, edges)
    assert_bipartite_matching(3, 3, edges, m)
    assert len(m) == 3


def test_step1_greedy_trap():
    # greedy takes (0,0) and blocks 1; the maximum needs an augmenting path
    edges = [(0, 0), (0, 1), (1, 0)]
    m = lab.hopcroft_karp(2, 2, edges)
    assert m == {0: 1, 1: 0}


def test_step1_empty():
    assert lab.hopcroft_karp(3, 4, []) == {}


@pytest.mark.parametrize("seed", range(40))
def test_step1_matches_networkx(seed):
    nl, nr, edges = bipartite(seed)
    with time_limit(10):
        m = lab.hopcroft_karp(nl, nr, edges)
    assert_bipartite_matching(nl, nr, edges, m)
    assert len(m) == nx_matching_size(nl, nr, edges)


def test_step1_long_augmenting_path():
    # a chain where every augmentation must reroute the whole matching
    n = 30
    edges = [(i, i) for i in range(n)] + [(i + 1, i) for i in range(n - 1)]
    with time_limit(10):
        m = lab.hopcroft_karp(n, n, edges[::-1])
    assert len(m) == n


# ---------------------------------------------------------------- step 2 ---

def is_cover(edges, left, right):
    return all(l in left or r in right for l, r in edges)


def test_step2_small():
    edges = [(0, 0), (0, 1), (1, 0), (2, 0)]
    m = lab.hopcroft_karp(3, 2, edges)
    left, right = lab.konig_cover(3, 2, edges, m)
    assert is_cover(edges, left, right)
    assert len(left) + len(right) == len(m) == 2


@pytest.mark.parametrize("seed", range(40))
def test_step2_cover_size_equals_matching(seed):
    nl, nr, edges = bipartite(seed)
    m = lab.hopcroft_karp(nl, nr, edges)
    left, right = lab.konig_cover(nl, nr, edges, m)
    assert is_cover(edges, set(left), set(right)), "not a vertex cover"
    assert len(left) + len(right) == len(m), "König: |cover| must equal |matching|"


def test_step2_uses_given_matching_only():
    # a hand-given maximum matching; the cover must be built from it
    edges = [(0, 0), (1, 0), (1, 1)]
    left, right = lab.konig_cover(2, 2, edges, {0: 0, 1: 1})
    assert is_cover(edges, set(left), set(right)) and len(left) + len(right) == 2


# ---------------------------------------------------------------- step 3 ---

def test_step3_textbook():
    cost = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    assign, total, u, v = lab.hungarian(cost)
    assert total == 5 == sum(cost[i][assign[i]] for i in range(3))
    assert sorted(assign) == [0, 1, 2]


def test_step3_one_by_one():
    assign, total, u, v = lab.hungarian([[7]])
    assert assign == [0] and total == 7


@pytest.mark.parametrize("seed", range(40))
def test_step3_matches_scipy(seed):
    cost = random_cost(seed)
    with time_limit(10):
        assign, total, u, v = lab.hungarian(cost)
    assert sorted(assign) == list(range(len(cost)))
    assert total == sum(cost[i][assign[i]] for i in range(len(cost)))
    assert total == scipy_optimum(cost)


@pytest.mark.parametrize("seed", range(10))
def test_step3_negative_costs(seed):
    cost = [[x - 25 for x in row] for row in random_cost(seed + 100)]
    assign, total, u, v = lab.hungarian(cost)
    assert total == scipy_optimum(cost)


@pytest.mark.parametrize("seed", range(10))
def test_step3_fractional_costs(seed):
    r = random.Random(seed + 400)
    n = r.randint(2, 8)
    cost = [[round(r.uniform(0, 3), 2) for _ in range(n)] for _ in range(n)]
    assign, total, u, v = lab.hungarian(cost)
    assert total == pytest.approx(float(np.array(cost)[linear_sum_assignment(np.array(cost))].sum()))


def test_step3_larger():
    cost = random_cost(7, n=60, high=1000)
    with time_limit(20):
        assign, total, u, v = lab.hungarian(cost)
    assert total == scipy_optimum(cost)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(30))
def test_step4_hungarian_potentials_certify(seed):
    cost = random_cost(seed + 200)
    assign, total, u, v = lab.hungarian(cost)
    assert lab.certify_assignment(cost, assign, u, v), "your potentials should prove optimality"
    assert sum(u) + sum(v) == total, "strong duality"


def test_step4_rejects_infeasible_duals():
    cost = [[4, 1], [2, 3]]
    assert lab.certify_assignment(cost, [1, 0], [1, 2], [0, 0])
    assert not lab.certify_assignment(cost, [1, 0], [1, 3], [0, 0])     # u1 + v0 = 3 > 2


def test_step4_rejects_slack_on_assigned_pair():
    cost = [[4, 1], [2, 3]]
    assert not lab.certify_assignment(cost, [1, 0], [0, 2], [0, 0])     # 0 + 0 < 1 on (0,1)


def test_step4_rejects_non_permutation():
    cost = [[1, 1], [1, 1]]
    assert lab.certify_assignment(cost, [1, 0], [1, 1], [0, 0])
    assert not lab.certify_assignment(cost, [0, 0], [1, 1], [0, 0])     # duals are fine; [0, 0] is not an assignment


def test_step4_fractional_violation():
    cost = [[0.5, 1.0], [1.0, 0.5]]
    assert lab.certify_assignment(cost, [0, 1], [0.5, 0.5], [0.0, 0.0])
    tricky = [[0.5, 0.4], [1.0, 0.5]]
    assert not lab.certify_assignment(tricky, [0, 1], [0.5, 0.5], [0.0, 0.0])     # tight on the diagonal, but 0.5 > 0.4 at (0, 1)


@pytest.mark.parametrize("seed", range(10))
def test_step4_rejects_suboptimal(seed):
    cost = random_cost(seed + 300, n=5)
    assign, total, u, v = lab.hungarian(cost)
    other = next(p for p in itertools.permutations(range(5))
                 if sum(cost[i][p[i]] for i in range(5)) > total)
    assert not lab.certify_assignment(cost, list(other), u, v)


# ---------------------------------------------------------------- step 5 ---

def test_step5_is_stable_small():
    pp = [[0, 1], [0, 1]]
    rp = [[1, 0], [1, 0]]
    assert lab.is_stable(pp, rp, {0: 1, 1: 0})
    assert not lab.is_stable(pp, rp, {0: 0, 1: 1})     # 1 and receiver 0 block


@pytest.mark.parametrize("seed", range(30))
def test_step5_gale_shapley_is_stable_perfect(seed):
    n = random.Random(seed).randint(1, 9)
    pp, rp = random_prefs(seed, n)
    with time_limit(10):
        m = lab.gale_shapley(pp, rp)
    assert sorted(m) == list(range(n)) and sorted(m.values()) == list(range(n))
    assert lab.is_stable(pp, rp, m)


@pytest.mark.parametrize("seed", range(20))
def test_step5_proposer_optimal(seed):
    n = random.Random(seed).randint(2, 6)
    pp, rp = random_prefs(seed + 50, n)
    m = lab.gale_shapley(pp, rp)
    stable = [s for s in (dict(enumerate(p)) for p in itertools.permutations(range(n)))
              if all(not (pp[p].index(r) < pp[p].index(s[p])
                          and rp[r].index(p) < rp[r].index({v: k for k, v in s.items()}[r]))
                     for p in range(n) for r in range(n))]
    for s in stable:
        assert all(pp[p].index(m[p]) <= pp[p].index(s[p]) for p in range(n)), \
            "every proposer should get their best stable partner"


@pytest.mark.parametrize("seed", range(20))
def test_step5_is_stable_agrees_with_definition(seed):
    n = random.Random(seed).randint(2, 5)
    pp, rp = random_prefs(seed + 80, n)
    for perm in itertools.permutations(range(n)):
        s = dict(enumerate(perm))
        inv = {r: p for p, r in s.items()}
        truth = all(not (pp[p].index(r) < pp[p].index(s[p]) and rp[r].index(p) < rp[r].index(inv[r]))
                    for p in range(n) for r in range(n))
        assert lab.is_stable(pp, rp, s) == truth


# ---------------------------------------------------- step 6 (stretch) ---

def general_graph(seed):
    r = random.Random(seed)
    n = r.randint(4, 24)
    p = r.uniform(0.08, 0.3)
    return n, [(a, b) for a in range(n) for b in range(a + 1, n) if r.random() < p]


def assert_general_matching(n, edges, mate):
    es = {frozenset(e) for e in edges}
    assert len(mate) == n
    for a, b in enumerate(mate):
        if b != -1:
            assert mate[b] == a, "mate must be symmetric"
            assert frozenset((a, b)) in es, "matched pair is not an edge"


def test_step6_odd_cycle_needs_a_blossom():
    # triangle 0-1-2 with pendants 3 (on 2) and 4 (on 0): maximum matching 2
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (0, 4)]
    mate = lab.blossom(5, edges)
    assert_general_matching(5, edges, mate)
    assert sum(m != -1 for m in mate) // 2 == 2


def test_step6_petersen_is_perfect():
    G = nx.petersen_graph()
    mate = lab.blossom(10, list(G.edges))
    assert_general_matching(10, list(G.edges), mate)
    assert all(m != -1 for m in mate)


@pytest.mark.parametrize("seed", range(150))
def test_step6_matches_networkx(seed):
    n, edges = general_graph(seed)
    with time_limit(10):
        mate = lab.blossom(n, edges)
    assert_general_matching(n, edges, mate)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    assert sum(m != -1 for m in mate) // 2 == len(nx.max_weight_matching(G, maxcardinality=True))
