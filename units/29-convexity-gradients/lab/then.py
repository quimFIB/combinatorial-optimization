"""Unit 29 — "Then": your first-order methods against scipy.optimize and CVXPY.

  1. Quadratics with condition number 100 and 10 000: iterations to 1e-8 suboptimality for gradient descent,
     heavy ball, Nesterov, scipy's CG and L-BFGS-B, and the rates theory predicts. Plot: out/convergence.png.
  2. Rosenbrock: fixed-step methods against BFGS.
  3. Least squares on the probability simplex (n = 200): projected gradient, Frank-Wolfe with the simplex's
     vertex oracle, and CVXPY, by accuracy and seconds.
  4. Frank-Wolfe over a random polytope with your unit-02 simplex as the oracle, against HiGHS as the oracle.
  5. KKT at an LP optimum: the residuals of HiGHS's primal-dual pair, and unit 03's certificate on the same pair.

    uv run co then 29
"""

import math
import time
from pathlib import Path

import cvxpy as cp
import numpy as np
from scipy.optimize import minimize

from colib.ref import unit
from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def conditioned(n, kappa, seed):
    rng = np.random.default_rng(seed)
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    Q = U @ np.diag(np.geomspace(1, kappa, n)) @ U.T
    return (Q + Q.T) / 2, rng.standard_normal(n)


def first_below(values, tol):
    return next((k for k, v in enumerate(values) if v <= tol), None)


def quadratics():
    print("1. Quadratics, n = 100: iterations until f - f* <= 1e-8 (relative to f(x0) - f*)\n")
    curves = {}
    print(f"  {'kappa':>7} {'GD':>7} {'heavy ball':>11} {'Nesterov':>9} {'CG':>5} {'L-BFGS-B':>9}   predicted GD / HB / Nesterov bound")
    for kappa in (100.0, 10_000.0):
        Q, b = conditioned(100, kappa, 1)
        f, g = lab.quadratic(Q, b)
        xs = np.linalg.solve(Q, b)
        fs = f(xs)
        x0 = np.zeros(100)
        scale = f(x0) - fs
        L, mu = kappa, 1.0
        iters = 20000
        gd = [(f(x) - fs) / scale for x in lab.gradient_descent(g, x0, 1 / L, iters)]
        hb = [(f(x) - fs) / scale for x in lab.heavy_ball(g, x0, 4 / (math.sqrt(L) + math.sqrt(mu)) ** 2,
                                                          ((math.sqrt(kappa) - 1) / (math.sqrt(kappa) + 1)) ** 2, iters)]
        ag = [(f(x) - fs) / scale for x in lab.nesterov(g, x0, 1 / L, iters)]
        curves[kappa] = (gd, hb, ag)
        cg = minimize(f, x0, jac=g, method="CG", options={"gtol": 1e-10, "maxiter": 100000})
        lb = minimize(f, x0, jac=g, method="L-BFGS-B", options={"ftol": 1e-16, "gtol": 1e-10, "maxiter": 100000})
        # predicted: GD (1 - 1/kappa)^(2k); heavy ball ((sqrt k - 1)/(sqrt k + 1))^(2k); Nesterov's convex bound 2 L R^2/(k+1)^2
        pred_gd = math.ceil(math.log(1e-8) / (2 * math.log(1 - 1 / kappa)))
        pred_hb = math.ceil(math.log(1e-8) / (2 * math.log((math.sqrt(kappa) - 1) / (math.sqrt(kappa) + 1))))
        R2 = float(xs @ xs)
        pred_ag = math.ceil(math.sqrt(2 * L * R2 / (1e-8 * scale)))
        fmt = lambda k: f"{k:>7}" if k is not None else f"{'>' + str(iters):>7}"
        print(f"  {kappa:>7.0f} {fmt(first_below(gd, 1e-8))} {fmt(first_below(hb, 1e-8)):>11} {fmt(first_below(ag, 1e-8)):>9}"
              f" {cg.nit:>5} {lb.nit:>9}   {pred_gd} / {pred_hb} / {pred_ag}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        OUT.mkdir(exist_ok=True)
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, (kappa, (gd, hb, ag)) in zip(axes, curves.items()):
            for name, curve in (("gradient descent", gd), ("heavy ball", hb), ("Nesterov", ag)):
                ax.semilogy(np.maximum(curve, 1e-17)[:5000], label=name)
            ax.set_title(f"condition number {kappa:.0f}")
            ax.set_xlabel("iteration")
            ax.set_ylabel("relative suboptimality")
            ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "convergence.png", dpi=130)
        print(f"\n  plot: {OUT / 'convergence.png'}")
    except ImportError:
        pass


def rosenbrock():
    print("\n2. Rosenbrock from (-1.2, 1): iterations to within 1e-6 of (1, 1)\n")
    f, g = lab.rosenbrock()
    x0 = np.array([-1.2, 1.0])
    for name, traj in (("GD, step 1e-3", lab.gradient_descent(g, x0, 1e-3, 100_000)),
                       ("Nesterov, step 1e-3", lab.nesterov(g, x0, 1e-3, 100_000))):
        k = next((k for k, x in enumerate(traj) if np.linalg.norm(x - 1) < 1e-6), None)
        print(f"  {name:>22}: {k if k is not None else '> 100000'}   (final distance {np.linalg.norm(traj[-1] - 1):.1e})")
    res = minimize(f, x0, jac=g, method="BFGS", options={"gtol": 1e-10})
    print(f"  {'scipy BFGS':>22}: {res.nit}   (final distance {np.linalg.norm(res.x - 1):.1e})")


