"""Tests for unit 03. Run with `uv run co test 03`. You should not need to edit this."""

import random
from fractions import Fraction as F

import pytest

from colib import ref
from colib.lp import GeneralLP, fractions, random_general_lp, random_lp
from colib.solvers import highs_general
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
simplex = ref.unit("02")

SMALL = ([[F(1), F(1)], [F(2), F(1)]], [F(4), F(6)], [F(3), F(2)])   # opt 10 at (2,2), duals (1,1)


def solved(seed, m=4, n=5):
    A, b, c = fractions(*random_lp(m, n, seed, kind="bounded"))
    return A, b, c, simplex.two_phase(A, b, c)


# ---------------------------------------------------------------- step 1 ---

def test_step1_textbook_pair():
    # max 3x + 2y, x + y <= 4, 2x + y <= 6, x, y >= 0   <->   min 4u + 6v, u + 2v >= 3, u + v >= 2, u, v >= 0
    P = GeneralLP("max", (3, 2), ((1, 1), (2, 1)), ("<=", "<="), (4, 6), (">=0", ">=0"))
    D = lab.dual(P)
    assert D == GeneralLP("min", (4, 6), ((1, 2), (1, 1)), (">=", ">="), (3, 2), (">=0", ">=0"))


def test_step1_every_sign_rule_for_a_max_primal():
    P = GeneralLP("max", (1, 1, 1), ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                  ("<=", ">=", "="), (1, 2, 3), (">=0", "<=0", "free"))
    D = lab.dual(P)
    assert D.sense == "min" and D.signs == (">=0", "<=0", "free") and D.senses == (">=", "<=", "=")


def test_step1_every_sign_rule_for_a_min_primal():
    P = GeneralLP("min", (1, 1, 1), ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                  ("<=", ">=", "="), (1, 2, 3), (">=0", "<=0", "free"))
    D = lab.dual(P)
    assert D.sense == "max" and D.signs == ("<=0", ">=0", "free") and D.senses == ("<=", ">=", "=")


@pytest.mark.parametrize("seed", range(40))
def test_step1_dual_of_dual_and_strong_duality(seed):
    P = random_general_lp(4, 4, seed)
    D = lab.dual(P)
    assert lab.dual(D) == P, "the dual of the dual must be the primal, exactly"
    hp, hd = highs_general(P), highs_general(D)
    if hp.status == "optimal":
        assert hd.status == "optimal" and abs(hp.value - hd.value) < 1e-7
    elif hp.status == "unbounded":
        assert hd.status == "infeasible"


# ---------------------------------------------------------------- step 2 ---

def test_step2_duals_of_the_textbook_lp():
    r = simplex.two_phase(*SMALL)
    assert tuple(lab.duals_from_tableau(r, 2, 2)) == (1, 1)


@pytest.mark.parametrize("seed", range(30))
def test_step2_duals_are_dual_feasible_with_equal_objective(seed):
    A, b, c, r = solved(seed)
    y = lab.duals_from_tableau(r, len(c), len(b))
    assert len(y) == len(b) and all(v >= 0 for v in y)
    assert all(sum(A[i][j] * y[i] for i in range(len(b))) >= c[j] for j in range(len(c)))
    assert sum(bi * yi for bi, yi in zip(b, y)) == r.value


def test_step2_refuses_non_optimal():
    r = simplex.two_phase(*fractions([[1, -1]], [1], [1, 1]))
    with pytest.raises(ValueError):
        lab.duals_from_tableau(r, 2, 1)


# ---------------------------------------------------------------- step 3 ---

def test_step3_accepts_an_optimal_pair():
    ok, _ = lab.certify_optimal(*SMALL, (2, 2), (1, 1))
    assert ok


