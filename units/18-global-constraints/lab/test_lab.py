"""Tests for unit 18. Run with `uv run co test 18`. You should not need to edit this."""

import itertools
import math
import random

import pytest

from colib.oracle import brute_force
from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
cp = unit("17")

HARD = [[int(ch) for ch in row] for row in
        ("800000000", "003600000", "070090200", "050007000", "000045700",
         "000100030", "001000068", "008500010", "090000400")]


def gac_alldifferent(dom, offsets):
    n = len(dom)
    keep = [set() for _ in range(n)]
    for t in itertools.product(*(sorted(d) for d in dom)):
        if len({a + o for a, o in zip(t, offsets)}) == n:
            for i, a in enumerate(t):
                keep[i].add(a)
    return keep


def apply(prop, dom):
    out = prop.prune(dom)
    if out is None:
        return None
    return [frozenset(out.get(i, d)) & d for i, d in enumerate(dom)]


# ---------------------------------------------------------------- step 1 ---

def test_step1_value_graph():
    dom = [frozenset({1, 2}), frozenset({2, 3})]
    values, edges = lab.value_graph(dom, [0, 1], [0, 10])
    assert values == [1, 2, 12, 13]
    assert sorted(edges) == [(0, 0), (0, 1), (1, 2), (1, 3)]


@pytest.mark.parametrize("seed", range(30))
def test_step1_maximum_matching(seed):
    r = random.Random(seed)
    n = r.randint(1, 7)
    dom = [frozenset(r.sample(range(6), r.randint(1, 3))) for _ in range(n)]
    offsets = [r.randint(-1, 1) for _ in range(n)]
    m = lab.maximum_matching(dom, list(range(n)), offsets)
    values, edges = lab.value_graph(dom, list(range(n)), offsets)
    assert all((i, k) in set(edges) for i, k in m.items()) and len(set(m.values())) == len(m)
    shifted = [sorted({a + o for a in d}) for d, o in zip(dom, offsets)]
    perfect = any(len(set(t)) == n for t in itertools.product(*shifted))
    assert (len(m) == n) == perfect, "Hall's theorem: a perfect matching exactly when distinct values exist"


# ---------------------------------------------------------------- step 2 ---

def test_step2_classic_hall_set():
    dom = [frozenset({1, 2}), frozenset({1, 2}), frozenset({1, 2, 3})]
    got = apply(lab.AllDifferent([0, 1, 2]), dom)
    assert got == [{1, 2}, {1, 2}, {3}]
    assert lab.hall_set(dom, [0, 1, 2], [0, 0, 0], 2, 1) == [0, 1]
    assert lab.hall_set(dom, [0, 1, 2], [0, 0, 0], 2, 3) is None


def test_step2_fails_without_a_matching():
    dom = [frozenset({1, 2})] * 3
    assert lab.AllDifferent([0, 1, 2]).prune(dom) is None


@pytest.mark.parametrize("seed", range(80))
def test_step2_generalised_arc_consistency(seed):
    r = random.Random(seed)
    n = r.randint(1, 6)
    dom = [frozenset(r.sample(range(7), r.randint(1, 4))) for _ in range(n)]
    offsets = [r.randint(-2, 2) for _ in range(n)] if seed % 2 else [0] * n
    got = apply(lab.AllDifferent(range(n), offsets), dom)
    keep = gac_alldifferent(dom, offsets)
    if not keep[0]:
        assert got is None
    else:
        assert got == [frozenset(k) for k in keep], "exactly the values with a support"


@pytest.mark.parametrize("seed", range(40))
def test_step2_hall_sets_explain_every_removal(seed):
    r = random.Random(seed + 500)
    keep = [()]
    while not keep[0]:                                        # draw until satisfiable
        n = r.randint(2, 6)
        dom = [frozenset(r.sample(range(6), r.randint(1, 3))) for _ in range(n)]
        offsets = [0] * n
        keep = gac_alldifferent(dom, offsets)
    for i in range(n):
        for a in dom[i]:
            S = lab.hall_set(dom, list(range(n)), offsets, i, a)
            if a in keep[i]:
                assert S is None
            else:
                union = set().union(*(dom[j] for j in S))
                assert i not in S and len(union) == len(S) and a in union, (i, a, S)


def test_step2_not_the_decomposition():
    # x1, x2 in {1, 2}, x3 in {1, 2, 3}, x4 in {2, 3, 4} (positions 0-3): pairwise != prunes nothing;
    # alldifferent sees that {x1, x2} use up {1, 2}
    dom = [frozenset({1, 2}), frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({2, 3, 4})]
    pairwise = [cp.NotEqual(i, j) for i in range(4) for j in range(i + 1, 4)]
    assert all(apply(p, dom) == dom for p in pairwise)
    assert apply(lab.AllDifferent(range(4)), dom) == [{1, 2}, {1, 2}, {3}, {4}]


# ---------------------------------------------------------------- step 3 ---

def overload_free(t, durations, demands, capacity):
    horizon = max(a + d for a, d in zip(t, durations)) + 1
    return all(sum(r for a, d, r in zip(t, durations, demands) if a <= u < a + d) <= capacity for u in range(horizon))


