"""Unit 08's recorded Gomory rounds, for units/08-cutting-planes/explore.html.

Each run is the reference gomory_loop on a two-variable pure integer program; the LP
optimum before each cut is re-solved with unit 02's reference two_phase on the rows known
at that round (the same calls gomory_loop makes), so the figure can draw every round.
`co viz 08` writes units/08-cutting-planes/viz-data.js.
"""

from __future__ import annotations

from fractions import Fraction as F

from colib import ref

L = ref.unit("08")
S = ref.unit("02")

INSTANCES = [
    ("deck", "the deck's example", "max x₂ over 3x₁ + 2x₂ ≤ 6, −3x₁ + 2x₂ ≤ 0", [[3, 2], [-3, 2]], [6, 0], [0, 1]),
    ("diamond", "a flat top", "max x₁ + x₂ over 2x₁ + 2x₂ ≤ 3, x₁ − x₂ ≤ 1, −x₁ + x₂ ≤ 1", [[2, 2], [1, -1], [-1, 1]], [3, 1, 1], [1, 1]),
    ("four", "four rounds", "max 2x₁ + 3x₂ over 4x₁ + 5x₂ ≤ 22, −2x₁ + x₂ ≤ 11", [[4, 5], [-2, 1]], [22, 11], [2, 3]),
]


def fmt(v):
    v = F(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def run(A, b, c):
    bounds, cuts, final = L.gomory_loop(A, b, c, rounds=12)
    states = []
    rows = [list(r) + [bb] for r, bb in zip(A, b)]
    for k in range(len(cuts) + 1):
        AA = [[F(v) for v in r[:2]] for r in rows]
        bb = [F(r[2]) for r in rows]
        res = S.two_phase(AA, bb, [F(v) for v in c])
        x = [float(v) for v in res.x]
        integral = all(F(v).denominator == 1 for v in res.x)
        cut = cuts[k] if k < len(cuts) else None
        note = (f"round {k}: LP optimum ({', '.join(fmt(v) for v in res.x)}), value {fmt(res.value)}"
                + (", integral: done" if cut is None and integral else ""))
        states.append({"rows": [list(map(float, r)) for r in rows], "base": len(A), "point": x,
                       "point_exact": [fmt(v) for v in res.x], "value": fmt(res.value),
                       "cut": None if cut is None else [float(cut[0][0]), float(cut[0][1]), float(cut[1])],
                       "note": note})
        if cut is not None:
            rows.append([cut[0][0], cut[0][1], cut[1]])
    assert [fmt(s["value"]) for s in states] == [fmt(v) for v in bounds]
    return states


def data():
    return {key: {"title": title, "lp": lp, "c": c, "states": run(A, b, c)} for key, title, lp, A, b, c in INSTANCES}
