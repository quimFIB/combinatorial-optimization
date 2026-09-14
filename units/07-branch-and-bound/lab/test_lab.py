"""Tests for unit 07. Run with `uv run co test 07`. You should not need to edit this."""

import math
from functools import lru_cache

import pytest

from colib import ref
from colib.bb import BBResult, NodeLP, multi_knapsack, solve_node
from colib.mip import MILP, FacilityLocation, scip_mip
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
formulations = ref.unit("05")


@lru_cache(maxsize=None)
def instance(kind, seed):
    if kind == "knap":
        return multi_knapsack(13, 2, seed)
    return formulations.ufl_aggregated(FacilityLocation.random(4, 7, seed), 7)


@lru_cache(maxsize=None)
def optimum(kind, seed):
    return scip_mip(instance(kind, seed)).value


CASES = [("knap", s) for s in range(6)] + [("ufl", s) for s in range(3)]


def node_at(x, milp):
    lb, ub = milp.bounds()
    return (tuple(lb), tuple(ub), NodeLP("optimal", 0.0, tuple(x)))


# ---------------------------------------------------------------- step 1 ---

def test_step1_most_fractional_and_children():
    m = MILP(c=(0, 0, 0, 0), integer=(True, True, False, True), ub=(5, 5, 5, 5))
    assert lab.most_fractional(m, node_at((0.2, 1.5, 0.5, 2.6), m), {}) == 1     # x2 continuous, ignored
    assert lab.most_fractional(m, node_at((0.25, 2.0, 0.5, 1.75), m), {}) == 0   # tie: lowest index
    assert lab.most_fractional(m, node_at((1.0, 2.0, 0.4, 3.0), m), {}) is None
    down, up = lab.children((0, 0, 0), (5, 5, 5), 1, 2.4)
    assert tuple(down[0]) == (0, 0, 0) and tuple(down[1]) == (5, 2, 5)
    assert tuple(up[0]) == (0, 3, 0) and tuple(up[1]) == (5, 5, 5)


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("selection", ["best", "dfs"])
@pytest.mark.parametrize("kind, seed", CASES)
def test_step2_finds_the_optimum(kind, seed, selection):
    m = instance(kind, seed)
    with time_limit(60, "Is the tree pruning by bound?"):
        r = lab.branch_and_bound(m, lab.most_fractional, selection)
    assert isinstance(r, BBResult) and r.status == "optimal"
    assert abs(r.value - optimum(kind, seed)) < 1e-6
    assert m.is_feasible(r.x) and abs(m.objective(r.x) - r.value) < 1e-6
    assert r.lp_solves == r.nodes, "most-fractional branching solves exactly one LP per node"


def test_step2_best_first_needs_no_more_nodes_than_dfs_overall():
    best = sum(lab.branch_and_bound(instance(k, s), lab.most_fractional, "best").nodes for k, s in CASES)
    dfs = sum(lab.branch_and_bound(instance(k, s), lab.most_fractional, "dfs").nodes for k, s in CASES)
    assert best <= dfs


def test_step2_infeasible_and_node_limit():
    infeasible = MILP(c=(1, 1), A_ub=((2, 2),), b_ub=(1,), A_eq=((1, 1),), b_eq=(1,),
                      ub=(1, 1), integer=(True, True))          # x1 + x2 = 1 but 2x1 + 2x2 <= 1
    assert lab.branch_and_bound(infeasible).status == "infeasible"
    parity = MILP(c=(-1,), A_eq=((2,),), b_eq=(1,), ub=(10,), integer=(True,))   # 2x = 1: LP feasible, IP not
    assert lab.branch_and_bound(parity).status == "infeasible"
    r = lab.branch_and_bound(instance("knap", 0), lab.most_fractional, "dfs", node_limit=5)
    assert r.status == "node_limit" and r.nodes <= 5


# ---------------------------------------------------------------- step 3 ---

def test_step3_product_score():
    assert lab.product_score(2.0, 3.0) == pytest.approx(6.0)
    assert lab.product_score(0.0, 5.0) > 0, "a zero gain must not zero out the other side"
    assert lab.product_score(0.0, 5.0) < lab.product_score(1.0, 1.0)


