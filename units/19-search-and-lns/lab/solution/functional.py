"""Unit 19 lab — search, restarts and LNS.  REFERENCE SOLUTION, functional.

The engine's hooks are effectful by nature (on_failure is a callback), so DomWDeg keeps its
weights in a persistent map that it rebinds rather than mutates; everything else is folds
and unfolds: Luby by recursion, restarts as an unfold over (restart index, accumulated
stats), LNS as an unfold over (incumbent, trace).
"""

from __future__ import annotations

import math
import random

import toolz as tz

from colib.ref import unit

cp = unit("17")
gc = unit("18")


# ---------------------------------------------------------------- step 1 ---

def luby(i):
    k = next(k for k in range(1, 64) if (1 << k) - 1 >= i)
    return 1 << (k - 1) if i == (1 << k) - 1 else luby(i - (1 << (k - 1)) + 1)


def random_first_fail(rng):
    def choose(store, stats=None):
        sizes = [(len(d), v) for v, d in enumerate(store.dom) if len(d) > 1]
        if not sizes:
            return None
        smallest = min(sizes)[0]
        return rng.choice([v for s, v in sizes if s == smallest])
    return choose


def qcp_model(grid):
    n = len(grid)
    domains = [range(n) if grid[i][j] is None else [grid[i][j]] for i in range(n) for j in range(n)]
    props = [p for i in range(n) for a in range(n) for b in range(a + 1, n)
             for p in (cp.NotEqual(i * n + a, i * n + b), cp.NotEqual(a * n + i, b * n + i))]
    return domains, props


# ---------------------------------------------------------------- step 2 ---

class DomWDeg:
    def __init__(self, props, rng=None):
        self.weight = {id(p): 1 for p in props}
        self.on = tz.valmap(lambda pairs: [p for _, p in pairs], tz.groupby(0, [(v, p) for p in props for v in set(p.vars)]))
        self.rng = rng

    def on_failure(self, p):
        self.weight = tz.assoc(self.weight, id(p), self.weight.get(id(p), 1) + 1)

    def wdeg(self, store, v):
        return sum(self.weight[id(p)] for p in self.on.get(v, ())
                   if any(u != v and len(store.dom[u]) > 1 for u in p.vars))

    def choose(self, store, stats=None):
        scores = [(len(d) / w if (w := self.wdeg(store, v)) else math.inf, v)
                  for v, d in enumerate(store.dom) if len(d) > 1]
        if not scores:
            return None
        best = min(scores)[0]
        ties = [v for s, v in scores if abs(s - best) <= 1e-12 or s == best]
        return self.rng.choice(ties) if self.rng else ties[0]


# ---------------------------------------------------------------- step 3 ---

def solve_with_restarts(domains, props, choose, on_failure=None, base=32, max_restarts=10_000, node_budget=None):
    def step(state):
        r, total, _, _ = state
        limit = base * luby(r + 1) if node_budget is None else min(base * luby(r + 1), node_budget - total.nodes)
        if limit <= 0:
            return r, total, None, True
        sols, st = cp.solve(domains, props, choose=choose, node_limit=limit, on_failure=on_failure)
        total = cp.Stats(nodes=total.nodes + st.nodes, failures=total.failures + st.failures,
                         propagations=total.propagations + st.propagations, seconds=total.seconds + st.seconds,
                         extra={"restarts": r})
        done = bool(sols) or st.extra["complete"] or r + 1 >= max_restarts
        return r + 1, total, sols[0] if sols else None, done

    _, total, solution, _ = next(s for s in tz.iterate(step, (0, cp.Stats(), None, False)) if s[3])
    return solution, total


# ---------------------------------------------------------------- step 4 ---

def runtime_distribution(run, seeds):
    return sorted(((nodes, solved) for solved, nodes in map(run, seeds)), key=lambda t: t[0])


def summarise(samples):
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
    def dispatch(state, jk):
        starts, job_ready, machine_ready = state
        j, k = jk
        m, d = shop.jobs[j][k]
        t = max(job_ready.get(j, 0), machine_ready.get(m, 0))
        return {**starts, (j, k): t}, {**job_ready, j: t + d}, {**machine_ready, m: t + d}

    order = [(j, k) for k in range(max(len(job) for job in shop.jobs))
             for j, job in enumerate(shop.jobs) if k < len(job)]
    return tz.reduce(dispatch, order, ({}, {}, {}))[0]


def lns_jobshop(shop, horizon, iterations=100, relax=0.3, node_limit=200, seed=0):
    rng = random.Random(seed)
    domains, props, mk = gc.jobshop(shop, horizon, True)
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    machine = lambda op: shop.jobs[op[0]][op[1]][0]
    duration = lambda op: shop.jobs[op[0]][op[1]][1]
    greedy = greedy_schedule(shop)
    start = [greedy[op] for op in ops] + [schedule_makespan(shop, greedy)]
    if start[mk] > horizon:
        raise ValueError("horizon is below the greedy schedule's makespan")

    def neighbourhood(current, best, freed):
        kept = tz.groupby(lambda t: machine(t[2]),
                          sorted((current[v], v, op) for v, op in enumerate(ops) if op[0] not in freed))
        chain = [cp.LinearLe([a, b], [1, -1], -duration(opa))
                 for m in sorted(kept) for (_, a, opa), (_, b, _) in zip(kept[m], kept[m][1:])]
        return [cp.LinearLe([mk], [1], best - 1)] + chain

    def step(state):
        it, current, trace = state
        freed = set(rng.sample(range(len(shop.jobs)), max(1, round(relax * len(shop.jobs)))))
        sols, _ = cp.solve(domains, props + neighbourhood(current, current[mk], freed), node_limit=node_limit)
        return (it + 1, sols[0], trace + [(it + 1, sols[0][mk])]) if sols else (it + 1, current, trace)

    _, current, trace = tz.nth(iterations, tz.iterate(step, (0, start, [(0, start[mk])])))
    return current[mk], {op: current[v] for v, op in enumerate(ops)}, trace
