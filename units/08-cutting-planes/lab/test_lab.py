"""Tests for unit 08. Run with `uv run co test 08`. You should not need to edit this."""

import itertools
import random
from fractions import Fraction as F
from functools import lru_cache

import pytest

from colib import ref
from colib.bb import multi_knapsack
from colib.mip import lp_relaxation, scip_mip
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
simplex = ref.unit("02")


def small_ip(seed, n=3, m=3):
    r = random.Random(seed)
    A = [[r.randint(1, 9) for _ in range(n)] for _ in range(m)]
    b = [r.randint(10, 40) for _ in range(m)]
    c = [r.randint(1, 9) for _ in range(n)]
    return A, b, c


def integer_points(A, b):
    n = len(A[0])
    U = max(b)
    for x in itertools.product(range(U + 1), repeat=n):
        if all(sum(a * v for a, v in zip(row, x)) <= bb for row, bb in zip(A, b)):
            yield x


@lru_cache(maxsize=None)
def ip_opt(seed):
    A, b, c = small_ip(seed)
    return max(sum(ci * v for ci, v in zip(c, x)) for x in integer_points(A, b))


def fractional_rows(res, n):
    return [i for i, j in enumerate(res.basis) if j < n and res.tableau[i][-1].denominator != 1]


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(12))
def test_step1_gomory_cut_is_valid_and_cuts_off_the_vertex(seed):
    k = seed
    while True:                                               # skip instances whose LP optimum is already integral
        A, b, c = small_ip(k)
        res = simplex.two_phase(*[[list(map(F, r)) for r in A], list(map(F, b)), list(map(F, c))])
        if fractional_rows(res, 3):
            break
        k += 1000
    for row in fractional_rows(res, 3):
        a, beta = lab.gomory_cut(res, A, b, row)
        assert all(isinstance(v, int) for v in a) and isinstance(beta, int), "scale the cut to integers"
        assert sum(ai * xi for ai, xi in zip(a, res.x)) > beta, "the cut must be violated by the LP vertex"
        for x in integer_points(A, b):
            assert sum(ai * xi for ai, xi in zip(a, x)) <= beta, f"cut {a} <= {beta} removes integer point {x}"


def test_step1_textbook_cut():
    # max x2, 3x1 + 2x2 <= 6, -3x1 + 2x2 <= 0: LP optimum (1, 1.5); integer optimum has x2 = 1
    A, b, c = [[3, 2], [-3, 2]], [6, 0], [0, 1]
    res = simplex.two_phase([list(map(F, r)) for r in A], list(map(F, b)), list(map(F, c)))
    row = next(i for i, j in enumerate(res.basis) if j == 1)
    a, beta = lab.gomory_cut(res, A, b, row)
    assert a[1] > 0 and F(beta, a[1]) >= 1 and sum(ai * xi for ai, xi in zip(a, res.x)) > beta
    assert all(sum(ai * xi for ai, xi in zip(a, x)) <= beta for x in [(0, 0), (1, 0), (2, 0), (1, 1)])


def test_step1_fractional_row():
    A, b, c = small_ip(3)
    res = simplex.two_phase([list(map(F, r)) for r in A], list(map(F, b)), list(map(F, c)))
    i = lab.fractional_row(res, 3)
    assert i in fractional_rows(res, 3)
    A2, b2, c2 = [[1, 0], [0, 1]], [2, 3], [1, 1]
    res2 = simplex.two_phase([list(map(F, r)) for r in A2], list(map(F, b2)), list(map(F, c2)))
    assert lab.fractional_row(res2, 2) is None


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(15))
def test_step2_gomory_loop(seed):
    A, b, c = small_ip(seed)
    with time_limit(60):
        bounds, cuts, res = lab.gomory_loop(A, b, c, rounds=40)
    assert all(b2 <= b1 for b1, b2 in zip(bounds, bounds[1:])), "adding cuts can only lower a max LP bound"
    assert bounds[-1] >= ip_opt(seed)
    assert len(bounds) == len(cuts) + 1
    if res.status == "optimal" and all(v.denominator == 1 for v in res.x):
        assert res.value == ip_opt(seed)


def test_step2_closes_the_gap_on_most_instances():
    solved = sum(lab.gomory_loop(*small_ip(s), rounds=60)[0][-1] == ip_opt(s) for s in range(15))
    assert solved >= 12


