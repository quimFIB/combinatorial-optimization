"""Unit 03's recorded dual simplex runs, for units/03-duality/explore.html.

Each run starts from the reference two_phase optimum of the textbook LP
max 3x + 2y, x + y <= 4, 2x + y <= 6, adds one cut with the reference add_constraint,
and re-optimises with the reference dual_simplex. The pivots are recorded by wrapping the
pivot function dual_simplex calls, so every tableau shown is one the reference produced.
`uv run co viz 03` writes units/03-duality/viz-data.js.
"""

from __future__ import annotations

from fractions import Fraction as F

from colib import ref

L3 = ref.unit("03")
L2 = ref.unit("02")

A = [[1, 1], [2, 1]]
B = [4, 6]
C = [3, 2]


def fmt(v) -> str:
    v = F(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def row_text(a, beta):
    terms = []
    for k, name in zip(a, ("x", "y")):
        if k == 0:
            continue
        mag = "" if abs(k) == 1 else fmt(abs(k))
        terms.append(("−" if k < 0 else "+") + " " + mag + name)
    s = " ".join(terms).lstrip("+ ").replace("− ", "−", 1) if terms else "0"
    return f"{s} ≤ {fmt(beta)}"


def point_of(T, basis, n=2):
    x = [F(0)] * n
    for i, j in enumerate(basis):
        if j < n:
            x[j] = T[i][-1]
    return x


def trace_cut(cut, beta):
    base = L2.two_phase([[F(v) for v in r] for r in A], [F(v) for v in B], [F(v) for v in C])
    T0, basis0 = L3.add_constraint(base, [F(v) for v in cut], F(beta))
    names = ["x", "y", "s1", "s2", "s3"]

    def state(T, basis, note, explain="", row=None, col=None, ratios=None):
        x = point_of(T, basis)
        return {
            "tableau": [[fmt(v) for v in r] for r in T],
            "basis": [names[j] for j in basis],
            "point": [float(v) for v in x], "point_exact": [fmt(v) for v in x],
            "z": fmt(T[-1][-1]), "leave": row, "enter": col, "ratios": ratios,
            "duals": [fmt(T[-1][2 + i]) for i in range(len(T) - 1)],
            "note": note, "explain": explain,
        }

    pivots = []
    original = L2.pivot

    def recording_pivot(T, basis, r, s):
        m, width = len(T) - 1, len(T[0]) - 1
        ratios = [fmt(T[m][j] / -T[r][j]) if j < width and T[r][j] < 0 else None for j in range(width + 1)]
        pivots.append(state(T, basis, f"{names[basis[r]]} leaves (most negative rhs), {names[s]} enters (smallest ratio)",
                            "", r, s, ratios))
        return original(T, basis, r, s)

    L2.pivot = recording_pivot
    try:
        result = L3.dual_simplex(T0, basis0, 2)
    finally:
        L2.pivot = original

    states = [state(base.tableau, list(base.basis), "the optimum before the cut",
                    "The primal simplex of unit 02 stopped here: no negative entry in the objective row, "
                    "every rhs ≥ 0. The slack columns of the objective row are the duals.")]
    cut_explain = ("Added in the current basis, the cut's row has the basic variables eliminated, so the objective row "
                   "is untouched and still ≥ 0: the basis stays dual feasible. Only the new rhs can be negative.")
    ratio_explain = (" The dual simplex takes the row with the most negative rhs out, and among that row's negative "
                     "entries the column with the smallest ratio, objective-row entry ÷ −(row entry), in. That choice "
                     "keeps the objective row ≥ 0 after the pivot.")
    if pivots:
        pivots[0]["note"] = "the cut, in the current basis: " + pivots[0]["note"]
        pivots[0]["explain"] = cut_explain + ratio_explain
        states += pivots
    if result.status == "optimal":
        if not pivots:
            states.append(state(T0, basis0, "the cut is already satisfied", cut_explain))
        states.append(state(result.tableau, list(result.basis), "optimal again: every rhs ≥ 0, objective row still ≥ 0",
                            "One pivot restored primal feasibility without touching dual feasibility. The new slack "
                            "columns of the objective row are the new duals."))
    else:
        T, basis = result.tableau, list(result.basis)
        r = min((i for i in range(len(T) - 1) if T[i][-1] < 0), key=lambda i: (T[i][-1], i))
        st = state(T, basis, f"infeasible: row {names[basis[r]]} has rhs < 0 and no negative entry", "", r, None)
        st["infeasible"] = True
        st["explain"] = (cut_explain + " Here that row reads (nonnegative entries) · (variables ≥ 0) = negative, "
                         "which no point satisfies: the dual simplex stops and reports the LP infeasible. "
                         "The row's multipliers are a Farkas certificate.")
        states.append(st)
    return {"cut": [list(cut), float(beta)], "cut_text": row_text(cut, beta), "status": result.status,
            "pivots": result.pivots, "states": states}


RUNS = [
    ("cut-x", "Cut x ≤ 1.5 (the deck's example)", (1, 0), F(3, 2)),
    ("cut-x1", "Cut x ≤ 1", (1, 0), F(1)),
    ("cut-y", "Cut y ≤ 1", (0, 1), F(1)),
    ("cut-infeasible", "Cut x + y ≥ 5: nothing is left", (-1, -1), F(-5)),
]


def data():
    out = {"lp": {"A": A, "b": B, "c": C}}
    for key, title, cut, beta in RUNS:
        run = trace_cut(cut, beta)
        run["title"] = title
        out[key] = run
    return out
