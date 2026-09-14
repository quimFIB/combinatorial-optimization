"""Unit 16 — "Then": three algorithms for TSP, a pseudo-polynomial wall, and treewidth made visible.

  1. Exact TSP for n = 8..20: your Held–Karp, unit 07's branch-and-bound on the
     MTZ formulation, unit 09's lazy subtour elimination (HiGHS), and SCIP on MTZ.
  2. Knapsack with the same items, weights scaled by 10^k: your DP's time grows with
     the capacity *value*; a MIP solver does not care.
  3. Vertex cover by your tree-decomposition DP on partial k-trees, k = 2..11:
     time against width, and a prediction from the table sizes, sum over bags of 2^|bag|.

    uv run co then 16
"""

import random
import time

from colib.graphs import partial_ktree
from colib.mip import MILP, highs_mip, scip_mip
from colib.problems import TSP
from colib.ref import unit
from colib.testing import load_lab

lab = load_lab(__file__)
BUDGET = 60.0                                                 # a method that takes longer is dropped


def timed(f, *args, **kw):
    t = time.perf_counter()
    out = f(*args, **kw)
    return out, time.perf_counter() - t


def mtz(tsp):
    """Directed MTZ: x_ij for i != j, then u_1..u_{n-1} in [1, n-1]."""
    n = tsp.n
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    col = {a: k for k, a in enumerate(arcs)}
    nv = len(arcs) + n - 1
    row = lambda: [0] * nv
    A_eq, b_eq = [], []
    for v in range(n):
        out, inn = row(), row()
        for w in range(n):
            if w != v:
                out[col[(v, w)]] = 1
                inn[col[(w, v)]] = 1
        A_eq += [out, inn]
        b_eq += [1, 1]
    A_ub, b_ub = [], []
    for i, j in arcs:
        if i and j:
            r = row()
            r[len(arcs) + i - 1], r[len(arcs) + j - 1], r[col[(i, j)]] = 1, -1, n - 1
            A_ub.append(r)
            b_ub.append(n - 2)
    c = [tsp.dist[i][j] for i, j in arcs] + [0] * (n - 1)
    return MILP(c=tuple(c), A_ub=tuple(map(tuple, A_ub)), b_ub=tuple(b_ub), A_eq=tuple(map(tuple, A_eq)),
                b_eq=tuple(b_eq), lb=(0,) * len(arcs) + (1,) * (n - 1), ub=(1,) * len(arcs) + (n - 1,) * (n - 1),
                integer=(True,) * len(arcs) + (False,) * (n - 1))


def tsp_race():
    print("1. Exact TSP, Euclidean, seconds  ('—' = dropped: over the time budget, or B&B hit 20 000 nodes)\n")
    bb, lazy = unit("07"), unit("09")
    alive = {"held_karp": True, "B&B (07)": True, "lazy DFJ (09)": True, "SCIP MTZ": True}
    print(f"  {'n':>3} {'optimum':>8} " + " ".join(f"{k:>14}" for k in alive) + f"  {'B&B nodes':>9}")
    for n in range(8, 21, 2):
        tsp = TSP.random(n, seed=n)
        cells, values, nodes = {}, [], "—"
        if alive["held_karp"]:
            (v, _), t = timed(lab.held_karp, tsp.dist)
            cells["held_karp"], alive["held_karp"] = t, t < BUDGET
            values.append(v)
        if alive["B&B (07)"]:
            res, t = timed(bb.branch_and_bound, mtz(tsp), node_limit=20_000)
            if res.status == "optimal":
                cells["B&B (07)"] = t
                values.append(round(res.value))
                nodes = res.nodes
            alive["B&B (07)"] = res.status == "optimal" and t < BUDGET
        if alive["lazy DFJ (09)"]:
            (v, *_), t = timed(lazy.tsp_exact, tsp)
            cells["lazy DFJ (09)"], alive["lazy DFJ (09)"] = t, t < BUDGET
            values.append(v)
        if alive["SCIP MTZ"]:
            res, t = timed(scip_mip, mtz(tsp), time_limit=BUDGET)
            if res.status == "optimal":
                cells["SCIP MTZ"] = t
                values.append(round(res.value))
            alive["SCIP MTZ"] = res.status == "optimal"
        assert len(set(values)) <= 1, values
        print(f"  {n:>3} {values[0] if values else '?':>8} "
              + " ".join(f"{cells[k]:>14.3f}" if k in cells else f"{'—':>14}" for k in alive) + f"  {nodes:>9}")


def pseudo_polynomial():
    print("\n2. Knapsack, 50 items, weights and capacity scaled by 10^k (seconds)\n")
    r = random.Random(1)
    values = [r.randint(10, 100) for _ in range(50)]
    base = [r.randint(10, 100) for _ in range(50)]
    print(f"  {'k':>2} {'capacity':>10} {'your DP':>9} {'HiGHS MIP':>10}  {'same value':>10}")
    for k in range(5):
        weights = [w * 10 ** k + r.randint(0, 10 ** k - 1) for w in base] if k else base
        C = sum(weights) // 3
        (v, _), t = timed(lab.knapsack, values, weights, C)
        milp = MILP(c=tuple(-x for x in values), A_ub=(tuple(weights),), b_ub=(C,), ub=(1,) * 50, integer=(True,) * 50)
        mip, tm = timed(highs_mip, milp, options={"mip_rel_gap": 0.0})
        print(f"  {k:>2} {C:>10} {t:>9.3f} {tm:>10.3f}  {str(v == -round(mip.value)):>10}")
        if t > BUDGET:
            break


def treewidth():
    print("\n3. Vertex cover on partial k-trees (n = 150, keep 70% of edges) by your decomposition DP\n")
    print(f"  {'k':>3} {'width':>5} {'bags':>5} {'sum 2^|bag|':>12} {'DP s':>8} {'predicted':>9} {'HiGHS s':>8}")
    rate = None
    for k in range(2, 12):
        n, edges = partial_ktree(150, k, keep=0.7, seed=k)
        weights = [random.Random(k).randint(1, 20) for _ in range(n)]
        (bags, te), _ = timed(lab.elimination_decomposition, n, edges)
        w = lab.width(bags)
        work = sum(2 ** len(b) for b in bags)
        (value, _), t = timed(lab.td_vertex_cover, n, edges, weights, bags, te)
        milp = MILP(c=tuple(weights), A_ub=tuple(tuple(-1 if v in e else 0 for v in range(n)) for e in edges),
                    b_ub=(-1,) * len(edges), ub=(1,) * n, integer=(True,) * n)
        mip, tm = timed(highs_mip, milp, options={"mip_rel_gap": 0.0})
        assert value == round(mip.value)
        predicted = "" if rate is None else f"{rate * work:>9.3f}"
        if k == 4:                                             # calibrate once, on a small instance
            rate = t / work
        print(f"  {k:>3} {w:>5} {len(bags):>5} {work:>12} {t:>8.3f} {predicted:>9} {tm:>8.3f}")
        if t > BUDGET:
            break


if __name__ == "__main__":
    tsp_race()
    pseudo_polynomial()
    treewidth()
