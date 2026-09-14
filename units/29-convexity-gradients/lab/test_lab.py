"""Tests for unit 29. Run with `uv run co test 29`. You should not need to edit this."""

import math

import cvxpy as cp
import numpy as np
import pytest

from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)


def random_quadratic(seed, n=12, low=1.0, high=100.0, psd=False):
    rng = np.random.default_rng(seed)
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    eig = np.linspace(low, high, n)
    if psd:
        eig[: n // 3] = 0.0
    Q = U @ np.diag(eig) @ U.T
    b = Q @ rng.standard_normal(n) if psd else rng.standard_normal(n)      # b in the range of Q keeps f bounded
    return (Q + Q.T) / 2, b, max(eig)


def fstar(Q, b):
    x = np.linalg.lstsq(Q, b, rcond=None)[0]
    return 0.5 * x @ Q @ x - b @ x, x


# ---------------------------------------------------------------- step 1 ---

def test_step1_quadratic():
    Q = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([1.0, -1.0])
    f, g = lab.quadratic(Q, b)
    x = np.array([0.5, -2.0])
    assert f(x) == pytest.approx(0.5 * x @ Q @ x - b @ x)
    assert np.allclose(g(x), Q @ x - b)


def test_step1_rosenbrock():
    f, g = lab.rosenbrock()
    assert f(np.array([1.0, 1.0])) == 0 and np.allclose(g(np.array([1.0, 1.0])), 0)
    assert f(np.array([0.0, 0.0])) == 1
    assert np.allclose(g(np.array([-1.2, 1.0])), [-215.6, -88.0])


@pytest.mark.parametrize("seed", range(5))
def test_step1_gradient_check(seed):
    rng = np.random.default_rng(seed)
    f, g = lab.rosenbrock()
    x = rng.uniform(-2, 2, 2)
    assert lab.gradient_check(f, g, x) < 1e-4
    wrong = lambda z: g(z) * np.array([1.0, 1.01])
    assert lab.gradient_check(f, wrong, x) > 1e-4 or abs(g(x)[1]) < 1e-2
    Q, b, _ = random_quadratic(seed)
    fq, gq = lab.quadratic(Q, b)
    assert lab.gradient_check(fq, gq, rng.standard_normal(12)) < 1e-5
    assert lab.gradient_check(fq, lambda z: Q.T @ z, rng.standard_normal(12)) > 0.01


def test_step1_gradient_check_uses_central_differences():
    f = lambda x: x[0] ** 3
    g = lambda x: np.array([3 * x[0] ** 2])
    # a forward difference with h = 1e-3 at x = 1 is off by about 3e-3; a central one by 1e-6
    assert lab.gradient_check(f, g, np.array([1.0]), h=1e-3) < 1e-5


# ---------------------------------------------------------------- step 2 ---

def test_step2_hand_traces():
    g = lambda x: x                      # f = x^2 / 2
    x0 = np.array([1.0])
    assert [float(v[0]) for v in lab.gradient_descent(g, x0, 0.5, 3)] == [1.0, 0.5, 0.25, 0.125]
    assert [float(v[0]) for v in lab.heavy_ball(g, x0, 0.5, 0.5, 3)] == [1.0, 0.5, 0.0, -0.25]
    assert [float(v[0]) for v in lab.nesterov(g, x0, 0.5, 3)] == pytest.approx([1.0, 0.5, 0.25, 0.09375])


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("psd", [False, True])
def test_step2_gd_and_nesterov_rates(seed, psd):
    Q, b, L = random_quadratic(seed, psd=psd)
    f, g = lab.quadratic(Q, b)
    fs, xs = fstar(Q, b)
    x0 = np.zeros(len(b))
    R2 = float((x0 - xs) @ (x0 - xs))
    gd = lab.gradient_descent(g, x0, 1 / L, 200)
    ag = lab.nesterov(g, x0, 1 / L, 200)
    assert len(gd) == len(ag) == 201
    for k in range(1, 201):
        assert f(gd[k]) - fs <= L * R2 / (2 * k) + 1e-9
        assert f(ag[k]) - fs <= 2 * L * R2 / (k + 1) ** 2 + 1e-9
    if not psd:     # condition number 100: acceleration shows by iteration 30 (the PSD case is well conditioned on its range)
        assert f(ag[30]) - fs < f(gd[30]) - fs


@pytest.mark.parametrize("seed", range(4))
def test_step2_heavy_ball_rate(seed):
    Q, b, L = random_quadratic(seed, low=1.0, high=100.0)
    f, g = lab.quadratic(Q, b)
    _, xs = fstar(Q, b)
    mu, kappa = 1.0, 100.0
    step, beta = 4 / (math.sqrt(L) + math.sqrt(mu)) ** 2, ((math.sqrt(kappa) - 1) / (math.sqrt(kappa) + 1)) ** 2
    hb = lab.heavy_ball(g, np.zeros(len(b)), step, beta, 150)
    gd = lab.gradient_descent(g, np.zeros(len(b)), 1 / L, 150)
    e0 = np.linalg.norm(xs)
    assert np.linalg.norm(hb[-1] - xs) < 1e-8 * e0
    assert np.linalg.norm(gd[-1] - xs) > 1e-2 * e0, "plain gradient descent is still far away"


# ---------------------------------------------------------------- step 3 ---

def test_step3_projection_by_hand():
    assert np.allclose(lab.project_simplex([0.5, 1.2, -0.3]), [0.15, 0.85, 0.0])
    assert np.allclose(lab.project_simplex([0.2, 0.3, 0.5]), [0.2, 0.3, 0.5])
    assert np.allclose(lab.project_simplex([5.0, 5.0]), [0.5, 0.5])
    assert np.allclose(lab.project_simplex([-3.0, -1.0, -2.0]), [0.0, 1.0, 0.0])


@pytest.mark.parametrize("seed", range(20))
def test_step3_projection_is_the_nearest_point(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(2, 15))
    v = rng.normal(0, 2, n)
    p = lab.project_simplex(v)
    assert p.min() >= 0 and p.sum() == pytest.approx(1)
    for j in range(n):                    # (v - p) . (e_j - p) <= 0 for every vertex: optimality over the simplex
        e = np.zeros(n)
        e[j] = 1
        assert (v - p) @ (e - p) <= 1e-9
    assert np.allclose(lab.project_simplex(p), p)


@pytest.mark.parametrize("seed", range(4))
def test_step3_projected_gradient(seed):
    Q, b, L = random_quadratic(seed, n=8, low=0.5, high=20)
    f, g = lab.quadratic(Q, b)
    x = cp.Variable(8)
    cp.Problem(cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) - b @ x), [x >= 0, cp.sum(x) == 1]).solve()
    traj = lab.projected_gradient(g, lab.project_simplex, np.ones(8) * 3, 1 / L, 2000)
    assert traj[0].sum() == pytest.approx(1), "starts from the projection of x0"
    assert f(traj[-1]) == pytest.approx(f(x.value), abs=1e-5)


