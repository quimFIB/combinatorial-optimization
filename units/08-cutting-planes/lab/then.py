"""Unit 08 — "Then": what cuts are worth, yours and SCIP's.

  1. Gomory's loop on small integer programs: rounds to reach the integer
     optimum, the ones that stall, and how the cut coefficients grow.
  2. Your lifted cover cuts at the root of multi-dimensional knapsacks: gap closed.
  3. SCIP on the same knapsacks with presolve off, cuts off vs on: root bound,
     gap closed at the root, and nodes.

    uv run co then 08
"""

import itertools
import random

from colib.bb import multi_knapsack
from colib.mip import lp_relaxation, scip_mip
from colib.testing import load_lab

lab = load_lab(__file__)


def small_ip(seed, n=3, m=3):
    r = random.Random(seed)
    A = [[r.randint(1, 9) for _ in range(n)] for _ in range(m)]
    return A, [r.randint(10, 40) for _ in range(m)], [r.randint(1, 9) for _ in range(n)]


def ip_opt(A, b, c):
    U = max(b)
    return max(sum(ci * v for ci, v in zip(c, x)) for x in itertools.product(range(U + 1), repeat=len(c))
               if all(sum(a * v for a, v in zip(row, x)) <= bb for row, bb in zip(A, b)))


def part1():
    print("\n1 · Gomory fractional cuts, 20 random 3-variable integer programs, up to 80 rounds")
    print(f"   {'seed':>4}{'LP bound':>10}{'IP opt':>8}{'final':>9}{'cuts':>6}{'max |coef| digits':>19}")
    reached = 0
    for seed in range(20):
        A, b, c = small_ip(seed)
        opt = ip_opt(A, b, c)
        bounds, cuts, _ = lab.gomory_loop(A, b, c, rounds=80)
        digits = max((len(str(abs(v))) for a, beta in cuts for v in list(a) + [beta]), default=0)
        ok = bounds[-1] == opt
        reached += ok
        if cuts:
            print(f"   {seed:>4}{float(bounds[0]):>10.2f}{opt:>8}{float(bounds[-1]):>9.2f}{len(cuts):>6}{digits:>19}"
                  f"{'' if ok else '   <- stalled'}")
    print(f"   reached the integer optimum on {reached}/20 (the rest needed no cut or stalled)")
    print("   Pure Gomory converges in theory (lexicographic rules) but stalls in practice: each cut")
    print("   moves the bound less, and coefficients grow. Solvers use a few rounds of Gomory MIR cuts only.")


def part2_and_3():
    bare = {"presolving/maxrounds": 0, "separating/maxrounds": 0, "separating/maxroundsroot": 0}
    cuts_on = {"presolving/maxrounds": 0}
    print("\n2 · Root gap closed on multi-dimensional knapsacks (20 items, 2 constraints)")
    print(f"   {'seed':>4}{'LP':>10}{'opt':>8}{'yours: bound':>14}{'closed':>8}{'cuts':>6}"
          f"{'SCIP root, cuts':>17}{'closed':>8}")
    rows = []
    for seed in range(6):
        m = multi_knapsack(20, 2, seed, tightness=0.4)
        lp = lp_relaxation(m).value
        opt = scip_mip(m).value
        bounds, sizes, added = lab.root_cut_loop(m, rounds=30)
        sc = scip_mip(m, settings=cuts_on)
        gap = opt - lp
        mine = (bounds[-1] - lp) / gap if gap > 1e-9 else 1.0
        theirs = (sc.root_bound - lp) / gap if gap > 1e-9 and sc.root_bound is not None and sc.root_bound < 1e19 else float("nan")
        rows.append((seed, m, mine, theirs))
        root = (f"{sc.root_bound:>17.2f}{100 * theirs:>7.0f}%" if theirs == theirs
                else f"{'(not reported)':>17}{'':>8}")
        print(f"   {seed:>4}{lp:>10.2f}{opt:>8.0f}{bounds[-1]:>14.2f}{100 * mine:>7.0f}%{added:>6}{root}")
    print("\n3 · SCIP nodes with presolve off: cuts off vs cuts on")
    print(f"   {'seed':>4}{'cuts off':>10}{'cuts on':>10}")
    for seed, m, _, _ in rows:
        off, on = scip_mip(m, settings=bare), scip_mip(m, settings=cuts_on)
        print(f"   {seed:>4}{off.nodes:>10}{on.nodes:>10}")
    print("   SCIP separates many families at the root (knapsack covers among them), with its own lifting.")


if __name__ == "__main__":
    part1()
    part2_and_3()