# ---------------------------------------------------------------- step 3 ---

def violated_cover_exists(w, cap, x):
    n = len(w)
    return any(sum(w[j] for j in C) > cap and sum(1 - x[j] for j in C) < 1 - 1e-9
               for k in range(1, n + 1) for C in itertools.combinations(range(n), k))


@pytest.mark.parametrize("seed", range(25))
def test_step3_separation_is_exact(seed):
    r = random.Random(seed)
    n = 8
    w = [r.randint(3, 20) for _ in range(n)]
    cap = sum(w) // 2
    x = [round(r.random(), 3) for _ in range(n)]
    C = lab.separate_cover(w, cap, x)
    if C is None:
        assert not violated_cover_exists(w, cap, x)
    else:
        C = tuple(C)
        assert sum(w[j] for j in C) > cap, "a cover's weight must exceed the capacity"
        assert sum(x[j] for j in C) > len(C) - 1 + 1e-9, "the cover inequality must be violated"


def test_step3_finds_the_most_violated():
    w, cap = [5, 5, 5, 5], 9                 # any two items form a cover
    x = [1.0, 0.9, 0.2, 0.1]
    assert tuple(lab.separate_cover(w, cap, x)) == (0, 1)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(20))
def test_step4_lifted_cover_is_valid_and_maximal(seed):
    r = random.Random(100 + seed)
    n = 9
    w = [r.randint(3, 20) for _ in range(n)]
    cap = sum(w) // 2
    feasible = [x for x in itertools.product((0, 1), repeat=n) if sum(a * v for a, v in zip(w, x)) <= cap]
    # a minimal cover: greedily add the heaviest items until the weight exceeds the capacity
    order = sorted(range(n), key=lambda j: -w[j])
    C, tot = [], 0
    for j in order:
        C.append(j)
        tot += w[j]
        if tot > cap:
            break
    C = tuple(sorted(C))
    alpha = list(lab.lift_cover(w, cap, C))
    rhs = len(C) - 1
    assert len(alpha) == n and all(alpha[j] == 1 for j in C) and all(a >= 0 for a in alpha)
    assert all(sum(a * v for a, v in zip(alpha, x)) <= rhs for x in feasible), "lifted cut must stay valid"
    for j in range(n):
        if j in C:
            continue
        stronger = alpha.copy()
        stronger[j] += 1
        assert any(sum(a * v for a, v in zip(stronger, x)) > rhs for x in feasible), \
            f"coefficient of x{j} could be raised: lifting was not maximal"


# ---------------------------------------------------------------- step 5 ---

def test_step5_age_pool():
    pool = [((1, 1), 1, 0), ((1, 0), 1, 2), ((0, 1), 5, 3)]
    x = (0.5, 0.5)
    out = [tuple(p) for p in lab.age_pool(pool, x, max_age=3)]
    assert out == [((1, 1), 1, 0), ((1, 0), 1, 3)], "tight -> age 0, slack -> age+1, too old -> dropped"


@lru_cache(maxsize=None)
def knap(seed):
    return multi_knapsack(11, 2, seed, tightness=0.4)


@pytest.mark.parametrize("seed", range(6))
def test_step5_root_loop_raises_the_bound_with_valid_cuts(seed):
    m = knap(seed)
    with time_limit(60):
        bounds, sizes, added = lab.root_cut_loop(m)
    opt = scip_mip(m).value
    assert abs(bounds[0] - lp_relaxation(m).value) < 1e-6
    assert all(b2 >= b1 - 1e-7 for b1, b2 in zip(bounds, bounds[1:])), "a min LP bound must not decrease"
    assert bounds[-1] <= opt + 1e-6, "cuts must never cut off the integer optimum"
    assert len(sizes) == len(bounds) and added >= sizes[-1]


def test_step5_closes_part_of_the_gap():
    closed = []
    for s in range(6):
        m = knap(s)
        bounds, _, _ = lab.root_cut_loop(m)
        opt = scip_mip(m).value
        if opt - bounds[0] > 1e-6:
            closed.append((bounds[-1] - bounds[0]) / (opt - bounds[0]))
    assert closed and sum(closed) / len(closed) > 0.05