# ---------------------------------------------------------------- step 4 ---

POLY_A = [[1, 2, 1], [3, 1, 2], [1, 1, 4]]
POLY_B = [4, 6, 5]


@pytest.mark.parametrize("seed", range(10))
def test_step4_lmo(seed):
    rng = np.random.default_rng(seed)
    g = rng.standard_normal(3)
    s = lab.simplex_lmo(POLY_A, POLY_B)(g)
    assert s.min() >= -1e-9 and np.all(np.array(POLY_A) @ s <= np.array(POLY_B) + 1e-9)
    ref = highs_lp(POLY_A, POLY_B, -g, sense="max")
    assert g @ s == pytest.approx(-ref.value, abs=1e-9)


def box_diameter_squared():
    total = 0.0
    for j in range(3):
        c = [0.0] * 3
        c[j] = 1.0
        total += highs_lp(POLY_A, POLY_B, c, sense="max").value ** 2
    return total


@pytest.mark.parametrize("seed", range(4))
def test_step4_frank_wolfe(seed):
    rng = np.random.default_rng(seed)
    Q, _, L = random_quadratic(seed, n=3, low=1, high=10)
    b = rng.normal(0, 8, 3)
    f, g = lab.quadratic(Q, b)
    x = cp.Variable(3)
    prob = cp.Problem(cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) - b @ x), [x >= 0, np.array(POLY_A) @ x <= POLY_B])
    prob.solve()
    fs = prob.value
    traj, gaps = lab.frank_wolfe(g, lab.simplex_lmo(POLY_A, POLY_B), np.zeros(3), 300)
    assert len(traj) == 301 and len(gaps) == 300
    D2 = box_diameter_squared()
    for k, (xk, gap) in enumerate(zip(traj, gaps)):
        assert xk.min() >= -1e-9 and np.all(np.array(POLY_A) @ xk <= np.array(POLY_B) + 1e-9)
        assert gap >= f(xk) - fs - 1e-6, "the Frank-Wolfe gap bounds the suboptimality"
        if k >= 1:
            assert f(xk) - fs <= 2 * L * D2 / (k + 2) + 1e-6
    assert f(traj[-1]) - fs < 0.05 * (f(traj[0]) - fs + 1e-9) + 1e-3


