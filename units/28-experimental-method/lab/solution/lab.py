"""Unit 28 lab — experimental method.  REFERENCE SOLUTION, imperative.

A benchmark is a set of runs: (experiment, solver, instance, seed) -> status, seconds, value, nodes. Runs live in
SQLite so they can be queried, resumed and re-analysed without re-running anything. A run counts as solved iff
its status is "optimal". Everything after step 2 works on lists of run dicts.
"""

from __future__ import annotations

import math
import sqlite3
import time

FIELDS = ("experiment", "solver", "instance", "seed", "status", "seconds", "value", "nodes")


# ---------------------------------------------------------------- step 1 ---

def open_store(path=":memory:"):
    """A SQLite connection with a table `runs` holding FIELDS, whose primary key is (experiment, solver,
    instance, seed). Opening an existing file keeps its runs."""
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE IF NOT EXISTS runs (
        experiment TEXT NOT NULL, solver TEXT NOT NULL, instance TEXT NOT NULL, seed INTEGER NOT NULL,
        status TEXT NOT NULL, seconds REAL NOT NULL, value REAL, nodes INTEGER,
        PRIMARY KEY (experiment, solver, instance, seed))""")
    conn.commit()
    return conn


def save_run(conn, run):
    """Insert a run dict (all FIELDS; value and nodes may be None), replacing any run with the same key."""
    conn.execute(f"INSERT OR REPLACE INTO runs ({', '.join(FIELDS)}) VALUES ({', '.join('?' * len(FIELDS))})",
                 tuple(run[f] for f in FIELDS))
    conn.commit()


def load_runs(conn, experiment, solver=None):
    """Runs of one experiment (and optionally one solver) as dicts, ordered by solver, instance, seed."""
    sql = f"SELECT {', '.join(FIELDS)} FROM runs WHERE experiment = ?"
    args = [experiment]
    if solver is not None:
        sql += " AND solver = ?"
        args.append(solver)
    rows = conn.execute(sql + " ORDER BY solver, instance, seed", args).fetchall()
    return [dict(zip(FIELDS, row)) for row in rows]


# ---------------------------------------------------------------- step 2 ---

def run_benchmark(conn, experiment, solvers, instances, seeds, timeout, clock=time.perf_counter):
    """For each instance (in dict order), each solver (in dict order) and each seed: skip it if the store already
    has that run; otherwise time solver(instance_data, seed, timeout) with `clock`, which returns a dict with
    "status" and optionally "value" and "nodes". If it took longer than timeout, record status "timeout" and
    seconds = timeout; otherwise record what it returned and the measured seconds. Returns the number of runs
    performed (not skipped)."""
    have = {(r["solver"], r["instance"], r["seed"]) for r in load_runs(conn, experiment)}
    done = 0
    for iname, data in instances.items():
        for sname, solve in solvers.items():
            for seed in seeds:
                if (sname, iname, seed) in have:
                    continue
                t0 = clock()
                out = solve(data, seed, timeout)
                seconds = clock() - t0
                status = out["status"]
                if seconds > timeout:
                    status, seconds = "timeout", timeout
                save_run(conn, {"experiment": experiment, "solver": sname, "instance": iname, "seed": seed,
                                "status": status, "seconds": seconds, "value": out.get("value"),
                                "nodes": out.get("nodes")})
                done += 1
    return done


# ---------------------------------------------------------------- step 3 ---

def shifted_geometric_mean(values, shift=10.0):
    """exp(mean(log(v + shift))) - shift."""
    return math.exp(sum(math.log(v + shift) for v in values) / len(values)) - shift


def par_seconds(run, timeout, penalty=1):
    """Penalised run time: the measured seconds if solved, penalty * timeout otherwise (PAR-1 for penalty 1)."""
    return run["seconds"] if run["status"] == "optimal" else penalty * timeout


def sgm_by_solver(runs, timeout, shift=10.0, penalty=1):
    """{solver: shifted geometric mean of par_seconds over all its runs}."""
    by = {}
    for r in runs:
        by.setdefault(r["solver"], []).append(par_seconds(r, timeout, penalty))
    return {s: shifted_geometric_mean(v, shift) for s, v in by.items()}


# ---------------------------------------------------------------- step 4 ---

def _problems(runs):
    """{(instance, seed): {solver: run}}."""
    table = {}
    for r in runs:
        table.setdefault((r["instance"], r["seed"]), {})[r["solver"]] = r
    return table


def performance_profile(runs, taus):
    """Dolan and More. A problem is an (instance, seed) pair. Its ratio for a solver is seconds / (the fastest
    solved seconds among solvers on that problem), or infinity if that solver didn't solve it; a problem no
    solver solved gives infinity to everyone. Returns {solver: [fraction of problems with ratio <= tau, for tau
    in taus]}."""
    table = _problems(runs)
    solvers = sorted({r["solver"] for r in runs})
    ratios = {s: [] for s in solvers}
    for by_solver in table.values():
        solved = [r["seconds"] for r in by_solver.values() if r["status"] == "optimal"]
        best = min(solved) if solved else None
        for s in solvers:
            r = by_solver.get(s)
            if r is None or r["status"] != "optimal" or best is None:
                ratios[s].append(math.inf)
            else:
                ratios[s].append(r["seconds"] / best if best > 0 else (1.0 if r["seconds"] == 0 else math.inf))
    return {s: [sum(1 for q in ratios[s] if q <= tau) / len(ratios[s]) for tau in taus] for s in solvers}


def virtual_best(runs):
    """{(instance, seed): (solver, seconds)} for the fastest solved run on each problem (ties: solver name
    order), or (None, None) if nobody solved it."""
    out = {}
    for key, by_solver in _problems(runs).items():
        solved = sorted((r["seconds"], s) for s, r in by_solver.items() if r["status"] == "optimal")
        out[key] = (solved[0][1], solved[0][0]) if solved else (None, None)
    return out


# ---------------------------------------------------------------- step 5 ---

def bootstrap_ci(values, statistic, rng, level=0.95, resamples=2000):
    """Percentile bootstrap: `resamples` resamples of len(values) drawn with rng.choices, the statistic of each,
    sorted; return (the ((1 - level) / 2)-quantile, the ((1 + level) / 2)-quantile), each taken as the element at
    index floor(q * (resamples - 1))."""
    stats = sorted(statistic(rng.choices(values, k=len(values))) for _ in range(resamples))
    lo = stats[math.floor((1 - level) / 2 * (resamples - 1))]
    hi = stats[math.floor((1 + level) / 2 * (resamples - 1))]
    return lo, hi


def geometric_ratio_ci(a, b, rng, shift=10.0, level=0.95, resamples=2000):
    """Paired a[i] against b[i] (e.g. two solvers' times on the same problems): the ratio of shifted geometric
    means is exp(mean(log((a_i + shift) / (b_i + shift)))). Returns (ratio, (low, high)) with the interval from
    bootstrap_ci on the per-problem log ratios, exponentiated."""
    logs = [math.log((x + shift) / (y + shift)) for x, y in zip(a, b)]
    mean = lambda v: sum(v) / len(v)
    lo, hi = bootstrap_ci(logs, mean, rng, level, resamples)
    return math.exp(mean(logs)), (math.exp(lo), math.exp(hi))


# ---------------------------------------------------------------- step 6 ---

def holm(pvalues):
    """Holm-Bonferroni adjusted p-values, in the original order: sort ascending, multiply the k-th smallest (k = 1..m)
    by (m - k + 1), take running maxima, cap at 1."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adjusted = [0.0] * m
    running = 0.0
    for k, i in enumerate(order):
        running = max(running, min(1.0, (m - k) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def wilcoxon_signed_rank(a, b):
    """Paired two-sided Wilcoxon signed-rank test, normal approximation with tie and continuity corrections; zero
    differences are dropped. Returns (T, p) with T the smaller of the positive and negative rank sums."""
    d = [x - y for x, y in zip(a, b) if x != y]
    n = len(d)
    if n == 0:
        return 0.0, 1.0
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    tie_term = 0.0
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        t = j - i + 1
        tie_term += t ** 3 - t
        i = j + 1
    plus = sum(r for r, x in zip(ranks, d) if x > 0)
    minus = sum(r for r, x in zip(ranks, d) if x < 0)
    T = min(plus, minus)
    mu = n * (n + 1) / 4
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24 - tie_term / 48)
    if sigma == 0:
        return T, 1.0
    z = (abs(T - mu) - 0.5) / sigma
    return T, min(1.0, math.erfc(max(z, 0.0) / math.sqrt(2)))