def simplex_least_squares():
    print("\n3. min ||M x - y||^2 over the probability simplex, n = 200\n")
    rng = np.random.default_rng(3)
    M = rng.standard_normal((150, 200))
    target = rng.dirichlet(np.ones(200) * 0.1)
    y = M @ target + 0.01 * rng.standard_normal(150)
    Q, q = M.T @ M, M.T @ y
    f = lambda x: 0.5 * x @ Q @ x - q @ x
    g = lambda x: Q @ x - q
    L = float(np.linalg.eigvalsh(Q).max())
    x = cp.Variable(200)
    t = time.perf_counter()
    prob = cp.Problem(cp.Minimize(0.5 * cp.sum_squares(M @ x - y)), [x >= 0, cp.sum(x) == 1])
    prob.solve(solver="CLARABEL")
    t_cvx = time.perf_counter() - t
    fs = f(x.value)
    x0 = np.ones(200) / 200
    vertex = lambda grad: np.eye(200)[int(np.argmin(grad))]
    print(f"  {'method':>22} {'iterations':>11} {'f - f*':>10} {'seconds':>8}")
    for name, run in (("projected gradient", lambda k: lab.projected_gradient(g, lab.project_simplex, x0, 1 / L, k)),
                      ("Frank-Wolfe", lambda k: lab.frank_wolfe(g, vertex, x0, k)[0])):
        for k in (100, 1000, 5000):
            t = time.perf_counter()
            traj = run(k)
            dt = time.perf_counter() - t
            print(f"  {name:>22} {k:>11} {f(traj[-1]) - fs:>10.2e} {dt:>8.2f}")
    print(f"  {'CVXPY (CLARABEL)':>22} {'-':>11} {0.0:>10.2e} {t_cvx:>8.2f}")
    fw = lab.frank_wolfe(g, vertex, x0, 1000)[0][-1]
    pg = lab.projected_gradient(g, lab.project_simplex, x0, 1 / L, 1000)[-1]
    print(f"  nonzeros after 1000 iterations: Frank-Wolfe {int((fw > 1e-9).sum())}, projected gradient"
          f" {int((pg > 1e-9).sum())}, CVXPY {int((x.value > 1e-6).sum())}")


def polytope():
    print("\n4. Frank-Wolfe over {x >= 0, A x <= b}, n = 30, m = 20, with unit 02's simplex as the oracle\n")
    rng = np.random.default_rng(4)
    A = rng.uniform(0, 1, (20, 30))
    b = rng.uniform(5, 10, 20)
    center = rng.uniform(0, 2, 30)
    f = lambda x: 0.5 * float((x - center) @ (x - center))
    g = lambda x: x - center
    x = cp.Variable(30)
    prob = cp.Problem(cp.Minimize(0.5 * cp.sum_squares(x - center)), [x >= 0, A @ x <= b])
    prob.solve(solver="CLARABEL")
    fs = prob.value
    lmo_simplex = lab.simplex_lmo(A.tolist(), b.tolist())
    lmo_highs = lambda grad: np.array(highs_lp(A, b, -grad, sense="max").x)
    for name, lmo in (("your simplex (unit 02)", lmo_simplex), ("HiGHS", lmo_highs)):
        t = time.perf_counter()
        traj, gaps = lab.frank_wolfe(g, lmo, np.zeros(30), 200)
        dt = time.perf_counter() - t
        print(f"  {name:>24}: 200 iterations, f - f* = {f(traj[-1]) - fs:.2e}, last gap {gaps[-1]:.2e},"
              f" {dt:.2f} s ({1000 * dt / 200:.1f} ms per oracle call)")


def kkt():
    print("\n5. KKT at an LP optimum (max c.x, A x <= b, x >= 0; m = 30, n = 50)\n")
    rng = np.random.default_rng(5)
    A = rng.uniform(0, 5, (30, 50))
    b = rng.uniform(20, 60, 30)
    c = rng.uniform(1, 10, 50)
    res = highs_lp(A, b, c, sense="max")
    y = np.abs(res.row_duals)
    r = lab.lp_kkt_residuals(A, b, c, res.x, y)
    print("  residuals: " + ", ".join(f"{k} {v:.1e}" for k, v in r.items()))
    print(f"  duality gap c.x - b.y = {c @ res.x - b @ y:.1e}")
    ok, why = unit("03").certify_optimal(A.tolist(), b.tolist(), c.tolist(), [round(v, 9) for v in res.x], [round(v, 9) for v in y])
    print(f"  unit 03's exact certificate on the rounded pair: {ok} ({why})")


if __name__ == "__main__":
    quadratics()
    rosenbrock()
    simplex_least_squares()
    polytope()
    kkt()
