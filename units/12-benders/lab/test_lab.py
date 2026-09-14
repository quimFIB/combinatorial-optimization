"""Tests for unit 12. Run with `uv run co test 12`. You should not need to edit this."""

import itertools
import random

import numpy as np
import pytest
from scipy.optimize import linprog

from colib.colgen import StochasticFacility
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
INF = float("inf")


def small(seed, penalty=50.0):
    r = random.Random(seed)
    ratio = 1.6 if penalty is not None else 2.5              # without a penalty, keep "all open" feasible
    return StochasticFacility.random(r.randint(2, 5), r.randint(3, 8), r.randint(1, 5), seed=seed, penalty=penalty,
                                     capacity_ratio=ratio)


def recourse_scipy(inst, s, y):
    """The scenario LP by scipy, independently of your code. INF if infeasible."""
    F, C = inst.F, inst.C
    pen = inst.penalty is not None
    nv = F * C + (C if pen else 0)
    c = [inst.cost[i][j] for i in range(F) for j in range(C)] + ([inst.penalty] * C if pen else [])
    A, b = [], []
    for j in range(C):                                        # -(sum_i x_ij + z_j) <= -d_j
        row = [0.0] * nv
        for i in range(F):
            row[i * C + j] = -1.0
        if pen:
            row[F * C + j] = -1.0
        A.append(row)
        b.append(-inst.demand[s][j])
    for i in range(F):
        row = [0.0] * nv
        for j in range(C):
            row[i * C + j] = 1.0
        A.append(row)
        b.append(inst.capacity[i] * y[i])
    res = linprog(c, A_ub=A, b_ub=b, bounds=(0, None), method="highs")
    return res.fun if res.status == 0 else INF


def total_cost(inst, y):
    qs = [recourse_scipy(inst, s, y) for s in range(inst.S)]
    return sum(f * v for f, v in zip(inst.open_cost, y)) + sum(p * q for p, q in zip(inst.prob, qs))


def brute_force(inst):
    return min(total_cost(inst, y) for y in itertools.product((0, 1), repeat=inst.F))


def cut_at(cut, y):
    const, coef = cut
    return const + sum(c * v for c, v in zip(coef, y))


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(20))
def test_step1_second_stage(seed):
    inst = small(seed)
    r = random.Random(seed)
    for s in range(inst.S):
        y = [r.randint(0, 1) for _ in range(inst.F)]
        q, v, alpha = lab.second_stage(inst, s, y)
        assert q == pytest.approx(recourse_scipy(inst, s, y), rel=1e-7, abs=1e-6)
        assert len(v) == inst.C and len(alpha) == inst.F
        assert all(x >= 0 for x in v) and all(x >= 0 for x in alpha), "duals v, alpha are nonnegative"
        dual_obj = sum(d * vj for d, vj in zip(inst.demand[s], v)) - sum(u * yi * a for u, yi, a in zip(inst.capacity, y, alpha))
        assert dual_obj == pytest.approx(q, rel=1e-7, abs=1e-6), "strong duality"
        assert all(v[j] - alpha[i] <= inst.cost[i][j] + 1e-7 for i in range(inst.F) for j in range(inst.C)), "dual feasible"


def test_step1_fractional_y():
    inst = small(3)
    y = [0.5] * inst.F
    q, _, _ = lab.second_stage(inst, 0, y)
    assert q == pytest.approx(recourse_scipy(inst, 0, y), abs=1e-6)


def test_step1_infeasible():
    inst = small(4, penalty=None)
    assert lab.second_stage(inst, 0, [0] * inst.F) == (INF, None, None)


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(15))
def test_step2_optimality_cuts_are_valid_and_tight(seed):
    inst = small(seed + 30)
    r = random.Random(seed)
    s = r.randrange(inst.S)
    y = [r.randint(0, 1) for _ in range(inst.F)]
    q, v, alpha = lab.second_stage(inst, s, y)
    cut = lab.optimality_cut(inst, s, v, alpha)
    assert len(cut[1]) == inst.F
    assert cut_at(cut, y) == pytest.approx(q, abs=1e-6), "tight at the y it came from"
    for other in itertools.product((0, 1), repeat=inst.F):
        assert cut_at(cut, other) <= recourse_scipy(inst, s, other) + 1e-6, "valid everywhere"


