"""Unit 06 — "Then": integrality for free, and where it stops.

  1. Assignment as a plain LP (HiGHS simplex, no integrality) against
     scipy.optimize.linear_sum_assignment, at growing n: always integral, and
     how much the special-purpose algorithm is worth.
  2. Maximum matching LP on random graphs: how often the LP optimum is
     fractional on non-bipartite graphs, and that fractional values are always 1/2.
  3. Your brute-force TU test as the matrix grows: why real TU recognition
     uses Seymour's decomposition instead.

    uv run co then 06
"""

import random
import time

import networkx as nx
import numpy as np
from scipy.optimize import linear_sum_assignment

from colib.solvers import highs_lp
from colib.testing import load_lab

lab = load_lab(__file__)


def part1():
    print("\n1 · Assignment: LP with no integrality vs the Hungarian-style solver")
    print(f"   {'n':>5}{'LP integral?':>14}{'same optimum':>14}{'LP s':>9}{'lsa s':>9}")
    for n in (20, 50, 100, 150):
        C = np.random.default_rng(n).integers(1, 1000, (n, n))
        t = time.perf_counter()
        X = lab.assignment_lp(C.tolist())
        t_lp = time.perf_counter() - t
        t = time.perf_counter()
        r, c = linear_sum_assignment(C)
        t_lsa = time.perf_counter() - t
        integral = np.allclose(X, np.round(X), atol=1e-7)
        same = abs((C * X).sum() - C[r, c].sum()) < 1e-6
        print(f"   {n:>5}{str(integral):>14}{str(same):>14}{t_lp:>9.3f}{t_lsa:>9.4f}")
    print("   Integrality costs nothing to get; the dedicated O(n^3) algorithm is still far faster (unit 15).")


def part2():
    print("\n2 · Maximum matching LP (degree <= 1, no integrality) on random graphs, 12 vertices")
    stats = {True: [0, 0], False: [0, 0]}
    values = set()
    graphs = [nx.gnp_random_graph(12, 0.3, seed=s) for s in range(200)]
    graphs += [nx.convert_node_labels_to_integers(nx.bipartite.random_graph(6, 6, 0.4, seed=s)) for s in range(200)]
    for G in graphs:
        edges = list(G.edges())
        if not edges:
            continue
        A = lab.incidence_matrix(12, edges)
        res = highs_lp(A, [1] * 12, [1] * len(edges), sense="max")
        x = np.array(res.x)
        fractional = not np.allclose(x, np.round(x), atol=1e-7)
        values |= {round(float(v), 6) for v in x if 1e-7 < v < 1 - 1e-7}
        b = nx.is_bipartite(G)
        stats[b][0] += 1
        stats[b][1] += fractional
    for b in (True, False):
        total, frac = stats[b]
        print(f"   {'bipartite' if b else 'non-bipartite':<15} {total:>4} graphs, LP vertex fractional on {frac:>4}")
    print(f"   fractional values seen: {sorted(values) or 'none'}   (the matching LP polytope is half-integral)")


def part3():
    print("\n3 · Brute-force TU check: time vs size (random 0/±1 matrices that are TU: interval matrices)")
    print(f"   {'m x n':>8}{'square submatrices':>20}{'seconds':>10}")
    for k in (4, 6, 8, 9, 10):
        r = random.Random(k)
        intervals = [tuple(sorted(r.sample(range(k + 1), 2))) for _ in range(k)]
        A = lab.interval_matrix(k, intervals)
        count = sum(__import__("math").comb(k, s) ** 2 for s in range(1, k + 1))
        t = time.perf_counter()
        ok = lab.is_tu(A)
        dt = time.perf_counter() - t
        print(f"   {f'{k}x{k}':>8}{count:>20,}{dt:>10.3f}   {'TU' if ok else 'not TU'}")
    print("   Exponential. Seymour's decomposition theorem gives a polynomial test (Truemper's algorithm),")
    print("   but in modelling you recognise TU structure (flows, intervals, bipartite) rather than test for it.")


if __name__ == "__main__":
    part1()
    part2()
    part3()
