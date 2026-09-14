"""Unit 19 lab — search, restarts and large neighbourhood search.  REFERENCE SOLUTION, imperative.

Everything here plugs into unit 17's engine through its two hooks:
    cp.solve(domains, props, choose=..., node_limit=..., on_failure=...)
`choose(store, stats)` picks the next variable (None when all are fixed); `on_failure(p)`
is called with the propagator that failed. Unit 18's job-shop model is reused for LNS.
"""

from __future__ import annotations

import math
import random

from colib.ref import unit

cp = unit("17")
gc = unit("18")


# ---------------------------------------------------------------- step 1 ---

def luby(i):
    """The i-th term (i >= 1) of the Luby sequence 1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, ..."""
    k = 1
    while (1 << k) - 1 < i:
        k += 1
    while True:
        if i == (1 << k) - 1:
            return 1 << (k - 1)
        i -= (1 << (k - 1)) - 1
        k = 1
        while (1 << k) - 1 < i:
            k += 1


def random_first_fail(rng):
    """First-fail with ties broken uniformly at random by `rng`."""
    def choose(store, stats=None):
        best, ties = None, []
        for v, d in enumerate(store.dom):
            size = len(d)
            if size > 1:
                if best is None or size < best:
                    best, ties = size, [v]
                elif size == best:
                    ties.append(v)
        return rng.choice(ties) if ties else None
    return choose


def qcp_model(grid):
    """Quasigroup completion as pairwise != on rows and columns. Variable i * n + j; None is blank."""
    n = len(grid)
    domains = [range(n) if grid[i][j] is None else [grid[i][j]] for i in range(n) for j in range(n)]
    props = []
    for i in range(n):
        for a in range(n):
            for b in range(a + 1, n):
                props.append(cp.NotEqual(i * n + a, i * n + b))
                props.append(cp.NotEqual(a * n + i, b * n + i))
    return domains, props


# ---------------------------------------------------------------- step 2 ---

class DomWDeg:
    """dom/wdeg (Boussemart, Hemery, Lecoutre & Sais 2004). Every propagator starts with weight 1
    and gains 1 each time it fails. Choose the unfixed variable minimising
    |D(x)| / (sum of weights of propagators on x with at least one other unfixed variable),
    ties broken by `rng` (or lowest index when rng is None). Weights persist across searches."""

    def __init__(self, props, rng=None):
        self.weight = {id(p): 1 for p in props}
        self.on = {}
        for p in props:
            for v in set(p.vars):
                self.on.setdefault(v, []).append(p)
        self.rng = rng

    def on_failure(self, p):
        self.weight[id(p)] = self.weight.get(id(p), 1) + 1

    def wdeg(self, store, v):
        return sum(self.weight[id(p)] for p in self.on.get(v, ())
                   if any(u != v and len(store.dom[u]) > 1 for u in p.vars))

    def choose(self, store, stats=None):
        best, ties = None, []
        for v, d in enumerate(store.dom):
            if len(d) > 1:
                w = self.wdeg(store, v)
                score = len(d) / w if w else math.inf
                if best is None or score < best - 1e-12:
                    best, ties = score, [v]
                elif score == best or abs(score - best) <= 1e-12:
                    ties.append(v)
        if not ties:
            return None
        return self.rng.choice(ties) if self.rng else ties[0]


# ---------------------------------------------------------------- step 3 ---

def solve_with_restarts(domains, props, choose, on_failure=None, base=32, max_restarts=10_000, node_budget=None):
    """Restart search with node limits base * luby(1), base * luby(2), ... until a solution is found,
    max_restarts is reached, or the total nodes would exceed node_budget. `choose` and
    `on_failure` are passed to every search (so a DomWDeg keeps learning, and a randomised
    heuristic makes different choices each time).
    Returns (solution or None, stats): stats.nodes, .failures and .propagations summed over all
    searches, stats.extra['restarts'] = searches started minus one."""
    total = cp.Stats()
    for r in range(max_restarts):
        limit = base * luby(r + 1)
        if node_budget is not None:
            limit = min(limit, node_budget - total.nodes)
            if limit <= 0:
                break
        sols, st = cp.solve(domains, props, choose=choose, node_limit=limit, on_failure=on_failure)
        total.nodes += st.nodes
        total.failures += st.failures
        total.propagations += st.propagations
        total.seconds += st.seconds
        total.extra["restarts"] = r
        if sols:
            return sols[0], total
        if st.extra["complete"]:                             # proved infeasible
            break
    return None, total


