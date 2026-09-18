"""Unit 28 lab — experimental method.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 28
after each. Read README.md first; HINTS.org has a ladder of hints per step.

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
    raise NotImplementedError  # TODO step 1


def save_run(conn, run):
    """Insert a run dict (all FIELDS; value and nodes may be None), replacing any run with the same key."""
    raise NotImplementedError  # TODO step 1


def load_runs(conn, experiment, solver=None):
    """Runs of one experiment (and optionally one solver) as dicts, ordered by solver, instance, seed."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def run_benchmark(conn, experiment, solvers, instances, seeds, timeout, clock=time.perf_counter):
    """For each instance (in dict order), each solver (in dict order) and each seed: skip it if the store already
    has that run; otherwise time solver(instance_data, seed, timeout) with `clock`, which returns a dict with
    "status" and optionally "value" and "nodes". If it took longer than timeout, record status "timeout" and
    seconds = timeout; otherwise record what it returned and the measured seconds. Returns the number of runs
    performed (not skipped)."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def shifted_geometric_mean(values, shift=10.0):
    """exp(mean(log(v + shift))) - shift."""
    raise NotImplementedError  # TODO step 3


def par_seconds(run, timeout, penalty=1):
    """Penalised run time: the measured seconds if solved, penalty * timeout otherwise (PAR-1 for penalty 1)."""
    raise NotImplementedError  # TODO step 3


def sgm_by_solver(runs, timeout, shift=10.0, penalty=1):
    """{solver: shifted geometric mean of par_seconds over all its runs}."""
    raise NotImplementedError  # TODO step 3


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
    raise NotImplementedError  # TODO step 4


def virtual_best(runs):
    """{(instance, seed): (solver, seconds)} for the fastest solved run on each problem (ties: solver name
    order), or (None, None) if nobody solved it."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def bootstrap_ci(values, statistic, rng, level=0.95, resamples=2000):
    """Percentile bootstrap: `resamples` resamples of len(values) drawn with rng.choices, the statistic of each,
    sorted; return (the ((1 - level) / 2)-quantile, the ((1 + level) / 2)-quantile), each taken as the element at
    index floor(q * (resamples - 1))."""
    raise NotImplementedError  # TODO step 5


def geometric_ratio_ci(a, b, rng, shift=10.0, level=0.95, resamples=2000):
    """Paired a[i] against b[i] (e.g. two solvers' times on the same problems): the ratio of shifted geometric
    means is exp(mean(log((a_i + shift) / (b_i + shift)))). Returns (ratio, (low, high)) with the interval from
    bootstrap_ci on the per-problem log ratios, exponentiated."""
    raise NotImplementedError  # TODO step 5


# ---------------------------------------------------------------- step 6 ---

def holm(pvalues):
    """Holm-Bonferroni adjusted p-values, in the original order: sort ascending, multiply the k-th smallest (k = 1..m)
    by (m - k + 1), take running maxima, cap at 1."""
    raise NotImplementedError  # TODO step 6


def wilcoxon_signed_rank(a, b):
    """Paired two-sided Wilcoxon signed-rank test, normal approximation with tie and continuity corrections; zero
    differences are dropped. Returns (T, p) with T the smaller of the positive and negative rank sums."""
    raise NotImplementedError  # TODO step 6
