"""Unit 29 lab — convexity, gradients, and what continuity changes.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 29
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Vectors are numpy arrays. A method takes a gradient function and returns its whole trajectory (a list of
iterates, starting with x0), so convergence can be plotted and tested after the fact.
"""

from __future__ import annotations

import numpy as np

from colib.ref import unit


# ---------------------------------------------------------------- step 1 ---

def quadratic(Q, b):
    """f(x) = 1/2 x^T Q x - b^T x for symmetric Q. Returns (f, grad)."""
    raise NotImplementedError  # TODO step 1


def rosenbrock():
    """f(x, y) = (1 - x)^2 + 100 (y - x^2)^2. Returns (f, grad)."""
    raise NotImplementedError  # TODO step 1


def gradient_check(f, grad, x, h=1e-6):
    """The largest absolute difference between grad(x) and central differences (f(x + h e_i) - f(x - h e_i)) / 2h."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def gradient_descent(grad, x0, step, iterations):
    """x_{k+1} = x_k - step * grad(x_k)."""
    raise NotImplementedError  # TODO step 2


def heavy_ball(grad, x0, step, beta, iterations):
    """Polyak: x_{k+1} = x_k - step * grad(x_k) + beta (x_k - x_{k-1}), with x_{-1} = x0."""
    raise NotImplementedError  # TODO step 2


def nesterov(grad, x0, step, iterations):
    """Nesterov's accelerated gradient for smooth convex f: y_k = x_k + (k - 1) / (k + 2) (x_k - x_{k-1}),
    x_{k+1} = y_k - step * grad(y_k), for k = 0, 1, ..., with x_{-1} = x0."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def project_simplex(v):
    """Euclidean projection onto {x >= 0, sum x = 1} (Held, Wolfe and Crowder; Duchi et al. 2008): sort v
    descending as u, find the largest rho with u_rho - (sum_{i<=rho} u_i - 1) / rho > 0, theta = (sum_{i<=rho} u_i
    - 1) / rho, and return max(v - theta, 0)."""
    raise NotImplementedError  # TODO step 3


def projected_gradient(grad, project, x0, step, iterations):
    """x_{k+1} = project(x_k - step * grad(x_k)), starting from project(x0)."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def simplex_lmo(A, b):
    """A linear minimisation oracle over the polytope {x >= 0, A x <= b} (b >= 0, bounded): a function g -> a
    vertex s minimising g . s, computed by unit 02's simplex method (maximise -g . x) with eps = 1e-12."""
    raise NotImplementedError  # TODO step 4


def frank_wolfe(grad, lmo, x0, iterations):
    """Conditional gradient: s_k = lmo(grad(x_k)), gap_k = grad(x_k) . (x_k - s_k), x_{k+1} = x_k + 2/(k+2) (s_k - x_k).
    x0 must be feasible. Returns (trajectory, gaps) with len(gaps) == iterations."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def lp_kkt_residuals(A, b, c, x, y):
    """KKT conditions of max c.x, A x <= b, x >= 0, with multipliers y >= 0 for the constraints A x <= b (and the implied
    multipliers A^T y - c for x >= 0). Returns a dict of nonnegative residuals, each 0 exactly when that
    condition holds: "primal" (largest violation of A x <= b or x >= 0), "dual" (largest violation of
    A^T y >= c or y >= 0), "slack_rows" (complementarity for the constraints: largest |y_i (b - A x)_i|), "slack_columns"
    (complementarity for the variables: largest |x_j (A^T y - c)_j|)."""
    raise NotImplementedError  # TODO step 5


def qp_kkt_residuals(Q, q, A, b, x, lam):
    """KKT of min 1/2 x^T Q x + q.x subject to A x <= b (no sign constraints on x), multipliers lam >= 0.
    Returns {"stationarity": max |Q x + q + A^T lam|, "primal": max violation of A x <= b,
    "dual": max violation of lam >= 0, "slack": max |lam_i (b - A x)_i|}."""
    raise NotImplementedError  # TODO step 5
