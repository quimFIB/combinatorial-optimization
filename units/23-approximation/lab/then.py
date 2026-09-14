"""Unit 23 — "Then": actual ratios against CP-SAT-proved optima, next to the guarantees.

  1. Greedy set cover on random instances, and on the tight family.
  2. The matching cover for vertex cover, and farthest-first k-center.
  3. Metric TSP: double tree and Christofides against the optimal tour.
  4. Makespan: list scheduling and LPT.

    uv run co then 23
"""

import random
import statistics
import time
from fractions import Fraction

from ortools.sat.python import cp_model

from colib.approx import metric_tsp, random_processing_times
from colib.problems import SetCover, VertexCover
from colib.testing import load_lab

lab = load_lab(__file__)


def solver(limit=60):
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = limit
    return s


def summary(ratios, guarantee):
    return (f"mean {statistics.mean(ratios):.3f}   max {max(ratios):.3f}   "
            f"guarantee {guarantee}")


def cpsat_set_cover(sc):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(sc.n)]
    for e in range(sc.universe):
        m.add_bool_or([x[i] for i, s in enumerate(sc.sets) if e in s])
    m.minimize(sum(c * xi for c, xi in zip(sc.costs, x)))
    s = solver()
    assert s.solve(m) == cp_model.OPTIMAL
    return round(s.objective_value)


