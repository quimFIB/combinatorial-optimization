"""The capstone's recorded schedules, for units/capstone-cvrptw/explore.html.

The four-customer instance of "The recurrence, on four customers". Start times come from
the reference `schedule` and `latest_starts`, insertion costs from `insertion_delta`. For
an infeasible insertion `schedule` only says None, so the page also shows the unchecked
recurrence t = max(ready, previous + service + travel) to point at the customer that runs
late; those times are recomputed here and marked as such.
"""

from __future__ import annotations

from colib import ref
from colib.vrptw import VRPTW

L = ref.unit("capstone")

INST = VRPTW.build("tiny", [(0, 0), (0, 30), (40, 30), (40, 0), (80, 0)], [0, 1, 1, 1, 1],
                   [0, 0, 60, 100, 0], [400, 50, 100, 200, 300], [0, 10, 10, 10, 10], 5)


def _unchecked(inst, route):
    """Arrival-driven start times with no deadline check, and the return time to the depot."""
    t, last, out = inst.ready[0], 0, []
    for c in route:
        t = max(inst.ready[c], t + inst.service[last] + inst.dist[last][c])
        out.append(t)
        last = c
    return out, t + inst.service[last] + inst.dist[last][0]


def data():
    inst, base = INST, (1, 2, 3)
    starts, latest = L.schedule(inst, base), L.latest_starts(inst, base)
    options = []
    for pos in range(len(base) + 1):
        route = base[:pos] + (4,) + base[pos:]
        delta = L.insertion_delta(inst, base, starts, latest, pos, 4)
        times, back = _unchecked(inst, route)
        options.append({"pos": pos, "route": list(route), "delta": delta,
                        "schedule": L.schedule(inst, route), "times": times, "back": back,
                        "cost": inst.route_cost(route)})
    opt = (1, 2, 4, 3)
    return {"tiny": {
        "coords": [list(c) for c in inst.coords], "ready": list(inst.ready), "due": list(inst.due),
        "service": list(inst.service), "dist": [list(r) for r in inst.dist],
        "base": {"route": list(base), "starts": starts, "latest": latest, "cost": inst.route_cost(base),
                 "back": _unchecked(inst, base)[1]},
        "insert": options,
        "optimum": {"route": list(opt), "starts": L.schedule(inst, opt), "cost": inst.route_cost(opt),
                    "back": _unchecked(inst, opt)[1]},
    }}
