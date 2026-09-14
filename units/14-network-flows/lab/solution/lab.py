"""Unit 14 lab — network flows.  REFERENCE SOLUTION, imperative.

A network is (n, arcs) with arcs a list of (u, v, capacity) — or (u, v,
capacity, cost) for min-cost flow — on nodes 0..n-1. Parallel arcs are allowed.
A flow is a list with one value per arc, in the same order.
"""

from __future__ import annotations

import heapq
from collections import deque


class Residual:
    """Residual graph: arc k is stored as edge 2k (forward) and 2k+1 (backward)."""

    def __init__(self, n, arcs):
        self.n = n
        self.to, self.cap, self.cost = [], [], []
        self.adj = [[] for _ in range(n)]
        for u, v, c, *rest in arcs:
            w = rest[0] if rest else 0
            self.adj[u].append(len(self.to))
            self.to.append(v), self.cap.append(c), self.cost.append(w)
            self.adj[v].append(len(self.to))
            self.to.append(u), self.cap.append(0), self.cost.append(-w)
        self.original = [c for _, _, c, *_ in arcs]

    def push(self, e, amount):
        self.cap[e] -= amount
        self.cap[e ^ 1] += amount

    def flows(self):
        return [self.original[k] - self.cap[2 * k] for k in range(len(self.original))]


# ---------------------------------------------------------------- step 1 ---

def edmonds_karp(n, arcs, s, t):
    R = Residual(n, arcs)
    value = 0
    while True:
        parent = [-1] * n
        parent[s] = -2
        queue = deque([s])
        while queue and parent[t] == -1:
            u = queue.popleft()
            for e in R.adj[u]:
                v = R.to[e]
                if R.cap[e] > 0 and parent[v] == -1:
                    parent[v] = e
                    queue.append(v)
        if parent[t] == -1:
            return value, R.flows()
        bottleneck, v = float("inf"), t
        while v != s:
            e = parent[v]
            bottleneck = min(bottleneck, R.cap[e])
            v = R.to[e ^ 1]
        v = t
        while v != s:
            e = parent[v]
            R.push(e, bottleneck)
            v = R.to[e ^ 1]
        value += bottleneck


def min_cut(n, arcs, flow, s):
    """The source side of a minimum cut: nodes reachable from s in the residual graph of `flow`."""
    residual = [[] for _ in range(n)]
    for (u, v, c, *_), f in zip(arcs, flow):
        if f < c:
            residual[u].append(v)
        if f > 0:
            residual[v].append(u)
    seen, queue = {s}, deque([s])
    while queue:
        u = queue.popleft()
        for v in residual[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return seen


# ---------------------------------------------------------------- step 2 ---

def dinic(n, arcs, s, t):
    R = Residual(n, arcs)
    value = 0
    while True:
        level = [-1] * n
        level[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for e in R.adj[u]:
                if R.cap[e] > 0 and level[R.to[e]] < 0:
                    level[R.to[e]] = level[u] + 1
                    queue.append(R.to[e])
        if level[t] < 0:
            return value, R.flows()
        it = [0] * n

        def dfs(u, pushed):
            if u == t:
                return pushed
            while it[u] < len(R.adj[u]):
                e = R.adj[u][it[u]]
                v = R.to[e]
                if R.cap[e] > 0 and level[v] == level[u] + 1:
                    got = dfs(v, min(pushed, R.cap[e]))
                    if got > 0:
                        R.push(e, got)
                        return got
                it[u] += 1
            return 0

        while True:
            f = dfs(s, float("inf"))
            if f == 0:
                break
            value += f


# ---------------------------------------------------------------- step 3 ---

def push_relabel(n, arcs, s, t):
    """FIFO push–relabel. Returns (value, flow)."""
    R = Residual(n, arcs)
    height = [0] * n
    excess = [0] * n
    height[s] = n
    active = deque()
    for e in R.adj[s]:
        if R.cap[e] > 0:
            v = R.to[e]
            amount = R.cap[e]
            R.push(e, amount)
            excess[v] += amount
            excess[s] -= amount
            if v not in (s, t) and excess[v] == amount:
                active.append(v)
    current = [0] * n
    while active:
        u = active.popleft()
        while excess[u] > 0:
            if current[u] == len(R.adj[u]):                  # relabel
                height[u] = 1 + min(height[R.to[e]] for e in R.adj[u] if R.cap[e] > 0)
                current[u] = 0
                continue
            e = R.adj[u][current[u]]
            v = R.to[e]
            if R.cap[e] > 0 and height[u] == height[v] + 1:  # push
                amount = min(excess[u], R.cap[e])
                R.push(e, amount)
                excess[u] -= amount
                excess[v] += amount
                if v not in (s, t) and excess[v] == amount:
                    active.append(v)
            else:
                current[u] += 1
    return excess[t], R.flows()


# ---------------------------------------------------------------- step 4 ---

def min_cost_flow(n, arcs, s, t, demand):
    """Send `demand` units from s to t at minimum cost (arcs carry (u, v, cap, cost),
    costs may be negative on arcs but the network has no negative cycle).
    Successive shortest paths with Johnson potentials. Returns (cost, flow) or None
    if the demand cannot be met."""
    R = Residual(n, arcs)
    INF = float("inf")
    # initial potentials: Bellman–Ford from s over arcs with capacity
    pot = [INF] * n
    pot[s] = 0
    for _ in range(n - 1):
        changed = False
        for u in range(n):
            if pot[u] == INF:
                continue
            for e in R.adj[u]:
                if R.cap[e] > 0 and pot[u] + R.cost[e] < pot[R.to[e]]:
                    pot[R.to[e]] = pot[u] + R.cost[e]
                    changed = True
        if not changed:
            break
    pot = [p if p < INF else 0 for p in pot]
    sent, cost = 0, 0
    while sent < demand:
        dist = [INF] * n
        dist[s] = 0
        prev = [-1] * n
        heap = [(0, s)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for e in R.adj[u]:
                v = R.to[e]
                if R.cap[e] > 0:
                    nd = d + R.cost[e] + pot[u] - pot[v]        # reduced cost >= 0
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = e
                        heapq.heappush(heap, (nd, v))
        if dist[t] == INF:
            return None
        for v in range(n):
            if dist[v] < INF:
                pot[v] += dist[v]
        amount, v = demand - sent, t
        while v != s:
            amount = min(amount, R.cap[prev[v]])
            v = R.to[prev[v] ^ 1]
        v = t
        while v != s:
            R.push(prev[v], amount)
            cost += amount * R.cost[prev[v]]
            v = R.to[prev[v] ^ 1]
        sent += amount
    return cost, R.flows()


# ---------------------------------------------------------------- step 5 ---

def project_selection(profit, requires, max_flow=dinic):
    """Choose a set of projects closed under prerequisites (if p is chosen and
    (p, q) in requires, q is chosen) maximising total profit (profits may be
    negative). Reduction to minimum cut. Returns (best_profit, chosen_set)."""
    k = len(profit)
    s, t = k, k + 1
    INF = sum(abs(p) for p in profit) + 1
    arcs = []
    for p, w in enumerate(profit):
        if w > 0:
            arcs.append((s, p, w))
        elif w < 0:
            arcs.append((p, t, -w))
    for p, q in requires:
        arcs.append((p, q, INF))
    value, flow = max_flow(k + 2, arcs, s, t)
    side = min_cut(k + 2, arcs, flow, s)
    return sum(w for w in profit if w > 0) - value, {p for p in range(k) if p in side}
