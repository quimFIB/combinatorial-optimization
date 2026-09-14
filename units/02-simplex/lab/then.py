"""Unit 02 — "Then": your simplex against HiGHS.

  1. Agreement on 1000 random LPs of every kind (optimal, infeasible,
     unbounded), and the time each takes.
  2. Klee–Minty: pivots under Dantzig's and Bland's rules against HiGHS's
     primal simplex (its own pricing, presolve off) as n grows.
  3. Numerics: your code on floats, and HiGHS, against exact Fractions on a
     Hilbert-matrix system whose only solution is x = 1.

    uv run co then 02
"""

import math
import time
from fractions import Fraction
from pathlib import Path

from colib.lp import Cycling, fractions, random_lp
from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def part1():
    print("\n1 · Agreement with HiGHS on 1000 random LPs (4 constraints, 5 variables)")
    agree = 0
    kinds = {}
    t_mine = t_highs = 0.0
    for seed in range(1000):
        A, b, c = random_lp(4, 5, seed)
        t = time.perf_counter()
        r = lab.two_phase(*fractions(A, b, c))
        t_mine += time.perf_counter() - t
        h = highs_lp(A, b, c)
        t_highs += h.seconds
        kinds[h.status] = kinds.get(h.status, 0) + 1
        same = r.status == h.status and (h.status != "optimal" or abs(float(r.value) - h.value) < 1e-7)
        agree += same
        if not same and agree + 5 > seed:
            print(f"   disagree on seed {seed}: yours {r.status} {r.value}, HiGHS {h.status} {h.value}")
    print(f"   agree on {agree}/1000   ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))})")
    print(f"   mean time per LP: yours {1e3 * t_mine / 1000:.2f} ms (exact Fractions), "
          f"HiGHS {1e3 * t_highs / 1000:.2f} ms")
    print("   note: HiGHS's presolve labels some unbounded LPs 'infeasible'; colib re-solves without it.")


def part2():
    print("\n2 · Klee–Minty: pivots as n grows")
    print(f"{'n':>4}{'Dantzig':>10}{'2^n - 1':>10}{'Bland':>10}{'HiGHS':>8}")
    rows = []
    for n in range(2, 13):
        A, b, c = lab.klee_minty(n)
        d = lab.simplex(*fractions(A, b, c), rule="dantzig").pivots
        bl = lab.simplex(*fractions(A, b, c), rule="bland").pivots
        h = highs_lp(A, b, c, method="primal", presolve=False).iterations
        rows.append((n, d, bl, h))
        print(f"{n:>4}{d:>10}{2 ** n - 1:>10}{bl:>10}{h:>8}")
    return rows


def hilbert_lp(n):
    """max sum x  s.t.  H x = H 1 (as two inequalities),  x >= 0, with H the n x n
    Hilbert matrix, H_ij = 1/(i+j+1). H is nonsingular, so x = 1 is the only
    feasible point and the optimum is exactly n. But H is famously ill-conditioned."""
    H = [[Fraction(1, i + j + 1) for j in range(n)] for i in range(n)]
    b = [sum(row) for row in H]
    return H + [[-v for v in r] for r in H], b + [-v for v in b], [Fraction(1)] * n


def part3():
    import numpy as np
    print("\n3 · Numerics: H x = H 1 has the single solution x = 1, objective n")
    print(f"{'n':>4}{'cond(H)':>10}{'exact x':>9}{'yours, floats: value, max|x-1|':>34}{'HiGHS: value, max|x-1|':>28}")
    rows = []
    for n in range(2, 12):
        A, b, c = hilbert_lp(n)
        exact = lab.two_phase(A, b, c)
        fA = [[float(v) for v in r] for r in A]
        fb = [float(v) for v in b]
        cond = np.linalg.cond(np.array(fA[:n]))
        try:
            fl = lab.two_phase(fA, fb, [1.0] * n, eps=1e-9)
            fl_err = max(abs(v - 1) for v in fl.x) if fl.status == "optimal" else math.inf
            fl_s = f"{fl.value:.6f}  {fl_err:8.1e}" if fl.status == "optimal" else fl.status
        except (Cycling, ZeroDivisionError, OverflowError) as e:
            fl_s, fl_err = type(e).__name__, math.inf
        h = highs_lp(fA, fb, [1.0] * n)
        h_err = max(abs(v - 1) for v in h.x) if h.status == "optimal" else math.inf
        h_s = f"{h.value:.6f}  {h_err:8.1e}" if h.status == "optimal" else h.status
        ok = exact.status == "optimal" and all(v == 1 for v in exact.x)
        rows.append((n, fl_err, h_err))
        print(f"{n:>4}{cond:>10.1e}{'= 1' if ok else '??':>9}{fl_s:>34}{h_s:>28}")
    print("   The objective stays close to n long after x is wrong: at this conditioning,")
    print("   points far from x = 1 satisfy H x = H 1 to within the solvers' tolerance.")
    return rows


def plot(km, num):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    OUT.mkdir(exist_ok=True)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    ns = [r[0] for r in km]
    a1.semilogy(ns, [r[1] for r in km], "o-", label="Dantzig")
    a1.semilogy(ns, [r[2] for r in km], "s-", label="Bland")
    a1.semilogy(ns, [max(r[3], 1) for r in km], "^--", label="HiGHS primal")
    a1.set_xlabel("n")
    a1.set_ylabel("pivots (log)")
    a1.set_title("Klee–Minty")
    a1.legend()
    ns = [r[0] for r in num]
    big = 1e3
    a2.semilogy(ns, [min(max(r[1], 1e-17), big) for r in num], "o-", label="yours, floats")
    a2.semilogy(ns, [min(max(r[2], 1e-17), big) for r in num], "s--", label="HiGHS")
    a2.set_xlabel("n")
    a2.set_ylabel("max |x − 1|  (log)")
    a2.set_title("Hilbert system: error in the solution")
    a2.legend()
    fig.tight_layout()
    fig.savefig(OUT / "then.png", dpi=130)
    print(f"\nplot: {(OUT / 'then.png').relative_to(Path.cwd())}")


if __name__ == "__main__":
    part1()
    km = part2()
    num = part3()
    plot(km, num)
