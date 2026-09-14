"""Unit 31's recorded runs, for units/31-discrete-differentiable/explore.html.

Sinkhorn plans for the deck's 2×2 costs come from the reference `sinkhorn` (every
temperature on the slider, every iteration count) and `round_to_permutation`; Gumbel-max
samples come from the reference `gumbel_max_sample` with numpy's default_rng(0), as on the
slide, recorded as running counts.
"""

from __future__ import annotations

import math

import numpy as np

from colib import ref

L = ref.unit("31")

C = [[1.0, 3.0], [2.0, 5.0]]
EPS = [0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
ITERS = 30


def data():
    plans = {}
    for eps in EPS:
        per = []
        for k in range(1, ITERS + 1):
            P = L.sinkhorn(C, eps, k)
            per.append({"P": P.tolist(), "rows": P.sum(axis=1).tolist(), "cols": P.sum(axis=0).tolist()})
        final = np.array(per[-1]["P"])
        perm = L.round_to_permutation(final)
        closed = 1 / (1 + math.exp(1 / (2 * eps)))            # a/(1-a) = exp(-Δ/(2ε)), Δ = 1
        plans[str(eps)] = {"iters": per, "perm": perm, "cost": L.assignment_cost(C, perm), "closed_a": closed}

    logits = [1.0, 0.0, -1.0]
    rng = np.random.default_rng(0)
    n, counts, checkpoints, first = 20000, [0, 0, 0], [], []
    marks = sorted({int(round(10 ** (e / 20))) for e in range(0, 87)} | {n})
    for t in range(1, n + 1):
        i = L.gumbel_max_sample(logits, rng)
        counts[i] += 1
        if t <= 40:
            first.append(i)
        if t in marks:
            checkpoints.append([t, list(counts)])
    z = sum(math.exp(v) for v in logits)
    rng3 = np.random.default_rng(3)
    u = rng3.random(3)
    hand = {"u": u.tolist(), "g": [float(-math.log(-math.log(v))) for v in u]}
    hand["sample"] = int(np.argmax(np.array(logits) + np.array(hand["g"])))
    assert hand["sample"] == L.gumbel_max_sample(logits, np.random.default_rng(3))
    return {"sinkhorn": {"C": C, "eps": EPS, "plans": plans},
            "gumbel": {"logits": logits, "softmax": [math.exp(v) / z for v in logits],
                       "checkpoints": checkpoints, "first": first, "hand": hand}}
