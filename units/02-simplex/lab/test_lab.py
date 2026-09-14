"""Tests for unit 02. Run with `uv run co test 02`. You should not need to edit this."""

from fractions import Fraction as F

import pytest

from colib.lp import Cycling, LPResult, beale, fractions, random_lp
from colib.solvers import highs_lp
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)

SMALL = ([[F(1), F(1)], [F(2), F(1)]], [F(4), F(6)], [F(3), F(2)])   # opt 10 at (2, 2)


def rows(T):
    return [list(r) for r in T]


# ---------------------------------------------------------------- step 1 ---

def test_step1_initial_tableau_layout():
    T, basis = lab.initial_tableau(*SMALL)
    assert rows(T) == [[1, 1, 1, 0, 4], [2, 1, 0, 1, 6], [-3, -2, 0, 0, 0]]
    assert list(basis) == [2, 3]


def test_step1_pivot_makes_a_unit_column_and_updates_basis():
    T, basis = lab.initial_tableau(*SMALL)
    T, basis = lab.pivot(T, basis, 1, 0)
    assert [T[i][0] for i in range(3)] == [0, 1, 0]
    assert list(basis) == [2, 0]
    assert rows(T) == [[0, F(1, 2), 1, F(-1, 2), 1], [1, F(1, 2), 0, F(1, 2), 3], [0, F(-1, 2), 0, F(3, 2), 9]]


def test_step1_pivot_preserves_the_solution_set():
    """Row operations: a point satisfying the old equality rows satisfies the new ones."""
    T, basis = lab.initial_tableau(*SMALL)
    x = [F(1), F(1), F(2), F(3)]                        # x1 = x2 = 1, slacks 2 and 3
    T2, _ = lab.pivot(T, basis, 0, 1)
    for r in T2[:-1]:
        assert sum(a * v for a, v in zip(r[:-1], x)) == r[-1]


# ---------------------------------------------------------------- step 2 ---

def test_step2_entering_rules():
    T = [[1, 0, 0, 0, 5], [-1, -7, -7, 0, 0]]
    assert lab.entering(T, "dantzig") == 1              # most negative, lowest index on ties
    assert lab.entering(T, "bland") == 0                # lowest index with negative cost
    assert lab.entering([[1, 1, 3], [0, 2, 9]], "bland") is None


def test_step2_ratio_test_and_ties():
    T = [[2, 1, 4], [1, 0, 2], [0, -1, 7], [-1, 0, 0]]  # rows 0 and 1 tie at ratio 2 in column 0
    assert lab.leaving(T, [5, 3, 4], 0, "dantzig") == 0  # lowest row
    assert lab.leaving(T, [5, 3, 4], 0, "bland") == 1    # smallest basic variable index
    assert lab.leaving([[-1, 3], [0, 4], [-1, 0]], [2, 3], 0) is None   # no positive entry: unbounded


# ---------------------------------------------------------------- step 3 ---

def test_step3_small_lp():
    r = lab.simplex(*SMALL)
    assert isinstance(r, LPResult) and r.status == "optimal"
    assert r.value == 10 and tuple(r.x) == (2, 2)


def test_step3_unbounded():
    r = lab.simplex([[F(1), F(-1)]], [F(1)], [F(1), F(1)])
    assert r.status == "unbounded"


@pytest.mark.parametrize("rule", ["bland", "dantzig"])
@pytest.mark.parametrize("seed", range(25))
def test_step3_agrees_with_highs_on_feasible_origin_lps(seed, rule):
    A, b, c = random_lp(4, 5, seed, kind="bounded")
    r = lab.simplex(*fractions(A, b, c), rule=rule)
    h = highs_lp(A, b, c)
    assert r.status == h.status
    if h.status == "optimal":
        assert abs(float(r.value) - h.value) < 1e-9
        assert all(sum(a * x for a, x in zip(row, r.x)) <= bi for row, bi in zip(A, b))


def test_step3_beale_cycles_under_dantzig_and_not_under_bland():
    hint = "Does simplex() remember the bases it has visited and raise Cycling on a repeat?"
    with time_limit(10, hint), pytest.raises(Cycling):
        lab.simplex(*beale(), rule="dantzig")
    with time_limit(10, "Bland's rule should terminate on Beale's example."):
        r = lab.simplex(*beale(), rule="bland")
    assert r.status == "optimal" and r.value == F(5, 4)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(60))
def test_step4_two_phase_agrees_with_highs_on_any_lp(seed):
    A, b, c = random_lp(4, 5, seed, kind="any")
    r = lab.two_phase(*fractions(A, b, c))
    h = highs_lp(A, b, c)
    assert r.status == h.status, f"seed {seed}"
    if h.status == "optimal":
        assert abs(float(r.value) - h.value) < 1e-9


def test_step4_equality_via_two_inequalities_and_redundant_rows():
    # x1 + x2 = 3 written twice as <= and >=, plus a duplicate: phase 1 must cope
    A = [[1, 1], [-1, -1], [-1, -1], [1, 0]]
    b = [3, -3, -3, 2]
    r = lab.two_phase(*fractions(A, b, [1, 2]))
    assert r.status == "optimal" and r.value == 6


def test_step4_detects_infeasible():
    r = lab.two_phase(*fractions([[1, 0], [-1, 0]], [1, -2], [1, 1]))
    assert r.status == "infeasible"


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("n", range(1, 8))
def test_step5_klee_minty_takes_exponentially_many_dantzig_pivots(n):
    A, b, c = lab.klee_minty(n)
    assert len(A) == n and len(b) == n and len(c) == n
    r = lab.simplex(*fractions(A, b, c), rule="dantzig")
    assert r.status == "optimal" and r.value == 100 ** (n - 1)
    assert r.pivots == 2 ** n - 1
