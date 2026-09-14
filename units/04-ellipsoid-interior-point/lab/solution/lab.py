"""Unit 04 lab — polynomial-time LP: interior point and ellipsoid.  REFERENCE SOLUTION, imperative.

LPs are  max c.x  s.t.  A x <= b  (no sign constraints: put x >= 0 into A if
you want it). Floats and numpy throughout: these methods are about limits, not
exact vertices.
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- step 1 ---

def barrier(A, b, c, x, t):
    """f_t(x) = -t c.x - sum log(b - A x), its gradient and Hessian.
    Returns (inf, None, None) when x is not strictly feasible."""
    A, b, c, x = map(np.asarray, (A, b, c, x))
    s = b - A @ x
    if np.any(s <= 0):
        return math.inf, None, None
    f = -t * c @ x - np.sum(np.log(s))
    g = -t * c + A.T @ (1.0 / s)
    H = A.T @ ((1.0 / s**2)[:, None] * A)
    return f, g, H


# ---------------------------------------------------------------- step 2 ---

def newton_center(A, b, c, x0, t, tol=1e-9, max_iter=100):
    """Minimize f_t from a strictly feasible x0 by damped Newton with backtracking.
    Returns (x, newton_steps)."""
    x = np.asarray(x0, dtype=float)
    for k in range(max_iter):
        f, g, H = barrier(A, b, c, x, t)
        try:
            dx = -np.linalg.solve(H, g)
        except np.linalg.LinAlgError:              # Hessian numerically singular: as centred as floats allow
            return x, k
        decrement2 = -g @ dx
        if decrement2 / 2 <= tol:
            return x, k
        step = 1.0
        while step > 1e-12:
            fn, _, _ = barrier(A, b, c, x + step * dx, t)
            if fn <= f - 0.25 * step * decrement2:
                break
            step *= 0.5
        else:                                      # no decrease representable in floating point
            return x, k
        x = x + step * dx
    return x, max_iter


# ---------------------------------------------------------------- step 3 ---

def central_path(A, b, c, x0, t0=1.0, mu=10.0, eps=1e-5):
    """Barrier path-following. Returns a list of (t, x, y) with y = 1 / (t s)
    the dual point on the central path; stops once m / t <= eps."""
    A, b = np.asarray(A, float), np.asarray(b, float)
    m = len(b)
    t, x = t0, np.asarray(x0, float)
    path = []
    while True:
        x, _ = newton_center(A, b, c, x, t)
        y = 1.0 / (t * (b - A @ x))
        path.append((t, x, y))
        if m / t <= eps:
            return path
        t *= mu


# ---------------------------------------------------------------- step 4 ---

def ellipsoid_step(center, P, a):
    """Shrink the ellipsoid {z : (z-center)^T P^-1 (z-center) <= 1} to the
    smallest ellipsoid containing its half {z : a.z <= a.center}."""
    n = len(center)
    Pa = P @ a
    g = Pa / math.sqrt(a @ Pa)
    new_center = center - g / (n + 1)
    new_P = (n * n / (n * n - 1.0)) * (P - (2.0 / (n + 1)) * np.outer(g, g))
    return new_center, new_P


def ellipsoid_feasible(A, b, R, max_iter):
    """Look for x with A x <= b inside the ball of radius R around 0.
    Returns (x, iterations) or (None, iterations) if max_iter runs out."""
    A, b = np.asarray(A, float), np.asarray(b, float)
    n = A.shape[1]
    center, P = np.zeros(n), (R * R) * np.eye(n)
    for k in range(max_iter):
        viol = A @ center - b
        i = int(np.argmax(viol))
        if viol[i] <= 0:
            return center, k
        center, P = ellipsoid_step(center, P, A[i])
    return None, max_iter


# ---------------------------------------------------------------- step 5 ---

def iteration_bound(n, R, r):
    """Iterations after which the ellipsoid method may stop, if the feasible set,
    when nonempty, contains a ball of radius r and lies inside the ball of radius R:
    the volume shrinks by at least exp(-1/(2(n+1))) per step, so after
    2(n+1) n ln(R/r) steps no such ball can fit."""
    return math.ceil(2 * (n + 1) * n * math.log(R / r))
