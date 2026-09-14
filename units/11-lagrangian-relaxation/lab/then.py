"""Unit 11 — "Then": the Held–Karp bound against LP bounds, and the GAP zig-zag.

  1. TSP: your Held–Karp bound against the degree LP and the subtour LP (unit 09),
     with the optimum from unit 09's exact solver. Put TSPLIB files (EUC_2D) in
     data/tsplib/ to include them.
  2. GAP: the two relaxations against HiGHS's LP bound and optimum, and your
     Lagrangian heuristic.
  3. The zig-zag: the assignment relaxation's bound per iteration, as a sparkline.

    uv run co then 11
"""

import glob
import time
from pathlib import Path

from colib.colgen import GAP
from colib.formats import read_tsplib
from colib.mip import highs_mip, lp_relaxation
from colib.problems import TSP
from colib.ref import unit
from colib.testing import load_lab
from colib.tsp import degree_milp

lab = load_lab(__file__)
ROOT = Path(__file__).resolve().parents[3]


def timed(f, *args, **kw):
    t = time.perf_counter()
    out = f(*args, **kw)
    return out, time.perf_counter() - t


def tsp():
    u09 = unit("09")
    cases = [(f"random {n}", TSP.random(n, seed=n)) for n in (30, 60, 100, 150)]
    cases += [(Path(p).stem, read_tsplib(p)) for p in sorted(glob.glob(str(ROOT / "data" / "tsplib" / "*.tsp")))]
    print("1. TSP bounds (gap = (optimum - bound) / optimum)\n")
    print(f"  {'instance':>12} {'optimum':>7} {'degree LP':>9} {'subtour LP':>10} {'Held–Karp':>9} {'gap':>6}"
          f" {'iters':>5} {'s':>6} {'edges fixed':>11}")
    for name, inst in cases:
        n = inst.n
        length = u09.tsp_exact(inst)[0]
        degree = lp_relaxation(degree_milp(inst, integer=False)).value
        subtour = u09.subtour_lp(inst)[0]
        (bound, pi, history), t = timed(lab.held_karp_bound, inst.dist, length, iterations=1000)
        fixed = lab.fix_edges(inst.dist, pi, length)
        print(f"  {name:>12} {length:>7} {degree:>9.1f} {subtour:>10.2f} {bound:>9.2f} {100 * (length - bound) / length:>5.2f}%"
              f" {len(history):>5} {t:>6.1f} {100 * len(fixed) / (n * (n - 1) / 2):>10.1f}%")


def gap():
    print("\n2. GAP, 300 subgradient iterations each (A: dualise assignment -> knapsacks; B: dualise capacity)\n")
    print(f"  {'m x n':>7} {'optimum':>7} {'LP':>8} {'bound A':>8} {'bound B':>8} {'A s':>6} {'heuristic':>9}")
    for m, n, seed in ((5, 25, 1), (5, 40, 2), (8, 60, 3), (10, 80, 4)):
        g = GAP.random(m, n, seed=seed, tightness=0.9)
        opt = highs_mip(g.milp(), time_limit=60, options={"mip_rel_gap": 0.0})
        lp = lp_relaxation(g.milp()).value
        upper = opt.value
        (a, u, _), ta = timed(lab.subgradient_ascent, lambda u: lab.gap_relax_assignment(g, u), [0.0] * n, upper, 300)
        b, _, _ = lab.subgradient_ascent(lambda l: lab.gap_relax_capacity(g, l), [0.0] * m, upper, 300,
                                         project=lambda v: [max(0.0, x) for x in v])
        heur = lab.gap_repair(g, lab.gap_relax_assignment(g, u)[1])
        tag = "" if opt.status == "optimal" else "*"
        print(f"  {f'{m}x{n}':>7} {upper:>6.0f}{tag:1} {lp:>8.2f} {a:>8.2f} {b:>8.2f} {ta:>6.1f} {heur[0] if heur else 'none':>9}")


def zigzag():
    print("\n3. The zig-zag: bound A on GAP 8x60, iterations 31-300, every 3rd, scaled to that window\n")
    g = GAP.random(8, 60, seed=3, tightness=0.9)
    upper = highs_mip(g.milp(), options={"mip_rel_gap": 0.0}).value
    bars = "▁▂▃▄▅▆▇█"
    for lam, patience in ((2.0, 20), (2.0, 10_000), (0.1, 10_000)):
        best, _, history = lab.subgradient_ascent(lambda u: lab.gap_relax_assignment(g, u), [0.0] * g.n, upper, 300,
                                                  lam=lam, patience=patience)
        tail = history[30::3]
        lo, hi = min(tail), max(tail)
        line = "".join(bars[min(7, int(8 * (h - lo) / (hi - lo + 1e-9)))] for h in tail)
        drops = sum(1 for a, b in zip(history, history[1:]) if b < a)
        print(f"  lam={lam:<4} patience={patience:<6} best {best:7.2f}   {drops:3d} of {len(history) - 1} steps go down"
              f"   window {lo:.1f}..{hi:.1f}")
        print(f"  {line}")


if __name__ == "__main__":
    tsp()
    gap()
    zigzag()