@pytest.mark.parametrize("x, y, why", [
    ((3, 0), (0, F(3, 2)), "values agree at 9, but (u, v) = (0, 3/2) breaks u + v >= 2"),
    ((2, 2), (0, 2), "dual feasible, but x = 2 > 0 while its dual constraint u + 2v >= 3 has slack 1"),
    ((F(5, 2), F(5, 2)), (1, 1), "x infeasible"),
    ((2, 2), (1, F(1, 2)), "y infeasible"),
    ((2, 2), (-1, 3), "negative dual"),
    ((0, 0), (1, 1), "both feasible, but u = 1 > 0 while constraint 1 has slack 4"),
])
def test_step3_rejects(x, y, why):
    ok, reason = lab.certify_optimal(*SMALL, x, y)
    assert not ok, why
    assert isinstance(reason, str) and reason


@pytest.mark.parametrize("seed", range(20))
def test_step3_certifies_every_simplex_answer(seed):
    A, b, c, r = solved(seed)
    y = lab.duals_from_tableau(r, len(c), len(b))
    assert lab.certify_optimal(A, b, c, r.x, y)[0]


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(40))
def test_step4_warm_start_agrees_with_cold_solve(seed):
    A, b, c, r = solved(seed)
    rr = random.Random(seed)
    a = [F(rr.randint(-3, 6)) for _ in c]
    beta = F(int(sum(ai * xi for ai, xi in zip(a, r.x))) - rr.randint(0, 4))
    T, basis = lab.add_constraint(r, a, beta)
    assert len(T) == len(r.tableau) + 1 and len(T[0]) == len(r.tableau[0]) + 1
    with time_limit(20, "Does dual_simplex terminate?"):
        warm = lab.dual_simplex(T, basis, len(c))
    cold = simplex.two_phase(A + [a], b + [beta], c)
    assert warm.status == cold.status
    if cold.status == "optimal":
        assert warm.value == cold.value
        assert sum(ai * xi for ai, xi in zip(a, warm.x)) <= beta


def test_step4_redundant_cut_needs_no_pivots():
    r = simplex.two_phase(*SMALL)
    T, basis = lab.add_constraint(r, [F(1), F(0)], F(100))
    assert lab.dual_simplex(T, basis, 2).pivots == 0


def test_step4_cut_off_everything_is_infeasible():
    r = simplex.two_phase(*SMALL)
    T, basis = lab.add_constraint(r, [F(-1), F(-1)], F(-5))     # x + y >= 5, but x + y <= 4
    assert lab.dual_simplex(T, basis, 2).status == "infeasible"


# ---------------------------------------------------------------- step 5 ---

def test_step5_range_on_the_textbook_lp():
    r = simplex.two_phase(*SMALL)
    assert tuple(lab.rhs_range(r, 2, 0)) == (-1, 2)      # x + y <= 4 can move within [3, 6]
    assert lab.predict_objective(r, 2, 2, 0, F(1)) == 11
    assert lab.predict_objective(r, 2, 2, 0, F(3)) is None


@pytest.mark.parametrize("seed", range(25))
def test_step5_predictions_inside_the_range_are_exact(seed):
    A, b, c, r = solved(seed)
    for i in range(len(b)):
        lo, hi = lab.rhs_range(r, len(c), i)
        assert lo is None or lo <= 0
        assert hi is None or hi >= 0
        for delta in [d for d in (lo, hi, (lo or F(-2)) / 2, (hi or F(2)) / 2) if d is not None]:
            p = lab.predict_objective(r, len(c), len(b), i, delta)
            b2 = list(b)
            b2[i] += delta
            q = simplex.two_phase(A, b2, c)
            assert p is not None and q.status == "optimal" and q.value == p, (i, delta)


@pytest.mark.parametrize("seed", range(25))
def test_step5_just_outside_the_range_is_refused(seed):
    A, b, c, r = solved(seed)
    for i in range(len(b)):
        lo, hi = lab.rhs_range(r, len(c), i)
        if hi is not None:
            assert lab.predict_objective(r, len(c), len(b), i, hi + F(1, 1000)) is None
        if lo is not None:
            assert lab.predict_objective(r, len(c), len(b), i, lo - F(1, 1000)) is None
