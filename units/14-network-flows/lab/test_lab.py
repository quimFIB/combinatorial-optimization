"""Tests for unit 14. Run with `uv run co test 14`. You should not need to edit this."""

import itertools
import random

import networkx as nx
import pytest

from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def network(seed, n=8, p=0.4, cost=False):
    r = random.Random(seed)
    arcs = []
    for u in range(n):
        for v in range(n):
            if u != v and r.random() < p:
                arcs.append((u, v, r.randint(1, 10)) + ((r.randint(0, 9),) if cost else ()))
    return n, arcs


def nx_max_flow(n, arcs, s, t):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for u, v, c, *_ in arcs:
        G.add_edge(u, v, capacity=G[u][v]["capacity"] + c if G.has_edge(u, v) else c)
    return nx.maximum_flow_value(G, s, t)


def assert_valid_flow(n, arcs, s, t, value, flow):
    assert len(flow) == len(arcs)
    assert all(0 <= f <= c for (u, v, c, *_), f in zip(arcs, flow)), "capacity violated"
    for x in range(n):
        if x in (s, t):
            continue
        inflow = sum(f for (u, v, *_), f in zip(arcs, flow) if v == x)
        outflow = sum(f for (u, v, *_), f in zip(arcs, flow) if u == x)
        assert inflow == outflow, f"conservation violated at {x}"
    net_out = sum(f for (u, v, *_), f in zip(arcs, flow) if u == s) - sum(f for (u, v, *_), f in zip(arcs, flow) if v == s)
    assert net_out == value


ALGORITHMS = ["edmonds_karp", "dinic", "push_relabel"]


# ---------------------------------------------------------------- step 1 ---

def test_step1_textbook_network():
    arcs = [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 3), (2, 3, 2)]     # max flow 5
    value, flow = lab.edmonds_karp(4, arcs, 0, 3)
    assert value == 5
    assert_valid_flow(4, arcs, 0, 3, value, flow)
    S = lab.min_cut(4, arcs, flow, 0)
    assert 0 in S and 3 not in S and sum(c for u, v, c in arcs if u in S and v not in S) == 5


@pytest.mark.parametrize("seed", range(30))
def test_step1_edmonds_karp_and_its_certificate(seed):
    n, arcs = network(seed)
    value, flow = lab.edmonds_karp(n, arcs, 0, n - 1)
    assert value == nx_max_flow(n, arcs, 0, n - 1)
    assert_valid_flow(n, arcs, 0, n - 1, value, flow)
    S = set(lab.min_cut(n, arcs, flow, 0))
    assert 0 in S and n - 1 not in S
    assert sum(c for u, v, c in arcs if u in S and v not in S) == value, "max-flow = min-cut certificate"


def test_step1_parallel_arcs_and_no_path():
    arcs = [(0, 1, 2), (0, 1, 3), (1, 2, 4)]
    assert lab.edmonds_karp(3, arcs, 0, 2)[0] == 4
    assert lab.edmonds_karp(3, [(1, 0, 5), (2, 1, 5)], 0, 2)[0] == 0


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(30))
def test_step2_dinic(seed):
    n, arcs = network(100 + seed, n=10, p=0.35)
    with time_limit(20):
        value, flow = lab.dinic(n, arcs, 0, n - 1)
    assert value == nx_max_flow(n, arcs, 0, n - 1)
    assert_valid_flow(n, arcs, 0, n - 1, value, flow)


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(30))
def test_step3_push_relabel(seed):
    n, arcs = network(200 + seed, n=10, p=0.35)
    with time_limit(20, "Does every relabel strictly raise the height?"):
        value, flow = lab.push_relabel(n, arcs, 0, n - 1)
    assert value == nx_max_flow(n, arcs, 0, n - 1)
    assert_valid_flow(n, arcs, 0, n - 1, value, flow)


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(30))
def test_step4_min_cost_flow(seed):
    n, arcs = network(300 + seed, cost=True)
    seen, simple = set(), []
    for a in arcs:
        if a[:2] not in seen:
            seen.add(a[:2])
            simple.append(a)
    top = nx_max_flow(n, simple, 0, n - 1)
    if top == 0:
        assert lab.min_cost_flow(n, simple, 0, n - 1, 1) is None
        return
    demand = max(1, top // 2)
    D = nx.DiGraph()
    D.add_nodes_from(range(n))
    for u, v, c, w in simple:
        D.add_edge(u, v, capacity=c, weight=w)
    D.nodes[0]["demand"], D.nodes[n - 1]["demand"] = -demand, demand
    want = nx.cost_of_flow(D, nx.min_cost_flow(D))
    got = lab.min_cost_flow(n, simple, 0, n - 1, demand)
    assert got is not None and got[0] == want
    cost, flow = got
    assert sum(f * w for (u, v, c, w), f in zip(simple, flow)) == cost
    assert_valid_flow(n, simple, 0, n - 1, demand, flow)
    assert lab.min_cost_flow(n, simple, 0, n - 1, top + 1) is None


def test_step4_negative_costs_without_negative_cycles():
    arcs = [(0, 1, 2, 5), (0, 2, 2, 1), (2, 1, 2, -3), (1, 3, 3, 1), (2, 3, 1, 4)]
    cost, flow = lab.min_cost_flow(4, arcs, 0, 3, 3)
    D = nx.DiGraph()
    for u, v, c, w in arcs:
        D.add_edge(u, v, capacity=c, weight=w)
    D.nodes[0]["demand"], D.nodes[3]["demand"] = -3, 3
    assert cost == nx.cost_of_flow(D, nx.min_cost_flow(D))


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(40))
def test_step5_project_selection(seed):
    r = random.Random(seed)
    k = 8
    profit = [r.randint(-12, 12) for _ in range(k)]
    requires = [(p, q) for p in range(k) for q in range(k) if p != q and r.random() < 0.15]
    closed = lambda S: all(q in S for p, q in requires if p in S)
    best = max(sum(profit[i] for i in S) for m in range(k + 1) for S in itertools.combinations(range(k), m)
               if closed(set(S)))
    value, chosen = lab.project_selection(profit, requires)
    chosen = set(chosen)
    assert value == best and closed(chosen) and sum(profit[i] for i in chosen) == value
