"""Unit 09 lab — subtour elimination.  REFERENCE SOLUTION, functional.

Components are a fixpoint of label propagation. Stoer–Wagner is an unfold over
contracted graphs, each phase a fold that builds the maximum-adjacency order.
Both lazy loops are unfolds over the growing set of cuts.
"""

from __future__ import annotations

from dataclasses import replace
from functools import reduce

import toolz as tz

from colib.mip import highs_mip, lp_relaxation
from colib.tsp import degree_milp, edges, tour_from_edges


# ---------------------------------------------------------------- step 1 ---

def subtour_row(n, S):
    S = frozenset(S)
    return tuple(-1 if (i in S) != (j in S) else 0 for i, j in edges(n)), -2


def components(n, x, eps=1e-6):
    support = [(i, j) for (i, j), v in zip(edges(n), x) if v > eps]

    def relabel(labels):
        return tz.reduce(lambda lab, e: {**lab, e[0]: min(lab[e[0]], lab[e[1]]), e[1]: min(lab[e[0]], lab[e[1]])},
                         support, labels)

    labels = tz.iterate(relabel, {v: v for v in range(n)})
    fixpoint = next(b for a, b in tz.sliding_window(2, labels) if a == b)
    groups = tz.groupby(lambda v: fixpoint[v], range(n))
    return [tuple(sorted(vs)) for _, vs in sorted(groups.items())]


# ---------------------------------------------------------------- step 2 ---

def min_cut(n, x):
    weight = {(i, j): v for (i, j), v in zip(edges(n), x)}
    w0 = {frozenset((i, j)): v for (i, j), v in weight.items()}

    def phase(state):
        """One Stoer–Wagner phase: order, record the cut of the phase, merge the last two."""
        groups, w, best = state
        active = sorted(groups)

        def add(acc, _):
            order, attached = acc
            rest = [v for v in active if v not in order]
            u = max(rest, key=lambda v: (attached[v], -v))
            return order + (u,), {v: attached[v] + w.get(frozenset((u, v)), 0.0) for v in attached}

        order, attached = reduce(add, range(len(active)), ((), {v: 0.0 for v in active}))
        s, t = order[-2], order[-1]
        cut = sum(w.get(frozenset((t, v)), 0.0) for v in active if v != t)
        best = min(best, (cut, tuple(sorted(groups[t]))), key=lambda p: p[0])
        merged_w = tz.merge_with(sum, *({frozenset((s if a == t else a, s if b == t else b)): val}
                                       for (a, b), val in ((tuple(k), v) for k, v in w.items()) if {a, b} != {s, t}))
        new_groups = {**{k: v for k, v in groups.items() if k != t}, s: groups[s] + groups[t]}
        return new_groups, merged_w, best

    start = ({v: (v,) for v in range(n)}, w0, (float("inf"), None))
    final = next(st for st in tz.iterate(phase, start) if len(st[0]) == 1)
    return final[2]


# ---------------------------------------------------------------- step 3 ---

def separate_subtours(n, x, eps=1e-6):
    comps = components(n, x, eps)
    if len(comps) > 1:
        return comps
    value, S = min_cut(n, x)
    return [S] if value < 2 - eps else []


# ---------------------------------------------------------------- steps 4 and 5 ---

def lazy(milp, solve, separate, n):
    """Unfold: solve with the current cuts, separate, add. Stops when nothing is found."""
    def step(state):
        rows, solves, _, _ = state
        rhs = tuple(-2 for _ in rows)
        sol = solve(replace(milp, A_ub=tuple(rows), b_ub=rhs))
        found = separate(sol)
        return rows + tuple(subtour_row(n, S)[0] for S in found), solves + 1, sol, not found

    return next(s for s in tz.iterate(step, ((), 0, None, False)) if s[3])


def subtour_lp(tsp):
    n = tsp.n
    rows, solves, lp, _ = lazy(degree_milp(tsp, integer=False), lp_relaxation,
                               lambda lp: separate_subtours(n, lp.x), n)
    return lp.value, lp.x, len(rows), solves


def tsp_exact(tsp):
    n = tsp.n
    solve = lambda m: highs_mip(m, options={"mip_rel_gap": 0.0})
    separate = lambda sol: (lambda comps: comps if len(comps) > 1 else [])(components(n, sol.x, eps=0.5))
    rows, solves, sol, _ = lazy(degree_milp(tsp, integer=True), solve, separate, n)
    return round(sol.value), tour_from_edges(n, sol.x), len(rows), solves
