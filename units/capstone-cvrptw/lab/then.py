"""Capstone — "Then": the four methods refereed on Solomon's instances.

    uv run co data                        once: download the instances
    uv run co then capstone               run what's missing, then report (resumable)
    uv run co then capstone --report      only the report, from the runs already stored
    uv run co then capstone --sizes 25 --timeout 30 --jobs 4

Every (method, instance) pair runs once, seed 0, single-threaded, under the same wall-clock limit, in its
own process: SCIP branch-and-cut (a), branch-and-price (b), CP-SAT with one worker (c), ALNS (d). Runs go
through unit 28's run_benchmark into out/capstone.sqlite, so an interrupted run resumes where it stopped.
A process that outlives the limit by 30 s, or grows past 2.5 GB, is killed and recorded as "killed".
Several run side by side (--jobs), so absolute seconds carry some contention; every method pays it.

The report:
  1. Integrity: invalid solutions, and "optimal" claims refuted by a better solution from another method.
  2. Per series and size: instances solved to proven optimality, and the mean primal gap at the limit
     against the best value any method found.
  3. Head to head on primal gap, per size: Wilcoxon over instances, Holm over the six pairs.
  4. Head to head on time to proof among the exact methods (PAR1 seconds), per size.
  5. Which instance features go with which winner: window width, route length, clustering.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import os
import sqlite3
import statistics
import time
from pathlib import Path

from colib.ref import unit
from colib.testing import load_lab
from colib.vrptw import SINTEF_BEST_100, SOLOMON_NAMES, have_solomon, solomon

lab = load_lab(__file__)
u28 = unit("28")
OUT = Path(__file__).resolve().parent / "out"
EXPERIMENT = "capstone"
METHODS = {
    "mip": (lab.solve_mip, {}),
    "bp": (lab.branch_and_price, {}),
    "cpsat": (lab.solve_cpsat, {"workers": 1}),
    "alns": (lab.alns_vrptw, {}),
}
LABEL = {"mip": "(a) SCIP branch-and-cut", "bp": "(b) branch-and-price", "cpsat": "(c) CP-SAT, 1 worker",
         "alns": "(d) ALNS"}
SERIES = ("C1", "C2", "R1", "R2", "RC1", "RC2")


def instance_key(name, n):
    return f"{name}.{n}"


def _work(method, name, n, timeout, queue):
    """Child process: one run through unit 28's run_benchmark, into a private in-memory store."""
    try:
        conn = u28.open_store()
        f, options = METHODS[method]
        solve = lab.benchmark_solver(f, **options)
        # the method gets the limit; the harness allows 5 s over it for building and checking, so a method
        # that stops on time isn't recorded as a timeout
        u28.run_benchmark(conn, EXPERIMENT, {method: lambda inst, seed, _: solve(inst, seed, timeout)},
                          {instance_key(name, n): solomon(name, n)}, [0], timeout + 5)
        queue.put(u28.load_runs(conn, EXPERIMENT)[0])
    except Exception as e:                                    # a crash is a result too
        queue.put({"experiment": EXPERIMENT, "solver": method, "instance": instance_key(name, n), "seed": 0,
                   "status": f"crashed: {type(e).__name__}", "seconds": timeout, "value": None, "nodes": None})


