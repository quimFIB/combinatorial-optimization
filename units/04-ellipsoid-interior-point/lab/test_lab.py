"""Tests for unit 04. Run with `uv run co test 04`. You should not need to edit this."""

import math

import numpy as np
import pytest

from colib.polyhedra import inscribed_radius, random_polytope, shifted_polytope
from colib.solvers import highs_lp
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def instance(seed, n=3, m=8):
    rows = random_polytope(n, m, seed=seed)
    A = np.array([a for a, _ in rows], float)
    b = np.array([bb for _, bb in rows], float)
    c = np.random.default_rng(seed).integers(-5, 6, n).astype(float)
    return A, b, c


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(6))
def test_step1_gradient_and_hessian_match_finite_differences(seed):
    A, b, c = instance(seed)
    rng = np.random.default_rng(seed)
    x = rng.uniform(-0.5, 0.5, 3)                 # the origin is well inside; stay near it
    t = 3.0
    f, g, H = lab.barrier(A, b, c, x, t)
    h = 1e-6
    fd_g = np.array([(lab.barrier(A, b, c, x + h * e, t)[0] - lab.barrier(A, b, c, x - h * e, t)[0]) / (2 * h)
                     for e in np.eye(3)])
    assert np.allclose(g, fd_g, rtol=1e-5, atol=1e-5)
    fd_H = np.array([(lab.barrier(A, b, c, x + h * e, t)[1] - lab.barrier(A, b, c, x - h * e, t)[1]) / (2 * h)
                     for e in np.eye(3)])
    assert np.allclose(H, fd_H, rtol=1e-4, atol=1e-4)
    assert np.allclose(H, H.T) and np.all(np.linalg.eigvalsh(H) > 0)


def test_step1_outside_is_infinite():
    A, b, c = instance(0)
    far = np.array([100.0, 0, 0])
    f, g, H = lab.barrier(A, b, c, far, 1.0)
    assert f == math.inf and g is None and H is None
    on_boundary = np.array([10.0, 0, 0])          # the box constraint x1 <= 10 is tight
    assert lab.barrier(A, b, c, on_boundary, 1.0)[0] == math.inf


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("t", [0.1, 1.0, 50.0])
def test_step2_newton_finds_the_minimizer(seed, t):
    from scipy.optimize import minimize
    A, b, c = instance(seed)
    with time_limit(10, "Does the backtracking line search terminate?"):
        x, steps = lab.newton_center(A, b, c, np.zeros(3), t)
    f, g, _ = lab.barrier(A, b, c, x, t)
    assert f < math.inf, "the result must stay strictly feasible"
    assert np.linalg.norm(g) <= 1e-4 * (1 + t * np.linalg.norm(c))
    assert steps < 60
    ref = minimize(lambda z: lab.barrier(A, b, c, z, t)[0], np.zeros(3), method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-12, "maxiter": 20000})
    assert f <= ref.fun + 1e-6


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(12))
def test_step3_path_reaches_the_optimum(seed):
    A, b, c = instance(seed)
    with time_limit(30):
        path = lab.central_path(A, b, c, np.zeros(3))
    t, x, y = path[-1]
    assert len(b) / t <= 1e-5
    h = highs_lp(A, b, c, lower=None)
    assert abs(c @ x - h.value) <= 1e-4 * max(1.0, abs(h.value))


@pytest.mark.parametrize("seed", range(12))
def test_step3_points_are_central(seed):
    A, b, c = instance(seed)
    path = lab.central_path(A, b, c, np.zeros(3))
    ts = [p[0] for p in path]
    assert ts[0] == 1.0 and np.allclose(np.diff(np.log(ts)), np.log(10.0)), "t starts at t0 = 1 and grows by mu = 10"
    values = [c @ p[1] for p in path]
    assert all(v2 >= v1 - 1e-7 for v1, v2 in zip(values, values[1:])), "objective must improve along the path"
    m = len(b)
    for t, x, y in path:
        if t > 1e5:
            continue                              # floating point degrades beyond this (see then.py)
        assert np.all(y > 0)
        _, g, H = lab.barrier(A, b, c, x, t)
        assert g @ np.linalg.solve(H, g) <= 1e-6, "x(t) must be centred: Newton decrement ~ 0"
        # b.y - c.x = y.(b - Ax) + x.(A^T y - c) = m/t + x.(residual): allow for the residual term
        residual = np.abs(A.T @ y - c).max()
        assert residual <= 1e-2 * (1 + np.abs(c).max()), "y = 1/(t s) must be (nearly) dual feasible: A^T y = c"
        slack = np.abs(x).sum() * residual
        assert abs((b @ y - c @ x) - m / t) <= 1e-6 * m / t + 2 * slack + 1e-9, \
            "duality gap on the central path is m/t"


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("n", [2, 3, 5])
def test_step4_step_contains_the_half_and_shrinks(n):
    rng = np.random.default_rng(n)
    center = rng.normal(size=n)
    M = rng.normal(size=(n, n))
    P = M @ M.T + n * np.eye(n)
    a = rng.normal(size=n)
    c2, P2 = lab.ellipsoid_step(center, P, a)
    L = np.linalg.cholesky(P)
    Pinv2 = np.linalg.inv(P2)
    for _ in range(400):                          # random points of the old ellipsoid's kept half
        u = rng.normal(size=n)
        u *= rng.uniform() ** (1 / n) / np.linalg.norm(u)
        z = center + L @ u
        if a @ z <= a @ center:
            assert (z - c2) @ Pinv2 @ (z - c2) <= 1 + 1e-9
    ratio = math.sqrt(np.linalg.det(P2) / np.linalg.det(P))
    assert ratio < math.exp(-1 / (2 * (n + 1)))


@pytest.mark.parametrize("seed", range(10))
def test_step4_finds_a_point_away_from_the_origin(seed):
    A, b, p = shifted_polytope(4, 10, seed=seed)
    with time_limit(20):
        x, k = lab.ellipsoid_feasible(A, b, R=100, max_iter=2000)
    assert x is not None and np.all(A @ x <= b + 1e-9)
    assert k > 0, "the origin is outside; at least one step is needed"


def test_step4_gives_up_on_an_empty_system():
    x, k = lab.ellipsoid_feasible([[1.0, 0.0], [-1.0, 0.0]], [0.0, -1e-3], R=10, max_iter=300)
    assert x is None and k == 300


# ---------------------------------------------------------------- step 5 ---

def test_step5_bound_formula():
    assert lab.iteration_bound(2, 10, 1) == math.ceil(2 * 3 * 2 * math.log(10))
    assert lab.iteration_bound(4, 100, 1) == 185
    assert lab.iteration_bound(4, 100, 0.1) > lab.iteration_bound(4, 100, 1)


@pytest.mark.parametrize("seed", range(10))
def test_step5_the_method_stays_within_its_bound(seed):
    A, b, p = shifted_polytope(4, 10, seed=seed)
    r = inscribed_radius(A, b, p)
    bound = lab.iteration_bound(4, 100, r)
    x, k = lab.ellipsoid_feasible(A, b, R=100, max_iter=bound)
    assert x is not None and k <= bound