@pytest.mark.parametrize("seed", range(12))
def test_step2_feasibility_cuts(seed):
    inst = small(seed + 60, penalty=None)
    r = random.Random(seed)
    for s in range(inst.S):
        for y in itertools.product((0, 1), repeat=inst.F):
            cut = lab.feasibility_cut(inst, s, y)
            feasible = recourse_scipy(inst, s, y) < INF
            if feasible:
                assert cut is None
            else:
                assert cut is not None and cut_at(cut, y) > 1e-7, "the cut must cut off this y"
                for other in itertools.product((0, 1), repeat=inst.F):
                    if recourse_scipy(inst, s, other) < INF:
                        assert cut_at(cut, other) <= 1e-6, "and keep every feasible y"
            if r.random() < 0.7:
                break


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(12))
def test_step3_benders_is_optimal(seed):
    inst = small(seed + 90)
    ref = brute_force(inst)
    for multicut in (True, False):
        with time_limit(60):
            ub, y, history = lab.benders(inst, multicut=multicut)
        assert ub == pytest.approx(ref, rel=1e-5)
        assert total_cost(inst, y) == pytest.approx(ub, rel=1e-6), "the reported y must cost the reported bound"
        lowers = [h[0] for h in history]
        uppers = [h[1] for h in history]
        assert all(a <= b + 1e-6 for a, b in zip(lowers, lowers[1:])), "master bounds never decrease"
        assert all(a >= b - 1e-9 for a, b in zip(uppers, uppers[1:])), "record the best upper bound"
        assert all(lo <= ref + 1e-6 * max(1, ref) for lo in lowers)
        assert uppers[-1] - lowers[-1] <= 1e-6 * max(1.0, uppers[-1]) + 1e-9


@pytest.mark.parametrize("seed", range(6))
def test_step3_unequal_probabilities(seed):
    import dataclasses
    inst = StochasticFacility.random(4, 6, 6, seed=seed + 240)
    r = random.Random(seed)
    w = [r.uniform(0.1, 1.0) for _ in range(inst.S)]
    inst = dataclasses.replace(inst, prob=tuple(x / sum(w) for x in w))
    ref = brute_force(inst)
    for multicut in (True, False):
        ub, y, history = lab.benders(inst, multicut=multicut)
        assert ub == pytest.approx(ref, rel=1e-5)
        assert all(lo <= ref + 1e-6 * max(1, ref) for lo, _ in history), "cuts weighted by probability"


@pytest.mark.parametrize("seed", range(8))
def test_step3_with_feasibility_cuts(seed):
    inst = small(seed + 120, penalty=None)
    status, value, _, _, _ = inst.deterministic_equivalent()
    assert status == "optimal"
    with time_limit(60):
        ub, y, history = lab.benders(inst)
    assert ub == pytest.approx(value, rel=1e-5)
    assert total_cost(inst, y) == pytest.approx(ub, rel=1e-6)


def test_step3_matches_the_deterministic_equivalent():
    inst = StochasticFacility.random(8, 20, 15, seed=7)
    _, value, _, _, _ = inst.deterministic_equivalent()
    with time_limit(120):
        ub, _, _ = lab.benders(inst)
    assert ub == pytest.approx(value, rel=1e-5)


def test_step3_multicut_needs_fewer_iterations():
    multi = single = 0
    with time_limit(180):
        for seed in range(3):
            inst = StochasticFacility.random(10, 25, 8, seed=seed, capacity_ratio=2.5)
            multi += len(lab.benders(inst, multicut=True)[2])
            single += len(lab.benders(inst, multicut=False)[2])
    assert multi < single


