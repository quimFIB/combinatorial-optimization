"""Unit 01 lab — polyhedra, Fourier–Motzkin, and Farkas.

A system is a list of constraints, each a row `(a, b)` meaning  a . x <= b,
with `a` a tuple of ints. Everything is exact: no floats, no tolerances.

    uv run co test 01

Any style passes; the tests only check results. This lab is unusually
fold-shaped: eliminating every variable is reducing `eliminate` over
range(n). FUNCTIONAL.md at the project root has the Haskell-to-Python names;
toolz is installed.

Helpers you may use (from colib.polyhedra — they are not the lesson):
    dot(a, x)             inner product
    satisfies(system, x)  does x satisfy every constraint?
    normalize(row)        divide a constraint by the gcd of its entries
    solve_exact(A, b)     exact solution of a square system, or None if singular
"""

from __future__ import annotations

import itertools

from colib.polyhedra import dot, normalize, satisfies, solve_exact


# ---------------------------------------------------------------- step 1 ---

def eliminate(system, k):
    """Fourier–Motzkin: eliminate variable x_k from the system.

    Return a new list of constraints whose k-th coefficient is 0 (keep the column; do
    not shorten the tuples), such that a point y satisfies the new system
    exactly when some value of x_k makes y a solution of the old one.

    Constraints with a[k] == 0 pass through. Each constraint with a[k] > 0 is
    combined with each constraint with a[k] < 0, using positive multipliers
    that cancel x_k.

    Tidy-up is up to you but worth it: drop constraints that read 0 <= (something
    nonnegative), and remove duplicates after `normalize`. Keep a constraint 0 <= -3:
    that is how infeasibility shows itself.
    """
    raise NotImplementedError("step 1: eliminate")


# ---------------------------------------------------------------- step 2 ---

def fm_feasible(system) -> bool:
    """Decide whether the system has a real solution, by eliminating every
    variable in turn and inspecting what is left."""
    raise NotImplementedError("step 2: fm_feasible")


# ---------------------------------------------------------------- step 3 ---

def vertices(system):
    """All vertices of a bounded polyhedron in R^n, by basis enumeration.

    A vertex is a feasible point where some n linearly independent
    constraints are tight. Try every n-subset of constraints, solve it as
    equalities, keep the feasible solutions. Return a sorted list of tuples,
    each vertex once (a degenerate vertex is tight on more than n constraints
    and will be found many times).
    """
    raise NotImplementedError("step 3: vertices")


# ---------------------------------------------------------------- step 4 ---

def is_farkas_certificate(system, y) -> bool:
    """True iff y proves the system has no solution:
    one multiplier per constraint, all y_i >= 0, sum_i y_i a_i == 0 (the zero
    vector), and sum_i y_i b_i < 0. y may contain ints or Fractions."""
    raise NotImplementedError("step 4: is_farkas_certificate")


# ---------------------------------------------------------------- step 5 ---

def farkas_certificate(system):
    """Return a Farkas certificate (a tuple of nonnegative ints, one per
    constraint) if the system is infeasible, or None if it is feasible.

    No LP solver. Your step-1 `eliminate` already builds every derived
    constraint as a nonnegative combination of the original constraints; the
    task is to keep track of *which* combination. HINTS.org rung 2 has a way to
    do that without changing `eliminate` at all.
    """
    raise NotImplementedError("step 5: farkas_certificate")