# ---------------------------------------------------------------- step 4 ---

def test_step4_pseudocost_uses_the_history():
    m = MILP(c=(0, 0, 0), integer=(True, True, True), ub=(5, 5, 5))
    node = node_at((0.5, 0.5, 0.5), m)
    stats = {"lp_solves": 0, "pseudo": {(0, "down"): [1.0], (0, "up"): [1.0],
                                        (1, "down"): [9.0], (1, "up"): [9.0],
                                        (2, "down"): [0.1], (2, "up"): [0.1]}}
    assert lab.pseudocost(m, node, stats) == 1


def test_step4_tree_records_pseudocosts():
    seen = {}

    def spy(milp, node, stats):
        seen.update(stats["pseudo"])
        return lab.most_fractional(milp, node, stats)

    lab.branch_and_bound(instance("knap", 1), spy, "best")
    assert seen, "branch_and_bound must record per-unit gains in stats['pseudo']"
    assert all(k[1] in ("down", "up") and all(g >= 0 for g in v) for k, v in seen.items())


@pytest.mark.parametrize("kind, seed", CASES)
def test_step4_pseudocost_is_correct(kind, seed):
    r = lab.branch_and_bound(instance(kind, seed), lab.pseudocost, "best")
    assert r.status == "optimal" and abs(r.value - optimum(kind, seed)) < 1e-6


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("kind, seed", CASES)
def test_step5_strong_branching_is_correct_and_probes(kind, seed):
    r = lab.branch_and_bound(instance(kind, seed), lab.strong_branching, "best")
    assert r.status == "optimal" and abs(r.value - optimum(kind, seed)) < 1e-6
    if r.nodes > 1:
        assert r.lp_solves > r.nodes, "strong branching's probe LPs must be counted in stats['lp_solves']"


def test_step5_fewer_nodes_more_lps_than_most_fractional():
    mf = [lab.branch_and_bound(instance(k, s), lab.most_fractional, "best") for k, s in CASES]
    sb = [lab.branch_and_bound(instance(k, s), lab.strong_branching, "best") for k, s in CASES]
    assert sum(r.nodes for r in sb) < sum(r.nodes for r in mf)
    assert sum(r.lp_solves for r in sb) > sum(r.lp_solves for r in mf)


# ---------------------------------------------------------------- extra checks (mutation-driven) ---

def test_step2_best_first_branches_in_bound_order_and_never_above_the_optimum():
    order = []

    def spy(milp, node, stats):
        order.append(node[2].value)
        return lab.most_fractional(milp, node, stats)

    kind, seed = "knap", 2
    lab.branch_and_bound(instance(kind, seed), spy, "best")
    assert order == sorted(order), "best-first must always expand the open node with the smallest bound"
    assert max(order) <= optimum(kind, seed) + 1e-6


def test_step4_recorded_gain_is_per_unit_of_fractionality():
    # min -x - y, 2x <= 3, 2y <= 3: root (1.5, 1.5) = -3. Branch x: down x <= 1 gives -2.5,
    # a gain of 0.5 over a fractionality of 0.5, so 1.0 per unit; up x >= 2 is infeasible.
    m = MILP(c=(-1, -1), A_ub=((2, 0), (0, 2)), b_ub=(3, 3), ub=(5, 5), integer=(True, True))
    snapshots = []

    def spy(milp, node, stats):
        snapshots.append({k: list(v) for k, v in stats["pseudo"].items()})
        return lab.most_fractional(milp, node, stats)

    lab.branch_and_bound(m, spy, "best")
    assert len(snapshots) >= 2
    assert snapshots[1] == {(0, "down"): [pytest.approx(1.0)]}


def test_step4_scores_weight_pseudocosts_by_fractionality():
    m = MILP(c=(0, 0), integer=(True, True), ub=(5, 5))
    node = node_at((0.02, 0.5), m)
    stats = {"lp_solves": 0, "pseudo": {(0, "down"): [10.0], (0, "up"): [10.0],
                                        (1, "down"): [4.0], (1, "up"): [4.0]}}
    # x0: 0.02*10 x 0.98*10 = 1.96;  x1: 0.5*4 x 0.5*4 = 4.0
    assert lab.pseudocost(m, node, stats) == 1
