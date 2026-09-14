"""Unit 15 lab — matching.  REFERENCE SOLUTION, imperative.

Bipartite graphs: left vertices 0..nl-1, right vertices 0..nr-1, edges a list of
(l, r). A matching is returned as a dict {l: r}.
"""

from __future__ import annotations

from collections import deque

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def hopcroft_karp(nl, nr, edges):
    adj = [[] for _ in range(nl)]
    for l, r in edges:
        adj[l].append(r)
    match_l, match_r = [-1] * nl, [-1] * nr
    while True:
        dist = [INF] * nl                                    # BFS layers from free left vertices
        queue = deque()
        for l in range(nl):
            if match_l[l] == -1:
                dist[l] = 0
                queue.append(l)
        found = False
        while queue:
            l = queue.popleft()
            for r in adj[l]:
                m = match_r[r]
                if m == -1:
                    found = True
                elif dist[m] == INF:
                    dist[m] = dist[l] + 1
                    queue.append(m)
        if not found:
            break

        def dfs(l):
            for r in adj[l]:
                m = match_r[r]
                if m == -1 or (dist[m] == dist[l] + 1 and dfs(m)):
                    match_l[l], match_r[r] = r, l
                    return True
            dist[l] = INF
            return False

        for l in range(nl):
            if match_l[l] == -1:
                dfs(l)
    return {l: r for l, r in enumerate(match_l) if r != -1}


# ---------------------------------------------------------------- step 2 ---

def konig_cover(nl, nr, edges, matching):
    """A minimum vertex cover from a maximum matching: returns (left_set, right_set)."""
    adj = [[] for _ in range(nl)]
    for l, r in edges:
        adj[l].append(r)
    match_r = {r: l for l, r in matching.items()}
    reach_l = {l for l in range(nl) if l not in matching}
    reach_r = set()
    queue = deque(reach_l)
    while queue:                                             # alternating paths: free edge right, matched edge left
        l = queue.popleft()
        for r in adj[l]:
            if r not in reach_r and matching.get(l) != r:
                reach_r.add(r)
                m = match_r.get(r)
                if m is not None and m not in reach_l:
                    reach_l.add(m)
                    queue.append(m)
    return set(range(nl)) - reach_l, reach_r


# ---------------------------------------------------------------- step 3 ---

def hungarian(cost):
    """Min-cost perfect assignment on an n x n matrix. Returns (assign, total, u, v):
    assign[i] = column of row i; u, v dual potentials with u[i] + v[j] <= cost[i][j],
    equality on assigned pairs."""
    n = len(cost)
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)                                        # p[j]: row matched to column j (1-based; 0 = none)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    assign = [0] * n
    for j in range(1, n + 1):
        assign[p[j] - 1] = j - 1
    total = sum(cost[i][assign[i]] for i in range(n))
    return assign, total, u[1:], v[1:]


# ---------------------------------------------------------------- step 4 ---

def certify_assignment(cost, assign, u, v, tol=1e-9):
    """True iff (u, v) is dual feasible, tight on every assigned pair, and assign is a
    permutation. Together these prove the assignment optimal without re-solving."""
    n = len(cost)
    if sorted(assign) != list(range(n)):
        return False
    if any(u[i] + v[j] > cost[i][j] + tol for i in range(n) for j in range(n)):
        return False
    return all(abs(u[i] + v[assign[i]] - cost[i][assign[i]]) <= tol for i in range(n))


# ---------------------------------------------------------------- step 5 ---

def gale_shapley(proposer_prefs, receiver_prefs):
    """Proposer-optimal stable matching. prefs[x] lists the other side, best first.
    Returns {proposer: receiver}."""
    n = len(proposer_prefs)
    rank = [{p: k for k, p in enumerate(prefs)} for prefs in receiver_prefs]
    next_choice = [0] * n
    holder = {}                                              # receiver -> proposer
    free = deque(range(n))
    while free:
        p = free.popleft()
        r = proposer_prefs[p][next_choice[p]]
        next_choice[p] += 1
        current = holder.get(r)
        if current is None:
            holder[r] = p
        elif rank[r][p] < rank[r][current]:
            holder[r] = p
            free.append(current)
        else:
            free.append(p)
    return {p: r for r, p in holder.items()}


def is_stable(proposer_prefs, receiver_prefs, matching):
    """True iff no proposer and receiver both prefer each other to their partners."""
    partner_of_r = {r: p for p, r in matching.items()}
    for p, prefs in enumerate(proposer_prefs):
        for r in prefs:
            if r == matching[p]:
                break
            q = partner_of_r[r]
            if receiver_prefs[r].index(p) < receiver_prefs[r].index(q):
                return False
    return True


# ---------------------------------------------------------------- step 6 (stretch) ---

def blossom(n, edges):
    """Maximum-cardinality matching in a general graph (Edmonds' blossom algorithm,
    O(n^3)). Returns a list mate with mate[v] = partner or -1."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    mate = [-1] * n

    def find_path(root):
        parent = [-1] * n
        base = list(range(n))
        used = [False] * n
        used[root] = True
        queue = deque([root])

        def lca(a, b):
            seen = [False] * n
            while True:
                a = base[a]
                seen[a] = True
                if mate[a] == -1:
                    break
                a = parent[mate[a]]
            while True:
                b = base[b]
                if seen[b]:
                    return b
                b = parent[mate[b]]

        def mark_path(v, b, child, in_blossom):
            while base[v] != b:
                in_blossom[base[v]] = in_blossom[base[mate[v]]] = True
                parent[v] = child
                child = mate[v]
                v = parent[mate[v]]

        while queue:
            v = queue.popleft()
            for to in adj[v]:
                if base[v] == base[to] or mate[v] == to:
                    continue
                if to == root or (mate[to] != -1 and parent[mate[to]] != -1):
                    cur = lca(v, to)
                    in_blossom = [False] * n
                    mark_path(v, cur, to, in_blossom)
                    mark_path(to, cur, v, in_blossom)
                    for i in range(n):
                        if in_blossom[base[i]]:
                            base[i] = cur
                            if not used[i]:
                                used[i] = True
                                queue.append(i)
                elif parent[to] == -1:
                    parent[to] = v
                    if mate[to] == -1:
                        return to, parent
                    used[mate[to]] = True
                    queue.append(mate[to])
        return -1, parent

    for root in range(n):
        if mate[root] != -1:
            continue
        end, parent = find_path(root)
        while end != -1:
            pv = parent[end]
            ppv = mate[pv]
            mate[end], mate[pv] = pv, end
            end = ppv
    return mate
