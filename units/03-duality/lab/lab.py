"""Unit 03 lab — duality.

    uv run co test 03

Step 1 works on general-form LPs (colib.lp.GeneralLP). Steps 2–5 work on the
optimal tableaux that unit 02's simplex returns: LPs  max c.x, A x <= b, x >= 0
with n variables and m constraints, tableau layout

    rows 0..m-1   [ A | I | b ]   (in the final basis)
    row  m        [ -c | 0 | z ]

`simplex` below is unit 02's reference solution (two_phase, pivot, ...). Set
CO_MINE=02 to use your own instead. Tests pass Fractions: keep arithmetic exact.

Any style passes; the tests only check results. See FUNCTIONAL.md.
"""

from __future__ import annotations

from colib import ref
from colib.lp import GeneralLP, LPResult

simplex = ref.unit("02")


# ---------------------------------------------------------------- step 1 ---

def dual(lp: GeneralLP) -> GeneralLP:
    """The dual of a general-form LP, as a GeneralLP.

    sense flips (max <-> min); c and b swap; A is transposed (a tuple of
    tuples: row j of the dual is column j of the primal). Constraint senses and
    variable signs follow the table on the slides. Return tuples everywhere, so that
    dual(dual(lp)) == lp exactly.
    """
    raise NotImplementedError("step 1: dual")


# ---------------------------------------------------------------- step 2 ---

def duals_from_tableau(res: LPResult, n: int, m: int):
    """The optimal dual solution y (length m) read off res.tableau.
    Raise ValueError if res.status is not "optimal"."""
    raise NotImplementedError("step 2: duals_from_tableau")


# ---------------------------------------------------------------- step 3 ---

def certify_optimal(A, b, c, x, y) -> tuple[bool, str]:
    """Decide, without solving anything, whether x is optimal for
    max c.x, A x <= b, x >= 0, using y as the certificate.

    Return (True, <anything>) if x is primal feasible, y is dual feasible, and
    complementary slackness holds. Otherwise return (False, reason), where the
    reason names the first condition that fails. Arithmetic is exact: compare
    with ==, not a tolerance.
    """
    raise NotImplementedError("step 3: certify_optimal")


# ---------------------------------------------------------------- step 4 ---

def add_constraint(res: LPResult, a, beta):
    """Add the constraint  a.x <= beta  to an optimal tableau.

    Return (T, basis): a new tableau with one more column (the new slack,
    inserted just before the rhs) and one more row (inserted just before the
    objective row), written in terms of the current basis. That means its
    entries in the basic columns must be zero. The new slack is basic in the new
    row. The row's rhs may be negative: that is what the dual simplex fixes.
    """
    raise NotImplementedError("step 4: add_constraint")


def dual_simplex(T, basis, n, eps=0):
    """The dual simplex method from a dual feasible tableau (no negative entries
    in the objective row), possibly with negative right-hand sides.

    Leaving row: any row with rhs < -eps. The most negative one is the usual
    choice. Entering column: among columns with T[r][j] < -eps, the one
    minimizing T[-1][j] / -T[r][j]. If there is none, the LP is infeasible.

    Return LPResult: status "optimal" (with x of length n, value, basis, pivots,
    tableau) or "infeasible".
    """
    raise NotImplementedError("step 4: dual_simplex")


# ---------------------------------------------------------------- step 5 ---

def rhs_range(res: LPResult, n: int, i: int):
    """(lo, hi): how far b_i can move (b_i + delta, lo <= delta <= hi) before the
    optimal basis stops being feasible. Use None for an unbounded end.
    lo <= 0 <= hi always."""
    raise NotImplementedError("step 5: rhs_range")


def predict_objective(res: LPResult, n: int, m: int, i: int, delta):
    """The optimal value after b_i += delta, predicted from y_i without
    re-solving, or None when delta is outside rhs_range."""
    raise NotImplementedError("step 5: predict_objective")
