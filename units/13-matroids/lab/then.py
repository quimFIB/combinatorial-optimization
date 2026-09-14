"""Unit 13 — "Then": generic greedy against specialised code, and greedy's real ratio.

  1. Greedy with your graphic-matroid oracle against networkx's Kruskal on random
     graphs: the same forest, and what calling a generic oracle costs.
  2. Matroid intersection of two partition matroids against Hopcroft–Karp.
  3. Greedy maximum coverage against the exact optimum (HiGHS MIP) on instances
     too big to enumerate: the worst-case bound is 1 - 1/e = 0.632; the typical
     ratio is much better.

    uv run co then 13
"""

import math
import random
import time

import networkx as nx

from colib.mip import MILP, highs_mip
from colib.testing import load_lab

lab = load_lab(__file__)


def part1():
    print("\n1 · Maximum spanning forest: generic greedy + your oracle vs networkx Kruskal")
    print(f"   {'vertices':>9}{'edges':>7}{'same weight':>13}{'greedy s':>10}{'networkx s':>12}")
    for n in (30, 60, 120):
        r = random.Random(n)
        E = [(u, v) for u in range(n) for v in range(u + 1, n) if r.random() < 0.3]
        w = [r.randint(1, 1000) for _ in E]
        t = time.perf_counter()
        S = lab.greedy(len(E), w, lab.graphic(n, E))
        tg = time.perf_counter() - t
        G = nx.Graph()
        G.add_weighted_edges_from((u, v, wt) for (u, v), wt in zip(E, w))
        t = time.perf_counter()
        T = nx.maximum_spanning_tree(G)
        tn = time.perf_counter() - t
        same = sum(w[e] for e in S) == T.size(weight="weight")
        print(f"   {n:>9}{len(E):>7}{str(same):>13}{tg:>10.3f}{tn:>12.4f}")
    print("   The oracle rebuilds a union-find per call; Kruskal keeps one. Generality has a price.")


def part2():
    print("\n2 · Bipartite matching as intersection of two partition matroids vs Hopcroft–Karp")
    print(f"   {'side':>6}{'edges':>7}{'same size':>11}{'intersection s':>16}{'networkx s':>12}")
    for side in (8, 16, 24):
        r = random.Random(side)
        E = [(i, j) for i in range(side) for j in range(side) if r.random() < 0.2]
        m1 = lab.partition([i for i, _ in E], [1] * side)
        m2 = lab.partition([j for _, j in E], [1] * side)
        t = time.perf_counter()
        I = lab.intersection(len(E), m1, m2)
        ti = time.perf_counter() - t
        G = nx.Graph()
        G.add_edges_from((("l", i), ("r", j)) for i, j in E)
        t = time.perf_counter()
        M = nx.bipartite.maximum_matching(G, top_nodes=[v for v in G if v[0] == "l"])
        tn = time.perf_counter() - t
        print(f"   {side:>6}{len(E):>7}{str(len(I) == len(M) // 2):>11}{ti:>16.3f}{tn:>12.4f}")


def coverage_opt(sets, universe, k):
    """max coverage as a MILP: y_i choose set i, z_u element covered."""
    m = len(sets)
    n = m + universe
    rows = [tuple([-1 if u in sets[i] else 0 for i in range(m)] + [1 if v == u else 0 for v in range(universe)])
            for u in range(universe)]
    card = tuple([1] * m + [0] * universe)
    milp = MILP(c=tuple([0] * m + [-1] * universe), A_ub=tuple(rows) + (card,),
                b_ub=tuple([0] * universe + [k]), ub=(1,) * n, integer=(True,) * m + (False,) * universe)
    return -highs_mip(milp, options={"mip_rel_gap": 0.0}).value


def part3():
    print("\n3 · Greedy max coverage vs the exact optimum (40 sets over 120 elements)")
    print(f"   {'k':>3}{'instances':>11}{'mean ratio':>12}{'worst ratio':>13}{'bound':>8}")
    for k in (3, 6, 10):
        ratios = []
        for seed in range(15):
            r = random.Random(1000 * k + seed)
            sets = [set(r.sample(range(120), r.randint(3, 15))) for _ in range(40)]
            chosen = lab.greedy_coverage([sorted(s) for s in sets], k)
            got = len(set().union(*(sets[i] for i in chosen)))
            ratios.append(got / coverage_opt(sets, 120, k))
        print(f"   {k:>3}{len(ratios):>11}{sum(ratios) / len(ratios):>12.3f}{min(ratios):>13.3f}{1 - 1 / math.e:>8.3f}")
    print("   Tight examples for 1 - 1/e exist, but have to be built: random instances sit far above it.")


if __name__ == "__main__":
    part1()
    part2()
    part3()
