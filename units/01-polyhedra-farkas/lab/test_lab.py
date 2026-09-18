"""Tests for unit 01. Run with `uv run co test 01`. You should not need to edit this."""

import itertools
import random
from fractions import Fraction

import numpy as np
import pytest
from scipy.optimize import linprog
from scipy.spatial import HalfspaceIntersection

from colib.polyhedra import (box, dot, random_infeasible, random_polytope, rank,
                             satisfies)
from colib.testing import load_lab

lab = load_lab(__file__)


def lp_feasible(system) -> bool:
    A = np.array([a for a, _ in system], dtype=float)
    b = np.array([b for _, b in system], dtype=float)
    res = linprog(np.zeros(A.shape[1]), A_ub=A, b_ub=b, bounds=[(None, None)] * A.shape[1],
                  method="highs")
    return res.status == 0


def slice_nonempty(system, k, y):
    """Is there a real x_k such that (y with x_k) satisfies the system?"""
    lo, hi = None, None
    for a, b in system:
        rest = b - sum(a[j] * y[j] for j in range(len(a)) if j != k)
        if a[k] == 0:
            if rest < 0:
                return False
        elif a[k] > 0:
            v = Fraction(rest, a[k])
            hi = v if hi is None else min(hi, v)
        else:
            v = Fraction(rest, a[k])
            lo = v if lo is None else max(lo, v)
    return lo is None or hi is None or lo <= hi


# ---------------------------------------------------------------- step 1 ---

SQUARE_PLUS = [((1, 1), 4), ((-1, 0), 0), ((0, -1), 0), ((1, -1), 1)]


def test_step1_eliminated_variable_is_gone():
    out = lab.eliminate(SQUARE_PLUS, 0)
    assert out, "this polygon's projection is a bounded interval, so some constraints must remain"
    assert all(a[0] == 0 for a, _ in out)
    assert all(len(a) == 2 for a, _ in out), "keep the column, as zeros"


def test_step1_projection_of_a_triangle_by_hand():
    # x >= 0, y >= 0, x + y <= 4  projected onto y is 0 <= y <= 4
    tri = [((-1, 0), 0), ((0, -1), 0), ((1, 1), 4)]
    out = lab.eliminate(tri, 0)
    ys = [y for y in range(-3, 8) if satisfies(out, (0, y))]
    assert ys == [0, 1, 2, 3, 4]


@pytest.mark.parametrize("seed", range(8))
def test_step1_projection_is_exact_on_random_systems(seed):
    """y satisfies the eliminated system  <=>  some x_k extends y to a solution."""
    n = 3
    system = random_polytope(n, 6, seed=seed, R=6)
    r = random.Random(seed)
    for k in range(n):
        out = lab.eliminate(system, k)
        for _ in range(150):
            y = [r.randint(-8, 8) for _ in range(n)]
            y[k] = 0
            assert satisfies(out, y) == slice_nonempty(system, k, y), \
                f"eliminating x{k}: point {y} is classified wrongly"


def test_step1_row_count_is_bounded_by_the_pairing():
    system = random_polytope(4, 10, seed=3)
    k = 0
    p = sum(a[k] > 0 for a, _ in system)
    q = sum(a[k] < 0 for a, _ in system)
    z = len(system) - p - q
    assert len(lab.eliminate(system, k)) <= p * q + z


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(12))
def test_step2_agrees_with_highs(seed):
    system = random_infeasible(3, 6, seed=seed) if seed % 2 else random_polytope(3, 5, seed=seed)
    assert lab.fm_feasible(system) == lp_feasible(system)


def test_step2_empty_by_contradiction():
    assert not lab.fm_feasible([((1, 0), 1), ((-1, 0), -2)])       # x <= 1 and x >= 2
    assert lab.fm_feasible([((1, 0), 2), ((-1, 0), -2)])           # x = 2


# ---------------------------------------------------------------- step 3 ---

def test_step3_cube_has_eight_vertices():
    vs = lab.vertices(box(3, 1))
    assert sorted(tuple(map(int, v)) for v in vs) == sorted(itertools.product((-1, 1), repeat=3))


def test_step3_degenerate_apex_is_listed_once():
    # square pyramid: 4 facets meet at the apex, only 3 are needed to pin it
    pyramid = [((0, 0, -1), 0), ((1, 0, 1), 1), ((-1, 0, 1), 1), ((0, 1, 1), 1), ((0, -1, 1), 1)]
    vs = lab.vertices(pyramid)
    assert len(vs) == 5 and (0, 0, 1) in [tuple(map(int, v)) for v in vs]


@pytest.mark.parametrize("seed", range(6))
def test_step3_matches_qhull(seed):
    n = 3
    system = random_polytope(n, 5, seed=seed)
    mine = lab.vertices(system)
    for v in mine:
        assert satisfies(system, v), f"{v} is not in the polytope"
        tight = [a for a, b in system if dot(a, v) == b]
        assert rank(tight) == n, f"{v} is not a vertex: its tight constraints have rank {rank(tight)}"
    hs = np.array([[*a, -b] for a, b in system], dtype=float)
    ref = HalfspaceIntersection(hs, np.zeros(n)).intersections
    ref = {tuple(np.round(p, 6)) for p in ref}
    assert {tuple(np.round(np.array(v, dtype=float), 6)) for v in mine} == ref


# ---------------------------------------------------------------- step 4 ---

CONTRA = [((1, 0), 1), ((-1, 0), -2), ((0, 1), 5)]    # x <= 1, -x <= -2, y <= 5


def test_step4_accepts_a_real_certificate():
    assert lab.is_farkas_certificate(CONTRA, (1, 1, 0))
    assert lab.is_farkas_certificate(CONTRA, (3, 3, 0))


@pytest.mark.parametrize("y, why", [
    ((1, 1, 1), "y . A is not zero"),
    ((1, -1, 0), "negative multiplier"),
    ((0, 0, 0), "0 <= 0 proves nothing"),
    ((1, 1), "wrong length"),
])
def test_step4_rejects_non_certificates(y, why):
    assert not lab.is_farkas_certificate(CONTRA, y), why


def test_step4_works_with_fractions():
    assert lab.is_farkas_certificate(CONTRA, (Fraction(1, 2), Fraction(1, 2), 0))


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(15))
def test_step5_certificate_for_every_infeasible_system(seed):
    system = random_infeasible(3, 6, seed=seed)
    y = lab.farkas_certificate(system)
    assert y is not None, "this system is infeasible, so a certificate exists"
    assert lab_independent_check(system, y)


@pytest.mark.parametrize("seed", range(8))
def test_step5_none_for_feasible_systems(seed):
    assert lab.farkas_certificate(random_polytope(3, 5, seed=seed)) is None


def lab_independent_check(system, y):
    """Checked here from scratch, so a bug in your step 4 cannot hide one in step 5."""
    n = len(system[0][0])
    return (len(y) == len(system) and all(v >= 0 for v in y)
            and all(sum(v * a[j] for v, (a, _) in zip(y, system)) == 0 for j in range(n))
            and sum(v * b for v, (_, b) in zip(y, system)) < 0)
