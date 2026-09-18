"""Unit 27 lab — modelling for a real solver.  REFERENCE SOLUTION, imperative.

The running example is bin packing: item sizes (positive integers) and a bin capacity. Every model is a
pyscipopt Model minimising the number of bins, and each step is one intervention that must not change the
optimum. Tests check that it doesn't; `then` measures what each one buys.
"""

from __future__ import annotations

import math
import re

from pyscipopt import Model, quicksum


def _quiet(model):
    model.hideOutput()
    return model


# ---------------------------------------------------------------- step 1 ---

def assignment_model(sizes, capacity, nbins, linked=True, vtype="B"):
    """The assignment model. x[i, b] = item i in bin b, y[b] = bin b used; minimise sum y; each item in exactly
    one bin. linked=False: capacity constraints sum_i s_i x[i, b] <= capacity, plus x[i, b] <= y[b] for every pair.
    linked=True: capacity constraints sum_i s_i x[i, b] <= capacity * y[b], and no x <= y constraints.
    vtype="C" gives the LP relaxation (bounds 0..1). Returns (model, x, y) with x a dict and y a list."""
    m = _quiet(Model("binpacking"))
    n = len(sizes)
    x = {(i, b): m.addVar(vtype=vtype, lb=0, ub=1, name=f"x_{i}_{b}") for i in range(n) for b in range(nbins)}
    y = [m.addVar(vtype=vtype, lb=0, ub=1, obj=1, name=f"y_{b}") for b in range(nbins)]
    for i in range(n):
        m.addCons(quicksum(x[i, b] for b in range(nbins)) == 1)
    for b in range(nbins):
        load = quicksum(sizes[i] * x[i, b] for i in range(n))
        if linked:
            m.addCons(load <= capacity * y[b])
        else:
            m.addCons(load <= capacity)
            for i in range(n):
                m.addCons(x[i, b] <= y[b])
    m.setMinimize()
    return m, x, y


# ---------------------------------------------------------------- step 2 ---

def add_symmetry_breaking(model, x, y, n):
    """Bins are interchangeable, so break the symmetry without cutting off every optimum: y[b] >= y[b+1] (used
    bins come first), and item i may only go into bins 0..i (x[i, b] fixed to 0 for b > i)."""
    nbins = len(y)
    for b in range(nbins - 1):
        model.addCons(y[b] >= y[b + 1])
    for i in range(n):
        for b in range(i + 1, nbins):
            model.chgVarUb(x[i, b], 0)


# ---------------------------------------------------------------- step 3 ---

def first_fit_decreasing(sizes, capacity):
    """Items by decreasing size (ties: lower index first), each into the first bin with room. Returns a list of
    bins, each a list of item indices in insertion order."""
    bins, loads = [], []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        for b, load in enumerate(loads):
            if load + sizes[i] <= capacity:
                bins[b].append(i)
                loads[b] += sizes[i]
                break
        else:
            bins.append([i])
            loads.append(sizes[i])
    return bins


def lower_bound_l2(sizes, capacity):
    """Martello and Toth's L2. For alpha in {0} and every size <= capacity / 2: J1 = sizes > capacity - alpha,
    J2 = sizes in (capacity / 2, capacity - alpha], J3 = sizes in [alpha, capacity / 2];
    L(alpha) = |J1| + |J2| + max(0, ceil((sum J3 - (|J2| * capacity - sum J2)) / capacity)). L2 = max L(alpha)."""
    best = 0
    for alpha in [0] + [s for s in sizes if 2 * s <= capacity]:
        j1 = [s for s in sizes if s > capacity - alpha]
        j2 = [s for s in sizes if 2 * s > capacity and s <= capacity - alpha]
        j3 = [s for s in sizes if alpha <= s and 2 * s <= capacity]
        free = len(j2) * capacity - sum(j2)
        best = max(best, len(j1) + len(j2) + max(0, math.ceil((sum(j3) - free) / capacity)))
    return best


def bounded_model(sizes, capacity):
    """Linked assignment model with only as many bins as first-fit decreasing uses, symmetry breaking, and
    y[b] fixed to 1 for b < L2. Returns (model, x, y)."""
    nbins = len(first_fit_decreasing(sizes, capacity))
    m, x, y = assignment_model(sizes, capacity, nbins, linked=True)
    add_symmetry_breaking(m, x, y, len(sizes))
    for b in range(min(nbins, lower_bound_l2(sizes, capacity))):
        m.chgVarLb(y[b], 1)
    return m, x, y


# ---------------------------------------------------------------- step 4 ---

