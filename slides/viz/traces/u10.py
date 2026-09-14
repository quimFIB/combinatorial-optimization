"""Unit 10's recorded column-generation runs, for units/10-column-generation/explore.html.

Every master value, dual, pricing pattern and Farley bound comes from unit 10's reference
`initial_patterns`, `solve_master`, `price`, `farley_bound` and
`stabilised_column_generation`. `uv run co viz 10` writes units/10-column-generation/viz-data.js.
"""

from __future__ import annotations

from colib import ref
from colib.colgen import CuttingStock

L = ref.unit("10")


def small_run(W, widths, demands):
    """One state per iteration: the restricted master, its duals, and what pricing returns."""
    patterns = L.initial_patterns(W, widths)
    states, best = [], 0.0
    for _ in range(50):
        value, x, duals = L.solve_master(patterns, demands)
        pv, pattern = L.price(W, widths, duals)
        farley = L.farley_bound(demands, duals, pv)
        best = max(best, farley)
        rc = 1 - pv
        done = rc >= -1e-9
        states.append({
            "patterns": [list(p) for p in patterns], "x": [float(v) for v in x],
            "duals": [float(y) for y in duals], "value": float(value),
            "pricing": list(pattern), "price_value": float(pv), "reduced_cost": float(rc),
            "farley": float(farley), "best": float(best), "done": done,
        })
        if done:
            break
        patterns = patterns + [pattern]
    return states


def smoothing_runs(inst, alphas=(0.0, 0.5, 0.8)):
    out = []
    for a in alphas:
        value, _, _, history = L.stabilised_column_generation(inst.W, inst.widths, inst.demands, alpha=a)
        out.append({"alpha": a, "value": float(value),
                    "master": [float(h[0]) for h in history], "bound": [float(h[1]) for h in history]})
    return out


def data():
    W, widths, demands = 10, [3, 4, 6], [5, 3, 2]
    big = CuttingStock.random(25, seed=25, W=10000, low=0.01, high=0.2, demand=(10, 100))
    return {
        "small": {"title": "Rolls of 10, pieces 3, 4, 6, demands 5, 3, 2", "W": W, "widths": widths,
                  "demands": demands, "states": small_run(W, widths, demands)},
        "smoothing": {"title": f"25 piece widths, rolls of {big.W} (CuttingStock.random(25, seed=25))",
                      "runs": smoothing_runs(big)},
    }
