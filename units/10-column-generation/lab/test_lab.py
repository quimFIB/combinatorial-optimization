"""Tests for unit 10. Run with `uv run co test 10`. You should not need to edit this."""

import itertools
import math
import random

import numpy as np
import pytest

from colib.colgen import CVRP, CuttingStock
from colib.mip import MILP, highs_mip
from colib.ref import unit
from colib.solvers import highs_lp
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def all_patterns(W, widths):
    out = []

    def rec(i, left, cur):
        if i == len(widths):
            if any(cur):
                out.append(tuple(cur))
            return
        for k in range(left // widths[i] + 1):
            rec(i + 1, left - k * widths[i], cur + [k])

    rec(0, W, [])
    return out


def full_lp(inst):
    """The master LP over every pattern: the value column generation must reach."""
    P = all_patterns(inst.W, inst.widths)
    A = np.array([[p[i] for p in P] for i in range(inst.m)], float)
    return highs_lp(A, np.full(inst.m, np.inf), np.ones(len(P)), sense="min",
                    row_lower=np.array(inst.demands, float)).value


def small(seed):
    return CuttingStock.random(random.Random(seed).randint(2, 6), seed=seed, W=100)


def fits(inst, pattern):
    return len(pattern) == inst.m and all(k >= 0 for k in pattern) and \
        sum(k * w for k, w in zip(pattern, inst.widths)) <= inst.W


def covers(inst, patterns, counts):
    return all(sum(c * p[i] for c, p in zip(counts, patterns)) >= inst.demands[i] - 1e-6 for i in range(inst.m))


# ---------------------------------------------------------------- step 1 ---

def test_step1_initial_patterns():
    assert lab.initial_patterns(100, [30, 45, 60]) == [(3, 0, 0), (0, 2, 0), (0, 0, 1)]


@pytest.mark.parametrize("seed", range(15))
def test_step1_master_on_initial_patterns(seed):
    inst = small(seed)
    pats = lab.initial_patterns(inst.W, inst.widths)
    value, x, duals = lab.solve_master(pats, inst.demands)
    assert value == pytest.approx(sum(d / (inst.W // w) for d, w in zip(inst.demands, inst.widths)))
    assert len(x) == len(pats) and len(duals) == inst.m
    assert covers(inst, pats, x)


@pytest.mark.parametrize("seed", range(15))
def test_step1_duals_are_a_certificate(seed):
    inst = small(seed + 20)
    pats = all_patterns(inst.W, inst.widths)[: 3 * inst.m] + lab.initial_patterns(inst.W, inst.widths)
    value, x, duals = lab.solve_master(pats, inst.demands)
    assert all(y >= -1e-9 for y in duals), "covering constraints have nonnegative duals"
    assert all(sum(a * y for a, y in zip(p, duals)) <= 1 + 1e-7 for p in pats), "dual feasibility"
    assert sum(d * y for d, y in zip(inst.demands, duals)) == pytest.approx(value), "strong duality"


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(25))
def test_step2_price_is_the_best_pattern(seed):
    inst = small(seed + 40)
    r = random.Random(seed)
    duals = [round(r.uniform(0, 0.5), 4) for _ in range(inst.m)]
    value, pattern = lab.price(inst.W, inst.widths, duals)
    assert fits(inst, pattern)
    assert value == pytest.approx(sum(a * y for a, y in zip(pattern, duals)))
    assert value == pytest.approx(max(sum(a * y for a, y in zip(p, duals)) for p in all_patterns(inst.W, inst.widths)))


@pytest.mark.parametrize("seed", range(15))
def test_step2_farley_bound_is_valid(seed):
    inst = small(seed + 60)
    r = random.Random(seed)
    duals = [r.uniform(0, 0.6) for _ in range(inst.m)]
    pv, _ = lab.price(inst.W, inst.widths, duals)
    bound = lab.farley_bound(inst.demands, duals, pv)
    assert bound == pytest.approx(sum(d * y for d, y in zip(inst.demands, duals)) / pv)
    assert bound <= full_lp(inst) + 1e-6


def test_step2_farley_with_zero_duals():
    assert lab.farley_bound([3, 4], [0.0, 0.0], 0.0) == 0.0


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(25))
def test_step3_reaches_the_full_lp(seed):
    inst = small(seed)
    with time_limit(30):
        value, patterns, x, history = lab.column_generation(inst.W, inst.widths, inst.demands)
    ref = full_lp(inst)
    assert value == pytest.approx(ref, abs=1e-6)
    assert all(fits(inst, p) for p in patterns)
    assert len(x) == len(patterns) and covers(inst, patterns, x)
    assert sum(x) == pytest.approx(value)


@pytest.mark.parametrize("seed", range(15))
def test_step3_history(seed):
    inst = small(seed + 100)
    value, patterns, x, history = lab.column_generation(inst.W, inst.widths, inst.demands)
    ref = full_lp(inst)
    masters = [h[0] for h in history]
    bounds = [h[1] for h in history]
    assert all(a >= b - 1e-7 for a, b in zip(masters, masters[1:])), "the master value never increases"
    assert all(a <= b + 1e-12 for a, b in zip(bounds, bounds[1:])), "record the best bound so far"
    assert all(b <= ref + 1e-6 for b in bounds), "every bound is a lower bound"
    assert bounds[-1] == pytest.approx(value, abs=1e-6), "at the end the bound meets the master"
    assert masters[-1] == pytest.approx(value)
    assert len(patterns) == inst.m + len(history) - 1, "one new pattern per non-final iteration"


def test_step3_larger_instance():
    inst = CuttingStock.random(30, seed=3, W=1000)
    with time_limit(60):
        value, patterns, x, history = lab.column_generation(inst.W, inst.widths, inst.demands)
    _, _, duals = lab.solve_master(patterns, inst.demands)
    pv, _ = unit("16").unbounded_knapsack(duals, list(inst.widths), inst.W)
    assert pv <= 1 + 1e-7, "no pattern with negative reduced cost may remain"
    assert covers(inst, patterns, x)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(15))
def test_step4_round_up(seed):
    inst = small(seed + 200)
    value, patterns, x, _ = lab.column_generation(inst.W, inst.widths, inst.demands)
    rolls, counts = lab.round_up(patterns, x)
    assert all(isinstance(c, int) and c >= 0 for c in counts)
    assert rolls == sum(counts) and covers(inst, patterns, counts)
    assert counts == [math.ceil(v - 1e-9) for v in x]


@pytest.mark.parametrize("seed", range(15))
def test_step4_restricted_master_ip(seed):
    inst = small(seed + 300)
    value, patterns, x, _ = lab.column_generation(inst.W, inst.widths, inst.demands)
    rolls, counts = lab.restricted_master_ip(patterns, inst.demands)
    assert rolls == sum(counts) and covers(inst, patterns, counts)
    assert math.ceil(value - 1e-9) <= rolls <= lab.round_up(patterns, x)[0]
    P = all_patterns(inst.W, inst.widths)                      # the integer optimum, over every pattern
    opt = highs_mip(MILP(c=(1,) * len(P), A_ub=tuple(tuple(-p[i] for p in P) for i in range(inst.m)),
                         b_ub=tuple(-d for d in inst.demands), integer=(True,) * len(P)),
                    options={"mip_rel_gap": 0.0})
    assert opt.status == "optimal" and rolls >= round(opt.value)


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(15))
def test_step5_same_lp_value(seed):
    inst = small(seed + 400)
    with time_limit(30):
        value, patterns, x, history = lab.stabilised_column_generation(inst.W, inst.widths, inst.demands)
    ref = full_lp(inst)
    assert value == pytest.approx(ref, abs=1e-6)
    assert covers(inst, patterns, x) and all(fits(inst, p) for p in patterns)
    assert all(b <= ref + 1e-6 for _, b in history)
    assert history[-1][1] == pytest.approx(value, abs=1e-6)


