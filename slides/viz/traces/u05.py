"""Unit 05's recorded LP bounds, for units/05-formulations/explore.html.

The deck's tiny facility-location instance (2 facilities with opening cost 6, 3 customers),
solved by HiGHS through colib.mip.lp_relaxation on the reference formulations: the
aggregated model for a range of M, the disaggregated model, the integer optimum by the
reference brute force. `uv run co viz 05` writes units/05-formulations/viz-data.js.
"""

from __future__ import annotations

from colib import ref
from colib.mip import FacilityLocation, lp_relaxation

L = ref.unit("05")

INSTANCE = FacilityLocation((6, 6), ((1, 1, 5), (5, 5, 1)), (1, 1, 1), (3, 3))
M_VALUES = [3, 3.5, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]


def solve(milp):
    r = lp_relaxation(milp)
    F, C = INSTANCE.F, INSTANCE.C
    x = [float(v) for v in r.x]
    return {"value": float(r.value), "y": x[:F], "x": [x[F + i * C: F + (i + 1) * C] for i in range(F)]}


def data():
    best, open_set = L.ufl_brute_force(INSTANCE)
    return {"facility": {
        "open_cost": list(INSTANCE.open_cost), "serve_cost": [list(r) for r in INSTANCE.serve_cost],
        "ip": float(best), "ip_open": list(open_set),
        "aggregated": [{"M": M, **solve(L.ufl_aggregated(INSTANCE, M))} for M in M_VALUES],
        "disaggregated": solve(L.ufl_disaggregated(INSTANCE)),
    }}
