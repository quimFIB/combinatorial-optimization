"""Tests for unit 22. Run with `uv run co test 22`. You should not need to edit this."""

import itertools
import random

import pytest
from pysat.solvers import Solver as PySat

from colib.mip import MILP, highs_mip
from colib.oracle import brute_force
from colib.problems import SetCover, VertexCover
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def rand3cnf(n, m, seed):
    r = random.Random(seed)
    return [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), 3)] for _ in range(m)]


def all_eight(n=3):
    """The 8 clauses over x1, x2, x3 with every sign pattern: unsatisfiable."""
    return [[s1 * 1, s2 * 2, s3 * 3] for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]


def sat(clauses):
    with PySat(name="minisat22", bootstrap_with=clauses) as s:
        return s.solve(), (s.get_model() if s.solve() else None)


def vc_optimum(vc):
    milp = MILP(c=(1,) * vc.n, A_ub=tuple(tuple(-1 if v in e else 0 for v in range(vc.n)) for e in vc.edges),
                b_ub=(-1,) * len(vc.edges), ub=(1,) * vc.n, integer=(True,) * vc.n)
    res = highs_mip(milp, options={"mip_rel_gap": 0.0})
    return round(res.value), [int(round(x)) for x in res.x]


def sc_optimum(sc):
    milp = MILP(c=tuple(sc.costs),
                A_ub=tuple(tuple(-1 if e in s else 0 for s in sc.sets) for e in range(sc.universe)),
                b_ub=(-1,) * sc.universe, ub=(1,) * sc.n, integer=(True,) * sc.n)
    return round(highs_mip(milp, options={"mip_rel_gap": 0.0}).value)


def model_to_assignment(model, n):
    values = {abs(l): l > 0 for l in model}
    return [values.get(v, False) for v in range(1, n + 1)]


# ---------------------------------------------------------------- step 1 ---

def test_step1_gadget_shape():
    clauses = [[1, -2, 3], [-1, 2, -3]]
    vc, k = lab.sat_to_vertex_cover(3, clauses)
    assert vc.n == 6 + 6 and k == 3 + 4
    edges = set(vc.edges)
    assert all(a < b for a, b in vc.edges)
    assert (0, 1) in edges and (2, 3) in edges and (4, 5) in edges, "variable edges"
    assert {(6, 7), (6, 8), (7, 8), (9, 10), (9, 11), (10, 11)} <= edges, "clause triangles"
    assert (0, 6) in edges and (3, 7) in edges and (4, 8) in edges, "corner t joined to its literal"
    assert len(edges) == 3 + 6 + 6


@pytest.mark.parametrize("seed", range(20))
def test_step1_iff_by_brute_force(seed):
    r = random.Random(seed)
    clauses = rand3cnf(3, r.randint(1, 3), seed) if seed % 4 else all_eight()[:r.randint(1, 4)]
    vc, k = lab.sat_to_vertex_cover(3, clauses)
    satisfiable = sat(clauses)[0]
    oracle = brute_force(vc)
    assert (oracle.value <= k) == satisfiable
    assert oracle.value >= k, "a cover always needs one vertex per variable edge and two per triangle"


@pytest.mark.parametrize("seed", range(15))
def test_step1_iff_larger(seed):
    r = random.Random(seed + 100)
    n = r.randint(4, 12)
    m = int(r.choice([2.0, 4.26, 6.0]) * n)
    clauses = rand3cnf(n, m, seed + 100)
    vc, k = lab.sat_to_vertex_cover(n, clauses)
    satisfiable, model = sat(clauses)
    value, cover = vc_optimum(vc)
    assert (value <= k) == satisfiable
    if satisfiable:
        a = model_to_assignment(model, n)
        forward = lab.cover_from_assignment(n, clauses, a)
        assert vc.is_feasible(forward) and sum(forward) == k
        back = lab.assignment_from_cover(n, clauses, cover)
        assert lab.satisfies(back, clauses), "a minimum cover maps back to a satisfying assignment"


def test_step1_unsatisfiable_needs_a_bigger_cover():
    clauses = all_eight()
    vc, k = lab.sat_to_vertex_cover(3, clauses)
    value, _ = vc_optimum(vc)
    assert value == k + 1


def test_step1_satisfies():
    assert lab.satisfies([True, False], [[1], [-2, 1]])
    assert not lab.satisfies([True, False], [[2], [-1]])


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(40))
def test_step2_equisatisfiable_3cnf(seed):
    r = random.Random(seed)
    n = r.randint(1, 7)
    clauses = [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), r.randint(1, n))]
               for _ in range(r.randint(1, 9))]
    n3, c3 = lab.cnf_to_3cnf(n, clauses)
    assert all(len(c) == 3 for c in c3), "exactly three literals per clause"
    assert all(abs(l) <= n3 for c in c3 for l in c) and n3 >= n
    s1, m1 = sat(clauses)
    s3, m3 = sat(c3)
    assert s1 == s3, "equisatisfiable"
    if s1:
        extended = lab.extend_assignment(n, clauses, model_to_assignment(m1, n))
        assert len(extended) == n3 and lab.satisfies(extended, c3), "a model extends to the new formula"
        assert lab.satisfies(model_to_assignment(m3, n3)[:n], clauses), "a model restricts to the old formula"


