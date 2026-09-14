"""Unit 24's recorded data, for units/24-lp-rounding-primal-dual/explore.html.

Threshold rounding: the LP optimum of weighted vertex cover from the reference
`vertex_cover_lp` on the deck's weighted 5-cycle and two small graphs whose LP optimum mixes
0, ½ and 1, with the optimum by brute force. Primal–dual set cover on the deck's
four-element cycle: the loop of the reference `primal_dual_set_cover` copied here so each
dual raise can be recorded, checked against the reference's own result. Jain–Vazirani on
the deck's line: α and opening times from the reference `jv_dual_ascent`, kept facilities
from `jain_vazirani`. `co viz 24` writes the data file.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations

from colib import ref
from colib.approx import FacilityLocation
from colib.problems import SetCover

L = ref.unit("24")


def fr(v) -> str:
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def brute_cover(n, edges, weights):
    best = None
    for k in range(n + 1):
        for S in combinations(range(n), k):
            if all(u in S or v in S for u, v in edges):
                w = sum(weights[i] for i in S)
                if best is None or w < best[0]:
                    best = (w, sorted(S))
    return best


def rounding():
    runs = []
    presets = [
        ("the deck's weighted 5-cycle", 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)], [3, 2, 2, 3, 4]),
        ("a triangle with a tail", 5, [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4)], [2, 2, 2, 1, 3]),
        ("a graph whose LP is already integral", 6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (4, 5)], [1, 3, 1, 3, 9, 1]),
    ]
    for title, n, edges, weights in presets:
        value, x = L.vertex_cover_lp(n, edges, weights)
        x = [round(v * 2) / 2 for v in x]        # half-integral; remove solver noise
        opt, opt_set = brute_cover(n, edges, weights)
        runs.append({"title": title, "n": n, "edges": [list(e) for e in edges], "weights": weights,
                     "x": x, "lp": value, "opt": opt, "opt_set": opt_set})
    return runs


def primal_dual():
    sc = SetCover(4, (frozenset({0, 1}), frozenset({1, 2}), frozenset({2, 3}), frozenset({3, 0})), (3, 2, 3, 2))
    y = [Fraction(0)] * sc.universe
    paid = [Fraction(0)] * sc.n
    x = [0] * sc.n
    covered = [False] * sc.universe
    containing = [[j for j, s in enumerate(sc.sets) if e in s] for e in range(sc.universe)]
    snap = lambda note, e=None, delta=None: {
        "y": [fr(v) for v in y], "paid": [fr(v) for v in paid], "bought": list(x), "covered": list(covered),
        "element": e, "delta": None if delta is None else fr(delta), "note": note}
    states = [snap("All duals at 0. Each set's bar shows how much of its cost its elements have paid.")]
    for e in range(sc.universe):
        if covered[e]:
            states.append(snap(f"Element {e} is already covered: skip it.", e))
            continue
        delta = min(sc.costs[j] - paid[j] for j in containing[e])
        y[e] += delta
        for j in containing[e]:
            paid[j] += delta
        newly = []
        for j in containing[e]:
            if paid[j] == sc.costs[j] and not x[j]:
                x[j] = 1
                newly.append(j)
                for u in sc.sets[j]:
                    covered[u] = True
        states.append(snap(f"Raise y{e} by {fr(delta)}: S{', S'.join(map(str, newly))} goes tight and is bought.", e, delta))
    rx, ry = L.primal_dual_set_cover(sc)
    assert rx == x and ry == y
    cost = sum(c for c, b in zip(sc.costs, x) if b)
    states[-1]["note"] += f" Done: cost {cost}, dual sum {fr(sum(y))}, so cost ≤ f·Σy = {fr(2 * sum(y))}."
    return {"sets": [sorted(s) for s in sc.sets], "costs": list(sc.costs), "universe": sc.universe,
            "f": L.frequency(sc), "states": states, "opt": 4}


def jain_vazirani():
    fl = FacilityLocation((4, 4), ((1, 2, 9), (9, 8, 1)))
    alpha, opened_at = L.jv_dual_ascent(fl)
    opened, assign, _ = L.jain_vazirani(fl)
    brute = {}
    for k in (1, 2):
        for S in combinations(range(fl.nf), k):
            brute[",".join("AB"[i] for i in S)] = fl.cost(S)
    return {"facilities": [0, 10], "clients": [1, 2, 9], "open_cost": list(fl.open_cost),
            "dist": [list(r) for r in fl.dist], "alpha": [float(a) for a in alpha],
            "alpha_exact": [fr(a) for a in alpha], "opened_at": {str(i): float(t) for i, t in opened_at.items()},
            "kept": opened, "assign": assign, "cost": fl.cost(opened, assign), "brute": brute}


def data():
    return {"rounding": rounding(), "primaldual": primal_dual(), "jv": jain_vazirani()}
