"""Unit 30's recorded passes, for units/30-autodiff/explore.html: f(x, y) = x·y + sin x at (1, 2).

Forward mode runs the reference `Dual` class node by node with each seed; reverse mode
builds the graph from the reference `Var`, `vsin` and takes the visiting order from the
reference `backward`, replaying its adjoint loop one node at a time so every
intermediate adjoint can be shown. The final gradients are checked against
`reverse_gradient`.
"""

from __future__ import annotations

from colib import ref

L = ref.unit("30")

NODES = [
    {"id": "v0", "label": "v₀", "op": "x", "x": 90, "y": 110},
    {"id": "v1", "label": "v₁", "op": "y", "x": 90, "y": 290},
    {"id": "v2", "label": "v₂", "op": "v₀ · v₁", "x": 260, "y": 250},
    {"id": "v3", "label": "v₃", "op": "sin v₀", "x": 260, "y": 90},
    {"id": "v4", "label": "v₄", "op": "v₂ + v₃  (= f)", "x": 420, "y": 170},
]
EDGES = [["v0", "v2"], ["v1", "v2"], ["v0", "v3"], ["v2", "v4"], ["v3", "v4"]]


def _forward(seed):
    x = L.Dual(1.0, 1.0 if seed == "x" else 0.0)
    y = L.Dual(2.0, 1.0 if seed == "y" else 0.0)
    vals = {}
    steps = []
    order = [
        ("v0", lambda: x, [], f"x = 1 + {x.deriv:g}ε: seed {'1' if seed == 'x' else '0'}"),
        ("v1", lambda: y, [], f"y = 2 + {y.deriv:g}ε: seed {'1' if seed == 'y' else '0'}"),
        ("v2", lambda: vals["v0"] * vals["v1"], ["v0", "v1"], "product rule: (a + bε)(c + dε) = ac + (ad + bc)ε"),
        ("v3", lambda: L.sin(vals["v0"]), ["v0"], "sin(a + bε) = sin a + (cos a) b ε"),
        ("v4", lambda: vals["v2"] + vals["v3"], ["v2", "v3"], "sum: values add, ε parts add"),
    ]
    for node, op, inputs, why in order:
        vals[node] = op()
        steps.append({
            "active": node, "inputs": inputs,
            "values": {k: v.value for k, v in vals.items()},
            "tangents": {k: v.deriv for k, v in vals.items()},
            "note": f"{node}: value {vals[node].value:.4f}, ε part {vals[node].deriv:.4f}",
            "explain": why,
        })
    return steps


def _reverse():
    x, y = L.Var(1.0), L.Var(2.0)
    v2 = x * y
    v3 = L.vsin(x)
    v4 = v2 + v3
    names = {id(x): "v0", id(y): "v1", id(v2): "v2", id(v3): "v3", id(v4): "v4"}
    values = {names[id(n)]: n.value for n in (x, y, v2, v3, v4)}
    order = L.backward(v4)                      # the reference sweep, run once for its order and grads
    final = {names[id(n)]: n.grad for n in order}
    locals_ = {names[id(n)]: [[names[id(p)], loc] for p, loc in n.parents] for n in order}
    steps = []
    for k, name in enumerate(["v0", "v1", "v2", "v3", "v4"]):
        steps.append({"phase": "record", "active": name, "values": {n: values[n] for n in ["v0", "v1", "v2", "v3", "v4"][:k + 1]},
                      "adjoints": {}, "locals": locals_,
                      "note": f"forward: record {name} = {values[name]:.4f}",
                      "explain": "The forward pass evaluates normally and writes each operation and its local derivatives on the tape."})
    adj = {n: 0.0 for n in values}
    adj["v4"] = 1.0
    steps.append({"phase": "sweep", "active": "v4", "values": values, "adjoints": dict(adj), "locals": locals_, "edges": [],
                  "note": "backward: seed the output, adjoint of v₄ = 1", "explain": "∂f/∂f = 1. Now visit the tape in reverse."})
    for node in reversed(order):
        name = names[id(node)]
        if not node.parents:
            continue
        edges, parts = [], []
        for parent, local in node.parents:
            pn = names[id(parent)]
            adj[pn] += adj[name] * local
            edges.append([pn, name])
            parts.append(f"adj {pn} += {adj[name]:g} × {local:.4f}")
        steps.append({"phase": "sweep", "active": name, "values": values, "adjoints": dict(adj), "locals": locals_, "edges": edges,
                      "note": f"visit {name}: " + "; ".join(parts),
                      "explain": "Each parent's adjoint collects (this node's adjoint) × (local derivative). A node fed into two places collects twice: that is the chain rule's sum."})
    value, grads = L.reverse_gradient(lambda v: v[0] * v[1] + L.vsin(v[0]), [1.0, 2.0])
    assert abs(adj["v0"] - grads[0]) < 1e-12 and abs(adj["v1"] - grads[1]) < 1e-12
    steps[-1]["explain"] = (f"Done: ∂f/∂x = adj v₀ = {adj['v0']:.4f}, ∂f/∂y = adj v₁ = {adj['v1']:.4f}, both from one sweep "
                            f"(reverse_gradient agrees: {grads[0]:.7f}, {grads[1]:.7f}).")
    return steps


def data():
    return {"graph": {"nodes": NODES, "edges": EDGES},
            "forward-x": {"title": "forward, seed x", "mode": "forward", "states": _forward("x")},
            "forward-y": {"title": "forward, seed y", "mode": "forward", "states": _forward("y")},
            "reverse": {"title": "reverse: record, then sweep", "mode": "reverse", "states": _reverse()}}