def test_step4_frank_wolfe_step_sizes():
    lmo = lambda g: np.array([1.0, 0.0]) if g[0] < g[1] else np.array([0.0, 1.0])
    g = lambda x: np.array([0.0, 1.0])                   # the oracle always returns (1, 0)
    traj, gaps = lab.frank_wolfe(g, lmo, np.array([0.0, 1.0]), 3)
    assert np.allclose(traj[1], [1.0, 0.0]), "step 2/(0+2) = 1"
    assert np.allclose(traj[2], [1.0, 0.0])
    assert gaps[0] == pytest.approx(1.0) and gaps[1] == pytest.approx(0.0)


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(8))
def test_step5_lp_kkt_at_the_optimum(seed):
    rng = np.random.default_rng(seed)
    m, n = 4, 6
    A = rng.uniform(0, 5, (m, n))
    b = rng.uniform(5, 20, m)
    c = rng.uniform(1, 10, n)
    res = highs_lp(A, b, c, sense="max")
    y = np.abs(res.row_duals)
    r = lab.lp_kkt_residuals(A, b, c, res.x, y)
    assert set(r) == {"primal", "dual", "slack_rows", "slack_columns"}
    assert max(r.values()) < 1e-7
    moved = lab.lp_kkt_residuals(A, b, c, res.x * 0.5, y)
    assert moved["slack_rows"] > 1e-6 and moved["primal"] == 0, "feasible but not complementary"
    assert lab.lp_kkt_residuals(A, b, c, res.x, y * 0.5)["dual"] > 1e-6


def test_step5_lp_kkt_by_hand():
    A, b, c = [[1, 1]], [2], [1, 2]
    r = lab.lp_kkt_residuals(A, b, c, [0, 2], [2])
    assert r == {"primal": 0.0, "dual": 0.0, "slack_rows": 0.0, "slack_columns": 0.0}
    r = lab.lp_kkt_residuals(A, b, c, [1, 1], [2])
    assert r["slack_columns"] == pytest.approx(1.0) and r["primal"] == 0.0
    r = lab.lp_kkt_residuals(A, b, c, [3, 0], [-1])
    assert r["primal"] == pytest.approx(1.0) and r["dual"] == pytest.approx(3.0)
    assert lab.lp_kkt_residuals(A, b, c, [-1, 0], [2])["primal"] == pytest.approx(1.0), "x >= 0 is part of primal"
    assert lab.lp_kkt_residuals(A, b, [-5, -5], [0, 0], [-1])["dual"] == pytest.approx(1.0), "y >= 0 is part of dual"


def test_step5_qp_kkt_by_hand():
    r = lab.qp_kkt_residuals([[1.0]], [0.0], [[1.0]], [1.0], [0.0], [2.0])
    assert r == {"stationarity": 2.0, "primal": 0.0, "dual": 0.0, "slack": 2.0}
    r = lab.qp_kkt_residuals([[1.0]], [0.0], [[1.0]], [1.0], [2.0], [-2.0])
    assert r == {"stationarity": 0.0, "primal": 1.0, "dual": 2.0, "slack": 2.0}


@pytest.mark.parametrize("seed", range(5))
def test_step5_qp_kkt(seed):
    rng = np.random.default_rng(seed)
    Q, _, _ = random_quadratic(seed, n=5, low=1, high=10)
    q = rng.standard_normal(5) * 5
    A = rng.standard_normal((3, 5))
    b = rng.uniform(0, 1, 3)
    x = cp.Variable(5)
    cons = [A @ x <= b]
    cp.Problem(cp.Minimize(0.5 * cp.quad_form(x, cp.psd_wrap(Q)) + q @ x), cons).solve(solver="CLARABEL")
    r = lab.qp_kkt_residuals(Q, q, A, b, x.value, cons[0].dual_value)
    assert set(r) == {"stationarity", "primal", "dual", "slack"}
    assert max(r.values()) < 1e-6
    lam = cons[0].dual_value
    assert lab.qp_kkt_residuals(Q, q, A, b, x.value, -lam)["dual"] == pytest.approx(max(0.0, lam.max()), abs=1e-9)
    assert lab.qp_kkt_residuals(Q, q, A, b, x.value + 1, cons[0].dual_value)["stationarity"] > 1e-3
