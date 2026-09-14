"""Unit 15 — "Then": your matching code against scipy, OR-Tools and networkx.

  1. Assignment: your Hungarian against scipy's linear_sum_assignment (a
     shortest-augmenting-path code in C, LAPJV-style) and OR-Tools'
     LinearSumAssignment (a cost-scaling push–relabel), and against the LP
     solved by HiGHS (unit 06: the assignment polytope is integral).
  2. Bipartite cardinality matching: your Hopcroft–Karp against networkx's.
  3. General matching: your blossom against networkx's max_weight_matching.

    uv run co then 15
"""

import random
import time

import networkx as nx
import numpy as np
from ortools.graph.python import linear_sum_assignment as ort_lsa
from scipy.optimize import linear_sum_assignment

from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)


def timed(f, *args):
    t = time.perf_counter()
    out = f(*args)
    return out, time.perf_counter() - t


def ortools_assignment(C):
    n = len(C)
    a = ort_lsa.SimpleLinearSumAssignment()
    for i in range(n):
        for j in range(n):
            a.add_arc_with_cost(i, j, int(C[i, j]))
    a.solve()
    return a.optimal_cost()


def lp_assignment(C):
    n = len(C)
    A = np.zeros((2 * n, n * n))
    for i in range(n):
        A[i, i * n:(i + 1) * n] = 1
        A[n + i, i::n] = 1
    info = highs_lp(A, np.ones(2 * n), C.flatten(), sense="min", row_lower=np.ones(2 * n))
    frac = int(np.sum((info.x > 1e-9) & (info.x < 1 - 1e-9)))
    return info.value, frac


def assignment():
    print("1. Assignment, costs uniform in 0..10^6 (seconds)\n")
    print(f"  {'n':>5} {'yours':>8} {'scipy':>8} {'OR-Tools':>9} {'HiGHS LP':>9}  {'all equal':>9}  fractional LP entries")
    for n in (50, 100, 200, 400):
        C = np.random.default_rng(n).integers(0, 10**6, (n, n))
        (_, mine, _, _), t_mine = timed(lab.hungarian, C.tolist())
        (r, c), t_sp = timed(linear_sum_assignment, C)
        ort, t_ort = timed(ortools_assignment, C)
        (lp, frac), t_lp = timed(lp_assignment, C.astype(float))
        same = mine == int(C[r, c].sum()) == ort == round(lp)
        print(f"  {n:>5} {t_mine:>8.3f} {t_sp:>8.4f} {t_ort:>9.4f} {t_lp:>9.3f}  {str(same):>9}  {frac}")


def bipartite():
    print("\n2. Bipartite cardinality matching, average degree 4 (seconds)\n")
    print(f"  {'side':>6} {'edges':>7} {'yours':>8} {'networkx':>9}  {'size':>6}")
    for side in (1000, 4000, 16000):
        r = random.Random(side)
        edges = list({(l, r.randrange(side)) for l in range(side) for _ in range(4)})
        m, t_mine = timed(lab.hopcroft_karp, side, side, edges)
        G = nx.Graph()
        G.add_nodes_from(range(2 * side))
        G.add_edges_from((l, side + rr) for l, rr in edges)
        nxm, t_nx = timed(nx.bipartite.hopcroft_karp_matching, G, range(side))
        assert len(m) == len(nxm) // 2
        print(f"  {side:>6} {len(edges):>7} {t_mine:>8.3f} {t_nx:>9.3f}  {len(m):>6}")


def general():
    print("\n3. General matching, random graphs with average degree 3 (seconds)\n")
    print(f"  {'n':>5} {'edges':>6} {'yours':>8} {'networkx':>9}  {'size':>5}  {'odd cycles mattered':>19}")
    for n in (200, 800, 2000):
        r = random.Random(n)
        edges = list({tuple(sorted(r.sample(range(n), 2))) for _ in range(3 * n // 2)})
        mate, t_mine = timed(lab.blossom, n, edges)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)
        nxm, t_nx = timed(nx.max_weight_matching, G, True)
        size = sum(x != -1 for x in mate) // 2
        assert size == len(nxm)
        # the bipartite algorithm on the double cover finds an upper bound; a gap means blossoms were needed
        B = nx.Graph()
        B.add_edges_from(((("a", u), ("b", v)) for a, b in edges for u, v in ((a, b), (b, a))))
        cover = len(nx.bipartite.hopcroft_karp_matching(B, [x for x in B if x[0] == "a"])) // 2
        print(f"  {n:>5} {len(edges):>6} {t_mine:>8.3f} {t_nx:>9.3f}  {size:>5}  {'yes' if cover / 2 > size else 'no':>19}")


if __name__ == "__main__":
    assignment()
    bipartite()
    general()
