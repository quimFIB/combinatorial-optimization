"""Unit 04's recorded runs, for units/04-ellipsoid-interior-point/explore.html.

Ellipsoid runs: the loop of the reference `ellipsoid_feasible` (take the most violated row,
call the reference `ellipsoid_step`), recorded one iteration at a time: centre, matrix P,
the row cut on, and the violations. Central path: the reference `central_path` on unit 01's
polygon with a small growth factor, so a slider can move along it. `uv run co viz 04`
writes units/04-ellipsoid-interior-point/viz-data.js.
"""

from __future__ import annotations

import math

import numpy as np

from colib import ref

L = ref.unit("04")

POLYGON = [[-1, 0, 0], [0, -1, 0], [1, 1, 4], [1, -1, 1]]


def ellipsoid_run(rows, R, max_iter):
    A = np.array([r[:2] for r in rows], float)
    b = np.array([r[2] for r in rows], float)
    center, P = np.zeros(2), (R * R) * np.eye(2)
    states = []
    for k in range(max_iter + 1):
        viol = A @ center - b
        i = int(np.argmax(viol))
        area = math.pi * math.sqrt(max(np.linalg.det(P), 0.0))
        state = {"center": center.tolist(), "P": P.tolist(), "row": i, "violation": float(viol[i]),
                 "area": area, "feasible": bool(viol[i] <= 0)}
        states.append(state)
        if viol[i] <= 0 or k == max_iter:
            break
        center, P = L.ellipsoid_step(center, P, A[i])
    return states


def central(rows, c, t0=0.01, mu=1.25, eps=2e-3):
    A = [r[:2] for r in rows]
    b = [r[2] for r in rows]
    path = L.central_path(A, b, c, [0.5, 0.5], t0=t0, mu=mu, eps=eps)
    out = []
    Am, bv = np.array(A, float), np.array(b, float)
    for t, x, y in path:
        s = bv - Am @ x
        out.append({"t": float(t), "x": [float(v) for v in x], "y": [float(v) for v in y], "s": [float(v) for v in s],
                    "gap": float(bv @ y - np.array(c, float) @ x), "Aty": [float(v) for v in Am.T @ y],
                    "obj": float(np.array(c, float) @ x)})
    return out


def data():
    runs = {}
    specs = [
        ("deck", "Polygon with x + y ≥ 3 (the deck's example), R = 5", POLYGON + [[-1, -1, -3]], 5.0, 40),
        ("corner", "A thin corner: x + y ≥ 3.6 and x − y ≥ 0.4, R = 5", POLYGON + [[-1, -1, -3.6], [-1, 1, -0.4]], 5.0, 40),
        ("empty", "An empty set: y ≥ 0.2 and y ≤ 0.1, R = 5 (stopped after 30 steps)", POLYGON + [[0, -1, -0.2], [0, 1, 0.1]], 5.0, 30),
    ]
    for key, title, rows, R, max_iter in specs:
        runs[key] = {"title": title, "rows": rows, "R": R, "states": ellipsoid_run(rows, R, max_iter),
                     "ratio": 2 / 3 * 2 / math.sqrt(3)}
    return {**runs, "path": {"rows": POLYGON, "c": [2, 1], "points": central(POLYGON, [2, 1])}}
