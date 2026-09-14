"""Unit 12's recorded Benders runs, for units/12-benders/explore.html.

Every recourse value, dual, cut and master solution comes from unit 12's reference
`second_stage`, `optimality_cut`, `feasibility_cut` and `solve_master`, driven in the same
multi-cut loop as the reference `benders`, but logging what the master believes about every
first-stage choice at each iteration. `uv run co viz 12` writes units/12-benders/viz-data.js.
"""

from __future__ import annotations

import itertools

from colib import ref
from colib.colgen import StochasticFacility

L = ref.unit("12")
INF = float("inf")


def run(inst, max_iter=20):
    F, S = inst.F, inst.S
    choices = [list(y) for y in itertools.product((0, 1), repeat=F)]
    true = {}
    for y in choices:
        qs = [L.second_stage(inst, s, y)[0] for s in range(S)]
        opening = sum(f * v for f, v in zip(inst.open_cost, y))
        true[tuple(y)] = None if any(q == INF for q in qs) else opening + sum(p * q for p, q in zip(inst.prob, qs))
    opt_cuts, feas_cuts, states, best = [], [], [], INF
    for it in range(max_iter):
        lower, ybar, theta = L.solve_master(inst, opt_cuts, feas_cuts, multicut=True)
        # what the master believes each choice costs, with the cuts it has now
        belief = []
        for y in choices:
            excluded = any(c0 + sum(ci * yi for ci, yi in zip(cf, y)) > 1e-9 for c0, cf in feas_cuts)
            th = [max([0.0] + [c0 + sum(ci * yi for ci, yi in zip(cf, y)) for s2, c0, cf in opt_cuts if s2 == s]) for s in range(S)]
            est = sum(f * v for f, v in zip(inst.open_cost, y)) + sum(p * t for p, t in zip(inst.prob, th))
            belief.append({"y": y, "estimate": None if excluded else est, "true": true[tuple(y)]})
        new_opt, new_feas, recourse, feasible = [], [], [], True
        for s in range(S):
            q, v, alpha = L.second_stage(inst, s, ybar)
            if q == INF:
                cut = L.feasibility_cut(inst, s, ybar)
                new_feas.append({"s": s, "const": cut[0], "coef": cut[1]})
                feasible = False
                continue
            recourse.append(q)
            c0, cf = L.optimality_cut(inst, s, v, alpha)
            if theta[s] < q - 1e-7:
                new_opt.append({"s": s, "const": c0, "coef": cf, "duals": {"v": v, "alpha": alpha}})
        upper = INF
        if feasible:
            upper = sum(f * v for f, v in zip(inst.open_cost, ybar)) + sum(p * q for p, q in zip(inst.prob, recourse))
            best = min(best, upper)
        states.append({"master_y": ybar, "lower": lower, "theta": theta, "upper": upper if upper < INF else None,
                       "best": best if best < INF else None, "recourse": recourse if feasible else None,
                       "belief": belief, "new_opt": new_opt, "new_feas": new_feas})
        if best < INF and best - lower <= 1e-6:
            break
        opt_cuts += [(c["s"], c["const"], c["coef"]) for c in new_opt]
        feas_cuts += [(c["const"], c["coef"]) for c in new_feas]
    return states


def data():
    common = dict(open_cost=(10, 6), capacity=(5, 5), cost=((1,), (3,)), demand=((4,), (8,)), prob=(0.5, 0.5))
    with_penalty = StochasticFacility(**common, penalty=10.0)
    no_penalty = StochasticFacility(**common, penalty=None)
    three = StochasticFacility.random(3, 4, 2, seed=0, capacity_ratio=3.0)
    return {
        "runs": [
            {"title": "The deck's example: unmet demand costs 10", "facilities": ["A", "B"], "states": run(with_penalty)},
            {"title": "Same, but all demand must be met (feasibility cuts)", "facilities": ["A", "B"], "states": run(no_penalty)},
            {"title": "3 facilities, 4 customers, 2 scenarios, loose capacities (random, seed 0)",
             "facilities": ["A", "B", "C"], "states": run(three)},
        ],
    }
