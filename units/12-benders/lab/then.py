"""Unit 12 — "Then": where Benders overtakes the monolithic model.

  1. Two-stage stochastic facility location (10 facilities, 30 customers) with a growing
     number of scenarios: HiGHS on the deterministic equivalent against your Benders
     (multi-cut, single-cut, LP-first). Seconds, plus a log-scale crossover plot.
  2. The same comparison with looser capacities, where Benders needs many more iterations,
     and what Pareto-optimal cuts do there.

    uv run co then 12
"""

import math
import time

from colib.colgen import StochasticFacility
from colib.testing import load_lab

lab = load_lab(__file__)
BUDGET = 240.0


def timed(f, *args, **kw):
    t = time.perf_counter()
    out = f(*args, **kw)
    return out, time.perf_counter() - t


def plot(rows, labels):
    """rows: list of (S, {label: seconds or None}); a log-scale dot plot, one line per S."""
    all_t = [t for _, cells in rows for t in cells.values() if t]
    lo, hi = math.log10(min(all_t)), math.log10(max(all_t))
    width = 60
    marks = {lab_: ch for lab_, ch in zip(labels, "DMSL")}
    print(f"\n  log10 seconds from {lo:.1f} to {hi:.1f};  " + "  ".join(f"{ch} = {name}" for name, ch in marks.items()))
    for S, cells in rows:
        line = [" "] * (width + 1)
        for name, t in cells.items():
            if t:
                pos = int(round(width * (math.log10(t) - lo) / (hi - lo + 1e-12)))
                line[pos] = marks[name] if line[pos] == " " else "*"
        print(f"  S={S:<4} |{''.join(line)}|")


def crossover(capacity_ratio, scenarios, pareto_at=None):
    labels = ["DE (HiGHS)", "multi-cut", "single-cut", "LP-first"]
    print(f"  {'S':>4} {'DE vars':>8} {'DE s':>7} {'optimum':>9} | {'multi s':>8} {'it':>3} | {'single s':>8} {'it':>3} |"
          f" {'LP-first s':>10} {'it':>3}")
    rows, alive = [], {name: True for name in labels}
    for S in scenarios:
        inst = StochasticFacility.random(10, 30, S, seed=S, capacity_ratio=capacity_ratio)
        cells = {}
        status, value, _, t_de, _ = inst.deterministic_equivalent(time_limit=BUDGET)
        cells["DE (HiGHS)"] = t_de if status == "optimal" else None
        runs = {}
        for name, kw in (("multi-cut", {}), ("single-cut", {"multicut": False}), ("LP-first", {"lp_first": True})):
            if not alive[name]:
                runs[name] = None
                continue
            (ub, _, history), t = timed(lab.benders, inst, **kw)
            assert status != "optimal" or abs(ub - value) <= 1e-4 * value, (name, ub, value)
            runs[name] = (t, len(history))
            cells[name] = t
            alive[name] = t < BUDGET
        rows.append((S, cells))
        fmt = lambda r, w: (f"{r[0]:>{w}.2f} {r[1]:>3}" if r else f"{'—':>{w}} {'':>3}")
        de = f"{t_de:>7.2f}" if status == "optimal" else f"{'>' + str(int(BUDGET)):>7}"
        print(f"  {S:>4} {10 + 30 * S * 11:>8} {de} {value:>9.1f} | {fmt(runs['multi-cut'], 8)} | {fmt(runs['single-cut'], 8)} |"
              f" {fmt(runs['LP-first'], 10)}")
        if pareto_at == S:
            (ub, _, history), t = timed(lab.benders, inst, pareto=True)
            print(f"  {'':>4} {'':>8} {'':>7} {'':>9} | Pareto-optimal cuts: {t:.2f} s, {len(history)} iterations")
    plot(rows, labels)


if __name__ == "__main__":
    print("1. Capacity 1.6x mean demand: tight, few Benders iterations\n")
    crossover(1.6, (5, 10, 25, 50, 100, 200, 400))
    print("\n2. Capacity 3x mean demand: loose, many near-equivalent facility choices\n")
    crossover(3.0, (5, 10, 25, 50, 100), pareto_at=25)
