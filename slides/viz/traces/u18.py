"""Unit 18's recorded data, for units/18-global-constraints/explore.html.

Régin's filter: the reference `value_graph`, `maximum_matching`, `_digraph`, `_sccs`,
`AllDifferent.prune` and `hall_set`, run on two instances and cut into steps.
Cumulative: the reference `Cumulative.prune` on every choice of start windows for the deck's
three tasks, so the page only looks results up. `uv run co viz 18` writes the data file.
"""

from __future__ import annotations

from itertools import product

from colib import ref

G = ref.unit("18")


def regin(title, doms):
    n = len(doms)
    dom = [frozenset(d) for d in doms]
    xs, offs = list(range(n)), [0] * n
    values, edges = G.value_graph(dom, xs, offs)
    matching = G.maximum_matching(dom, xs, offs)
    succ = G._digraph(n, values, edges, matching)
    comp = G._sccs(succ)
    out = G.AllDifferent(xs).prune(dom) or {}
    # nodes that can reach a free value (the path case)
    pred = [[] for _ in succ]
    for u, ws in enumerate(succ):
        for w in ws:
            pred[w].append(u)
    free = [k for k in range(len(values)) if k not in set(matching.values())]
    reach = set(n + k for k in free)
    stack = list(reach)
    while stack:
        w = stack.pop()
        for u in pred[w]:
            if u not in reach:
                reach.add(u)
                stack.append(u)
    E = [[i + 1, values[k]] for i, k in edges]
    matched = [[i + 1, values[k]] for i, k in sorted(matching.items())]
    arcs = [[("x", u) if u < n else ("v", values[u - n]), ("x", w) if w < n else ("v", values[w - n])] for u, ws in enumerate(succ) for w in ws]
    arcs = [[f"x{a[1] + 1}" if a[0] == "x" else f"v{a[1]}", f"x{b[1] + 1}" if b[0] == "x" else f"v{b[1]}"] for a, b in arcs]
    groups = {}
    for node, c in enumerate(comp):
        groups.setdefault(c, []).append(f"x{node + 1}" if node < n else f"v{values[node - n]}")
    sccs = [g for g in groups.values() if len(g) > 1]
    removed = []
    for i in range(n):
        for a in sorted(dom[i] - out.get(i, dom[i])):
            hs = G.hall_set(dom, xs, offs, i, a)
            removed.append({"x": i + 1, "value": a, "hall": [j + 1 for j in hs] if hs else None, "hall_values": sorted({v for j in hs for v in dom[j]}) if hs else None})
    kept = lambda i, a: a in out.get(i, dom[i])
    base = {"domains": [sorted(d) for d in dom], "values": values, "edges": E}
    states = [
        {**base, "stage": "graph", "note": "the value graph: an edge for every value in every domain",
         "explain": f"{len(E)} edges between {n} variables and {len(values)} values. alldifferent asks for one edge per variable, no value used twice: a matching covering every variable."},
        {**base, "stage": "matching", "matching": matched, "note": f"a maximum matching: {len(matched)} of {n} variables covered",
         "explain": "It covers every variable, so the constraint is satisfiable. " + (f"Free values (matched to nobody): {', '.join(str(values[k]) for k in free)}." if free else "Every value is used: no free values.")},
        {**base, "stage": "orient", "matching": matched, "arcs": arcs, "note": "orient: matched edges value → variable, the others variable → value",
         "explain": "An edge can be swapped into another maximum matching exactly when it lies on a directed cycle (a strongly connected component) or on a path to a free value."},
        {**base, "stage": "scc", "matching": matched, "arcs": arcs, "sccs": sccs, "reach": sorted(f"x{u + 1}" if u < n else f"v{values[u - n]}" for u in reach),
         "note": f"strongly connected components: {len(sccs)} with more than one node" + (", plus nodes that reach a free value" if free else ""),
         "explain": "; ".join("{" + ", ".join(g) + "}" for g in sccs) + ". Edges inside a component, matched edges and edges leading to a free value are kept."},
        {**base, "stage": "filter", "matching": matched, "arcs": arcs, "sccs": sccs, "reach": sorted(f"x{u + 1}" if u < n else f"v{values[u - n]}" for u in reach),
         "removed": removed, "result": [sorted(out.get(i, dom[i])) for i in range(n)],
         "note": f"remove the other {len(removed)} edges" if removed else "nothing to remove",
         "explain": "Every removed value is blocked by a Hall set: variables that between them own exactly as many values as there are variables."},
    ]
    return {"title": title, "n": n, "states": states}


def cumulative():
    durations, demands, capacity = [4, 3, 2], [1, 1, 1], 2
    horizon = [(0, 2), (1, 2), (0, 5)]           # the deck's start windows, the widest allowed here
    table = {}
    windows = [[(lo, hi) for lo in range(a, b + 1) for hi in range(lo, b + 1)] for a, b in horizon]
    for wins in product(*windows):
        dom = [frozenset(range(lo, hi + 1)) for lo, hi in wins]
        c = G.Cumulative([0, 1, 2], durations, demands, capacity)
        res = c.prune(dom)
        parts = [list(c.compulsory(dom, i)) for i in range(3)]
        key = ",".join(f"{lo}-{hi}" for lo, hi in wins)
        table[key] = {"fail": res is None, "parts": parts,
                      "keep": None if res is None else [sorted(res.get(i, dom[i])) for i in range(3)]}
    return {"names": ["A", "B", "C"], "durations": durations, "demands": demands, "capacity": capacity,
            "horizon": horizon, "start": ["0-2", "1-2", "0-5"], "table": table}


def data():
    return {
        "regin-deck": regin("the deck's example", [{1, 2}, {1, 2}, {1, 2, 3}, {2, 3, 4}]),
        "regin-free": regin("with a free value, 5", [{1, 2}, {1, 2}, {1, 2, 3, 4}, {3, 4, 5}]),
        "cumulative": cumulative(),
    }
