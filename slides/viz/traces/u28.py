"""Unit 28's recorded summaries, for units/28-experimental-method/explore.html.

Performance profiles: the reference `performance_profile` and `virtual_best`, on the slides' three
solvers and four instances, for every non-empty subset of solvers, at every ratio where some
curve can step. Bootstrap: the resample means drawn exactly as the reference `bootstrap_ci`
draws them (`rng.choices`, seed 1), and for each resample count its interval from
`bootstrap_ci` itself, checked against the recorded means.
`uv run co viz 28` writes units/28-experimental-method/viz-data.js.
"""

from __future__ import annotations

import math
import random
from itertools import combinations

from colib import ref

L = ref.unit("28")

TIMES = {  # seconds per instance, None = failed ("—" on the slide)
    "X": [2, 10, 1, None],
    "Y": [4, 5, 1, 8],
    "Z": [3, None, 2, 4],
}
INSTANCES = ["p1", "p2", "p3", "p4"]


def _runs(solvers):
    return [{"instance": inst, "seed": 0, "solver": s,
             "seconds": float(TIMES[s][i]) if TIMES[s][i] is not None else 20.0,
             "status": "optimal" if TIMES[s][i] is not None else "timeout"}
            for s in solvers for i, inst in enumerate(INSTANCES)]


def profiles():
    all_ratios = set()
    subsets = [c for k in (1, 2, 3) for c in combinations(sorted(TIMES), k)]
    best = {}
    for sub in subsets:
        vb = L.virtual_best(_runs(sub))
        best[sub] = {inst: vb[(inst, 0)] for inst in INSTANCES}
        for s in sub:
            for i, inst in enumerate(INSTANCES):
                t, b = TIMES[s][i], best[sub][inst][1]
                if t is not None and b:
                    all_ratios.add(t / b)
    taus = sorted(all_ratios | {1.0}) + [4.0]
    out = {"solvers": sorted(TIMES), "instances": INSTANCES, "times": TIMES, "taus": taus, "subsets": {}}
    for sub in subsets:
        prof = L.performance_profile(_runs(sub), taus)
        ratios = {s: [None if TIMES[s][i] is None else TIMES[s][i] / best[sub][inst][1] for i, inst in enumerate(INSTANCES)]
                  for s in sub}
        out["subsets"]["".join(sub)] = {
            "profile": prof, "ratios": ratios,
            "best": {inst: {"solver": best[sub][inst][0], "seconds": best[sub][inst][1]} for inst in INSTANCES},
        }
    return out


def bootstrap(values=(0.6, 0.8, 0.9, 1.1, 0.7), seed=1, most=2000):
    values = list(values)
    mean = lambda v: sum(v) / len(v)
    rng = random.Random(seed)
    resamples = [rng.choices(values, k=len(values)) for _ in range(most)]
    means = [mean(r) for r in resamples]
    counts = [5, 10, 20, 50, 100, 200, 500, 1000, 2000]
    intervals = {}
    for n in counts:
        lo, hi = L.bootstrap_ci(values, mean, random.Random(seed), level=0.95, resamples=n)
        s = sorted(means[:n])
        assert (s[math.floor(0.025 * (n - 1))], s[math.floor(0.975 * (n - 1))]) == (lo, hi)
        intervals[str(n)] = [lo, hi]
    return {"values": values, "mean": mean(values), "seed": seed, "counts": counts,
            "means": [round(m, 6) for m in means], "first": resamples[:8], "intervals": intervals}


def data():
    return {"profile": profiles(), "bootstrap": bootstrap()}
