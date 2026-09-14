"""Unit 21 — "Then": what learning from propagation buys, and CP-SAT's log read by name.

  1. Job-shop makespan: unit 18's CP engine (propagation, no learning) against your LCG solver
     (the same kind of propagation, explained, with clause learning): proofs, effort, seconds.
  2. Inside LCG: with and without the explained timetable (Unary), with and without restarts.
  3. CP-SAT's search log on a 15 x 15 job-shop, with the components you have built named.

    uv run co then 21
"""

import random
import time

from ortools.sat.python import cp_model

from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
gc = unit("18")


def shops():
    out = [("ft06", JobShop.ft06(), 60)]
    for n, machines, seed in ((6, 4, 1), (8, 4, 2), (8, 5, 3)):
        shop = JobShop.random(n, seed=seed, machines=machines)
        out.append((f"random {n}x{machines} #{seed}", shop, sum(d for job in shop.jobs for _, d in job) // 2))
    return out


def learning_vs_not():
    print("1. Makespan with and without learning (limits: 100 000 CP nodes, 20 000 conflicts)\n")
    print(f"  {'instance':<18} | {'CP: best':>8} {'proven':>6} {'nodes':>7} {'s':>6} | {'LCG: best':>9} {'proven':>6}"
          f" {'conflicts':>9} {'explanations':>12} {'s':>6}")
    for name, shop, horizon in shops():
        t = time.perf_counter()
        best, _, stats, _ = gc.minimise(*gc.jobshop(shop, horizon, True), node_limit=100_000)
        tc = time.perf_counter() - t
        t = time.perf_counter()
        lbest, proven, lstats, _ = lab.minimise_makespan(shop, horizon, conflict_limit=20_000)
        tl = time.perf_counter() - t
        print(f"  {name:<18} | {best!s:>8} {str(stats.extra['complete']):>6} {stats.nodes:>7} {tc:>6.1f} |"
              f" {lbest!s:>9} {str(proven):>6} {lstats['conflicts']:>9} {lstats['explanations']:>12} {tl:>6.1f}")


def ablation():
    print("\n2. LCG on ft06 with parts removed\n")
    print(f"  {'variant':<34} {'best':>5} {'proven':>6} {'conflicts':>9} {'s':>6}")
    shop = JobShop.ft06()

    def run(label, drop_unary=False, **kw):
        model, starts, mk = lab.jobshop_model(shop, 60)
        if drop_unary:
            model.propagators = [p for p in model.propagators if type(p).__name__ != "Unary"]
        solver = lab.LCGSolver(model, **kw)
        best, t = None, time.perf_counter()
        while True:
            result = solver.solve(conflict_limit=20_000)
            if result is not True:
                break
            best = mk.value(solver)
            solver.cancel_until(0)
            if not solver.add_clause([mk.le(best - 1)]):
                result = False
                break
        print(f"  {label:<34} {best!s:>5} {str(result is False):>6} {solver.stats['conflicts']:>9} {time.perf_counter() - t:>6.1f}")

    run("disjunctions + timetable")
    run("disjunctions only", drop_unary=True)
    run("no restarts (restart_base = 10^9)", restart_base=10 ** 9)


SECTIONS = [
    ("Presolve summary", "presolve: simplification before search (unit 27)"),
    ("Starting search", "the portfolio of workers: full-problem CDCL/LP searches, first-solution heuristics, LNS"),
    ("Search stats", "CDCL search per worker: conflicts, branches, restarts (units 19, 20), Boolean and integer propagations (17, 18, 21)"),
    ("SAT stats", "clause learning and conflict-clause minimisation (unit 20)"),
    ("Clause deletion", "learned-clause deletion (unit 20's reduce_db)"),
    ("Lp stats", "the linear relaxation run alongside, with cuts: Part II inside Part IV"),
    ("Lp Cut", "which cuts: Gomory/MIR (unit 08) and no-overlap-specific ones"),
    ("LNS stats", "large neighbourhood search workers (unit 19)"),
]


def cpsat_log():
    print("\n3. CP-SAT's log on a 15 x 15 job-shop (durations 1–99), 5 seconds, 8 workers\n")
    r = random.Random(3)
    jobs = []
    for _ in range(15):
        order = list(range(15))
        r.shuffle(order)
        jobs.append([(m, r.randint(1, 99)) for m in order])
    m = cp_model.CpModel()
    H = sum(d for job in jobs for _, d in job)
    per, ends = {k: [] for k in range(15)}, []
    for job in jobs:
        prev = None
        for mach, d in job:
            s = m.new_int_var(0, H, "")
            per[mach].append(m.new_interval_var(s, d, s + d, ""))
            if prev is not None:
                m.add(s >= prev)
            prev = s + d
        ends.append(prev)
    for ivs in per.values():
        m.add_no_overlap(ivs)
    mk = m.new_int_var(0, H, "")
    m.add_max_equality(mk, ends)
    m.minimize(mk)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    solver.parameters.num_workers = 8
    solver.parameters.log_search_progress = True
    solver.parameters.log_to_stdout = False
    lines = []
    solver.log_callback = lines.append
    solver.solve(m)
    text = "\n".join(lines).splitlines()
    print(f"  makespan {solver.objective_value:.0f}, bound {solver.best_objective_bound:.0f} "
          f"({len(text)} log lines). Selected sections, first rows:\n")
    for header, meaning in SECTIONS:
        at = next((k for k, ln in enumerate(text) if ln.strip().startswith(header)), None)
        print(f"  ▸ {meaning}")
        if at is None:
            print("      (section not in this version's log)")
            continue
        for ln in text[at:at + 4]:
            if ln.strip():
                print(f"      | {ln.rstrip()[:118]}")


if __name__ == "__main__":
    learning_vs_not()
    ablation()
    cpsat_log()
