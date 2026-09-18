"""Unit 27 — "Then": one intervention at a time, measured with SCIP.

Ten bin packing instances (six uniform, four "triplets" where every bin must be exactly full), 20 s each:

  A  assignment model, x <= y linking, one bin per item
  B  capacity constraints linked to y
  B' the same with SCIP's own symmetry handling switched off
  C  B + symmetry-breaking constraints
  D  C + first-fit-decreasing bin count + L2 fixing (bounded_model)
  E  D + the first-fit-decreasing packing as a MIP start
  F  arc-flow reformulation

Each row reports solved count, shifted geometric mean time (shift 1 s, timeouts at 20 s), median nodes,
mean final gap, and the heuristic that found the best solution most often (parsed with your parse_statistics).

If units/27-*/lab/miplib/ holds .mps or .mps.gz files (download them from miplib.zib.de yourself), section 2
runs SCIP and HiGHS on each for 60 s. That path hasn't been run here: there's no MIPLIB file in the repo.

    uv run co then 27
"""

import math
import random
import statistics
import tempfile
import time
from collections import Counter
from pathlib import Path

from colib.testing import load_lab

lab = load_lab(__file__)
LIMIT = 20.0
HERE = Path(__file__).parent


def uniform(n, seed):
    r = random.Random(seed)
    return [r.randint(20, 60) for _ in range(n)], 100


def triplets(m, seed, capacity=1000):
    """m bins each filled exactly by three items in [250, 500): the optimum is m, with no slack anywhere."""
    r = random.Random(seed)
    sizes = []
    for _ in range(m):
        a = r.randint(250, 499)
        b = r.randint(max(250, capacity - a - 499), min(499, capacity - a - 250))
        sizes += [a, b, capacity - a - b]
    r.shuffle(sizes)
    return sizes, capacity


def instances():
    return ([(f"uniform-40 #{s}", *uniform(40, s)) for s in range(6)]
            + [(f"triplets-30 #{s}", *triplets(10, s)) for s in range(4)])


def run(build, sizes, capacity, seed_shift=0):
    model, extra = build(sizes, capacity)
    model.setParam("limits/time", LIMIT)
    model.setParam("randomization/randomseedshift", seed_shift)
    for key, value in extra.items():
        model.setParam(key, value)
    t = time.perf_counter()
    model.optimize()
    seconds = time.perf_counter() - t
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "stats.txt"
        model.writeStatistics(str(path))
        text = path.read_text()
    try:
        stats = lab.parse_statistics(text)
        nodes = stats["nodes"]
    except (KeyError, IndexError, ValueError) as e:     # keep going, and keep the report that broke the parser
        (HERE / "out").mkdir(exist_ok=True)
        (HERE / "out" / "unparsed_statistics.txt").write_text(text)
        print(f"    (parse_statistics failed with {e!r}; report saved to out/unparsed_statistics.txt)")
        stats, nodes = {"gap_percent": None, "found_by": None}, model.getNTotalNodes()
    solved = model.getStatus() == "optimal"
    return {"solved": solved, "seconds": seconds if solved else LIMIT, "nodes": nodes,
            "gap": stats["gap_percent"], "found_by": stats["found_by"]}


def config_a(sizes, C):
    m, _, _ = lab.assignment_model(sizes, C, len(sizes), linked=False)
    return m, {}


def config_b(sizes, C):
    m, _, _ = lab.assignment_model(sizes, C, len(sizes), linked=True)
    return m, {}


def config_b_nosym(sizes, C):
    m, _, _ = lab.assignment_model(sizes, C, len(sizes), linked=True)
    return m, {"misc/usesymmetry": 0}


def config_c(sizes, C):
    m, x, y = lab.assignment_model(sizes, C, len(sizes), linked=True)
    lab.add_symmetry_breaking(m, x, y, len(sizes))
    return m, {}


def config_d(sizes, C):
    m, _, _ = lab.bounded_model(sizes, C)
    return m, {}


def config_e(sizes, C):
    m, x, y = lab.bounded_model(sizes, C)
    assert lab.add_start(m, x, y, lab.first_fit_decreasing(sizes, C))
    return m, {}


