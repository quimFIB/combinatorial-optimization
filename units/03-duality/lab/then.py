"""Unit 03 — "Then": your duals against HiGHS's, and what warm starts are worth.

  1. Sign conventions: the same LP's shadow prices as you compute them, as
     HiGHS reports them for max and for min, and as scipy reports them.
  2. Ranging: your rhs ranges against HiGHS's own ranging report, on the
     binding constraints of 50 random LPs.
  3. Warm start: add a cut to a solved LP; your dual simplex's pivots against a
     cold two-phase re-solve, and HiGHS warm against HiGHS cold.

    uv run co then 03
"""

import random
from fractions import Fraction as F

import numpy as np

from colib import ref
from colib.lp import fractions, random_lp
from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)
simplex = ref.unit("02")


def part1():
    import highspy  # noqa: F401  (highs_lp imports it; keep the import order explicit)
    from scipy.optimize import linprog
    print("\n1 · One LP, four sign conventions:  max 3x + 2y,  x + y <= 4,  2x + y <= 6")
    A, b, c = [[1, 1], [2, 1]], [4, 6], [3, 2]
    r = simplex.two_phase(*fractions(A, b, c))
    mine = lab.duals_from_tableau(r, 2, 2)
    hmax = highs_lp(A, b, c, sense="max").row_duals
    hmin = highs_lp(A, b, [-v for v in c], sense="min").row_duals
    sp = linprog([-v for v in c], A_ub=A, b_ub=b, method="highs").ineqlin.marginals
    print(f"   {'source':<42}{'u':>6}{'v':>6}")
    print(f"   {'yours (reduced costs of the slacks)':<42}{str(mine[0]):>6}{str(mine[1]):>6}")
    print(f"   {'HiGHS, sense=max':<42}{hmax[0]:>6.3g}{hmax[1]:>6.3g}")
    print(f"   {'HiGHS, same LP written as min -c.x':<42}{hmin[0]:>6.3g}{hmin[1]:>6.3g}")
    print(f"   {'scipy linprog (always min), ineqlin.marginals':<42}{sp[0]:>6.3g}{sp[1]:>6.3g}")
    print("   All four are the same fact: loosening a constraint by 1 raises the max by 1.")
    print("   A 'dual' is d(objective)/d(rhs) in the solver's own objective sense.")


def part2():
    print("\n2 · Ranging against HiGHS on 50 random LPs, binding constraints")
    rows = agree = loose = 0
    for seed in range(50):
        A, b, c = random_lp(4, 5, seed, kind="bounded")
        r = simplex.two_phase(*fractions(A, b, c))
        h = highs_lp(A, b, c, presolve=False)
        if r.status != "optimal" or h.status != "optimal":
            continue
        _, rg = h.extra["highs"].getRanging()
        for i in range(len(b)):
            if len(c) + i in r.basis:          # slack basic: the row is not binding
                loose += 1
                continue
            lo, hi = lab.rhs_range(r, len(c), i)
            mine = (float(b[i] + lo) if lo is not None else -np.inf,
                    float(b[i] + hi) if hi is not None else np.inf)
            dn, up = rg.row_bound_dn.value_[i], rg.row_bound_up.value_[i]
            theirs = (-np.inf if dn <= -1e30 else dn, np.inf if up >= 1e30 else up)
            rows += 1
            same = all((np.isinf(a) and np.isinf(t)) or abs(a - t) < 1e-6 for a, t in zip(mine, theirs))
            agree += same
            if not same and rows - agree <= 3:
                print(f"   seed {seed} constraint {i}: yours [{mine[0]:.4g}, {mine[1]:.4g}]"
                      f"  HiGHS [{theirs[0]:.4g}, {theirs[1]:.4g}]")
    print(f"   rhs ranges agree on {agree}/{rows} binding constraints")
    print(f"   ({loose} non-binding constraints skipped: their range is [activity, +inf) by the argument")
    print("    on the slides, and HiGHS's ranging report uses a different convention for them.)")


def part3():
    import highspy
    print("\n3 · Warm start after adding one cut, 200 LPs")
    warm = cold = hwarm = hcold = n = 0
    for seed in range(200):
        A, b, c = fractions(*random_lp(4, 5, seed, kind="bounded"))
        r = simplex.two_phase(A, b, c)
        if r.status != "optimal":
            continue
        rr = random.Random(seed)
        a = [F(rr.randint(-3, 6)) for _ in c]
        beta = F(int(sum(ai * xi for ai, xi in zip(a, r.x))) - rr.randint(0, 4))
        T, basis = lab.add_constraint(r, a, beta)
        w = lab.dual_simplex(T, basis, len(c))
        cs = simplex.two_phase(A + [a], b + [beta], c)
        if w.status != "optimal":
            continue
        n += 1
        warm += w.pivots
        cold += cs.pivots
        fA, fb, fc = [[float(v) for v in row] for row in A], [float(v) for v in b], [float(v) for v in c]
        h = highs_lp(fA, fb, fc, presolve=False)
        hh = h.extra["highs"]
        hh.addRow(-highspy.kHighsInf, float(beta), len(a), np.arange(len(a), dtype=np.int32),
                  np.array([float(v) for v in a]))
        hh.run()
        hwarm += hh.getInfo().simplex_iteration_count
        hcold += highs_lp(fA + [[float(v) for v in a]], fb + [float(beta)], fc, presolve=False).iterations
    print(f"   {n} LPs where the cut left a feasible LP")
    print(f"   yours:  dual simplex {warm / n:.2f} pivots per re-solve,  cold two-phase {cold / n:.2f}")
    print(f"   HiGHS:  warm {hwarm / n:.2f} iterations,  cold {hcold / n:.2f}")
    print("   Branch-and-bound re-solves one LP per node, each a small change from its parent.")


if __name__ == "__main__":
    part1()
    part2()
    part3()
