"""Unit 24 — "Then": the LP bound, the integer optimum and your rounded solution, on the same instances.

  1. Weighted vertex cover: LP (HiGHS), optimum (CP-SAT), threshold rounding, primal-dual.
  2. Set cover: LP, optimum, randomized rounding (failure rate against the union bound), primal-dual,
     and unit 23's greedy for comparison.
  3. The GF(2)^k gap family: LP below 2, optimum k.
  4. Facility location: Jain-Vazirani against the LP and the optimum.
  Plot: out/then.png, three numbers per instance.

    uv run co then 24
"""

import math
import random
import statistics
from pathlib import Path

from ortools.sat.python import cp_model

from colib.approx import FacilityLocation, covering_lp
from colib.mip import highs_mip, lp_relaxation
from colib.problems import SetCover, VertexCover
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
OUT = Path(__file__).parent / "out"


def cpsat_cover(nrows, cols_of_row, costs, limit=60):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in costs]
    for r in range(nrows):
        m.add_bool_or([x[j] for j in cols_of_row[r]])
    m.minimize(sum(c * xj for c, xj in zip(costs, x)))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = limit
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def weighted_graph(n, p, seed):
    r = random.Random(seed)
    edges = tuple((u, v) for u in range(n) for v in range(u + 1, n) if r.random() < p)
    return edges, [r.randint(1, 20) for _ in range(n)]


def vertex_cover(rows):
    print("1. Weighted vertex cover, weights 1..20: ratios to the optimum\n")
    print(f"  {'graph':>12} {'LP/OPT':>12} {'rounding/OPT':>14} {'primal-dual/OPT':>16} {'half-integral':>14}")
    for n, p in ((40, 0.15), (80, 0.08), (160, 0.04)):
        lp_r, rd_r, pd_r, halves = [], [], [], []
        for seed in range(8):
            edges, w = weighted_graph(n, p, seed)
            value, x = lab.vertex_cover_lp(n, edges, w)
            opt, proven = cpsat_cover(len(edges), [list(e) for e in edges], w)
            assert proven
            cover = lab.threshold_rounding(x, 0.5)
            sc = SetCover(len(edges), tuple(frozenset(k for k, e in enumerate(edges) if v in e) for v in range(n)), tuple(w))
            xp, _ = lab.primal_dual_set_cover(sc)
            lp_r.append(value / opt)
            rd_r.append(sum(wi for wi, c in zip(w, cover) if c) / opt)
            pd_r.append(sc.objective(xp) / opt)
            halves.append(all(min(abs(xv), abs(xv - 0.5), abs(xv - 1)) < 1e-7 for xv in x))
            rows.append(("vertex cover", value, opt, rd_r[-1] * opt))
        print(f"  {f'G({n}, {p})':>12} {statistics.mean(lp_r):>12.3f} {statistics.mean(rd_r):>14.3f} "
              f"{statistics.mean(pd_r):>16.3f} {sum(halves):>11}/{len(halves)}")


