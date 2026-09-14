"""Unit 28 lab — experimental method.  REFERENCE SOLUTION, functional.

The store is SQLite, which is state by design: the functional version still writes rows, but builds every row
and query as a value first. The analysis half is pure: groupings with toolz, statistics as comprehensions,
Holm's step-down as an accumulate.
"""

from __future__ import annotations

import math
import sqlite3
import time
from itertools import accumulate, groupby

import toolz as tz

FIELDS = ("experiment", "solver", "instance", "seed", "status", "seconds", "value", "nodes")


# ---------------------------------------------------------------- step 1 ---

def open_store(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS runs (experiment TEXT NOT NULL, solver TEXT NOT NULL, instance TEXT NOT NULL,"
                 " seed INTEGER NOT NULL, status TEXT NOT NULL, seconds REAL NOT NULL, value REAL, nodes INTEGER,"
                 " PRIMARY KEY (experiment, solver, instance, seed))")
    conn.commit()
    return conn


def save_run(conn, run):
    with conn:
        conn.execute(f"INSERT OR REPLACE INTO runs ({', '.join(FIELDS)}) VALUES ({', '.join('?' * len(FIELDS))})",
                     tuple(run[f] for f in FIELDS))


def load_runs(conn, experiment, solver=None):
    where, args = ("experiment = ? AND solver = ?", (experiment, solver)) if solver is not None else ("experiment = ?", (experiment,))
    rows = conn.execute(f"SELECT {', '.join(FIELDS)} FROM runs WHERE {where} ORDER BY solver, instance, seed", args)
    return [dict(zip(FIELDS, row)) for row in rows]


# ---------------------------------------------------------------- step 2 ---

def run_benchmark(conn, experiment, solvers, instances, seeds, timeout, clock=time.perf_counter):
    have = frozenset((r["solver"], r["instance"], r["seed"]) for r in load_runs(conn, experiment))
    todo = [(i, s, seed) for i in instances for s in solvers for seed in seeds if (s, i, seed) not in have]

    def perform(iname, sname, seed):
        t0 = clock()
        out = solvers[sname](instances[iname], seed, timeout)
        seconds = clock() - t0
        late = seconds > timeout
        save_run(conn, {"experiment": experiment, "solver": sname, "instance": iname, "seed": seed,
                        "status": "timeout" if late else out["status"], "seconds": timeout if late else seconds,
                        "value": out.get("value"), "nodes": out.get("nodes")})
        return 1

    return sum(perform(*job) for job in todo)


# ---------------------------------------------------------------- step 3 ---

def shifted_geometric_mean(values, shift=10.0):
    return math.exp(sum(math.log(v + shift) for v in values) / len(values)) - shift


def par_seconds(run, timeout, penalty=1):
    return run["seconds"] if run["status"] == "optimal" else penalty * timeout


def sgm_by_solver(runs, timeout, shift=10.0, penalty=1):
    return tz.valmap(lambda rs: shifted_geometric_mean([par_seconds(r, timeout, penalty) for r in rs], shift),
                     tz.groupby("solver", runs))


# ---------------------------------------------------------------- step 4 ---

def _problems(runs):
    return tz.valmap(lambda rs: {r["solver"]: r for r in rs}, tz.groupby(lambda r: (r["instance"], r["seed"]), runs))


def performance_profile(runs, taus):
    solvers = sorted({r["solver"] for r in runs})
    problems = list(_problems(runs).values())

    def ratio(by_solver, s):
        best = min((r["seconds"] for r in by_solver.values() if r["status"] == "optimal"), default=None)
        r = by_solver.get(s)
        if best is None or r is None or r["status"] != "optimal":
            return math.inf
        return r["seconds"] / best if best > 0 else (1.0 if r["seconds"] == 0 else math.inf)

    ratios = {s: [ratio(p, s) for p in problems] for s in solvers}
    return {s: [sum(q <= tau for q in ratios[s]) / len(problems) for tau in taus] for s in solvers}


def virtual_best(runs):
    def best(by_solver):
        solved = sorted((r["seconds"], s) for s, r in by_solver.items() if r["status"] == "optimal")
        return (solved[0][1], solved[0][0]) if solved else (None, None)
    return tz.valmap(best, _problems(runs))


# ---------------------------------------------------------------- step 5 ---

def bootstrap_ci(values, statistic, rng, level=0.95, resamples=2000):
    stats = sorted(statistic(rng.choices(values, k=len(values))) for _ in range(resamples))
    at = lambda q: stats[math.floor(q * (resamples - 1))]
    return at((1 - level) / 2), at((1 + level) / 2)


def geometric_ratio_ci(a, b, rng, shift=10.0, level=0.95, resamples=2000):
    logs = [math.log((x + shift) / (y + shift)) for x, y in zip(a, b)]
    mean = lambda v: sum(v) / len(v)
    lo, hi = bootstrap_ci(logs, mean, rng, level, resamples)
    return math.exp(mean(logs)), (math.exp(lo), math.exp(hi))


# ---------------------------------------------------------------- step 6 ---

def holm(pvalues):
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    stepped = accumulate((min(1.0, (m - k) * pvalues[i]) for k, i in enumerate(order)), max)
    return [adj for _, adj in sorted(zip(order, stepped))]


def wilcoxon_signed_rank(a, b):
    d = [x - y for x, y in zip(a, b) if x != y]
    n = len(d)
    if n == 0:
        return 0.0, 1.0
    ordered = sorted(d, key=abs)
    groups = [list(g) for _, g in groupby(ordered, key=abs)]
    starts = list(accumulate((len(g) for g in groups), initial=0))
    signed = [((starts[k] + starts[k + 1] + 1) / 2, x) for k, g in enumerate(groups) for x in g]
    plus = sum(r for r, x in signed if x > 0)
    minus = sum(r for r, x in signed if x < 0)
    T = min(plus, minus)
    tie_term = sum(len(g) ** 3 - len(g) for g in groups)
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24 - tie_term / 48)
    if sigma == 0:
        return T, 1.0
    z = max(abs(T - n * (n + 1) / 4) - 0.5, 0.0) / sigma
    return T, min(1.0, math.erfc(z / math.sqrt(2)))
