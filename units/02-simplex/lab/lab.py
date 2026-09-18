"""Unit 02 lab — simplex, honestly.

    uv run co test 02

LPs here are  maximize c.x  subject to  A x <= b,  x >= 0.  Tests pass
Fractions, so arithmetic is exact and `eps` stays 0; `then` also runs your code
on floats with eps > 0 to see where the numerics fail.

Tableau layout (m constraints, n variables):

    rows 0..m-1   [ A | I | b ]        one row per constraint; I = slack columns
    row  m        [ -c | 0 | z ]       reduced costs, and the objective value z

Columns 0..n-1 are the original variables, n..n+m-1 the slacks, and the last
column is the right-hand side. `basis[i]` is the column basic in row i.

Any style passes; the tests only check results. A tableau may be a list of
lists you update in place or a tuple of tuples you rebuild; see FUNCTIONAL.md.

From colib.lp: LPResult(status, x, value, basis, pivots, tableau) and the
Cycling exception.
"""

from __future__ import annotations

from colib.lp import Cycling, LPResult


# ---------------------------------------------------------------- step 1 ---

def initial_tableau(A, b, c):
    """Return (T, basis) for the layout above, with the slacks as the starting basis."""
    raise NotImplementedError("step 1: initial_tableau")


def pivot(T, basis, row, col):
    """Pivot on T[row][col]: scale that row so the entry is 1, then eliminate
    column `col` from every other row, objective row included. Record that
    `col` is now basic in `row`.

    Return (T, basis). Updating in place and returning the same objects is
    fine, and so is returning new ones.
    """
    raise NotImplementedError("step 1: pivot")


# ---------------------------------------------------------------- step 2 ---

def entering(T, rule="bland", eps=0):
    """The entering column, or None if no reduced cost is below -eps (optimal).

    rule="dantzig": the most negative reduced cost; on ties, the lowest column.
    rule="bland":   the lowest column with a negative reduced cost.
    """
    raise NotImplementedError("step 2: entering")


def leaving(T, basis, col, rule="bland", eps=0):
    """The pivot row for entering column `col`, or None if the LP is unbounded
    along it (no entry above eps in that column).

    Minimum ratio T[i][-1] / T[i][col] over rows with T[i][col] > eps.
    Ties (within eps): rule="dantzig" takes the lowest row; rule="bland" takes
    the row whose basic variable has the smallest column index.
    """
    raise NotImplementedError("step 2: leaving")


# ---------------------------------------------------------------- step 3 ---

def simplex(A, b, c, rule="bland", eps=0):
    """The simplex method from the slack basis. Requires b >= 0 (raise
    ValueError otherwise).

    Return LPResult with status "optimal" (and x, value, basis, pivots) or
    "unbounded". Keep the set of bases visited: if a pivot produces a basis
    seen before, raise Cycling.
    """
    raise NotImplementedError("step 3: simplex")


# ---------------------------------------------------------------- step 4 ---

def two_phase(A, b, c, rule="bland", eps=0):
    """The two-phase method for any b.

    Phase 1: negate each constraint with b_i < 0 and give it an artificial variable.
    Maximize -(sum of artificials) from the basis of slacks and artificials.
    If that optimum is below -eps, return status "infeasible". Otherwise pivot
    any artificial still basic (at value 0) out of the basis; if its row has no
    nonzero entry among the real columns, the row is redundant, so delete it.

    Phase 2: drop the artificial columns, restore the real objective, make it
    consistent with the current basis, and continue with simplex pivots.
    `pivots` in the result counts both phases.
    """
    raise NotImplementedError("step 4: two_phase")


# ---------------------------------------------------------------- step 5 ---

def klee_minty(n):
    """Klee–Minty cube, Chvátal's form: return (A, b, c) for

        max  sum_j 10^(n-j) x_j
        s.t. 2 sum_{j<i} 10^(i-j) x_j + x_i <= 100^(i-1)    for i = 1..n
             x >= 0

    (indices 1-based as written; your lists are 0-based).
    """
    raise NotImplementedError("step 5: klee_minty")
