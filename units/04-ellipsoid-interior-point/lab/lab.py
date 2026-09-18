"""Unit 04 lab — polynomial-time LP: interior point and ellipsoid.

    uv run co test 04

LPs here are  max c.x  s.t.  A x <= b,  with no separate sign constraints (put
x >= 0 into A if you want it). Use numpy arrays and floats: these methods
approach the optimum, they don't land on a vertex.

Any style passes; the tests only check results. The iterative methods loop
tens to hundreds of times, so write the loop as a loop or as an iterator (see
FUNCTIONAL.md), not as recursion.
"""

from __future__ import annotations

import math

import numpy as np


# ---------------------------------------------------------------- step 1 ---

def barrier(A, b, c, x, t):
    """The barrier objective for a max LP, and its derivatives:

        f_t(x) = -t c.x - sum_i log(b_i - a_i.x)

    Return (f, gradient, Hessian) as (float, array n, array n x n).
    If x is not strictly feasible (some b_i - a_i.x <= 0) return (math.inf, None, None).
    """
    raise NotImplementedError("step 1: barrier")


# ---------------------------------------------------------------- step 2 ---

def newton_center(A, b, c, x0, t, tol=1e-9, max_iter=100):
    """Minimize f_t starting from the strictly feasible x0, by Newton's method
    with backtracking.

    Each step: dx = -H^-1 g; stop when the Newton decrement g.(H^-1 g) / 2 <= tol.
    Otherwise try step 1, 1/2, 1/4, ... until f_t(x + step dx) <= f - 0.25 step g.(H^-1 g)
    (infeasible points have f = inf, so backtracking also keeps you inside).
    Stop instead if the step falls below 1e-12 or H is singular: floating point
    has run out. Return (x, number_of_newton_steps_taken).
    """
    raise NotImplementedError("step 2: newton_center")


# ---------------------------------------------------------------- step 3 ---

def central_path(A, b, c, x0, t0=1.0, mu=10.0, eps=1e-5):
    """Barrier path-following.

    For t = t0, t0*mu, t0*mu^2, ...: centre with newton_center, starting from the
    previous centre, and record (t, x, y), where y = 1 / (t * (b - A x)) is the
    dual point that comes free with the centre. Stop after recording the first
    point with m / t <= eps (m = number of constraints). Return the list of (t, x, y).
    """
    raise NotImplementedError("step 3: central_path")


# ---------------------------------------------------------------- step 4 ---

def ellipsoid_step(center, P, a):
    """One ellipsoid update. The ellipsoid is {z : (z - center)^T P^-1 (z - center) <= 1}.
    Return (new_center, new_P) for the smallest ellipsoid containing its half
    {z : a.z <= a.center}:

        g = P a / sqrt(a^T P a)
        new_center = center - g / (n + 1)
        new_P = n^2 / (n^2 - 1) * (P - 2 / (n + 1) * g g^T)
    """
    raise NotImplementedError("step 4: ellipsoid_step")


def ellipsoid_feasible(A, b, R, max_iter):
    """Search for x with A x <= b, assuming any solution lies within distance R
    of the origin. Start with the ball of radius R (center 0, P = R^2 I). While
    the centre violates some constraint, cut with the most violated one. Return
    (center, iterations) once the centre is feasible, or (None, max_iter).
    """
    raise NotImplementedError("step 4: ellipsoid_feasible")


# ---------------------------------------------------------------- step 5 ---

def iteration_bound(n, R, r):
    """How many ellipsoid steps suffice in dimension n, if the feasible set lies
    inside the ball of radius R and, when nonempty, contains a ball of radius r.
    Use the volume argument from the slides and return an int (round up)."""
    raise NotImplementedError("step 5: iteration_bound")
