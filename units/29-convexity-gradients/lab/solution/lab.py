"""Unit 29 lab — convexity, gradients, and what continuity changes.  REFERENCE SOLUTION, imperative.

Vectors are numpy arrays. A method takes a gradient function and returns its whole trajectory (a list of
iterates, starting with x0), so convergence can be plotted and tested after the fact.
"""

from __future__ import annotations

import numpy as np

from colib.ref import unit


# ---------------------------------------------------------------- step 1 ---

def quadratic(Q, b):
    """f(x) = 1/2 x^T Q x - b^T x for symmetric Q. Returns (f, grad)."""
    Q, b = np.asarray(Q, float), np.asarray(b, float)
    return (lambda x: 0.5 * x @ Q @ x - b @ x), (lambda x: Q @ x - b)


def rosenbrock():
    """f(x, y) = (1 - x)^2 + 100 (y - x^2)^2. Returns (f, grad)."""
    def f(z):
        x, y = z
        return (1 - x) ** 2 + 100 * (y - x * x) ** 2

    def grad(z):
        x, y = z
        return np.array([-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)])

    return f, grad


def gradient_check(f, grad, x, h=1e-6):
    """The largest absolute difference between grad(x) and central differences (f(x + h e_i) - f(x - h e_i)) / 2h."""
    x = np.asarray(x, float)
    g = grad(x)
    worst = 0.0
    for i in range(len(x)):
        e = np.zeros_like(x)
        e[i] = h
        worst = max(worst, abs(g[i] - (f(x + e) - f(x - e)) / (2 * h)))
    return worst


# ---------------------------------------------------------------- step 2 ---

def gradient_descent(grad, x0, step, iterations):
    """x_{k+1} = x_k - step * grad(x_k)."""
    xs = [np.asarray(x0, float)]
    for _ in range(iterations):
        xs.append(xs[-1] - step * grad(xs[-1]))
    return xs


def heavy_ball(grad, x0, step, beta, iterations):
    """Polyak: x_{k+1} = x_k - step * grad(x_k) + beta (x_k - x_{k-1}), with x_{-1} = x0."""
    xs = [np.asarray(x0, float)]
    prev = xs[0]
    for _ in range(iterations):
        x = xs[-1]
        xs.append(x - step * grad(x) + beta * (x - prev))
        prev = x
    return xs


def nesterov(grad, x0, step, iterations):
    """Nesterov's accelerated gradient for smooth convex f: y_k = x_k + (k - 1) / (k + 2) (x_k - x_{k-1}),
    x_{k+1} = y_k - step * grad(y_k), for k = 0, 1, ..., with x_{-1} = x0."""
    xs = [np.asarray(x0, float)]
    prev = xs[0]
    for k in range(iterations):
        x = xs[-1]
        y = x + (k - 1) / (k + 2) * (x - prev)
        xs.append(y - step * grad(y))
        prev = x
    return xs


# ---------------------------------------------------------------- step 3 ---

def project_simplex(v):
    """Euclidean projection onto {x >= 0, sum x = 1} (Held, Wolfe and Crowder; Duchi et al. 2008): sort v
    descending as u, find the largest rho with u_rho - (sum_{i<=rho} u_i - 1) / rho > 0, theta = (sum_{i<=rho} u_i
    - 1) / rho, and return max(v - theta, 0)."""
    v = np.asarray(v, float)
    u = np.sort(v)[::-1]
    cumulative = np.cumsum(u)
    rho = max(k for k in range(1, len(u) + 1) if u[k - 1] - (cumulative[k - 1] - 1) / k > 0)
    theta = (cumulative[rho - 1] - 1) / rho
    return np.maximum(v - theta, 0.0)


def projected_gradient(grad, project, x0, step, iterations):
    """x_{k+1} = project(x_k - step * grad(x_k)), starting from project(x0)."""
    xs = [project(np.asarray(x0, float))]
    for _ in range(iterations):
        xs.append(project(xs[-1] - step * grad(xs[-1])))
    return xs


# ---------------------------------------------------------------- step 4 ---

def simplex_lmo(A, b):
    """A linear minimisation oracle over the polytope {x >= 0, A x <= b} (b >= 0, bounded): a function g -> a
    vertex s minimising g . s, computed by unit 02's simplex method (maximise -g . x) with eps = 1e-12."""
    solver = unit("02").simplex
    A = [list(map(float, row)) for row in A]
    b = list(map(float, b))

    def lmo(g):
        res = solver(A, b, [-float(v) for v in g], eps=1e-12)
        assert res.status == "optimal", res.status
        return np.array(res.x, float)

    return lmo


def frank_wolfe(grad, lmo, x0, iterations):
    """Conditional gradient: s_k = lmo(grad(x_k)), gap_k = grad(x_k) . (x_k - s_k), x_{k+1} = x_k + 2/(k+2) (s_k - x_k).
    x0 must be feasible. Returns (trajectory, gaps) with len(gaps) == iterations."""
    xs, gaps = [np.asarray(x0, float)], []
    for k in range(iterations):
        x = xs[-1]
        g = grad(x)
        s = lmo(g)
        gaps.append(float(g @ (x - s)))
        xs.append(x + 2 / (k + 2) * (s - x))
    return xs, gaps


# ---------------------------------------------------------------- step 5 ---

def lp_kkt_residuals(A, b, c, x, y):
    """KKT conditions of max c.x, A x <= b, x >= 0, with multipliers y >= 0 for the constraints A x <= b (and the implied
    multipliers A^T y - c for x >= 0). Returns a dict of nonnegative residuals, each 0 exactly when that
    condition holds: "primal" (largest violation of A x <= b or x >= 0), "dual" (largest violation of
    A^T y >= c or y >= 0), "slack_rows" (complementarity for the constraints: largest |y_i (b - A x)_i|), "slack_columns"
    (complementarity for the variables: largest |x_j (A^T y - c)_j|)."""
    A, b, c, x, y = (np.asarray(v, float) for v in (A, b, c, x, y))
    row_slack = b - A @ x
    reduced = A.T @ y - c
    return {
        "primal": float(max(0.0, -row_slack.min(initial=0.0), -x.min(initial=0.0))),
        "dual": float(max(0.0, -reduced.min(initial=0.0), -y.min(initial=0.0))),
        "slack_rows": float(np.abs(y * row_slack).max(initial=0.0)),
        "slack_columns": float(np.abs(x * reduced).max(initial=0.0)),
    }


def qp_kkt_residuals(Q, q, A, b, x, lam):
    """KKT of min 1/2 x^T Q x + q.x subject to A x <= b (no sign constraints on x), multipliers lam >= 0.
    Returns {"stationarity": max |Q x + q + A^T lam|, "primal": max violation of A x <= b,
    "dual": max violation of lam >= 0, "slack": max |lam_i (b - A x)_i|}."""
    Q, q, A, b, x, lam = (np.asarray(v, float) for v in (Q, q, A, b, x, lam))
    slack = b - A @ x
    return {
        "stationarity": float(np.abs(Q @ x + q + A.T @ lam).max(initial=0.0)),
        "primal": float(max(0.0, -slack.min(initial=0.0))),
        "dual": float(max(0.0, -lam.min(initial=0.0))),
        "slack": float(np.abs(lam * slack).max(initial=0.0)),
    }