def test_step3_master_relaxation_flag():
    inst = small(5)
    value, y, theta = lab.solve_master(inst, [], [], multicut=True, relax=True)
    assert value == pytest.approx(0.0) and len(theta) == inst.S
    value, y, theta = lab.solve_master(inst, [], [], multicut=False)
    assert all(v in (0, 1) for v in y) and len(theta) == 1


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(12))
def test_step4_pareto_cut(seed):
    inst = small(seed + 150)
    r = random.Random(seed)
    s = r.randrange(inst.S)
    y = [r.randint(0, 1) for _ in range(inst.F)]
    core = [r.uniform(0.2, 0.8) for _ in range(inst.F)]
    q, v, alpha = lab.second_stage(inst, s, y)
    mw = lab.pareto_cut(inst, s, y, core, q)
    plain = lab.optimality_cut(inst, s, v, alpha)
    assert cut_at(mw, y) == pytest.approx(q, rel=1e-6, abs=1e-5), "still tight at y"
    assert cut_at(mw, core) >= cut_at(plain, core) - 1e-6, "at least as strong at the core point"
    for other in itertools.product((0, 1), repeat=inst.F):
        assert cut_at(mw, other) <= recourse_scipy(inst, s, other) + 1e-5, "valid everywhere"
    assert cut_at(mw, core) == pytest.approx(best_at_core(inst, s, y, core, q), rel=1e-5, abs=1e-4), \
        "the strongest cut at the core point among those tight at y"


def best_at_core(inst, s, y, core, q):
    """max over optimal duals at y of the cut's value at core, by scipy."""
    F, C = inst.F, inst.C
    d, u = inst.demand[s], inst.capacity
    A, b = [], []
    for i in range(F):
        for j in range(C):
            row = [0.0] * (C + F)
            row[j], row[C + i] = 1.0, -1.0
            A.append(row)
            b.append(inst.cost[i][j])
    A.append([-float(x) for x in d] + [u[i] * y[i] for i in range(F)])      # value at y >= q
    b.append(-q + 1e-7 * max(1.0, abs(q)))
    c = [-float(x) for x in d] + [u[i] * core[i] for i in range(F)]
    res = linprog(c, A_ub=A, b_ub=b, bounds=[(0, inst.penalty)] * C + [(0, None)] * F, method="highs")
    return -res.fun


def test_step4_pareto_cut_picks_among_degenerate_duals():
    # one customer (demand 10), two facilities (capacity 10, unit costs 1 and 2), only the first open:
    # it runs at capacity, so the optimal duals are v - alpha_0 = 1 with v anywhere in [1, 50].
    # At the core point (0.5, 0.5) the strongest of those cuts has value 15; v = 1 gives only 10.
    inst = StochasticFacility(open_cost=(1, 1), capacity=(10, 10), cost=((1.0,), (2.0,)), demand=((10,),),
                              prob=(1.0,), penalty=50.0)
    q, _, _ = lab.second_stage(inst, 0, [1, 0])
    assert q == pytest.approx(10.0)
    mw = lab.pareto_cut(inst, 0, [1, 0], [0.5, 0.5], q)
    assert cut_at(mw, [1, 0]) == pytest.approx(10.0, abs=1e-5)
    assert cut_at(mw, [0.5, 0.5]) == pytest.approx(15.0, abs=1e-4)


@pytest.mark.parametrize("seed", range(6))
def test_step4_benders_with_pareto_cuts(seed):
    inst = small(seed + 180)
    with time_limit(60):
        ub, y, _ = lab.benders(inst, pareto=True)
    assert ub == pytest.approx(brute_force(inst), rel=1e-5)


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(8))
def test_step5_lp_first_is_optimal(seed):
    inst = small(seed + 210)
    with time_limit(60):
        ub, y, history = lab.benders(inst, lp_first=True)
    assert ub == pytest.approx(brute_force(inst), rel=1e-5)
    assert all(isinstance(v, int) and v in (0, 1) for v in y), "the answer comes from the integer phase"


def test_step5_lp_first_saves_integer_masters():
    plain = warm = 0
    with time_limit(240):
        for seed in range(3):
            inst = StochasticFacility.random(12, 30, 8, seed=seed, capacity_ratio=3.0)
            plain += len(lab.benders(inst)[2])
            warm += len(lab.benders(inst, lp_first=True)[2])
    assert warm < plain
