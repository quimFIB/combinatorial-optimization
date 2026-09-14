"""Unit 09's recorded Stoer–Wagner runs, for units/09-separation-optimization/explore.html.

The loop of the reference min_cut is copied here with a record of every step of every
phase (who is added, with what attachment) and every merge; the result is checked against
the reference min_cut itself. `co viz 09` writes units/09-separation-optimization/viz-data.js.
"""

from __future__ import annotations

from colib import ref
from colib.tsp import edges

L = ref.unit("09")

FOUR = {"n": 4, "weights": {(0, 1): 3, (0, 2): 1, (1, 2): 1, (1, 3): 1, (2, 3): 3},
        "pos": [[90, 90], [90, 290], [330, 90], [330, 290]]}
SIX = {"n": 6, "weights": {(0, 1): 1, (1, 2): 1, (0, 2): 0.5, (3, 4): 1, (4, 5): 1, (3, 5): 0.5, (0, 3): 0.5, (2, 5): 0.5},
       "pos": [[90, 80], [40, 200], [150, 320], [370, 80], [420, 200], [310, 320]]}


def trace(inst):
    n = inst["n"]
    x = [inst["weights"].get(e, 0) for e in edges(n)]
    w = [[0.0] * n for _ in range(n)]
    for (i, j), v in zip(edges(n), x):
        w[i][j] = w[j][i] = v
    groups = [[v] for v in range(n)]
    active = list(range(n))
    best_val, best_set = float("inf"), None
    states = [{"groups": [list(groups[v]) for v in active], "order": [], "attach": {}, "phase": 0,
               "best": None, "note": "every vertex is its own group; phase 1 starts from the lowest-numbered one"}]
    phase = 0
    while len(active) > 1:
        phase += 1
        weights = {v: 0.0 for v in active}
        order = []
        remaining = set(active)
        while remaining:
            u = max(remaining, key=lambda v: (weights[v], -v))
            added_with = weights[u]
            order.append(u)
            remaining.remove(u)
            for v in remaining:
                weights[v] += w[u][v]
            label = "+".join(map(str, sorted(groups[u])))
            states.append({
                "groups": [list(groups[v]) for v in active], "phase": phase,
                "order": [sorted(groups[v]) for v in order],
                "attach": {"+".join(map(str, sorted(groups[v]))): weights[v] for v in remaining},
                "best": None if best_val == float("inf") else [best_val, list(best_set)],
                "note": (f"phase {phase}: start with {{{label}}}" if len(order) == 1 else
                         f"phase {phase}: add {{{label}}}, the most attached (weight {added_with:g})"),
            })
        s, t = order[-2], order[-1]
        cut = weights[t]
        improved = cut < best_val
        if improved:
            best_val, best_set = cut, sorted(groups[t])
        states[-1]["cut"] = [sorted(groups[t]), cut]
        states[-1]["best"] = [best_val, list(best_set)]
        states[-1]["note"] += (f"; cut of the phase: {{{','.join(map(str, sorted(groups[t])))}}} alone, weight {cut:g}"
                               + (" (best so far)" if improved else ""))
        merged = sorted(groups[s] + groups[t])
        groups[s] += groups[t]
        for v in active:
            w[s][v] += w[t][v]
            w[v][s] = w[s][v]
        w[s][s] = 0.0
        active.remove(t)
        states.append({"groups": [sorted(groups[v]) for v in active], "order": [], "attach": {}, "phase": phase,
                       "best": [best_val, list(best_set)], "merged": merged,
                       "note": f"merge the last two, into {{{','.join(map(str, merged))}}}"})
    ref_val, ref_set = L.min_cut(n, x)
    assert abs(ref_val - best_val) < 1e-9 and sorted(ref_set) == sorted(best_set), (ref_val, ref_set, best_val, best_set)
    states[-1]["note"] = f"one group left: the minimum cut is {{{','.join(map(str, best_set))}}}, weight {best_val:g}" + (
        ", below 2, so a subtour row is violated" if best_val < 2 - 1e-9 and n == 6 else "")
    return {"n": n, "pos": inst["pos"], "edges": [[i, j, v] for (i, j), v in zip(edges(n), x) if v > 0], "states": states}


def data():
    return {"four": {"title": "four vertices (the deck's Stoer–Wagner example)", **trace(FOUR)},
            "six": {"title": "six cities: the fractional point with a thin connection", **trace(SIX)}}
