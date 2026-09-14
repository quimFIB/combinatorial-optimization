"""Unit 10 — "Then": why column generation exists.

  1. Cutting stock, compact (Kantorovich) model in HiGHS vs your column generation:
     model size, the two LP bounds, and what 30 seconds of branch-and-cut achieves.
  2. The Farley bound as a stopping rule: how many iterations you could skip.
  3. Dual smoothing on instances with many small items.
  4. CVRP: the set-partitioning LP bound by ESPPRC pricing, as n grows.

    uv run co then 10
"""

import math
import time

from colib.colgen import CVRP, CuttingStock
from colib.mip import MILP, highs_mip, lp_relaxation
from colib.testing import load_lab

lab = load_lab(__file__)
LIMIT = 30.0


def timed(f, *args, **kw):
    t = time.perf_counter()
    out = f(*args, **kw)
    return out, time.perf_counter() - t


def compact_vs_colgen():
    print(f"1. Cutting stock, W = 1000, widths 10–45% of W, demands 5–50. HiGHS gets {LIMIT:.0f} s on the compact model.\n")
    print(f"  {'items':>5} {'rolls K':>7} {'vars':>7} {'nonzeros':>8} | {'LP':>7} {'best':>5} {'bound':>6} {'s':>5} |"
          f" {'CG LP':>8} {'cols':>5} {'s':>5} {'RMP-IP':>6}")
    for m in (10, 20, 40):
        inst = CuttingStock.random(m, seed=m, W=1000)
        milp = inst.kantorovich()
        K = inst.first_fit_decreasing()
        nnz = sum(1 for row in milp.A_ub for v in row if v)
        lp = lp_relaxation(milp).value
        mip, tm = timed(highs_mip, milp, time_limit=LIMIT)
        (value, patterns, x, history), tc = timed(lab.column_generation, inst.W, inst.widths, inst.demands)
        rolls, _ = lab.restricted_master_ip(patterns, inst.demands)
        best = f"{round(mip.value)}" if mip.value is not None and math.isfinite(mip.value) else "none"
        print(f"  {m:>5} {K:>7} {milp.n:>7} {nnz:>8} | {lp:>7.1f} {best:>5} {math.ceil(mip.bound - 1e-6):>6} {tm:>5.1f} |"
              f" {value:>8.2f} {len(patterns):>5} {tc:>5.2f} {rolls:>6}")
    big = CuttingStock.random(200, seed=1, W=10000, low=0.01, high=0.2, demand=(100, 1000))
    K = big.first_fit_decreasing()
    print(f"\n  200 small items with demands 100–1000: FFD uses {K} rolls, so the compact model would have "
          f"{K * (big.m + 1):,} variables and about {K * big.m * 2:,} nonzeros.")
    (value, patterns, _, history), tc = timed(lab.column_generation, big.W, big.widths, big.demands)
    print(f"  Column generation: LP {value:.2f} with {len(patterns)} patterns in {tc:.1f} s ({len(history)} iterations).")


def farley_stopping():
    print("\n2. Stopping early: the first iteration where ceil(Farley bound) = ceil(master value)\n")
    print(f"  {'items':>5} {'iterations':>10} {'could stop at':>13} {'LP':>9} {'ceil':>5}")
    for m in (20, 40, 80):
        inst = CuttingStock.random(m, seed=m, W=1000)
        value, _, _, history = lab.column_generation(inst.W, inst.widths, inst.demands)
        stop = next(k for k, (v, b) in enumerate(history) if math.ceil(b - 1e-6) == math.ceil(v - 1e-6))
        print(f"  {m:>5} {len(history):>10} {stop + 1:>13} {value:>9.3f} {math.ceil(value - 1e-6):>5}")


def smoothing():
    print("\n3. Wentges smoothing, W = 10000, widths 1–20% of W (many items per pattern)\n")
    alphas = (0.0, 0.5, 0.8, 0.9)
    print(f"  {'items':>5} " + " ".join(f"{'a=' + str(a):>14}" for a in alphas) + "   (iterations / seconds)")
    for m in (25, 50):
        inst = CuttingStock.random(m, seed=m, W=10000, low=0.01, high=0.2, demand=(10, 100))
        cells = []
        for a in alphas:
            (value, _, _, history), t = timed(lab.stabilised_column_generation, inst.W, inst.widths, inst.demands, alpha=a)
            cells.append(f"{len(history):>6} / {t:>5.2f}")
        print(f"  {m:>5} " + " ".join(f"{c:>14}" for c in cells))


def vrp():
    print("\n4. CVRP, capacity 20, demands 1–9: the set-partitioning LP by ESPPRC pricing\n")
    print(f"  {'n':>3} {'LP bound':>9} {'routes':>6} {'s':>7} {'RMP-IP':>7} {'gap':>6}")
    for n in (8, 12, 16, 20):
        cv = CVRP.random(n, seed=n, capacity=20)
        (value, routes, x), t = timed(lab.vrp_column_generation, cv)
        milp = MILP(c=tuple(cv.route_cost(r) for r in routes),
                    A_eq=tuple(tuple(1 if v in r else 0 for r in routes) for v in range(1, n + 1)),
                    b_eq=(1,) * n, ub=(1,) * len(routes), integer=(True,) * len(routes))
        ip = highs_mip(milp, time_limit=LIMIT).value
        print(f"  {n:>3} {value:>9.2f} {len(routes):>6} {t:>7.2f} {ip:>7.0f} {100 * (ip - value) / ip:>5.1f}%")
        if t > 60:
            break


if __name__ == "__main__":
    compact_vs_colgen()
    farley_stopping()
    smoothing()
    vrp()
