# Hints — lab 14

One rung at a time; then `solution/lab.py` or `solution/functional.py`.

## Step 1 — Edmonds–Karp, and the cut

<details><summary>Rung 1 — the residual graph</summary>

Parallel lists `to`, `cap`, and `adj[u]` (edge ids leaving u). For arc k = (u, v, c):
append edge 2k (to v, cap c) to `adj[u]`, and edge 2k+1 (to u, cap 0) to `adj[v]`.
Pushing *a* on edge e: `cap[e] -= a; cap[e ^ 1] += a`. The flow on arc k is
`c_k - cap[2k]`.
</details>

<details><summary>Rung 2 — one augmentation</summary>

BFS from s, recording `parent[v] = edge used`. If t is unreached, stop. Walk back
from t via `to[parent[v] ^ 1]` (the edge's tail) to find the bottleneck, then walk
again to push it.
</details>

<details><summary>Rung 3 — the cut</summary>

From the finished flow (not the residual structure): residual u → v if f &lt; c,
and v → u if f &gt; 0. BFS from s. Everything you reach is the source side, and the
original arcs leaving it are saturated. Their capacities sum to the flow value.
</details>

<details><summary>Functional route</summary>

Residual capacities are an immutable tuple, with arc k stored as edges 2k and 2k + 1, so `e ^ 1` is the
reverse edge and `push(caps, e, amount)` returns a new tuple. BFS is an unfold over `(parent map, frontier)`
cut off by `takewhile`. The path is `tz.iterate` over parent edges. Edmonds–Karp is an unfold over `(caps,
value, done)`, and the cut is one more BFS over the residual arcs, read off with `tz.last`.
</details>

## Step 2 — Dinic

<details><summary>Rung 1</summary>

Levels by BFS over edges with `cap > 0`. The DFS `dfs(u, pushed)` returns how much
it pushed. It walks `adj[u]` from `it[u]` onwards, only to v with
`level[v] == level[u] + 1`, recurses, and on success pushes and returns. Advance
`it[u]` only when an edge is useless, so a saturated or dead edge is never tried
again in this phase.
</details>

<details><summary>Functional route</summary>

Two nested unfolds: phases over `(caps, value, done)`, and inside each phase, blocking paths until none
is left. The level graph comes from the BFS parents (parents precede children in BFS order). The path search
is a recursive DFS that returns `None` or a list of edges, with the visited set passed down as a frozenset.
It holds no mutable state, at the cost of re-searching from s after every augmentation.
</details>

## Step 3 — Push–relabel

<details><summary>Rung 1 — initialisation</summary>

`height[s] = n`. Saturate every edge out of s, adding its capacity to the head's
excess. The queue holds each node other than s and t whose excess became positive.
</details>

<details><summary>Rung 2 — discharge</summary>

While `excess[u] > 0`: if `current[u]` has run past `adj[u]`, relabel
`height[u] = 1 + min(height[to[e]] for e in adj[u] if cap[e] > 0)` and reset
`current[u] = 0`. Else, if the current edge is admissible, push
`min(excess[u], cap[e])`, and enqueue the head if its excess was zero before (and
it isn't s or t). Otherwise advance `current[u]`.
</details>

<details><summary>Functional route</summary>

The state is a frozen dataclass `PR(caps, height, excess, active queue)`, and one discharge step returns a
new one with `dataclasses.replace`: push along the first admissible edge, or relabel when none exists. The
queue is a tuple: u goes back to the front while it still has excess, and a newly active v joins at the end.
Stop at the first state with an empty queue.
</details>

## Step 4 — Min-cost flow

<details><summary>Rung 1 — potentials</summary>

Bellman–Ford from s over edges with `cap > 0` gives `pot`, and unreachable nodes get
0. Reduced cost of residual edge e from u to v: `cost[e] + pot[u] - pot[v] >= 0`,
where the reverse edge has `cost[e ^ 1] = -cost[e]`.
</details>

<details><summary>Rung 2 — each round</summary>

Dijkstra with reduced costs gives `dist`. If t is unreachable, return None. Then
`pot[v] += dist[v]` for reached v, which keeps reduced costs nonnegative next
round. Augment by the minimum of the remaining demand and the path's residual
capacities, and add `amount * cost[e]` (the real cost) for each edge on the path.
</details>

<details><summary>Functional route</summary>

Bellman–Ford for the initial potentials is a fold over range(n − 1), each round a new tuple. Dijkstra is an
unfold over `(dist, prev, heap as a sorted tuple, done)`. The successive-shortest-paths loop is an unfold over
`(caps, potentials, sent, cost, status)`, whose status becomes "done" or "infeasible". A tuple heap costs a
sort per pop; at lab sizes that is fine.
</details>

## Step 5 — Project selection

<details><summary>Rung 1 — why the cut is the answer</summary>

A finite cut can't cut an infinite p → q arc, so if p is on the source side, q is
too: the source side is closed. Its capacity is the positive profits you *don't*
take plus the costs you *do* pay. Total positive profit minus that is exactly the
profit of the source side.
</details>

<details><summary>Functional route</summary>

No state: the network is three comprehensions (source arcs, sink arcs, infinite requirement arcs), one
call to your max-flow function, and one to `min_cut`. The chosen projects are the source side.
</details>
