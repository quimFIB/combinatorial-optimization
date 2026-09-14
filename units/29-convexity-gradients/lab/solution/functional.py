"""Unit 29 lab — convexity, gradients, and what continuity changes.  REFERENCE SOLUTION, functional.

Iterative methods are unfolds over states: gradient descent's state is x, heavy ball's and Nesterov's are
(x, previous x, k), Frank-Wolfe's is (x, k). tz.iterate produces the states and take keeps the first
iterations + 1. Projection and the KKT residuals are single numpy expressions.
"""

from __future__ import annotations

import numpy as np
import toolz as tz

from colib.ref import unit


def _unfold(step, state, iterations, view=lambda s: s):
    return [view(s) for s in tz.take(iterations + 1, tz.iterate(step, state))]


# ---------------------------------------------------------------- step 1 ---

def quadratic(Q, b):
    Q, b = np.asarray(Q, float), np.asarray(b, float)
    return (lambda x: 0.5 * x @ Q @ x - b @ x), (lambda x: Q @ x - b)


def rosenbrock():
    f = lambda z: (1 - z[0]) ** 2 + 100 * (z[1] - z[0] ** 2) ** 2
    grad = lambda z: np.array([-2 * (1 - z[0]) - 400 * z[0] * (z[1] - z[0] ** 2), 200 * (z[1] - z[0] ** 2)])
    return f, grad


def gradient_check(f, grad, x, h=1e-6):
    x = np.asarray(x, float)
    E = np.eye(len(x)) * h
    numeric = np.array([(f(x + e) - f(x - e)) / (2 * h) for e in E])
    return float(np.max(np.abs(grad(x) - numeric)))


# ---------------------------------------------------------------- step 2 ---

def gradient_descent(grad, x0, step, iterations):
    return _unfold(lambda x: x - step * grad(x), np.asarray(x0, float), iterations)


def heavy_ball(grad, x0, step, beta, iterations):
    x0 = np.asarray(x0, float)
    move = lambda s: (s[0] - step * grad(s[0]) + beta * (s[0] - s[1]), s[0])
    return _unfold(move, (x0, x0), iterations, view=lambda s: s[0])


def nesterov(grad, x0, step, iterations):
    x0 = np.asarray(x0, float)

    def move(s):
        x, prev, k = s
        y = x + (k - 1) / (k + 2) * (x - prev)
        return y - step * grad(y), x, k + 1

    return _unfold(move, (x0, x0, 0), iterations, view=lambda s: s[0])


# ---------------------------------------------------------------- step 3 ---

def project_simplex(v):
    v = np.asarray(v, float)
    u = np.sort(v)[::-1]
    ks = np.arange(1, len(u) + 1)
    thresholds = (np.cumsum(u) - 1) / ks
    rho = int(ks[u - thresholds > 0].max())
    return np.maximum(v - thresholds[rho - 1], 0.0)


def projected_gradient(grad, project, x0, step, iterations):
    return _unfold(lambda x: project(x - step * grad(x)), project(np.asarray(x0, float)), iterations)


# ---------------------------------------------------------------- step 4 ---

def simplex_lmo(A, b):
    solver = unit("02").simplex
    A = [list(map(float, row)) for row in A]
    b = list(map(float, b))

    def lmo(g):
        res = solver(A, b, [-float(v) for v in g], eps=1e-12)
        assert res.status == "optimal", res.status
        return np.array(res.x, float)

    return lmo


def frank_wolfe(grad, lmo, x0, iterations):
    def move(state):
        x, k, _ = state
        g = grad(x)
        s = lmo(g)
        return x + 2 / (k + 2) * (s - x), k + 1, float(g @ (x - s))

    states = _unfold(move, (np.asarray(x0, float), 0, None), iterations)
    return [s[0] for s in states], [s[2] for s in states[1:]]


# ---------------------------------------------------------------- step 5 ---

def lp_kkt_residuals(A, b, c, x, y):
    A, b, c, x, y = (np.asarray(v, float) for v in (A, b, c, x, y))
    row_slack, reduced = b - A @ x, A.T @ y - c
    worst_negative = lambda *arrays: float(max([0.0] + [-a.min(initial=0.0) for a in arrays]))
    return {"primal": worst_negative(row_slack, x), "dual": worst_negative(reduced, y),
            "slack_rows": float(np.abs(y * row_slack).max(initial=0.0)),
            "slack_columns": float(np.abs(x * reduced).max(initial=0.0))}


def qp_kkt_residuals(Q, q, A, b, x, lam):
    Q, q, A, b, x, lam = (np.asarray(v, float) for v in (Q, q, A, b, x, lam))
    slack = b - A @ x
    return {"stationarity": float(np.abs(Q @ x + q + A.T @ lam).max(initial=0.0)),
            "primal": float(max(0.0, -slack.min(initial=0.0))),
            "dual": float(max(0.0, -lam.min(initial=0.0))),
            "slack": float(np.abs(lam * slack).max(initial=0.0))}