def _rss_bytes(pid):
    try:
        with open(f"/proc/{pid}/statm") as fh:
            return int(fh.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except OSError:
        return 0


def run_all(store, sizes, timeout, jobs):
    have = {(r["solver"], r["instance"]) for r in u28.load_runs(store, EXPERIMENT)}
    todo = [(m, name, n) for n in sizes for name in SOLOMON_NAMES for m in METHODS
            if (m, instance_key(name, n)) not in have]
    if not todo:
        return
    print(f"running {len(todo)} runs, {jobs} at a time, {timeout:g} s each "
          f"(at most {len(todo) * timeout / jobs / 3600:.1f} h)", flush=True)
    ctx = mp.get_context("fork")
    live = {}
    done = 0
    t0 = time.perf_counter()
    while todo or live:
        while todo and len(live) < jobs:
            task = todo.pop(0)
            q = ctx.Queue()
            p = ctx.Process(target=_work, args=(*task, timeout, q), daemon=True)
            p.start()
            live[p] = (task, q, time.perf_counter())
        time.sleep(0.2)
        for p, (task, q, started) in list(live.items()):
            row = None
            if not q.empty():
                row = q.get()
            elif time.perf_counter() - started > timeout + 30 or _rss_bytes(p.pid) > 2.5 * 2**30:
                p.kill()
                m, name, n = task
                row = {"experiment": EXPERIMENT, "solver": m, "instance": instance_key(name, n), "seed": 0,
                       "status": "killed", "seconds": timeout, "value": None, "nodes": None}
            elif not p.is_alive() and q.empty():
                m, name, n = task
                row = {"experiment": EXPERIMENT, "solver": m, "instance": instance_key(name, n), "seed": 0,
                       "status": "crashed", "seconds": timeout, "value": None, "nodes": None}
            if row is not None:
                p.join(1)
                u28.save_run(store, row)
                del live[p]
                done += 1
                if done % 20 == 0:
                    print(f"  {done} runs done, {(time.perf_counter() - t0) / 60:.0f} min", flush=True)


# ---------------------------------------------------------------- report

def features(name, n):
    inst = solomon(name, n)
    widths = [inst.due[c] - inst.ready[c] for c in inst.customers]
    return {"series": inst.series(), "width": statistics.mean(widths) / inst.due[0],
            "clustered": inst.series().startswith("C")}


def fmt_gap(g):
    return "   0   " if g == 0 else f"{100 * g:6.2f}%"


def report(store, sizes, timeout):
    runs = [r for r in u28.load_runs(store, EXPERIMENT) if int(r["instance"].split(".")[1]) in sizes]
    if not runs:
        print("no runs stored yet")
        return
    ref = lab.references(runs)
    by = {(r["solver"], r["instance"]): r for r in runs}
    methods = list(METHODS)

    print("\n1. Integrity")
    bad = [r for r in runs if r["status"] == "invalid" or r["status"].startswith(("crashed", "killed"))]
    counts = {}
    for r in bad:
        counts[(r["solver"], r["status"])] = counts.get((r["solver"], r["status"]), 0) + 1
    print(f"   {len(runs)} runs stored. Invalid, crashed or killed: "
          + (", ".join(f"{LABEL[m]} {s} x{k}" for (m, s), k in sorted(counts.items())) or "none"))
    contra = lab.contradictions(runs)
    print(f"   'optimal' claims refuted by another method's better solution: {contra or 'none'}")
    proven = {}
    for r in runs:
        if r["status"] == "optimal":
            proven.setdefault(r["instance"], set()).add(r["value"])
    disagree = {i: v for i, v in proven.items() if len(v) > 1}
    print(f"   instances where two methods prove different optima: {disagree or 'none'}")

    gap = lambda r: lab.primal_gap(r["value"], ref[r["instance"]][0]) if r["instance"] in ref else 1.0
    for n in sizes:
        names = [instance_key(nm, n) for nm in SOLOMON_NAMES if all((m, instance_key(nm, n)) in by for m in methods)]
        if not names:
            continue
        print(f"\n2. n = {n}: proven optimal (of instances), and mean primal gap at {timeout:g} s against the best found")
        print(f"   {'series':<6} {'inst':>4} " + " ".join(f"{m:>15}" for m in methods) + "   best proven")
        for s in SERIES + ("all",):
            group = [i for i in names if s == "all" or solomon(i.split(".")[0], n).series() == s]
            if not group:
                continue
            cells = []
            for m in methods:
                solved = sum(by[m, i]["status"] == "optimal" for i in group)
                g = statistics.mean(gap(by[m, i]) for i in group)
                cells.append(f"{solved:>3} {fmt_gap(g):>8}" if m != "alns" else f"  - {fmt_gap(g):>8}")
            closed = sum(ref.get(i, (0, False))[1] for i in group)
            print(f"   {s:<6} {len(group):>4} " + " ".join(f"{c:>15}" for c in cells) + f"   {closed:>4}")

        sub = [r for r in runs if r["instance"] in names]
        pairs = [(a, b) for k, a in enumerate(methods) for b in methods[k + 1:]]
        print(f"\n3. n = {n}: head to head on primal gap ({len(names)} instances; Wilcoxon, Holm over {len(pairs)} pairs)")
        for row in lab.head_to_head(sub, pairs, gap):
            print(f"   {row['a']:>5} vs {row['b']:<5}  {row['a']} better on {row['wins']:>2}, {row['b']} on {row['losses']:>2},"
                  f" tied {row['ties']:>2}   p = {row['p']:.2g} (Holm {row['p_holm']:.2g})   verdict: {row['verdict']}")
        exact = [m for m in methods if m != "alns"]
        par = lambda r: u28.par_seconds(r, timeout)
        epairs = [(a, b) for k, a in enumerate(exact) for b in exact[k + 1:]]
        sgm = {m: u28.shifted_geometric_mean([par(by[m, i]) for i in names], 1.0) for m in exact}
        print(f"\n4. n = {n}: time to proof, PAR1 seconds (SGM, shift 1: "
              + ", ".join(f"{m} {sgm[m]:.1f}" for m in exact) + ")")
        for row in lab.head_to_head(sub, epairs, par):
            print(f"   {row['a']:>5} vs {row['b']:<5}  faster on {row['wins']:>2} / {row['losses']:>2}, tied {row['ties']:>2}"
                  f"   p = {row['p']:.2g} (Holm {row['p_holm']:.2g})   verdict: {row['verdict']}")

        print(f"\n5. n = {n}: who wins each instance (smallest gap, then fastest proof; '=' when no method is ahead)")
        wins = {}
        for i in names:
            key = lambda m: (gap(by[m, i]), par(by[m, i]) if m != "alns" else timeout + 1)
            ranked = sorted(methods, key=key)
            winner = ranked[0] if key(ranked[0]) < key(ranked[1]) else "="
            f = features(*i.split(".")[0:1], n)
            wins.setdefault(f["series"], []).append(winner)
        print(f"   {'series':<6} {'window/horizon':>14}  " + "  ".join(f"{m:>5}" for m in methods + ['=']))
        for s in SERIES:
            if s in wins:
                group = [i for i in names if solomon(i.split('.')[0], n).series() == s]
                w = statistics.mean(features(i.split('.')[0], n)["width"] for i in group)
                print(f"   {s:<6} {w:>14.2f}  " + "  ".join(f"{wins[s].count(m):>5}" for m in methods + ['=']))

    if 100 in sizes:
        print("\n6. n = 100 against SINTEF's best known (hierarchical objective, untruncated distances: a sanity check, not a score)")
        ratios = [ref[instance_key(nm, 100)][0] / 10 / SINTEF_BEST_100[nm][1] for nm in SOLOMON_NAMES
                  if instance_key(nm, 100) in ref]
        if ratios:
            print(f"   best found / SINTEF distance over {len(ratios)} instances: median {statistics.median(ratios):.3f},"
                  f" range [{min(ratios):.3f}, {max(ratios):.3f}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[25, 50, 100])
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--jobs", type=int, default=max(1, min(5, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--report", action="store_true", help="only report on the runs already stored")
    ap.add_argument("--store", default=str(OUT / "capstone.sqlite"))
    args = ap.parse_args()
    if not have_solomon():
        raise SystemExit("Solomon's instances are missing: run `uv run co data` first")
    OUT.mkdir(exist_ok=True)
    store = u28.open_store(args.store)
    if not args.report:
        run_all(store, args.sizes, args.timeout, args.jobs)
    report(store, args.sizes, args.timeout)


if __name__ == "__main__":
    main()
