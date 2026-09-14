"""Unit 22's recorded data, for units/22-hardness/explore.html.

The gadget: the deck's formula (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ ¬x3) through the reference
`sat_to_vertex_cover`, and for each of the 8 assignments the vertex set the forward rule
builds (the reference `cover_from_assignment` when the assignment satisfies the formula)
with the edges it leaves uncovered. The FPTAS: the deck's four items through the reference
`knapsack_fptas` at a range of ε, against `knapsack_by_value`.
`co viz 22` writes units/22-hardness/viz-data.js.
"""

from __future__ import annotations

from itertools import product

from colib import ref
from colib.oracle import brute_force

L = ref.unit("22")

NVARS = 3
CLAUSES = [[1, -2, 3], [-1, 2, -3]]
VALUES, WEIGHTS, CAPACITY = [16, 28, 16, 25], [8, 12, 7, 7], 24


def lit_name(lit):
    return ("x" if lit > 0 else "¬x") + str(abs(lit))


def gadget():
    vc, k = L.sat_to_vertex_cover(NVARS, CLAUSES)
    names = [lit_name(v if s == 0 else -v) for v in range(1, NVARS + 1) for s in (0, 1)]
    names += [f"c{j + 1}.{t + 1}" for j in range(len(CLAUSES)) for t in range(3)]
    assignments = []
    for bits in product([True, False], repeat=NVARS):
        a = list(bits)
        sat = L.satisfies(a, CLAUSES)
        if sat:
            cover = L.cover_from_assignment(NVARS, CLAUSES, a)
            assert L.assignment_from_cover(NVARS, CLAUSES, cover) is not None
        else:
            # the forward rule with no true literal to skip: skip corner 1, and show what breaks
            cover = [0] * vc.n
            for v in range(1, NVARS + 1):
                cover[L.literal_vertex(v if a[v - 1] else -v)] = 1
            for j, clause in enumerate(CLAUSES):
                keep = next((t for t, lit in enumerate(clause) if a[abs(lit) - 1] == (lit > 0)), 0)
                for t in range(3):
                    if t != keep:
                        cover[2 * NVARS + 3 * j + t] = 1
        uncovered = [list(e) for e in vc.edges if not (cover[e[0]] or cover[e[1]])]
        clause_ok = [any(a[abs(l) - 1] == (l > 0) for l in c) for c in CLAUSES]
        assignments.append({"values": a, "satisfies": sat, "clauses": clause_ok, "cover": cover,
                            "size": sum(cover), "uncovered": uncovered})
    best = brute_force(vc)
    return {"nvars": NVARS, "clauses": CLAUSES, "n": vc.n, "edges": [list(e) for e in vc.edges], "k": k,
            "names": names, "assignments": assignments, "min_cover": best.value, "covers": best.feasible}


def fptas():
    opt, opt_items = L.knapsack_by_value(VALUES, WEIGHTS, CAPACITY)
    n = len(VALUES)
    runs = []
    for eps in [x / 20 for x in range(1, 21)] + [1.5, 2.0]:
        value, items = L.knapsack_fptas(VALUES, WEIGHTS, CAPACITY, eps)
        vmax = max(VALUES)
        K = eps * vmax / n
        scaled = [int(v // K) for v in VALUES]
        runs.append({"eps": eps, "K": K, "scaled": scaled, "items": items, "value": value,
                     "rounded_score": sum(scaled[i] for i in items),
                     "table_size": sum(scaled) + 1, "bound": opt - n * K})
    return {"values": VALUES, "weights": WEIGHTS, "capacity": CAPACITY, "opt": opt, "opt_items": opt_items,
            "exact_table_size": sum(VALUES) + 1, "runs": runs}


def data():
    return {"gadget": gadget(), "fptas": fptas()}
