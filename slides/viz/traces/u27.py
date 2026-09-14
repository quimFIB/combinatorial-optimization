"""Unit 27's recorded models, for units/27-modelling-practice/explore.html.

The arc-flow figures use the reference `arcflow_model` solved by SCIP, integer and LP relaxation;
the flow is split into paths (one path per bin, possibly fractional) by a greedy decomposition done
here, and each decomposition is checked to add back up to SCIP's arc values. The symmetry figure
enumerates every assignment of the running example's items to three labelled bins, and keeps the
packings that respect capacity and use every bin; the symmetry-breaking filter is the reference
rule of `add_symmetry_breaking` ("item i only in bins 0..i", used bins first), applied to the list.
`uv run co viz 27` writes units/27-modelling-practice/viz-data.js.
"""

from __future__ import annotations

from itertools import product

from colib import ref

L = ref.unit("27")


def _solve_arcflow(sizes, capacity, vtype):
    m, z = L.arcflow_model(sizes, capacity, vtype=vtype)
    m.optimize()
    flows = {}
    for var in m.getVars():
        name, val = var.name, m.getVal(var)
        if abs(val) < 1e-9 or name == "z":
            continue
        if name.startswith("loss_"):
            d = int(name.split("_")[1])
            flows[(d, d + 1, 0)] = val
        else:
            _, d, s = name.split("_")
            flows[(int(d), int(d) + int(s), int(s))] = val
    return m.getObjVal(), flows


def _decompose(flows, capacity):
    """Greedy path decomposition from node 0 to node capacity; returns [(amount, [arcs])]."""
    left = {a: v for a, v in flows.items() if v > 1e-9}
    paths = []
    while any(a[0] == 0 for a in left):
        node, path = 0, []
        while node != capacity:
            # prefer item arcs, largest size first, so a bin reads "items, then waste"
            arc = max((a for a in left if a[0] == node), key=lambda a: (a[2] > 0, a[2]))
            path.append(arc)
            node = arc[1]
        amount = min(left[a] for a in path)
        for a in path:
            left[a] -= amount
            if left[a] < 1e-9:
                del left[a]
        paths.append((amount, path))
    assert not left, f"flow not decomposed: {left}"
    return paths


def arcflow(sizes, capacity):
    arcs = [(d, d + s, s) for s in sorted(set(sizes), reverse=True) for d in range(capacity - s + 1)]
    arcs += [(d, d + 1, 0) for d in range(capacity)]
    out = {"sizes": sizes, "capacity": capacity, "arcs": [list(a) for a in arcs], "solutions": {}}
    counts = {s: sizes.count(s) for s in set(sizes)}
    for key, vtype in (("integer", "I"), ("lp", "C")):
        value, flows = _solve_arcflow(sizes, capacity, vtype)
        paths = _decompose(flows, capacity)
        back = {}
        for amount, path in paths:
            for a in path:
                back[a] = back.get(a, 0) + amount
        assert all(abs(back.get(a, 0) - v) < 1e-7 for a, v in flows.items())
        carried = {s: sum(v for a, v in flows.items() if a[2] == s) for s in counts}
        out["solutions"][key] = {
            "value": round(value, 6),
            "flows": [[*a, round(v, 6)] for a, v in sorted(flows.items())],
            "paths": [{"amount": round(amt, 6),
                       "arcs": [list(a) for a in path],
                       "items": [a[2] for a in path if a[2] > 0],
                       "waste": sum(1 for a in path if a[2] == 0)} for amt, path in paths],
            "carried": {str(s): round(carried[s], 6) for s in counts},
        }
    out["needed"] = {str(s): c for s, c in counts.items()}
    return out


def symmetry(sizes, capacity, nbins):
    n = len(sizes)
    assignments = []
    for a in product(range(nbins), repeat=n):
        loads = [0] * nbins
        for i, b in enumerate(a):
            loads[b] += sizes[i]
        if any(l > capacity for l in loads) or any(l == 0 for l in loads):
            continue
        # the packing it labels: blocks of item indices, order-free
        blocks = sorted(tuple(i for i in range(n) if a[i] == b) for b in range(nbins))
        used = [loads[b] > 0 for b in range(nbins)]
        kept = all(a[i] <= i for i in range(n)) and all(used[b] >= used[b + 1] for b in range(nbins - 1))
        assignments.append({"bins": list(a), "packing": [list(bl) for bl in blocks], "kept": kept})
    packings = sorted({tuple(tuple(b) for b in x["packing"]) for x in assignments})
    for x in assignments:
        x["packing_id"] = packings.index(tuple(tuple(b) for b in x["packing"]))
    assignments.sort(key=lambda x: (x["packing_id"], x["bins"]))
    return {"sizes": sizes, "capacity": capacity, "nbins": nbins, "assignments": assignments,
            "packings": len(packings), "kept": sum(x["kept"] for x in assignments)}


def data():
    return {
        "arcflow": {
            "example": {"title": "The running example: sizes 3, 3, 2, 2, 2, capacity 5", "short": "sizes 3,3,2,2,2 · C = 5", **arcflow([3, 3, 2, 2, 2], 5)},
            "seven": {"title": "Sizes 4, 3, 3, 2, 2, 2, 1, capacity 7", "short": "sizes 4,3,3,2,2,2,1 · C = 7", **arcflow([4, 3, 3, 2, 2, 2, 1], 7)},
        },
        "symmetry": symmetry([3, 3, 2, 2, 2], 5, 3),
    }
