"""Unit 07's recorded branch-and-bound runs, for units/07-branch-and-bound/explore.html.

The running example of the deck, min -x - 5y with 7x + 3y <= 22 and -3x + 3y <= 2,
solved by the reference branch-and-bound's own pieces (colib.bb.solve_node, the reference
most_fractional and children), with the loop of the reference branch_and_bound copied
here so every pop can be recorded. `co viz 07` writes units/07-branch-and-bound/viz-data.js.
"""

from __future__ import annotations

import heapq
import math
from itertools import count

from colib import ref
from colib.bb import is_integral, solve_node
from colib.mip import MILP

L = ref.unit("07")

ROWS = [[7, 3, 22], [-3, 3, 2]]


def milp():
    return MILP(c=(-1.0, -5.0), A_ub=tuple((a, b) for a, b, _ in ROWS), b_ub=tuple(c for _, _, c in ROWS),
                ub=(10.0, 10.0), integer=(True, True), names=("x", "y"))


def run(selection):
    """Replay the reference loop; one state after the root and after every pop."""
    m = milp()
    lb, ub = (tuple(float(v) for v in b) for b in m.bounds())
    root = solve_node(m, lb, ub)
    nodes = [{"id": 0, "parent": None, "branch": "root", "lb": list(lb), "ub": list(ub),
              "value": root.value, "x": list(root.x), "status": "open"}]
    incumbent, best_x = math.inf, None
    tie = count()
    frontier = [(root.value, next(tie), 0)]
    states = []

    def snap(note, current=None):
        open_bounds = [nodes[i]["value"] for _, _, i in frontier]
        lower = min(open_bounds + ([incumbent] if incumbent < math.inf else [])) if (open_bounds or incumbent < math.inf) else None
        states.append({
            "nodes": [dict(n) for n in nodes], "current": current,
            "incumbent": None if incumbent == math.inf else incumbent,
            "incumbent_x": best_x, "lower": lower,
            "frontier": [i for _, _, i in (sorted(frontier) if selection == "best" else frontier)],
            "note": note,
        })

    snap(f"root LP: ({root.x[0]:.2f}, {root.x[1]:.2f}), value {root.value:.2f}")
    while frontier:
        _, _, i = heapq.heappop(frontier) if selection == "best" else frontier.pop()
        node = nodes[i]
        if node["value"] >= incumbent - 1e-9:
            node["status"] = "pruned by bound"
            snap(f"node {i}: bound {node['value']:.2f} ≥ incumbent {incumbent:.2f}, pruned", i)
            continue
        if is_integral(m, node["x"]):
            incumbent, best_x = node["value"], [round(v) for v in node["x"]]
            node["status"] = "incumbent"
            snap(f"node {i}: integral ({best_x[0]}, {best_x[1]}), new incumbent {incumbent:.0f}", i)
            continue
        lp = solve_node(m, tuple(node["lb"]), tuple(node["ub"]))
        j = L.most_fractional(m, (tuple(node["lb"]), tuple(node["ub"]), lp), {})
        v = node["x"][j]
        node["status"] = "branched"
        made = []
        for direction, (clb, cub) in zip(("down", "up"), L.children(tuple(node["lb"]), tuple(node["ub"]), j, v)):
            child = solve_node(m, clb, cub)
            name = "xy"[j]
            branch = f"{name} ≤ {math.floor(v)}" if direction == "down" else f"{name} ≥ {math.ceil(v)}"
            cid = len(nodes)
            rec = {"id": cid, "parent": i, "branch": branch, "lb": list(clb), "ub": list(cub),
                   "value": child.value if child.status == "optimal" else None,
                   "x": list(child.x) if child.status == "optimal" else None, "status": "open"}
            nodes.append(rec)
            if child.status != "optimal":
                rec["status"] = "infeasible"
                made.append(f"{branch} infeasible")
            elif child.value >= incumbent - 1e-9:
                rec["status"] = "pruned by bound"
                made.append(f"{branch} bound {child.value:.2f}, pruned")
            else:
                heapq.heappush(frontier, (child.value, next(tie), cid)) if selection == "best" else frontier.append((child.value, next(tie), cid))
                made.append(f"{branch} bound {child.value:.2f}")
        snap(f"node {i}: branch on {'xy'[j]} = {v:.2f}; " + "; ".join(made), i)
    snap(f"frontier empty: optimum {incumbent:.0f} at ({best_x[0]}, {best_x[1]}), proved")
    return states


def data():
    result = {"rows": ROWS, "c": [-1, -5], "runs": {}}
    for sel, title in (("best", "best-first"), ("dfs", "depth-first")):
        states = run(sel)
        ref_result = L.branch_and_bound(milp(), selection=sel)
        assert abs(ref_result.value - states[-1]["incumbent"]) < 1e-9
        assert ref_result.nodes == len(states[-1]["nodes"]), (ref_result.nodes, len(states[-1]["nodes"]))
        result["runs"][sel] = {"title": f"{title}: {ref_result.nodes} nodes", "states": states}
    return result