def random_set_cover(universe, nsets, seed):
    r = random.Random(seed)
    sets = [set(r.sample(range(universe), r.randint(2, universe // 6))) for _ in range(nsets)]
    for e in range(universe):
        if not any(e in s for s in sets):
            sets[r.randrange(nsets)].add(e)
    return SetCover(universe, tuple(frozenset(s) for s in sets),
                    tuple(len(s) + r.randint(0, 10) for s in sets))


def set_cover():
    print("1. Greedy set cover (120 elements, 80 sets, costs about the set size)\n")
    ratios, bounds = [], []
    for seed in range(20):
        sc = random_set_cover(120, 80, seed)
        x, _ = lab.greedy_set_cover(sc)
        ratios.append(sc.objective(x) / cpsat_set_cover(sc))
        bounds.append(float(lab.harmonic(max(len(s) for s in sc.sets))))
    print(f"  20 instances: {summary(ratios, f'H_d = {min(bounds):.2f} to {max(bounds):.2f}')}")
    print("\n  the tight family:")
    for n in (4, 8, 12, 16):
        sc = lab.greedy_tight_instance(n)
        x, _ = lab.greedy_set_cover(sc)
        print(f"    n = {n:>2}: greedy / optimum = {sc.objective(x) / (sc.costs[-1]):.3f}   H_n = {float(lab.harmonic(n)):.3f}")


def cpsat_vertex_cover(vc):
    m = cp_model.CpModel()
    x = [m.new_bool_var("") for _ in range(vc.n)]
    for a, b in vc.edges:
        m.add_bool_or([x[a], x[b]])
    m.minimize(sum(x))
    s = solver()
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def cpsat_k_center(dist, k):
    """Smallest radius among the distinct distances for which k balls cover every point (binary search)."""
    n = len(dist)
    radii = sorted({d for row in dist for d in row})
    lo, hi = 0, len(radii) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        m = cp_model.CpModel()
        y = [m.new_bool_var("") for _ in range(n)]
        m.add(sum(y) <= k)
        for v in range(n):
            m.add_bool_or([y[c] for c in range(n) if dist[v][c] <= radii[mid]])
        if solver().solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            hi = mid
        else:
            lo = mid + 1
    return radii[lo]


def packing_bounds():
    print("\n2. Lower bounds from packings\n")
    print("  vertex cover by maximal matching, G(n, p):")
    for n, p in ((50, 0.1), (100, 0.05), (150, 0.03), (200, 0.02)):
        ratios = []
        for seed in range(5):
            vc = VertexCover.random(n, seed=seed, p=p)
            cover, matching = lab.matching_vertex_cover(vc)
            opt, proven = cpsat_vertex_cover(vc)
            assert proven
            ratios.append(sum(cover) / opt)
        print(f"    G({n}, {p}): {summary(ratios, 2)}")
    print("\n  k-center by farthest-first, 80 points:")
    for k in (3, 6, 10):
        ratios = []
        for seed in range(5):
            dist = metric_tsp(80, seed).dist
            _, radius, _ = lab.k_center(dist, k)
            ratios.append(radius / cpsat_k_center(dist, k))
        print(f"    k = {k:>2}: {summary(ratios, 2)}")


def cpsat_tsp(dist):
    n = len(dist)
    m = cp_model.CpModel()
    arcs, cost = [], []
    for i in range(n):
        for j in range(n):
            if i != j:
                b = m.new_bool_var("")
                arcs.append((i, j, b))
                cost.append(dist[i][j] * b)
    m.add_circuit(arcs)
    m.minimize(sum(cost))
    s = solver(120)
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def tsp():
    print("\n3. Metric TSP: 10 instances per size, ratios to the CP-SAT optimum\n")
    print(f"  {'n':>3} {'double tree':>24} {'Christofides':>24} {'MST/opt':>9} {'matching/opt':>13} {'opt s':>6}")
    for n in (20, 40, 60):
        dt, ch, mst, mat, secs = [], [], [], [], []
        for seed in range(10):
            dist = metric_tsp(n, seed).dist
            t = time.perf_counter()
            opt, proven = cpsat_tsp(dist)
            secs.append(time.perf_counter() - t)
            assert proven, f"n={n} seed={seed} not proven"
            tour, w = lab.double_tree(dist)
            dt.append(sum(dist[tour[i]][tour[i - 1]] for i in range(n)) / opt)
            tour, w, mw = lab.christofides(dist)
            ch.append(sum(dist[tour[i]][tour[i - 1]] for i in range(n)) / opt)
            mst.append(w / opt)
            mat.append(mw / opt)
        print(f"  {n:>3}   mean {statistics.mean(dt):.3f} max {max(dt):.3f}   mean {statistics.mean(ch):.3f} "
              f"max {max(ch):.3f} {statistics.mean(mst):>9.3f} {statistics.mean(mat):>13.3f} {statistics.mean(secs):>6.1f}")


def cpsat_makespan(p, machines):
    m = cp_model.CpModel()
    x = [[m.new_bool_var("") for _ in range(machines)] for _ in p]
    C = m.new_int_var(0, sum(p), "C")
    for j in range(len(p)):
        m.add_exactly_one(x[j])
    for i in range(machines):
        m.add(sum(p[j] * x[j][i] for j in range(len(p))) <= C)
    m.minimize(C)
    s = solver()
    status = s.solve(m)
    return round(s.objective_value), status == cp_model.OPTIMAL


def scheduling():
    print("\n4. Makespan on identical machines, 20 instances each, times uniform in 1..100\n")
    for n, machines in ((12, 3), (30, 5), (60, 10)):
        ls, lp = [], []
        for seed in range(20):
            p = random_processing_times(n, seed)
            opt, proven = cpsat_makespan(p, machines)
            assert proven
            ls.append(lab.list_scheduling(p, machines)[0] / opt)
            lp.append(lab.lpt(p, machines)[0] / opt)
        print(f"  n = {n:>2}, m = {machines:>2}   list scheduling: {summary(ls, f'{2 - 1 / machines:.3f}')}")
        print(f"  {'':>15} LPT:             {summary(lp, f'{4 / 3 - 1 / (3 * machines):.3f}')}")
    print("\n  the tight families:")
    for machines in (3, 5, 10):
        p = lab.list_scheduling_tight(machines)
        q = lab.lpt_tight(machines)
        print(f"    m = {machines:>2}: list scheduling {lab.list_scheduling(p, machines)[0]}/{machines}"
              f" = {lab.list_scheduling(p, machines)[0] / machines:.3f}   LPT {lab.lpt(q, machines)[0]}/{3 * machines}"
              f" = {lab.lpt(q, machines)[0] / (3 * machines):.3f}")


if __name__ == "__main__":
    set_cover()
    packing_bounds()
    tsp()
    scheduling()