def add_start(model, x, y, bins):
    """Offer a packing (a list of bins of item indices, as first_fit_decreasing returns) as a MIP start: set every
    x and y, check it against the original problem (model.checkSol(sol, original=True)), and add it with
    model.addSol(sol) only if it passes. Returns True iff it was feasible and stored. Number the bins by their
    smallest item, so that a packing respects add_symmetry_breaking when the model has it."""
    order = sorted(range(len(bins)), key=lambda b: min(bins[b]))
    sol = model.createSol()
    where = {i: rank for rank, b in enumerate(order) for i in bins[b]}
    for (i, b), var in x.items():
        model.setSolVal(sol, var, 1.0 if where.get(i) == b else 0.0)
    for b, var in enumerate(y):
        model.setSolVal(sol, var, 1.0 if b < len(bins) else 0.0)
    if not model.checkSol(sol, original=True):
        model.freeSol(sol)
        return False
    return bool(model.addSol(sol, free=True))


# ---------------------------------------------------------------- step 5 ---

def arcflow_model(sizes, capacity, vtype="I"):
    """Valerio de Carvalho's arc-flow model. Nodes 0..capacity; for each distinct size s an item arc d -> d + s for
    every d with d + s <= capacity; a loss arc d -> d + 1 for every d < capacity. Integer flows; the flow z leaving
    node 0 equals the flow entering node capacity and is minimised; every other node conserves flow; the arcs of
    size s carry at least (number of items of size s). vtype="C" gives the LP relaxation.
    Returns (model, z)."""
    m = _quiet(Model("arcflow"))
    counts = {}
    for s in sizes:
        counts[s] = counts.get(s, 0) + 1
    arcs = {}
    for s in counts:
        for d in range(capacity - s + 1):
            arcs[(d, d + s, s)] = m.addVar(vtype=vtype, lb=0, name=f"f_{d}_{s}")
    for d in range(capacity):
        arcs[(d, d + 1, 0)] = m.addVar(vtype=vtype, lb=0, name=f"loss_{d}")
    z = m.addVar(vtype=vtype, lb=0, obj=1, name="z")
    out_of = {d: [] for d in range(capacity + 1)}
    into = {d: [] for d in range(capacity + 1)}
    for (a, b, _), var in arcs.items():
        out_of[a].append(var)
        into[b].append(var)
    m.addCons(quicksum(out_of[0]) == z)
    m.addCons(quicksum(into[capacity]) == z)
    for d in range(1, capacity):
        m.addCons(quicksum(into[d]) == quicksum(out_of[d]))
    for s, c in counts.items():
        m.addCons(quicksum(var for (a, b, t), var in arcs.items() if t == s) >= c)
    m.setMinimize()
    return m, z


# ---------------------------------------------------------------- step 6 ---

def _number(text):
    return float(text.replace("+", "")) if text not in ("-", "infinite") else None


def parse_statistics(text):
    """Read a SCIP statistics report (model.writeStatistics) into a dict:
    "nodes" (int, from B&B Tree's "nodes (total)"), "primal_bound" and "dual_bound" (floats, from Solution),
    "gap_percent" (float, or None if infinite), "first_lp_value" (float, from Root Node),
    "found_by" (the heuristic named in "Primal Bound ... found by <name>", or None),
    "cuts_applied" ({separator: Applied count} from the Separators table's top-level rows: not "cut pool" and
    not the indented "> name" rows, which break a separator's count down by cut family; zero counts omitted), and "heuristics_best" ({heuristic: Best count} from Primal
    Heuristics, zero counts omitted)."""
    lines = text.splitlines()
    out = {"cuts_applied": {}, "heuristics_best": {}, "found_by": None, "gap_percent": None}
    section = None
    header = []
    for line in lines:
        if not line.startswith(" "):
            name, _, rest = line.partition(":")
            section = name.strip()
            header = rest.split()
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        cells = rest.split()
        if section == "Separators" and key != "cut pool" and not key.startswith(">") and "Applied" in header:
            value = cells[header.index("Applied")]
            if value not in ("-", "0"):
                out["cuts_applied"][key] = int(value)
        elif section == "Primal Heuristics" and "Best" in header and len(cells) == len(header):
            value = cells[header.index("Best")]
            if value not in ("-", "0"):
                out["heuristics_best"][key] = int(value)
        elif section == "B&B Tree" and key == "nodes (total)":
            out["nodes"] = int(cells[0])
        elif section == "Root Node" and key == "First LP value":
            out["first_lp_value"] = _number(cells[0])
        elif section == "Solution":
            if key == "Primal Bound":
                out["primal_bound"] = _number(cells[0])
                found = re.search(r"found by <([^>]+)>", rest)
                out["found_by"] = found.group(1) if found else None
            elif key == "Dual Bound":
                out["dual_bound"] = _number(cells[0])
            elif key == "Gap":
                out["gap_percent"] = None if cells[0] == "infinite" else float(cells[0])
    return out
