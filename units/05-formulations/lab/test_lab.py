"""Tests for unit 05. Run with `uv run co test 05`. You should not need to edit this."""

from dataclasses import replace
from itertools import combinations

import numpy as np
import pytest

from colib.mip import MILP, FacilityLocation, highs_mip, lp_relaxation, scip_mip
from colib.testing import load_lab

lab = load_lab(__file__)


def instances(k=6, F=4, C=7):
    return [FacilityLocation.random(F, C, seed) for seed in range(k)]


def brute(inst):
    best = None
    for k in range(1, inst.F + 1):
        for S in combinations(range(inst.F), k):
            v = sum(inst.open_cost[i] for i in S) + sum(min(inst.serve_cost[i][j] for i in S) for j in range(inst.C))
            best = v if best is None else min(best, v)
    return best


def mip_value(m):
    """Integer optimum from two independent solvers. HiGHS 1.14.0's presolve once
    returned a wrong optimum on one of these instances; two solvers must agree."""
    a, b = highs_mip(m), scip_mip(m)
    assert a.status == b.status, f"solvers disagree on status: HiGHS {a.status}, SCIP {b.status}"
    if a.status == "optimal":
        assert abs(a.value - b.value) < 1e-6, f"solvers disagree: HiGHS {a.value}, SCIP {b.value}"
    return a


def fix_open(milp: MILP, F, S):
    lb = list(milp.bounds()[0])
    ub = list(milp.bounds()[1])
    for i in range(F):
        lb[i] = ub[i] = 1 if i in S else 0
    return replace(milp, lb=tuple(lb), ub=tuple(ub))


def check_shape(m, inst, rows_ub):
    assert isinstance(m, MILP)
    assert m.n == inst.F + inst.F * inst.C
    assert len(m.A_eq) == inst.C and len(m.A_ub) == rows_ub
    assert m.integer is not None and all(m.integer[:inst.F]) and not any(m.integer[inst.F:])
    assert m.ub is not None and all(u == 1 for u in m.ub)


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("inst", instances(), ids=lambda i: f"F{i.F}C{i.C}")
def test_step1_aggregated_is_a_correct_model(inst):
    m = lab.ufl_aggregated(inst, inst.C)
    check_shape(m, inst, inst.F)
    assert abs(mip_value(m).value - brute(inst)) < 1e-6


def test_step1_fixed_open_sets_cost_what_they_should():
    inst = FacilityLocation.random(4, 6, 11)
    m = lab.ufl_aggregated(inst, inst.C)
    for S in [(0,), (1, 3), (0, 1, 2, 3)]:
        want = sum(inst.open_cost[i] for i in S) + sum(min(inst.serve_cost[i][j] for i in S) for j in range(inst.C))
        assert abs(lp_relaxation(fix_open(m, inst.F, S)).value - want) < 1e-6, S


@pytest.mark.parametrize("inst", instances(), ids=lambda i: f"F{i.F}C{i.C}")
def test_step1_bigger_M_is_weaker(inst):
    tight = lp_relaxation(lab.ufl_aggregated(inst, inst.C)).value
    loose = lp_relaxation(lab.ufl_aggregated(inst, 10 * inst.C)).value
    assert loose <= tight + 1e-7 and tight <= brute(inst) + 1e-7


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("inst", instances(), ids=lambda i: f"F{i.F}C{i.C}")
def test_step2_disaggregated_is_correct_and_stronger(inst):
    m = lab.ufl_disaggregated(inst)
    check_shape(m, inst, inst.F * inst.C)
    assert abs(mip_value(m).value - brute(inst)) < 1e-6
    agg_lp = lp_relaxation(lab.ufl_aggregated(inst, inst.C)).value
    dis_lp = lp_relaxation(m).value
    assert agg_lp <= dis_lp + 1e-7 <= brute(inst) + 2e-7


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(8))
def test_step3_brute_force(seed):
    inst = FacilityLocation.random(5, 9, 100 + seed)
    value, S = lab.ufl_brute_force(inst)
    assert value == brute(inst)
    assert len(S) >= 1 and all(0 <= i < inst.F for i in S)
    recomputed = sum(inst.open_cost[i] for i in S) + sum(min(inst.serve_cost[i][j] for i in S) for j in range(inst.C))
    assert recomputed == value, "the open set you return must achieve the value you return"


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(6))
def test_step4_capacitated_variants_agree_and_strong_is_stronger(seed):
    inst = FacilityLocation.random(4, 8, 200 + seed, capacity_ratio=1.6)
    weak, strong = lab.cfl(inst, False), lab.cfl(inst, True)
    check_shape(weak, inst, inst.F)
    check_shape(strong, inst, inst.F + inst.F * inst.C + 1)
    mw, ms = mip_value(weak), mip_value(strong)
    assert mw.status == ms.status == "optimal" and abs(mw.value - ms.value) < 1e-6
    x = ms.x[inst.F:].reshape(inst.F, inst.C)
    assert np.all(x @ np.array(inst.demand) <= np.array(inst.capacity) * ms.x[:inst.F] + 1e-6)
    assert lp_relaxation(weak).value <= lp_relaxation(strong).value + 1e-7


# ---------------------------------------------------------------- step 5 ---

def test_step5_gap_closed():
    assert lab.gap_closed(80, 90, 100) == pytest.approx(0.5)
    assert lab.gap_closed(80, 100, 100) == pytest.approx(1.0)
    assert lab.gap_closed(80, 80, 100) == pytest.approx(0.0)
    assert lab.gap_closed(100, 100, 100) == pytest.approx(1.0), "no gap to close counts as fully closed"
