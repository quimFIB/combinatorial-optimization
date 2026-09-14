"""Unit 14 — "Then": your flow algorithms against OR-Tools and networkx.

  1. Max flow on three families — layered, random sparse, bipartite
     matching networks — for Edmonds–Karp, Dinic and push–relabel, against
     OR-Tools' SimpleMaxFlow and networkx. Which family favours which algorithm.
  2. Min-cost flow against OR-Tools' SimpleMinCostFlow.

    uv run co then 14
"""

import random
import time

import networkx as nx
from ortools.graph.python import max_flow as ort_max_flow
from ortools.graph.python import min_cost_flow as ort_min_cost_flow

from colib.testing import load_lab

lab = load_lab(__file__)


def layered(layers, width, seed):
    r = random.Random(seed)
    n = 2 + layers * width
    node = lambda l, i: 1 + l * width + i
    arcs = [(0, node(0, i), r.randint(5, 20)) for i in range(width)]
    for l in range(layers - 1):
        for i in range(width):
            for j in r.sample(range(width), 3):
                arcs.append((node(l, i), node(l + 1, j), r.randint(1, 10)))
    arcs += [(node(layers - 1, i), n - 1, r.randint(5, 20)) for i in range(width)]
    return n, arcs


def sparse(n, degree, seed):
    """Random sparse digraph; the source and sink each touch n/10 nodes so the flow is not trivial."""
    r = random.Random(seed)
    arcs = [(u, v, r.randint(1, 20)) for u in range(1, n - 1) for v in r.sample(range(1, n - 1), degree) if u != v]
    arcs += [(0, v, r.randint(10, 40)) for v in r.sample(range(1, n - 1), n // 10)]
    arcs += [(u, n - 1, r.randint(10, 40)) for u in r.sample(range(1, n - 1), n // 10)]
    return n, arcs


def bipartite(side, p, seed):
    r = random.Random(seed)
    n = 2 * side + 2
    arcs = [(0, 1 + i, 1) for i in range(side)] + [(1 + side + j, n - 1, 1) for j in range(side)]
    arcs += [(1 + i, 1 + side + j, 1) for i in range(side) for j in range(side) if r.random() < p]
    return n, arcs


def timed(f, *a):
    t = time.perf_counter()
    out = f(*a)
    return out, time.perf_counter() - t


def ortools_value(n, arcs):
    solver = ort_max_flow.SimpleMaxFlow()
    for u, v, c in arcs:
        solver.add_arc_with_capacity(u, v, c)
    solver.solve(0, n - 1)
    return solver.optimal_flow()


def nx_value(n, arcs):
    G = nx.DiGraph()
    for u, v, c in arcs:
        G.add_edge(u, v, capacity=G[u][v]["capacity"] + c if G.has_edge(u, v) else c)
    return nx.maximum_flow_value(G, 0, n - 1)


def part1():
    print("\n1 · Max flow (seconds; all values agree unless marked)")
    print(f"   {'family':<24}{'arcs':>7}{'EK':>8}{'Dinic':>8}{'push-rel':>10}{'OR-Tools':>10}{'networkx':>10}")
    cases = [("layered 20x30", layered(20, 30, 1)), ("layered 40x40", layered(40, 40, 2)),
             ("random n=600 deg 6", sparse(600, 6, 3)), ("random n=1500 deg 6", sparse(1500, 6, 4)),
             ("bipartite 150x150", bipartite(150, 0.05, 5)), ("bipartite 300x300", bipartite(300, 0.03, 6))]
    for name, (n, arcs) in cases:
        (ek, _), t_ek = timed(lab.edmonds_karp, n, arcs, 0, n - 1)
        (di, _), t_di = timed(lab.dinic, n, arcs, 0, n - 1)
        (pr, _), t_pr = timed(lab.push_relabel, n, arcs, 0, n - 1)
        ort, t_or = timed(ortools_value, n, arcs)
        nxv, t_nx = timed(nx_value, n, arcs)
        agree = len({ek, di, pr, ort, nxv}) == 1
        print(f"   {name:<24}{len(arcs):>7}{t_ek:>8.3f}{t_di:>8.3f}{t_pr:>10.3f}{t_or:>10.4f}{t_nx:>10.3f}"
              f"{'' if agree else '   DISAGREE'}")


def part2():
    print("\n2 · Min-cost flow: yours vs OR-Tools (random networks, demand = half the max flow)")
    print(f"   {'nodes':>6}{'arcs':>7}{'demand':>8}{'same cost':>11}{'yours s':>9}{'OR-Tools s':>12}")
    for n in (60, 150, 300):
        r = random.Random(n)
        seen, arcs = set(), []
        for u in range(n):
            for v in r.sample(range(n), 5 if u not in (0, n - 1) else n // 5):
                if u != v and (u, v) not in seen and v != 0 and u != n - 1:
                    seen.add((u, v))
                    arcs.append((u, v, r.randint(1, 15), r.randint(0, 30)))
        arcs += [(u, n - 1, 20, 0) for u in r.sample(range(1, n - 1), n // 5) if (u, n - 1) not in seen]
        top, _ = lab.dinic(n, [a[:3] for a in arcs], 0, n - 1)
        demand = max(1, top // 2)
        mine, t_m = timed(lab.min_cost_flow, n, arcs, 0, n - 1, demand)
        smcf = ort_min_cost_flow.SimpleMinCostFlow()
        for u, v, c, w in arcs:
            smcf.add_arc_with_capacity_and_unit_cost(u, v, c, w)
        smcf.set_node_supply(0, demand)
        smcf.set_node_supply(n - 1, -demand)
        t = time.perf_counter()
        smcf.solve()
        t_o = time.perf_counter() - t
        print(f"   {n:>6}{len(arcs):>7}{demand:>8}{str(mine[0] == smcf.optimal_cost()):>11}{t_m:>9.3f}{t_o:>12.4f}")


if __name__ == "__main__":
    part1()
    part2()
