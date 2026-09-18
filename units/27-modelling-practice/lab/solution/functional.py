"""Unit 27 lab — modelling for a real solver.  REFERENCE SOLUTION, functional.

A solver model is a mutable object by nature: pyscipopt builds it by calling addVar and addCons. So the
functional version keeps the model-building calls, but computes everything that goes into them (index
sets, constraints, the start solution, the arc set) as values first, and the pure parts (first-fit decreasing, L2,
the statistics parser) have no mutation at all. The lab sheet says so rather than pretending otherwise.
"""

from __future__ import annotations

import math
import re
from functools import reduce
from itertools import product

import toolz as tz
from pyscipopt import Model, quicksum


def _quiet(model):
    model.hideOutput()
    return model


# ---------------------------------------------------------------- step 1 ---

def assignment_model(sizes, capacity, nbins, linked=True, vtype="B"):
    m = _quiet(Model("binpacking"))
    n, bins = len(sizes), range(nbins)
    x = {(i, b): m.addVar(vtype=vtype, lb=0, ub=1, name=f"x_{i}_{b}") for i, b in product(range(n), bins)}
    y = [m.addVar(vtype=vtype, lb=0, ub=1, obj=1, name=f"y_{b}") for b in bins]
    load = lambda b: quicksum(sizes[i] * x[i, b] for i in range(n))
    rows = ([quicksum(x[i, b] for b in bins) == 1 for i in range(n)]
            + ([load(b) <= capacity * y[b] for b in bins] if linked
               else [load(b) <= capacity for b in bins] + [x[i, b] <= y[b] for b in bins for i in range(n)]))
    for row in rows:
        m.addCons(row)
    m.setMinimize()
    return m, x, y


# ---------------------------------------------------------------- step 2 ---

def add_symmetry_breaking(model, x, y, n):
    for row in [y[b] >= y[b + 1] for b in range(len(y) - 1)]:
        model.addCons(row)
    for i, b in ((i, b) for i in range(n) for b in range(i + 1, len(y))):
        model.chgVarUb(x[i, b], 0)


# ---------------------------------------------------------------- step 3 ---

def first_fit_decreasing(sizes, capacity):
    def place(bins, i):
        target = next((k for k, b in enumerate(bins) if sum(sizes[j] for j in b) + sizes[i] <= capacity), None)
        return bins + ((i,),) if target is None else bins[:target] + (bins[target] + (i,),) + bins[target + 1:]
    return [list(b) for b in reduce(place, sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)), ())]


def lower_bound_l2(sizes, capacity):
    def bound(alpha):
        j1 = [s for s in sizes if s > capacity - alpha]
        j2 = [s for s in sizes if 2 * s > capacity and s <= capacity - alpha]
        j3 = [s for s in sizes if alpha <= s and 2 * s <= capacity]
        return len(j1) + len(j2) + max(0, math.ceil((sum(j3) - (len(j2) * capacity - sum(j2))) / capacity))
    return max(map(bound, [0] + [s for s in sizes if 2 * s <= capacity]))


def bounded_model(sizes, capacity):
    nbins = len(first_fit_decreasing(sizes, capacity))
    m, x, y = assignment_model(sizes, capacity, nbins, linked=True)
    add_symmetry_breaking(m, x, y, len(sizes))
    for b in range(min(nbins, lower_bound_l2(sizes, capacity))):
        m.chgVarLb(y[b], 1)
    return m, x, y


# ---------------------------------------------------------------- step 4 ---

def add_start(model, x, y, bins):
    rank = {i: r for r, b in enumerate(sorted(bins, key=min)) for i in b}
    values = ([(var, float(rank.get(i) == b)) for (i, b), var in x.items()]
              + [(var, float(b < len(bins))) for b, var in enumerate(y)])     # solver variables aren't hashable
    sol = model.createSol()
    for var, value in values:
        model.setSolVal(sol, var, value)
    if not model.checkSol(sol, original=True):
        model.freeSol(sol)
        return False
    return bool(model.addSol(sol, free=True))


# ---------------------------------------------------------------- step 5 ---

def arcflow_model(sizes, capacity, vtype="I"):
    m = _quiet(Model("arcflow"))
    counts = tz.frequencies(sizes)
    arc_keys = ([(d, d + s, s) for s in counts for d in range(capacity - s + 1)]
                + [(d, d + 1, 0) for d in range(capacity)])
    arcs = {key: m.addVar(vtype=vtype, lb=0, name=f"f_{key[0]}_{key[2]}") for key in arc_keys}
    z = m.addVar(vtype=vtype, lb=0, obj=1, name="z")
    out_of = tz.groupby(lambda k: k[0], arc_keys)
    into = tz.groupby(lambda k: k[1], arc_keys)
    flow = lambda keys: quicksum(arcs[k] for k in keys)
    rows = ([flow(out_of[0]) == z, flow(into[capacity]) == z]
            + [flow(into[d]) == flow(out_of[d]) for d in range(1, capacity)]
            + [flow(k for k in arc_keys if k[2] == s) >= c for s, c in counts.items()])
    for row in rows:
        m.addCons(row)
    m.setMinimize()
    return m, z


# ---------------------------------------------------------------- step 6 ---

def _number(text):
    return None if text in ("-", "infinite") else float(text.replace("+", ""))


def parse_statistics(text):
    def sections(lines):
        heads = [k for k, line in enumerate(lines) if not line.startswith(" ")]
        for start, stop in zip(heads, heads[1:] + [len(lines)]):
            name, _, rest = lines[start].partition(":")
            rows = [(key.strip(), cells) for key, _, cells in (line.partition(":") for line in lines[start + 1:stop])]
            yield name.strip(), rest.split(), rows

    table = {name: (header, rows) for name, header, rows in sections(text.splitlines())}

    def column(section, col, skip=lambda key: False):
        header, rows = table.get(section, ([], []))
        if col not in header:
            return {}
        k = header.index(col)
        return {key: int(cells.split()[k]) for key, cells in rows
                if not skip(key) and len(cells.split()) == len(header) and cells.split()[k] not in ("-", "0")}

    fields = lambda section: dict(table.get(section, ([], []))[1])
    tree, root, solution = fields("B&B Tree"), fields("Root Node"), fields("Solution")
    found = re.search(r"found by <([^>]+)>", solution.get("Primal Bound", ""))
    gap = solution.get("Gap", "infinite").split()[0]
    return {
        "nodes": int(tree["nodes (total)"].split()[0]),
        "primal_bound": _number(solution["Primal Bound"].split()[0]),
        "dual_bound": _number(solution["Dual Bound"].split()[0]),
        "gap_percent": None if gap == "infinite" else float(gap),
        "first_lp_value": _number(root["First LP value"].split()[0]),
        "found_by": found.group(1) if found else None,
        "cuts_applied": column("Separators", "Applied", lambda key: key == "cut pool" or key.startswith(">")),
        "heuristics_best": column("Primal Heuristics", "Best"),
    }
