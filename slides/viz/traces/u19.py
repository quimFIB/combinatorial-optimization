"""Unit 19's recorded data, for units/19-search-and-lns/explore.html.

Luby: the reference `luby(i)` for i = 1..127. LNS: the loop of the reference `lns_jobshop`
(same random choices, same model from unit 18, same `solve` from unit 17) replayed with a
snapshot per iteration; each run is checked to end at the reference function's own result.
`uv run co viz 19` writes units/19-search-and-lns/viz-data.js.
"""

from __future__ import annotations

import random

from colib import ref
from colib.problems import JobShop

S = ref.unit("19")
cp, gc = ref.unit("17"), ref.unit("18")


def lns_run(title, shop, horizon, iterations, relax, node_limit, seed):
    rng = random.Random(seed)
    domains, props, mk = gc.jobshop(shop, horizon, True)
    ops = [(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))]
    greedy = S.greedy_schedule(shop)
    current = [greedy[op] for op in ops] + [S.schedule_makespan(shop, greedy)]
    best = current[mk]
    n_jobs = len(shop.jobs)

    def schedule(cur):
        return [[j, k, shop.jobs[j][k][0], cur[v], shop.jobs[j][k][1]] for v, (j, k) in enumerate(ops)]

    states = [{"it": 0, "ops": schedule(current), "makespan": best, "freed": [], "trace": [best],
               "note": f"greedy dispatch: makespan {best}",
               "explain": "Round-robin over the jobs, each operation as early as its job and machine allow. That is the starting incumbent."}]
    history = [best]
    for it in range(1, iterations + 1):
        freed = sorted(rng.sample(range(n_jobs), max(1, round(relax * n_jobs))))
        extra = [cp.LinearLe([mk], [1], best - 1)]
        for m in range(shop.machines):
            kept = sorted((current[v], v, op) for v, op in enumerate(ops)
                          if shop.jobs[op[0]][op[1]][0] == m and op[0] not in freed)
            for (_, a, opa), (_, b, _) in zip(kept, kept[1:]):
                extra.append(cp.LinearLe([a, b], [1, -1], -shop.jobs[opa[0]][opa[1]][1]))
        sols, _ = cp.solve(domains, props + extra, node_limit=node_limit)
        jobs = ", ".join(f"J{j}" for j in freed)
        if sols:
            old = best
            current = sols[0]
            best = current[mk]
            history.append(best)
            states.append({"it": it, "ops": schedule(current), "makespan": best, "freed": freed, "trace": list(history),
                           "note": f"iteration {it}: free {jobs}, repair: makespan {old} → {best}",
                           "explain": f"The other jobs keep their order on every machine; the solver re-places {jobs} with makespan at most {old - 1} and finds {best}."})
        else:
            history.append(best)
            states.append({"it": it, "ops": schedule(current), "makespan": best, "freed": freed, "trace": list(history),
                           "note": f"iteration {it}: free {jobs}, no better repair within {node_limit} nodes",
                           "explain": f"Keeping the other jobs' machine orders, no schedule with makespan ≤ {best - 1} was found. The incumbent stays."})
    ref_best, ref_starts, _ = S.lns_jobshop(shop, horizon, iterations=iterations, relax=relax, node_limit=node_limit, seed=seed)
    assert ref_best == best and all(ref_starts[op] == current[v] for v, op in enumerate(ops)), title
    return {"title": title, "jobs": [list(map(list, job)) for job in shop.jobs], "machines": shop.machines, "states": states}


def data():
    deck = JobShop((((1, 5), (0, 2), (2, 4)), ((2, 3), (0, 2), (1, 2)), ((0, 1), (2, 4), (1, 5))))
    big = JobShop.random(6, seed=3, machines=4)
    return {
        "luby": [S.luby(i) for i in range(1, 128)],
        "lns-deck": lns_run("the deck's 3 × 3 shop", deck,
                            sum(d for job in deck.jobs for _, d in job), iterations=2, relax=0.34, node_limit=200, seed=0),
        "lns-6x4": lns_run("a random 6 × 4 shop", big,
                           sum(d for job in big.jobs for _, d in job), iterations=10, relax=0.3, node_limit=150, seed=0),
    }