def test_step2_sizes():
    n3, c3 = lab.cnf_to_3cnf(2, [[1]])
    assert (n3, len(c3)) == (4, 4)
    n3, c3 = lab.cnf_to_3cnf(2, [[1, -2]])
    assert (n3, len(c3)) == (3, 2)
    n3, c3 = lab.cnf_to_3cnf(6, [[1, 2, 3, 4, 5, 6]])
    assert (n3, len(c3)) == (9, 4)
    assert lab.cnf_to_3cnf(3, [[1, 2, 3]]) == (3, [[1, 2, 3]])


def test_step2_chain_values():
    clauses = [[1, 2, 3, 4, 5]]
    for truth in itertools.product((False, True), repeat=5):
        if any(truth):
            ext = lab.extend_assignment(5, clauses, list(truth))
            assert ext[5:] == [not any(truth[:2]), not any(truth[:3])]


# ---------------------------------------------------------------- step 3 ---

def test_step3_set_cover_shape():
    vc = VertexCover(4, ((0, 1), (1, 2), (2, 3), (0, 3)))
    sc = lab.vertex_cover_to_set_cover(vc)
    assert isinstance(sc, SetCover) and sc.universe == 4 and sc.costs == (1, 1, 1, 1)
    assert sc.sets == (frozenset({0, 3}), frozenset({0, 1}), frozenset({1, 2}), frozenset({2, 3}))


@pytest.mark.parametrize("seed", range(20))
def test_step3_optimality_preserved(seed):
    vc = VertexCover.random(random.Random(seed).randint(3, 10), seed=seed, p=0.4)
    sc = lab.vertex_cover_to_set_cover(vc)
    for x in itertools.islice(itertools.product((0, 1), repeat=vc.n), 0, None, max(1, 2 ** vc.n // 64)):
        assert vc.is_feasible(list(x)) == sc.is_feasible(list(x)), "the same vectors are feasible"
        assert vc.objective(list(x)) == sc.objective(list(x))
    assert brute_force(vc).value == brute_force(sc).value


@pytest.mark.parametrize("seed", range(8))
def test_step3_chain_sat_to_set_cover(seed):
    n = 6
    clauses = rand3cnf(n, int(4.3 * n), seed + 300)
    sc, k = lab.sat_to_set_cover(n, clauses)
    assert (sc_optimum(sc) <= k) == sat(clauses)[0]


# ---------------------------------------------------------------- step 4 ---

def brute_knapsack(values, weights, C):
    n = len(values)
    return max(sum(values[i] for i in S) for k in range(n + 1) for S in itertools.combinations(range(n), k)
               if sum(weights[i] for i in S) <= C)


@pytest.mark.parametrize("seed", range(30))
def test_step4_by_value_is_exact(seed):
    r = random.Random(seed)
    n = r.randint(1, 11)
    values = [r.randint(1, 60) for _ in range(n)]
    weights = [r.randint(1, 30) for _ in range(n)]
    C = r.randint(0, 90)
    best, items = lab.knapsack_by_value(values, weights, C)
    assert best == brute_knapsack(values, weights, C)
    assert sum(weights[i] for i in items) <= C and sum(values[i] for i in items) == best and items == sorted(set(items))


@pytest.mark.parametrize("seed", range(30))
@pytest.mark.parametrize("eps", [0.5, 0.2, 0.05])
def test_step4_fptas_guarantee(seed, eps):
    r = random.Random(seed + 50)
    n = r.randint(1, 11)
    values = [r.randint(1, 1000) for _ in range(n)]
    weights = [r.randint(1, 30) for _ in range(n)]
    C = r.randint(0, 90)
    value, items = lab.knapsack_fptas(values, weights, C, eps)
    opt = brute_knapsack(values, weights, C)
    assert sum(weights[i] for i in items) <= C and value == sum(values[i] for i in items)
    assert value >= (1 - eps) * opt - 1e-9


def test_step4_fptas_scaling_makes_the_table_small():
    r = random.Random(4)
    n = 40
    values = [r.randint(10 ** 6, 10 ** 7) for _ in range(n)]
    weights = [r.randint(1, 100) for _ in range(n)]
    with time_limit(60):
        value, items = lab.knapsack_fptas(values, weights, 1000, 0.1)
    assert sum(weights[i] for i in items) <= 1000 and value > 0


def test_step4_fptas_scale_uses_n():
    # one item worth 100, ten worth 19 each; the ten fit together and are better. Scaling by eps * vmax
    # alone rounds every small item to 0 and loses the guarantee; eps * vmax / n does not.
    values = [100] + [19] * 10
    weights = [10] + [1] * 10
    value, items = lab.knapsack_fptas(values, weights, 10, 0.2)
    assert value >= 0.8 * 190


def test_step4_fptas_ignores_items_that_never_fit():
    # a huge item that cannot fit must not set the scale: otherwise everything else rounds to 0
    values = [10 ** 9] + [50, 60, 70]
    weights = [1000] + [5, 6, 7]
    value, items = lab.knapsack_fptas(values, weights, 13, 0.1)
    assert value >= 0.9 * 130 and 0 not in items


def test_step4_fptas_edge_cases():
    assert lab.knapsack_fptas([5, 7], [10, 12], 3, 0.1) == (0, [])
    assert lab.knapsack_fptas([], [], 10, 0.1) == (0, [])
    value, items = lab.knapsack_fptas([9], [3], 3, 0.5)
    assert (value, items) == (9, [0])
