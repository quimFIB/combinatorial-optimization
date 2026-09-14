"""Unit 19 lab — search, restarts and large neighbourhood search.

Fill in the parts marked TODO, one step at a time, and run
    uv run co test 19
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Everything plugs into unit 17's engine (`cp`) through its hooks:
    cp.solve(domains, props, choose=..., node_limit=..., on_failure=...)
`choose(store, stats)` returns the next variable to branch on, or None when all are fixed;
`on_failure(p)` is called with each propagator that fails. Unit 18's job-shop model is `gc`.
With CO_MINE=17,18 these are your own.
"""

from __future__ import annotations

import math
import random

from colib.problems import JobShop
from colib.ref import unit

cp = unit("17")
gc = unit("18")


# ---------------------------------------------------------------- step 1 ---

def luby(i):
    """The i-th term (i >= 1) of the Luby sequence 1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, ...:
    if i = 2^k - 1 it is 2^(k-1); otherwise it is luby(i - 2^(k-1) + 1) for the k with
    2^(k-1) <= i < 2^k - 1."""
    raise NotImplementedError  # TODO step 1


def random_first_fail(rng):
    """Return a choose(store, stats=None) function: the unfixed variable with the smallest domain,
    ties broken by rng.choice over the tied variables in increasing index order. None if all fixed."""
    raise NotImplementedError  # TODO step 1


def qcp_model(grid):
    """Quasigroup completion: grid is n x n with None for blanks. Variable i * n + j over range(n)
    (or the given value). One cp.NotEqual per pair of cells in the same row, and per pair in the
    same column. Returns (domains, props)."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

class DomWDeg:
    """The dom/wdeg heuristic. Every propagator starts with weight 1 and gains 1 each time it fails
    (on_failure). wdeg(store, v) sums the weights of the propagators on v that still have another
    unfixed variable. choose picks the unfixed variable with the smallest |D(v)| / wdeg(v) (a
    variable with wdeg 0 scores infinity); ties go to rng.choice in index order, or to the lowest
    index when rng is None. Weights persist for the life of the object."""

    def __init__(self, props, rng=None):
        raise NotImplementedError  # TODO step 2

    def on_failure(self, p):
        raise NotImplementedError  # TODO step 2

    def wdeg(self, store, v):
        raise NotImplementedError  # TODO step 2

    def choose(self, store, stats=None):
        raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def solve_with_restarts(domains, props, choose, on_failure=None, base=32, max_restarts=10_000, node_budget=None):
    """Search r = 0, 1, 2, ... with node_limit base * luby(r + 1), capped so the total never exceeds
    node_budget (stop when no budget is left). Pass `choose` and `on_failure` to every search.
    Stop at the first solution, when a search completes without one (infeasible), or after
    max_restarts searches.
    Returns (solution or None, cp.Stats) with nodes, failures, propagations and seconds summed, and
    stats.extra['restarts'] = the index r of the last search run."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def runtime_distribution(run, seeds):
    """run(seed) -> (solved, nodes). Returns [(nodes, solved), ...] over the seeds, sorted by nodes."""
    raise NotImplementedError  # TODO step 4


def summarise(samples):
    """For samples [(nodes, solved), ...]: a dict with
      n: how many; solved: the fraction solved; mean, median, max of nodes;
      p90: the nearest-rank 90th percentile (the ceil(0.9 n)-th smallest);
      tail: p90 / median (infinity if the median is 0).
    The median of an even count is the average of the two middle values."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def schedule_makespan(shop: JobShop, starts):
    return max(starts[(j, len(job) - 1)] + job[-1][1] for j, job in enumerate(shop.jobs))


def greedy_schedule(shop: JobShop):
    """Round-robin dispatch: repeatedly go through the jobs in order, scheduling each job's next
    operation (if any) at max(the job's ready time, its machine's ready time). Returns {(j, k): start}."""
    raise NotImplementedError  # TODO step 5


def lns_jobshop(shop: JobShop, horizon, iterations=100, relax=0.3, node_limit=200, seed=0):
    """Large neighbourhood search for job-shop makespan, using gc.jobshop(shop, horizon, True).

    The incumbent starts as greedy_schedule (values for every operation variable, then the makespan
    variable). With rng = random.Random(seed), each iteration:
      * freed = set(rng.sample(range(number of jobs), max(1, round(relax * number of jobs))));
      * for each machine m, take the operations on m of jobs not in freed, sorted by their incumbent
        start, and add cp.LinearLe([a, b], [1, -1], -duration(a)) for each consecutive pair;
      * add cp.LinearLe([makespan], [1], best - 1);
      * cp.solve with node_limit; a solution becomes the new incumbent.
    Returns (best makespan, {(j, k): start}, trace), where trace = [(0, greedy makespan)] plus
    (iteration, makespan) for each improvement."""
    raise NotImplementedError  # TODO step 5
