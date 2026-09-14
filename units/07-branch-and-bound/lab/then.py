"""Unit 07 — "Then": your branch-and-bound against HiGHS and SCIP.

  1. The matrix {most-fractional, pseudocost, strong} x {depth-first, best-first}
     on multi-dimensional knapsacks and on unit 05's weak facility-location model:
     nodes, LP solves, seconds.
  2. The same instances through SCIP with presolve and cuts off (a plain
     branch-and-bound with a far better LP and branching), SCIP default, and
     HiGHS default. Your factor of shame is the node ratio.

    uv run co then 07
"""

import time

from colib import ref
from colib.bb import multi_knapsack
from colib.mip import FacilityLocation, highs_mip, scip_mip
from colib.testing import load_lab

lab = load_lab(__file__)
formulations = ref.unit("05")
BARE = {"presolving/maxrounds": 0, "separating/maxrounds": 0, "separating/maxroundsroot": 0}
LIMIT = 20_000


def instances():
    yield "knapsack 22x3 #0", multi_knapsack(22, 3, 0)
    yield "knapsack 22x3 #1", multi_knapsack(22, 3, 1)
    yield "UFL 8x20 aggregated M=10C", formulations.ufl_aggregated(FacilityLocation.random(8, 20, 3), 200)


def main():
    rules = [("most-fractional", lab.most_fractional), ("pseudocost", lab.pseudocost),
             ("strong", lab.strong_branching)]
    totals = {}
    for name, m in instances():
        opt = scip_mip(m).value
        print(f"\n=== {name}   (optimum {opt:.0f}) ===")
        print(f"   {'rule':<17}{'selection':<11}{'nodes':>8}{'LP solves':>11}{'seconds':>9}  result")
        mine_best = None
        for rname, rule in rules:
            for sel in ("dfs", "best"):
                t = time.perf_counter()
                r = lab.branch_and_bound(m, rule, sel, node_limit=LIMIT)
                dt = time.perf_counter() - t
                ok = "optimal" if r.status == "optimal" and abs(r.value - opt) < 1e-6 else r.status
                print(f"   {rname:<17}{sel:<11}{r.nodes:>8}{r.lp_solves:>11}{dt:>9.2f}  {ok}", flush=True)
                a = totals.setdefault((rname, sel), [0, 0, 0.0])
                a[0] += r.nodes
                a[1] += r.lp_solves
                a[2] += dt
                if r.status == "optimal":
                    mine_best = r.nodes if mine_best is None else min(mine_best, r.nodes)
        bare, sd, hd = scip_mip(m, settings=BARE), scip_mip(m), highs_mip(m)
        print(f"   {'SCIP, presolve+cuts off':<28}{bare.nodes:>8}{'':>11}{bare.seconds:>9.2f}")
        print(f"   {'SCIP default':<28}{sd.nodes:>8}{'':>11}{sd.seconds:>9.2f}")
        print(f"   {'HiGHS default':<28}{hd.nodes:>8}{'':>11}{hd.seconds:>9.2f}")
        if mine_best:
            print(f"   factor of shame (your best node count / SCIP default): {mine_best / max(sd.nodes, 1):.0f}x;"
                  f"  vs SCIP bare: {mine_best / max(bare.nodes, 1):.1f}x")
    print("\n=== totals over the three instances ===")
    for (rname, sel), (nodes, lps, secs) in totals.items():
        print(f"   {rname:<17}{sel:<11}{nodes:>8}{lps:>11}{secs:>9.2f}")


if __name__ == "__main__":
    main()
