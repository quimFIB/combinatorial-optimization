"""Unit 04 lab — interior point and ellipsoid.  REFERENCE SOLUTION, functional.

numpy expressions are already pure. Each iterative method is an unfold over an
immutable state, read until a stopping condition, so none of them recurses.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import takewhile

import numpy as np
import toolz as tz


# ---------------------------------------------------------------- step 1 ---

def barrier(A, b, c, x, t):
    A, b, c, x = map(np.asarray, (A, b, c, x))
    s = b - A @ x
    if np.any(s <= 0):
        return math.inf, None, None
    return (-t * c @ x - np.sum(np.log(s)),
            -t * c + A.T @ (1.0 / s),
            A.T @ ((1.0 / s**2)[:, None] * A))


# ---------------------------------------------------------------- step 2 ---

@dataclass(frozen=True)
class Newton:
    x: np.ndarray
    k: int
    done: bool = False


def newton_center(A, b, c, x0, t, tol=1e-9, max_iter=100):
    def backtrack(x, dx, f, dec2):
        """Largest step 1, 1/2, 1/4, ... with sufficient decrease; None if none is representable."""
        steps = takewhile(lambda st: st > 1e-12, tz.iterate(lambda st: st / 2, 1.0))
        return next((st for st in steps
                     if barrier(A, b, c, x + st * dx, t)[0] <= f - 0.25 * st * dec2), None)

    def step(s: Newton) -> Newton:
        f, g, H = barrier(A, b, c, s.x, t)
        try:
            dx = -np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            return Newton(s.x, s.k, done=True)
        dec2 = -g @ dx
        st = None if dec2 / 2 <= tol else backtrack(s.x, dx, f, dec2)
        return Newton(s.x, s.k, done=True) if st is None else Newton(s.x + st * dx, s.k + 1)

    start = Newton(np.asarray(x0, dtype=float), 0)
    final = next(s for s in tz.iterate(step, start) if s.done or s.k >= max_iter)
    return final.x, final.k


# ---------------------------------------------------------------- step 3 ---

def central_path(A, b, c, x0, t0=1.0, mu=10.0, eps=1e-5):
    A, b = np.asarray(A, float), np.asarray(b, float)
    m = len(b)

    def point(t, x):
        xc, _ = newton_center(A, b, c, x, t)
        return t, xc, 1.0 / (t * (b - A @ xc))

    # The t sequence is known in advance: count the points needed, then take them.
    ts = tz.iterate(lambda t: t * mu, t0)
    count = next(k for k, t in enumerate(ts) if m / t <= eps) + 1
    path = tz.iterate(lambda p: point(p[0] * mu, p[1]), point(t0, np.asarray(x0, float)))
    return list(tz.take(count, path))


# ---------------------------------------------------------------- step 4 ---

def ellipsoid_step(center, P, a):
    n = len(center)
    g = (P @ a) / math.sqrt(a @ P @ a)
    return center - g / (n + 1), (n * n / (n * n - 1.0)) * (P - (2.0 / (n + 1)) * np.outer(g, g))


def ellipsoid_feasible(A, b, R, max_iter):
    A, b = np.asarray(A, float), np.asarray(b, float)
    n = A.shape[1]

    def step(state):
        k, center, P = state
        i = int(np.argmax(A @ center - b))
        return (k + 1, *ellipsoid_step(center, P, A[i]))

    feasible = lambda state: bool(np.all(A @ state[1] <= b))
    states = tz.iterate(step, (0, np.zeros(n), (R * R) * np.eye(n)))
    found = next(s for s in states if feasible(s) or s[0] >= max_iter)
    return (found[1], found[0]) if feasible(found) else (None, found[0])


# ---------------------------------------------------------------- step 5 ---

def iteration_bound(n, R, r):
    return math.ceil(2 * (n + 1) * n * math.log(R / r))