def config_f(sizes, C):
    m, _ = lab.arcflow_model(sizes, C)
    return m, {}


CONFIGS = [("A  x <= y linking", config_a), ("B  capacity linked", config_b),
           ("B' … symmetry handling off", config_b_nosym), ("C  B + symmetry breaking", config_c),
           ("D  C + FFD bins, L2 fixing", config_d), ("E  D + FFD as MIP start", config_e),
           ("F  arc flow", config_f)]


def sgm(values, shift=1.0):
    return math.exp(statistics.mean(math.log(v + shift) for v in values)) - shift


def interventions():
    insts = instances()
    print(f"1. Bin packing interventions, {len(insts)} instances, SCIP, {LIMIT:.0f} s limit\n")
    for name, sizes, C in insts:
        print(f"  {name}: n = {len(sizes)}, sum/C = {sum(sizes) / C:.2f}, L2 = {lab.lower_bound_l2(sizes, C)},"
              f" FFD = {len(lab.first_fit_decreasing(sizes, C))}")
    print(f"\n  {'configuration':>28} {'solved':>7} {'SGM s':>7} {'median nodes':>13} {'mean gap %':>11}  best found by (most often)")
    results = {}
    for label, build in CONFIGS:
        rows = results[label] = [run(build, sizes, C) for _, sizes, C in insts]
        gaps = [r["gap"] for r in rows if r["gap"] is not None]
        finder = Counter(r["found_by"] for r in rows).most_common(1)[0][0]
        print(f"  {label:>28} {sum(r['solved'] for r in rows):>4}/{len(rows)} {sgm([r['seconds'] for r in rows]):>7.2f}"
              f" {statistics.median(r['nodes'] for r in rows):>13.0f} {statistics.mean(gaps) if gaps else float('nan'):>11.2f}  {finder}")

    print("\n  seconds per instance (20.0 = not solved):")
    print("  " + " " * 16 + "".join(f"{label.split()[0]:>7}" for label, _ in CONFIGS))
    for k, (name, _, _) in enumerate(insts):
        print(f"  {name:>16}" + "".join(f"{results[label][k]['seconds']:>7.1f}" for label, _ in CONFIGS))

    print("\n  where consecutive rows disagree on solving an instance, re-run both with three more SCIP seeds:")
    labels = [label for label, _ in CONFIGS]
    for prev, cur in zip(labels, labels[1:]):
        for k, (name, sizes, C) in enumerate(insts):
            if results[prev][k]["solved"] != results[cur][k]["solved"]:
                builds = dict(CONFIGS)
                times = {lab_: [results[lab_][k]["seconds"]] + [run(builds[lab_], sizes, C, shift)["seconds"] for shift in (1, 2, 3)]
                         for lab_ in (prev, cur)}
                print(f"    {name}: {prev.split()[0]} " + " ".join(f"{t:.1f}" for t in times[prev])
                      + f"   |   {cur.split()[0]} " + " ".join(f"{t:.1f}" for t in times[cur]))


def miplib():
    folder = HERE / "miplib"
    files = sorted(folder.glob("*.mps*")) if folder.exists() else []
    if not files:
        print("\n2. MIPLIB: no files in lab/miplib/ (download a few from miplib.zib.de to run this section)")
        return
    import highspy
    from pyscipopt import Model
    print("\n2. MIPLIB instances, 60 s each\n")
    for f in files:
        m = Model()
        m.hideOutput()
        m.readProblem(str(f))
        m.setParam("limits/time", 60)
        m.optimize()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "stats.txt"
            m.writeStatistics(str(path))
            s = lab.parse_statistics(path.read_text())
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("time_limit", 60.0)
        h.readModel(str(f))
        h.run()
        info = h.getInfo()
        print(f"  {f.name}: SCIP {m.getStatus()} primal {s['primal_bound']} dual {s['dual_bound']} gap {s['gap_percent']}%"
              f" nodes {s['nodes']} | HiGHS {h.modelStatusToString(h.getModelStatus())} primal {info.objective_function_value}"
              f" dual {info.mip_dual_bound} nodes {info.mip_node_count}")


if __name__ == "__main__":
    interventions()
    miplib()