def timetable_oracle(dom, durations, demands, capacity):
    """What timetable filtering must return, straight from the definition."""
    n = len(dom)
    parts = []
    for i in range(n):
        lst, ect = max(dom[i]), min(dom[i]) + durations[i]
        parts.append(set(range(lst, ect)) if lst < ect else set())
    profile = {}
    for i in range(n):
        for u in parts[i]:
            profile[u] = profile.get(u, 0) + demands[i]
    if any(v > capacity for v in profile.values()):
        return None
    out = []
    for i in range(n):
        keep = {t for t in dom[i] if all(profile.get(u, 0) - (demands[i] if u in parts[i] else 0) + demands[i] <= capacity
                                         for u in range(t, t + durations[i]))}
        if not keep:
            return None
        out.append(keep)
    return out


@pytest.mark.parametrize("seed", range(60))
def test_step3_timetable(seed):
    r = random.Random(seed)
    n = r.randint(1, 5)
    capacity = r.randint(1, 3)
    durations = [r.randint(1, 4) for _ in range(n)]
    demands = [r.randint(1, capacity) for _ in range(n)]
    dom = [frozenset(r.sample(range(9), r.randint(1, 4))) for _ in range(n)]
    got = apply(lab.Cumulative(range(n), durations, demands, capacity), dom)
    ref = timetable_oracle(dom, durations, demands, capacity)
    assert (got is None) == (ref is None)
    if got is not None:
        assert got == [frozenset(k) for k in ref]
        for t in itertools.product(*(sorted(d) for d in dom)):
            if overload_free(t, durations, demands, capacity):
                assert all(t[i] in got[i] for i in range(n)), "a feasible schedule was cut"


def test_step3_compulsory_part_pushes_a_task():
    # task 0 must run during [3, 5): task 1 (duration 3) cannot start at 1, 2, 3 or 4
    dom = [frozenset({2, 3}), frozenset(range(8))]
    got = apply(lab.Cumulative([0, 1], [3, 3], [1, 1], 1), dom)
    assert got[1] == {0, 5, 6, 7}


def test_step3_overload_fails():
    dom = [frozenset({2}), frozenset({3})]
    assert lab.Cumulative([0, 1], [3, 3], [1, 1], 1).prune(dom) is None
    assert lab.Cumulative([0, 1], [3, 3], [1, 1], 2).prune(dom) is not None


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("n,count", [(4, 2), (5, 10), (6, 4), (7, 40), (8, 92)])
def test_step4_queens_global(n, count):
    sols, stats = cp.solve(*lab.queens_global(n), all_solutions=True)
    assert len(sols) == count
    _, dec = cp.solve(*cp.queens(n), all_solutions=True)
    assert stats.nodes <= dec.nodes


def test_step4_sudoku_global_needs_fewer_nodes():
    with time_limit(120):
        sols, st = cp.solve(*lab.sudoku_global(HARD), all_solutions=True)
        _, dec = cp.solve(*cp.sudoku(HARD), all_solutions=True)
    assert len(sols) == 1
    assert st.nodes * 5 < dec.nodes, "global alldifferent should cut the tree several times over"


@pytest.mark.parametrize("n", [4, 6, 7])
def test_step4_pigeonhole(n):
    with time_limit(60):
        _, glob = cp.solve(*lab.pigeonhole(n, True))
        _, dec = cp.solve(*lab.pigeonhole(n, False))
    assert glob.nodes == 0, "the matching fails at the root"
    assert dec.nodes >= math.factorial(n - 1), "pairwise != searches through the permutations"


@pytest.mark.parametrize("seed", range(6))
def test_step4_jobshop_is_optimal(seed):
    shop = JobShop.random(3, seed=seed, machines=3)
    ref = brute_force(shop).value
    horizon = sum(d for job in shop.jobs for _, d in job)
    for use_global in (True, False):
        with time_limit(60):
            best, sol, stats, trace = lab.minimise(*lab.jobshop(shop, horizon, use_global))
        assert best == ref and stats.extra["complete"]
        assert [v for v, _ in trace] == sorted({v for v, _ in trace}, reverse=True), "each solution improves"
        ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
        start = dict(zip(ops, sol))
        for j, job in enumerate(shop.jobs):
            for k in range(len(job) - 1):
                assert start[(j, k)] + job[k][1] <= start[(j, k + 1)]
        for a, b in itertools.combinations(ops, 2):
            (ma, da), (mb, db) = shop.jobs[a[0]][a[1]], shop.jobs[b[0]][b[1]]
            if ma == mb:
                assert start[a] + da <= start[b] or start[b] + db <= start[a]
        assert sol[-1] == max(start[(j, len(job) - 1)] + job[-1][1] for j, job in enumerate(shop.jobs))


def test_step4_jobshop_model_shape():
    shop = JobShop.random(3, seed=1, machines=3)
    doms, props, mk = lab.jobshop(shop, 40, True)
    assert mk == 9 and len(doms) == 10
    assert sum(isinstance(p, lab.Cumulative) for p in props) == 3
    doms, props, mk = lab.jobshop(shop, 40, False)
    assert sum(isinstance(p, cp.Binary) for p in props) == 9


def test_step4_minimise_node_limit():
    shop = JobShop.ft06()
    best, sol, stats, trace = lab.minimise(*lab.jobshop(shop, 70, True), node_limit=300)
    assert not stats.extra["complete"] and stats.nodes <= 300
    assert best is None or best <= 70


def test_step4_minimise_infeasible():
    best, sol, stats, trace = lab.minimise([range(3), range(3)], [cp.NotEqual(0, 1), cp.LinearLe([0, 1], [1, 1], 0)], 0)
    assert best is None and sol is None and trace == []