def random_set_cover(universe, nsets, seed):
    r = random.Random(seed)
    sets = [set(r.sample(range(universe), r.randint(3, universe // 5))) for _ in range(nsets)]
    for e in range(universe):
        if not any(e in s for s in sets):
            sets[r.randrange(nsets)].add(e)
    return SetCover(universe, tuple(frozenset(s) for s in sets), tuple(r.randint(1, 10) for _ in sets))


def set_cover(rows):
    print("\n2. Set cover, 150 elements and 100 sets: ratios to the optimum (10 instances)\n")
    greedy = unit("23").greedy_set_cover
    ratios = {"LP": [], "randomized, best of 20": [], "primal-dual": [], "greedy (unit 23)": []}
    rounds = math.ceil(math.log(150)) + 1
    fails = {t: [] for t in (1, 2, 4, rounds)}
    bounds = {t: lab.failure_bound(150, t) for t in fails}
    for seed in range(10):
        sc = random_set_cover(150, 100, seed)
        value, x = lab.set_cover_lp(sc)
        opt, proven = cpsat_cover(sc.universe, [[j for j, s in enumerate(sc.sets) if e in s] for e in range(sc.universe)], sc.costs)
        assert proven
        rng = random.Random(seed)
        for t in fails:
            draws = [lab.randomized_rounding(sc, x, t, rng) for _ in range(400)]
            fails[t].append(sum(not sc.is_feasible(d) for d in draws) / len(draws))
        covers = [d for d in (lab.randomized_rounding(sc, x, rounds, rng) for _ in range(20)) if sc.is_feasible(d)]
        best = min(sc.objective(d) for d in covers)
        ratios["LP"].append(value / opt)
        ratios["randomized, best of 20"].append(best / opt)
        ratios["primal-dual"].append(sc.objective(lab.primal_dual_set_cover(sc)[0]) / opt)
        ratios["greedy (unit 23)"].append(sc.objective(greedy(sc)[0]) / opt)
        rows.append(("set cover", value, opt, best))
    f = max(lab.frequency(random_set_cover(150, 100, s)) for s in range(10))
    for name, rs in ratios.items():
        print(f"  {name:>24}: mean {statistics.mean(rs):.3f}   max {max(rs):.3f}")
    print(f"  (largest frequency f = {f}, so primal-dual's guarantee is {f}; greedy's H_d is about 5)")
    print(f"\n  randomized rounding, failure rate over 4000 draws against the union bound 150·e^-t:")
    for t in fails:
        print(f"    t = {t}: measured {statistics.mean(fails[t]):.4f}   bound {min(1.0, bounds[t]):.4f}"
              f"   expected cost ≤ {t} × LP")


def gap_family(rows):
    print("\n3. The GF(2)^k family: no rounding of this LP can prove better than OPT/LP\n")
    print(f"  {'k':>3} {'sets':>5} {'LP':>7} {'OPT':>4} {'OPT/LP':>7} {'greedy':>7} {'primal-dual':>12}")
    greedy = unit("23").greedy_set_cover
    for k in (3, 4, 5, 6, 7):
        sc = lab.set_cover_gap_instance(k)
        value, _ = lab.set_cover_lp(sc)
        opt, proven = cpsat_cover(sc.universe, [[j for j, s in enumerate(sc.sets) if e in s] for e in range(sc.universe)], sc.costs)
        pd = sc.objective(lab.primal_dual_set_cover(sc)[0])
        g = sc.objective(greedy(sc)[0])
        print(f"  {k:>3} {sc.n:>5} {value:>7.3f} {opt:>3}{'' if proven else '?'} {opt / value:>7.2f} {g:>7} {pd:>12}")
        rows.append(("gap family", value, opt, g))


def facility_location(rows):
    print("\n4. Facility location, Jain-Vazirani (10 instances per size)\n")
    print(f"  {'F x C':>8} {'LP/OPT':>8} {'integral LPs':>13} {'JV/OPT':>18} {'sum alpha/OPT':>14}")
    for nf, nc in ((10, 40), (20, 80), (30, 120)):
        lp_r, jv_r, al_r, integral = [], [], [], 0
        for seed in range(10):
            fl = FacilityLocation.random(nf, nc, seed)
            milp = fl.milp()
            lp = lp_relaxation(milp).value
            opt = highs_mip(milp, options={"mip_rel_gap": 0.0}).value
            opened, assign, alpha = lab.jain_vazirani(fl)
            jv = fl.cost(opened, assign)
            lp_r.append(lp / opt)
            jv_r.append(jv / opt)
            al_r.append(float(sum(alpha)) / opt)
            integral += abs(lp - opt) < 1e-6
            rows.append(("facility location", lp, opt, jv))
        print(f"  {f'{nf}x{nc}':>8} {statistics.mean(lp_r):>8.3f} {integral:>10}/10 "
              f"   mean {statistics.mean(jv_r):.3f} max {max(jv_r):.3f} {statistics.mean(al_r):>14.3f}")


def plot(rows):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    OUT.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4))
    families = list(dict.fromkeys(r[0] for r in rows))
    xs = range(len(rows))
    ax.scatter(xs, [r[1] / r[2] for r in rows], marker="v", label="LP bound / OPT")
    ax.scatter(xs, [1.0] * len(rows), marker="_", color="k", label="OPT")
    ax.scatter(xs, [r[3] / r[2] for r in rows], marker="^", label="your algorithm / OPT")
    start = 0
    for fam in families:
        count = sum(1 for r in rows if r[0] == fam)
        ax.axvline(start - 0.5, color="0.8", lw=0.8)
        ax.text(start + count / 2, 2.3, fam, ha="center", fontsize=8)
        start += count
    ax.set_ylim(0.2, 2.4)
    ax.set_ylabel("ratio to the integer optimum")
    ax.set_xticks([])
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "then.png", dpi=130)
    print(f"\n  plot: {OUT / 'then.png'}")


if __name__ == "__main__":
    rows = []
    vertex_cover(rows)
    set_cover(rows)
    gap_family(rows)
    facility_location(rows)
    plot(rows)
