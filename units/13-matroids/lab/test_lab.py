"""Tests for unit 13. Run with `uv run co test 13`. You should not need to edit this."""

import itertools
import math
import random

import networkx as nx
import pytest

from colib.testing import load_lab

lab = load_lab(__file__)


def random_graph(seed, n=7, p=0.5):
    r = random.Random(seed)
    return n, [e for e in itertools.combinations(range(n), 2) if r.random() < p]


# ---------------------------------------------------------------- step 1 ---

def test_step1_graphic():
    edges = [(0, 1), (1, 2), (0, 2), (2, 3)]
    ind = lab.graphic(4, edges)
    assert ind([]) and ind([0, 1, 3]) and not ind([0, 1, 2]) and ind([2, 3])


def test_step1_uniform_partition_linear():
    assert lab.uniform(2)([0, 4]) and not lab.uniform(2)([0, 1, 2])
    part = lab.partition([0, 0, 1, 1, 1], [1, 2])
    assert part([0, 2, 3]) and not part([0, 1]) and not part([2, 3, 4])
    lin = lab.linear([(1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1)])
    assert lin([0, 1, 3]) and not lin([0, 1, 2]) and lin([2])


@pytest.mark.parametrize("seed", range(15))
def test_step1_graphic_matches_forest_check(seed):
    n, E = random_graph(seed)
    ind = lab.graphic(n, E)
    r = random.Random(seed)
    for _ in range(40):
        S = r.sample(range(len(E)), r.randint(0, len(E))) if E else []
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(E[i] for i in S)
        assert ind(S) == (nx.is_forest(G) and G.number_of_edges() == len(S))


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(25))
def test_step2_greedy_on_graphic_is_a_maximum_spanning_forest(seed):
    n, E = random_graph(seed)
    r = random.Random(seed)
    w = [r.randint(-5, 20) for _ in E]
    S = lab.greedy(len(E), w, lab.graphic(n, E))
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_weighted_edges_from((u, v, wt) for (u, v), wt in zip(E, w) if wt > 0)
    assert lab.graphic(n, E)(S) and all(w[e] > 0 for e in S)
    assert sum(w[e] for e in S) == nx.maximum_spanning_tree(G).size(weight="weight")


def test_step2_greedy_on_partition_and_uniform():
    w = [5, 9, 1, 7, 3]
    assert sorted(lab.greedy(5, w, lab.uniform(2))) == [1, 3]
    assert sorted(lab.greedy(5, w, lab.partition([0, 0, 1, 1, 1], [1, 1]))) == [1, 3]


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("name, n, oracle", [
    ("graphic K4", 6, lambda: lab.graphic(4, list(itertools.combinations(range(4), 2)))),
    ("uniform", 5, lambda: lab.uniform(3)),
    ("partition", 5, lambda: lab.partition([0, 0, 1, 1, 2], [1, 2, 1])),
    ("linear", 4, lambda: lab.linear([(1, 0), (0, 1), (1, 1), (2, 2)])),
])
def test_step3_real_matroids_have_no_witness(name, n, oracle):
    assert lab.matroid_witness(n, oracle()) is None, name


def test_step3_matchings_are_not_a_matroid():
    E = [(0, 1), (1, 2), (2, 3)]
    matching = lambda S: len({v for e in S for v in E[e]}) == 2 * len(set(S))
    w = lab.matroid_witness(3, matching)
    assert w is not None and w[0] == "exchange"
    A, B = set(w[1]), set(w[2])
    assert matching(sorted(A)) and matching(sorted(B)) and len(A) < len(B)
    assert not any(matching(sorted(A | {b})) for b in B - A)


def test_step3_other_failures():
    assert lab.matroid_witness(2, lambda S: len(S) > 0) == ("empty",)
    not_hereditary = lambda S: set(S) in ({0, 1}, set(), {0})
    w = lab.matroid_witness(2, not_hereditary)
    assert w is not None and w[0] == "hereditary" and not not_hereditary(list(w[2]))


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(25))
def test_step4_intersection_of_two_partitions_is_bipartite_matching(seed):
    r = random.Random(seed)
    E = [(i, j) for i in range(5) for j in range(5) if r.random() < 0.35]
    if not E:
        return
    m1 = lab.partition([i for i, _ in E], [1] * 5)
    m2 = lab.partition([j for _, j in E], [1] * 5)
    I = lab.intersection(len(E), m1, m2)
    assert m1(I) and m2(I)
    G = nx.Graph()
    G.add_edges_from((("l", i), ("r", j)) for i, j in E)
    size = len(nx.bipartite.maximum_matching(G, top_nodes=[v for v in G if v[0] == "l"])) // 2
    assert len(I) == size


@pytest.mark.parametrize("seed", range(10))
def test_step4_graphic_with_partition_matches_brute_force(seed):
    n, E = random_graph(seed, n=5, p=0.7)
    if not E:
        return
    r = random.Random(seed)
    colours = [r.randint(0, 2) for _ in E]
    m1, m2 = lab.graphic(n, E), lab.partition(colours, [1, 1, 1])
    I = lab.intersection(len(E), m1, m2)
    best = max(len(S) for k in range(len(E) + 1) for S in itertools.combinations(range(len(E)), k)
               if m1(list(S)) and m2(list(S)))
    assert m1(I) and m2(I) and len(I) == best


# ---------------------------------------------------------------- step 5 ---

def coverage(sets, chosen):
    return len(set().union(*[set(sets[i]) for i in chosen])) if chosen else 0


def test_step5_greedy_coverage_order():
    sets = [[0, 1, 2], [3, 4], [0, 3, 5, 6], [7]]
    assert lab.greedy_coverage(sets, 2) == [2, 0]


@pytest.mark.parametrize("seed", range(40))
def test_step5_one_minus_one_over_e(seed):
    r = random.Random(seed)
    sets = [r.sample(range(12), r.randint(1, 5)) for _ in range(8)]
    k = 3
    chosen = lab.greedy_coverage(sets, k)
    assert len(chosen) == k and len(set(chosen)) == k
    opt = max(coverage(sets, C) for C in itertools.combinations(range(8), k))
    assert coverage(sets, chosen) >= (1 - 1 / math.e) * opt - 1e-9