@pytest.mark.parametrize("seed", range(5))
def test_step5_alpha_zero_is_plain(seed):
    inst = CuttingStock.random(12, seed=seed, W=1000)
    plain = lab.column_generation(inst.W, inst.widths, inst.demands)
    zero = lab.stabilised_column_generation(inst.W, inst.widths, inst.demands, alpha=0.0)
    assert len(zero[3]) == len(plain[3]) and zero[0] == pytest.approx(plain[0])


def test_step5_fewer_iterations_overall():
    plain = stab = 0
    with time_limit(120):
        for seed in range(3):
            inst = CuttingStock.random(30, seed=seed, W=10000, low=0.01, high=0.2, demand=(10, 100))
            plain += len(lab.column_generation(inst.W, inst.widths, inst.demands)[3])
            stab += len(lab.stabilised_column_generation(inst.W, inst.widths, inst.demands)[3])
    assert stab < plain


# ---------------------------------------------------------------- step 6 ---

def subset_columns(cv):
    """Every capacity-feasible customer set with its optimal route cost (Held–Karp)."""
    hk = unit("16").held_karp
    cols = []
    for k in range(1, cv.n + 1):
        for S in itertools.combinations(range(1, cv.n + 1), k):
            if cv.route_load(S) <= cv.capacity:
                nodes = (0,) + S
                cols.append((S, hk([[cv.dist[a][b] for b in nodes] for a in nodes])[0]))
    return cols


