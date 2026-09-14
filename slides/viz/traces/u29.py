"""Unit 29's recorded runs, for units/29-convexity-gradients/explore.html.

Gradient descent is drawn live in the page from the quadratic's two eigenvalues; the
iterates recorded here, from the reference `gradient_descent`, `heavy_ball` and `nesterov`,
are what the page checks its own arithmetic against before drawing anything. Frank–Wolfe
and projected gradient are replayed from the reference `frank_wolfe` (with unit 02's
simplex as the oracle) and `projected_gradient`.
"""

from __future__ import annotations

import numpy as np

from colib import ref

L = ref.unit("29")


def _pts(xs):
    return [[float(v) for v in x] for x in xs]


def data():
    Q = np.diag([1.0, 10.0])
    grad = lambda x: Q @ x
    start = [1.0, 1.0]
    checks = {
        "gd-0.1": _pts(L.gradient_descent(grad, start, 0.1, 12)),
        "gd-0.19": _pts(L.gradient_descent(grad, start, 0.19, 12)),
        "hb-0.1-0.5": _pts(L.heavy_ball(grad, start, 0.1, 0.5, 12)),
        "nesterov-0.1": _pts(L.nesterov(grad, start, 0.1, 12)),
    }

    p = np.array([0.8, 0.6, -0.2])
    fgrad = lambda x: x - p
    f = lambda x: float(0.5 * np.sum((np.asarray(x) - p) ** 2))
    lmo = L.simplex_lmo([[1, 1, 1]], [1])
    xs, gaps = L.frank_wolfe(fgrad, lmo, [0.0, 0.0, 0.0], 12)
    proj = L.project_simplex(p)
    fw_states = []
    for k, x in enumerate(xs):
        state = {"x": [float(v) for v in x], "f": f(x), "path": _pts(xs[:k + 1])}
        if k < len(gaps):
            g = fgrad(x)
            s = lmo(g)
            state.update({"g": [float(v) for v in g], "s": [float(v) for v in s], "gap": gaps[k], "step": 2 / (k + 2)})
        fw_states.append(state)
    pg = L.projected_gradient(fgrad, L.project_simplex, [0.0, 0.0, 0.0], 0.5, 8)
    pg_states = [{"x": [float(v) for v in x], "f": f(x), "path": _pts(pg[:k + 1]),
                  "raw": [float(v) for v in (pg[k - 1] - 0.5 * fgrad(pg[k - 1]))] if k else None}
                 for k, x in enumerate(pg)]
    return {
        "gd": {"eig": [1.0, 10.0], "start": start, "checks": checks},
        "fw": {"p": p.tolist(), "projection": [float(v) for v in proj], "fstar": f(proj),
               "fw": fw_states, "pg": pg_states},
    }
