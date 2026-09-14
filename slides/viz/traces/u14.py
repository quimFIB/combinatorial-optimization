"""Unit 14's recorded flow runs, for units/14-network-flows/explore.html.

Augmenting paths run on the reference `Residual` class: Edmonds–Karp is a logged copy of the
reference `edmonds_karp` (BFS); "Ford–Fulkerson, depth first" picks paths by DFS in the same
adjacency order, which makes a poor first choice and then undoes it through a backward arc.
Push–relabel is a logged copy of the reference `push_relabel`. Every final flow is checked
against the reference functions before it is written.
"""

from __future__ import annotations

from collections import deque

from colib import ref

L = ref.unit("14")

NAMES = ["s", "a", "b", "t"]
ARCS = [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 3), (2, 3, 2)]     # sa, sb, ab, at, bt
S, T = 0, 3


def residual_view(R):
    """Every residual edge with capacity > 0: (u, v, cap, forward?, arc index)."""
    out = []
    for e in range(len(R.to)):
        if R.cap[e] > 0:
            out.append({"u": R.to[e ^ 1], "v": R.to[e], "cap": R.cap[e], "forward": e % 2 == 0, "arc": e // 2})
    return out


def augmenting(kind):
    R = L.Residual(len(NAMES), ARCS)
    states, value = [], 0

    def snap(note, path=None, bottleneck=None, cut=None, explain=""):
        states.append({"flow": R.flows(), "value": value, "residual": residual_view(R), "path": path,
                       "bottleneck": bottleneck, "cut": cut, "note": note, "explain": explain})

    snap("no flow yet: the residual graph is the network itself",
         explain="Each arc can take up to its capacity. A path from s to t in the residual graph is an augmenting path.")
    while True:
        parent = [-1] * len(NAMES)
        parent[S] = -2
        if kind == "bfs":
            queue = deque([S])
            while queue and parent[T] == -1:
                u = queue.popleft()
                for e in R.adj[u]:
                    if R.cap[e] > 0 and parent[R.to[e]] == -1:
                        parent[R.to[e]] = e
                        queue.append(R.to[e])
        else:
            def dfs(u):
                if u == T:
                    return True
                for e in R.adj[u]:
                    v = R.to[e]
                    if R.cap[e] > 0 and parent[v] == -1:
                        parent[v] = e
                        if dfs(v):
                            return True
                return False
            dfs(S)
        if parent[T] == -1:
            cut = sorted(L.min_cut(len(NAMES), ARCS, R.flows(), S))
            snap(f"no augmenting path: maximum flow {value}", cut=cut,
                 explain=f"Nodes still reachable from s: {', '.join(NAMES[v] for v in cut)}. The arcs leaving that set are full, "
                         f"and their capacities add up to {value}: a cut that proves the flow is maximum.")
            return states
        path, v = [], T
        while v != S:
            e = parent[v]
            path.append(e)
            v = R.to[e ^ 1]
        path.reverse()
        bottleneck = min(R.cap[e] for e in path)
        nodes = [S] + [R.to[e] for e in path]
        back = [e for e in path if e % 2 == 1]
        label = " → ".join(NAMES[x] for x in nodes)
        snap(f"augmenting path {label}, bottleneck {bottleneck}",
             path=[{"u": R.to[e ^ 1], "v": R.to[e], "forward": e % 2 == 0} for e in path], bottleneck=bottleneck,
             explain=("It uses a backward arc: pushing along it cancels flow sent earlier. " if back else "") +
                     "The smallest residual capacity on the path limits how much can be sent.")
        for e in path:
            R.push(e, bottleneck)
        value += bottleneck
        snap(f"sent {bottleneck}: flow value {value}",
             explain="Forward arcs on the path lose capacity; their reverses gain the same amount, "
                     "which is the flow that could later be undone.")


def push_relabel():
    """A logged copy of the reference push_relabel (FIFO), one state per push or relabel."""
    n = len(NAMES)
    R = L.Residual(n, ARCS)
    height, excess = [0] * n, [0] * n
    height[S] = n
    states = []

    def snap(note, active_node=None, arc=None, explain=""):
        states.append({"height": list(height), "excess": list(excess), "flow": R.flows(), "residual": residual_view(R),
                       "active": active_node, "arc": arc, "note": note, "explain": explain})

    snap("start: the source is lifted to height n = 4",
         explain="Flow only moves downhill, one level at a time. Lifting s above everything lets it flood its arcs.")
    active = deque()
    for e in R.adj[S]:
        if R.cap[e] > 0:
            v, amount = R.to[e], R.cap[e]
            R.push(e, amount)
            excess[v] += amount
            excess[S] -= amount
            if v not in (S, T) and excess[v] == amount:
                active.append(v)
            snap(f"saturate s → {NAMES[v]}: push {amount}", active_node=v, arc={"u": S, "v": v},
                 explain="The first move fills every arc out of the source, leaving excess at its neighbours.")
    current = [0] * n
    while active:
        u = active.popleft()
        while excess[u] > 0:
            if current[u] == len(R.adj[u]):
                old = height[u]
                height[u] = 1 + min(height[R.to[e]] for e in R.adj[u] if R.cap[e] > 0)
                current[u] = 0
                snap(f"relabel {NAMES[u]}: height {old} → {height[u]}", active_node=u,
                     explain=f"{NAMES[u]} has excess {excess[u]} but no residual arc goes one level down, "
                             "so it rises to one above its lowest residual neighbour.")
                continue
            e = R.adj[u][current[u]]
            v = R.to[e]
            if R.cap[e] > 0 and height[u] == height[v] + 1:
                amount = min(excess[u], R.cap[e])
                R.push(e, amount)
                excess[u] -= amount
                excess[v] += amount
                if v not in (S, T) and excess[v] == amount:
                    active.append(v)
                undo = e % 2 == 1
                snap(f"push {amount} {NAMES[u]} → {NAMES[v]}" + (" (undoing earlier flow)" if undo else ""),
                     active_node=u, arc={"u": u, "v": v},
                     explain=("This goes against an original arc: it returns flow that was pushed the wrong way. " if undo else "") +
                             f"{NAMES[u]} is exactly one level above {NAMES[v]}, so it can push min(excess, residual capacity).")
            else:
                current[u] += 1
    states[-1]["note"] += f"; no excess left, maximum flow {excess[T]}"
    return states


def data():
    ek, ff, pr = augmenting("bfs"), augmenting("dfs"), push_relabel()
    ref_value, ref_flow = L.edmonds_karp(len(NAMES), ARCS, S, T)
    pr_value, pr_flow = L.push_relabel(len(NAMES), ARCS, S, T)
    assert ek[-1]["value"] == ref_value and ek[-1]["flow"] == ref_flow, "Edmonds–Karp trace disagrees with the reference"
    assert ff[-1]["value"] == ref_value, "Ford–Fulkerson trace disagrees with the reference max flow"
    assert pr[-1]["flow"] == pr_flow and pr[-1]["excess"][T] == pr_value, "push–relabel trace disagrees with the reference"
    net = {"names": NAMES, "arcs": [list(a) for a in ARCS], "s": S, "t": T}
    return {
        "network": net,
        "ek": {"title": "Edmonds–Karp (breadth first)", "states": ek},
        "ff": {"title": "Ford–Fulkerson (depth first)", "states": ff},
        "pr": {"title": "FIFO push–relabel", "states": pr},
    }