# ---------------------------------------------------------------- step 4 ---

def runtime_distribution(run, seeds):
    """Call run(seed) -> (solved, nodes) for each seed. Returns a list of (nodes, solved), sorted by nodes."""
    return sorted(((nodes, solved) for solved, nodes in map(run, seeds)), key=lambda t: t[0])


def summarise(samples):
    """Summary of a runtime distribution: dict with n, solved (fraction), mean, median, p90 and max
    of the node counts (unsolved runs count at the nodes they used), and tail = p90 / median."""
    nodes = sorted(n for n, _ in samples)
    k = len(nodes)
    median = nodes[(k - 1) // 2] if k % 2 else (nodes[k // 2 - 1] + nodes[k // 2]) / 2
    p90 = nodes[min(k - 1, math.ceil(0.9 * k) - 1)]
    return {"n": k, "solved": sum(1 for _, s in samples if s) / k, "mean": sum(nodes) / k,
            "median": median, "p90": p90, "max": nodes[-1], "tail": p90 / median if median else math.inf}


# ---------------------------------------------------------------- step 5 ---

def schedule_makespan(shop, starts):
    return max(starts[(j, len(job) - 1)] + job[-1][1] for j, job in enumerate(shop.jobs))


def greedy_schedule(shop):
    """A feasible schedule by round-robin dispatch: take the jobs' next operations in turn and start
    each as soon as both its job and its machine are free. Returns {(j, k): start}."""
    job_ready = [0] * len(shop.jobs)
    machine_ready = [0] * shop.machines
    next_op = [0] * len(shop.jobs)
    starts = {}
    remaining = sum(len(job) for job in shop.jobs)
    while remaining:
        for j, job in enumerate(shop.jobs):
            k = next_op[j]
            if k < len(job):
                m, d = job[k]
                t = max(job_ready[j], machine_ready[m])
                starts[(j, k)] = t
                job_ready[j] = machine_ready[m] = t + d
                next_op[j] += 1
                remaining -= 1
    return starts


def lns_jobshop(shop, horizon, iterations=100, relax=0.3, node_limit=200, seed=0):
    """Large neighbourhood search for job-shop makespan with unit 18's model.

    Start from greedy_schedule (horizon must be at least its makespan). Each iteration: choose a
    random `relax` fraction of the jobs (at least one); for every machine, keep the order that the
    current schedule gives to the operations of the *other* jobs, as precedences
    start(a) + duration(a) <= start(b) between consecutive kept operations; require makespan <=
    best - 1; search with node_limit. A solution found becomes the new incumbent.
    Returns (best makespan, starts dict {(j, k): start}, trace [(iteration, makespan)] starting
    with (0, greedy makespan))."""
    rng = random.Random(seed)
    domains, props, mk = gc.jobshop(shop, horizon, True)
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    greedy = greedy_schedule(shop)
    current = [greedy[op] for op in ops] + [schedule_makespan(shop, greedy)]
    best = current[mk]
    if best > horizon:
        raise ValueError("horizon is below the greedy schedule's makespan")
    trace = [(0, best)]
    n_jobs = len(shop.jobs)
    for it in range(1, iterations + 1):
        freed = set(rng.sample(range(n_jobs), max(1, round(relax * n_jobs))))
        extra = [cp.LinearLe([mk], [1], best - 1)]
        for m in range(shop.machines):
            kept = sorted((current[v], v, op) for v, op in enumerate(ops)
                          if shop.jobs[op[0]][op[1]][0] == m and op[0] not in freed)
            for (_, a, opa), (_, b, _) in zip(kept, kept[1:]):
                extra.append(cp.LinearLe([a, b], [1, -1], -shop.jobs[opa[0]][opa[1]][1]))
        sols, _ = cp.solve(domains, props + extra, node_limit=node_limit)
        if sols:
            current = sols[0]
            best = current[mk]
            trace.append((it, best))
    starts = {op: current[v] for v, op in enumerate(ops)}
    return best, starts, trace