def instance(seed):
    return CVRP.random(random.Random(seed).randint(3, 8), seed=seed, capacity=15)


@pytest.mark.parametrize("seed", range(20))
def test_step6_espprc_brute_force(seed):
    cv = instance(seed)
    r = random.Random(seed + 9)
    duals = [0.0] + [round(r.uniform(0, 60), 2) for _ in range(cv.n)]
    with time_limit(30):
        found = lab.espprc(cv, duals)
    assert found, "at least one route exists"
    assert [f[0] for f in found] == sorted(f[0] for f in found), "sorted by reduced cost"
    for rc, route in found:
        assert len(set(route)) == len(route) and all(1 <= v <= cv.n for v in route), "elementary"
        assert cv.route_load(route) <= cv.capacity
        assert rc == pytest.approx(cv.route_cost(route) - sum(duals[v] for v in route))
    best = min(c - sum(duals[v] for v in S) for S, c in subset_columns(cv))
    assert found[0][0] == pytest.approx(best)


@pytest.mark.parametrize("seed", range(40))
def test_step6_espprc_long_routes(seed):
    # high duals and roomy vehicles make long routes attractive: dominance must respect visited sets
    r = random.Random(seed)
    n = r.randint(5, 8)
    cv = CVRP.random(n, seed=seed, capacity=r.choice([15, 25, 40]))
    duals = [0.0] + [round(r.uniform(20, 90), 2) for _ in range(n)]
    with time_limit(30):
        found = lab.espprc(cv, duals)
    best = min(c - sum(duals[v] for v in S) for S, c in subset_columns(cv))
    assert found[0][0] == pytest.approx(best)
    assert all(len(set(route)) == len(route) for _, route in found)


def test_step6_espprc_max_routes():
    cv = CVRP.random(6, seed=1, capacity=30)
    found = lab.espprc(cv, [0.0] + [50.0] * 6, max_routes=3)
    assert len(found) == 3


@pytest.mark.parametrize("seed", range(12))
def test_step6_vrp_lp_bound(seed):
    cv = instance(seed + 50)
    cols = subset_columns(cv)
    A = np.array([[1.0 if v in S else 0.0 for S, _ in cols] for v in range(1, cv.n + 1)])
    costs = np.array([c for _, c in cols], float)
    ref = highs_lp(A, np.ones(cv.n), costs, sense="min", row_lower=np.ones(cv.n)).value
    with time_limit(60):
        value, routes, x = lab.vrp_column_generation(cv)
    assert value == pytest.approx(ref, abs=1e-6)
    assert len(x) == len(routes)
    assert all(abs(sum(xi for xi, r in zip(x, routes) if v in r) - 1) < 1e-6 for v in range(1, cv.n + 1))
    assert value == pytest.approx(sum(xi * cv.route_cost(r) for xi, r in zip(x, routes)))
    ip = highs_mip(MILP(c=tuple(costs), A_eq=tuple(map(tuple, A)), b_eq=(1,) * cv.n, ub=(1,) * len(cols),
                        integer=(True,) * len(cols)))
    assert value <= ip.value + 1e-6
