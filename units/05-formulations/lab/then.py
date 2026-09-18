"""Unit 05 — "Then": the same facility-location problem, formulated three ways, through two solvers.

  1. Root LP bound and integrality gap of each formulation.
  2. SCIP with presolve and cutting planes switched off: pure branch-and-bound,
     where the formulation is all the solver has.
  3. HiGHS and SCIP with default settings: how much of a weak formulation
     modern presolve and cuts repair on their own.

    uv run co then 05
"""

from colib.mip import FacilityLocation, highs_mip, lp_relaxation, scip_mip
from colib.testing import load_lab

lab = load_lab(__file__)
BARE = {"presolving/maxrounds": 0, "separating/maxrounds": 0, "separating/maxroundsroot": 0}
SIZES = [(12, 40), (20, 60)]


def models(F, C):
    ufl = FacilityLocation.random(F, C, 1)
    cap = FacilityLocation.random(F, C, 1, capacity_ratio=1.5)
    return [
        ("UFL aggregated, M = 10C", lab.ufl_aggregated(ufl, 10 * C)),
        ("UFL aggregated, M = C", lab.ufl_aggregated(ufl, C)),
        ("UFL disaggregated", lab.ufl_disaggregated(ufl)),
        ("CFL capacity constraints only", lab.cfl(cap, False)),
        ("CFL + linking + cover", lab.cfl(cap, True)),
    ]


def main():
    for F, C in SIZES:
        rows = models(F, C)
        print(f"\n=== {F} facilities, {C} customers ===")
        print("\n1 · Root LP bound")
        opt = {}
        for name, m in rows:
            opt[name] = scip_mip(m, time_limit=120).value
        print(f"   {'formulation':<30}{'LP bound':>10}{'optimum':>10}{'gap':>8}")
        lps = {}
        for name, m in rows:
            lp = lp_relaxation(m).value
            lps[name] = lp
            print(f"   {name:<30}{lp:>10.1f}{opt[name]:>10.1f}{100 * (opt[name] - lp) / opt[name]:>7.1f}%")
        w, s = lps["UFL aggregated, M = C"], lps["UFL disaggregated"]
        print(f"   disaggregation closes {100 * lab.gap_closed(w, s, opt['UFL disaggregated']):.0f}% "
              f"of the M = C model's gap")

        print("\n2 · SCIP, presolve and cuts off (pure branch-and-bound)")
        print(f"   {'formulation':<30}{'nodes':>8}{'seconds':>9}")
        for name, m in rows:
            r = scip_mip(m, time_limit=120, settings=BARE)
            print(f"   {name:<30}{r.nodes:>8}{r.seconds:>9.2f}", flush=True)

        print("\n3 · Default settings")
        print(f"   {'formulation':<30}{'HiGHS nodes':>12}{'s':>7}{'SCIP nodes':>12}{'s':>7}")
        for name, m in rows:
            h, sc = highs_mip(m, time_limit=120), scip_mip(m, time_limit=120)
            print(f"   {name:<30}{h.nodes:>12}{h.seconds:>7.2f}{sc.nodes:>12}{sc.seconds:>7.2f}", flush=True)
    print("\nPresolve and cuts recover much of what a weak formulation loses, which is why a")
    print("bad model can look fine on a default solver. Part 2 shows what it costs when they can't.")


if __name__ == "__main__":
    main()
