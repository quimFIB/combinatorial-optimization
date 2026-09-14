"""Unit 26 lab — metaheuristics, benchmarked honestly.  REFERENCE SOLUTION, imperative.

TSP: dist is a symmetric integer matrix, a tour is a permutation of range(n) (any rotation or direction).
CVRP: colib.colgen.CVRP (vertex 0 the depot); a solution is a list of routes, each a list of customers.
"""

from __future__ import annotations

import math
from collections import deque


# ---------------------------------------------------------------- step 1 ---

def tour_length(dist, tour):
    """Length of the closed tour."""
    return sum(dist[tour[i - 1]][tour[i]] for i in range(len(tour)))


def neighbour_lists(dist, k):
    """For each city, its k nearest other cities, nearest first (ties: lower index)."""
    n = len(dist)
    return [sorted((c for c in range(n) if c != a), key=lambda c: (dist[a][c], c))[:k] for a in range(n)]


def nearest_neighbour_tour(dist, start=0):
    """Start at `start`, repeatedly go to the nearest unvisited city (ties: lower index)."""
    n = len(dist)
    tour, seen = [start], {start}
    while len(tour) < n:
        a = tour[-1]
        nxt = min((c for c in range(n) if c not in seen), key=lambda c: (dist[a][c], c))
        tour.append(nxt)
        seen.add(nxt)
    return tour


# ---------------------------------------------------------------- step 2 ---

def two_opt_move(dist, tour, pos, neighbours, a):
    """The first improving 2-opt move from city a (pos[c] is c's position in tour). For each direction
    (successor, then predecessor), let b be a's tour neighbour in that direction; for each c in neighbours[a]
    (in order) while dist[a][c] < dist[a][b], let d be c's neighbour in the same direction; skip c == b and
    d == a. If replacing edges ab and cd by ac and bd shortens the tour, return (i, j, (a, b, c, d)) where
    reversing the cyclic stretch of positions i, i+1, ..., j makes that exchange. Otherwise return None."""
    n = len(tour)
    ia = pos[a]
    for succ in (True, False):
        b = tour[(ia + 1) % n] if succ else tour[(ia - 1) % n]
        d_ab = dist[a][b]
        for c in neighbours[a]:
            d_ac = dist[a][c]
            if d_ac >= d_ab:
                break
            ic = pos[c]
            d = tour[(ic + 1) % n] if succ else tour[(ic - 1) % n]
            if c == b or d == a:
                continue
            if d_ac + dist[b][d] < d_ab + dist[c][d]:
                return ((ia + 1) % n, ic, (a, b, c, d)) if succ else (ia, (ic - 1) % n, (a, b, c, d))
    return None


def _reverse(tour, pos, i, j):
    """Reverse the cyclic stretch of positions i, i+1, ..., j (inclusive), updating pos."""
    n = len(tour)
    length = (j - i) % n + 1
    for _ in range(length // 2):
        a, b = tour[i], tour[j]
        tour[i], tour[j] = b, a
        pos[b], pos[a] = i, j
        i, j = (i + 1) % n, (j - 1) % n


def two_opt(dist, tour, neighbours, dont_look=True):
    """2-opt with neighbour lists, applying two_opt_move.
    dont_look=False: sweep all cities in tour order, applying the move found at each city (if any), until a
    sweep makes no change. The result has no improving move of two_opt_move's form.
    dont_look=True: keep a queue of cities (initially the whole tour, in order); pop a city, apply its move
    if it has one and push the four endpoints that aren't already queued; stop when the queue is empty.
    Faster, and very nearly as good, but not guaranteed locally optimal.
    Returns the new tour (the input is not modified)."""
    n = len(tour)
    tour = list(tour)
    if n < 4:
        return tour
    pos = [0] * n
    for i, c in enumerate(tour):
        pos[c] = i

    def improve_from(a):
        move = two_opt_move(dist, tour, pos, neighbours, a)
        if move is None:
            return None
        i, j, ends = move
        _reverse(tour, pos, i, j)
        return ends

    if not dont_look:
        changed = True
        while changed:
            changed = False
            for a in list(tour):
                if improve_from(a):
                    changed = True
        return tour
    queue = deque(tour)
    queued = [True] * n
    while queue:
        a = queue.popleft()
        queued[a] = False
        moved = improve_from(a)
        if moved:
            for v in moved:
                if not queued[v]:
                    queued[v] = True
                    queue.append(v)
    return tour


# ---------------------------------------------------------------- step 3 ---

def or_opt(dist, tour, neighbours):
    """Or-opt: move a segment of 1, 2 or 3 consecutive cities elsewhere, possibly reversed. Sweep start
    positions 0 .. n-1 and lengths 1, 2, 3; for the segment first..last with outside neighbours p and q,
    consider inserting it between each c in neighbours[first] + neighbours[last] (in that order) and c's
    successor e in the tour without the segment (skip c in the segment and c == p), as c,first..last,e
    and then as c,last..first,e. Apply the first strictly improving move and restart the sweep; stop when
    a full sweep finds none. Requires n >= 8. Returns the new tour."""
    n = len(tour)
    tour = list(tour)
    improved = True
    while improved:
        improved = False
        for i in range(n):
            for L in (1, 2, 3):
                seg = [tour[(i + k) % n] for k in range(L)]
                p, q = tour[(i - 1) % n], tour[(i + L) % n]
                first, last = seg[0], seg[-1]
                gain = dist[p][first] + dist[last][q] - dist[p][q]
                rest = [tour[(i + L + k) % n] for k in range(n - L)]      # starts at q, ends at p
                where = {c: k for k, c in enumerate(rest)}
                inseg = set(seg)
                for c in neighbours[first] + neighbours[last]:
                    if c in inseg or c == p:
                        continue
                    e = rest[(where[c] + 1) % len(rest)]
                    for x, y, piece in ((first, last, seg), (last, first, seg[::-1])):
                        if dist[c][x] + dist[y][e] - dist[c][e] < gain:
                            k = where[c]
                            tour = rest[:k + 1] + piece + rest[k + 1:]
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break
    return tour


def local_search(dist, tour, neighbours):
    """Alternate two_opt (dont_look=False) and or_opt until neither changes the tour length."""
    length = tour_length(dist, tour)
    while True:
        tour = or_opt(dist, two_opt(dist, tour, neighbours, dont_look=False), neighbours)
        new = tour_length(dist, tour)
        if new >= length:
            return tour
        length = new


# ---------------------------------------------------------------- step 4 ---

def accept(delta, temperature, u):
    """Metropolis: accept a non-worsening move always, a worsening one iff u < exp(-delta / temperature).
    A temperature of 0 accepts only non-worsening moves."""
    if delta <= 0:
        return True
    if temperature <= 0:
        return False
    return u < math.exp(-delta / temperature)


def temperature(t0, t_end, iterations, i):
    """Geometric cooling from t0 at i = 0 to t_end at i = iterations - 1."""
    if iterations <= 1:
        return t0
    return t0 * (t_end / t0) ** (i / (iterations - 1))


def simulated_annealing(dist, tour, rng, iterations, t0, t_end):
    """At iteration it: draw positions i < j with sorted(rng.sample(range(n), 2)), then u = rng.random() (always,
    even if the move is skipped). Propose reversing tour[i..j], a 2-opt move, skipping it if it would reverse
    the whole tour (i = 0 and j = n - 1). Accept with accept(delta, temperature(t0, t_end, iterations, it), u).
    Returns (best tour seen, its length)."""
    n = len(tour)
    tour = list(tour)
    length = tour_length(dist, tour)
    best, best_len = list(tour), length
    for it in range(iterations):
        i, j = sorted(rng.sample(range(n), 2))
        u = rng.random()
        if i == 0 and j == n - 1:
            continue
        a, b = tour[i - 1], tour[i]
        c, d = tour[j], tour[(j + 1) % n]
        delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
        if accept(delta, temperature(t0, t_end, iterations, it), u):
            tour[i:j + 1] = reversed(tour[i:j + 1])
            length += delta
            if length < best_len:
                best, best_len = list(tour), length
    return best, best_len


# ---------------------------------------------------------------- step 5 ---

def solution_cost(cvrp, routes):
    """Total distance of all routes (cvrp.route_cost adds the depot at both ends)."""
    return sum(cvrp.route_cost(r) for r in routes)


def random_removal(routes, q, rng):
    """Remove rng.sample(sorted customers, q). Returns (routes without them, empty routes dropped; removed list)."""
    customers = sorted(c for r in routes for c in r)
    removed = rng.sample(customers, q)
    gone = set(removed)
    kept = [[c for c in r if c not in gone] for r in routes]
    return [r for r in kept if r], removed


def worst_removal(cvrp, routes, q):
    """q times: remove the customer whose removal saves the most distance (ties: lower customer number).
    Returns (routes, empty routes dropped; removed customers in removal order)."""
    routes = [list(r) for r in routes]
    removed = []
    for _ in range(q):
        best = None
        for ri, r in enumerate(routes):
            path = [0, *r, 0]
            for k, c in enumerate(r):
                saving = cvrp.dist[path[k]][c] + cvrp.dist[c][path[k + 2]] - cvrp.dist[path[k]][path[k + 2]]
                if best is None or (saving, -c) > (best[0], -best[1]):
                    best = (saving, c, ri, k)
        _, c, ri, k = best
        del routes[ri][k]
        removed.append(c)
        routes = [r for r in routes if r]
    return routes, removed


def greedy_insertion(cvrp, routes, removed):
    """Insert customers in the given order, each at its cheapest feasible position over all routes and
    positions (ties: earlier route, then earlier position); if no route has capacity, open a new route at the
    end. Returns the new routes."""
    routes = [list(r) for r in routes]
    for c in removed:
        best = None
        for ri, r in enumerate(routes):
            if cvrp.route_load(r) + cvrp.demand[c] > cvrp.capacity:
                continue
            path = [0, *r, 0]
            for k in range(len(path) - 1):
                extra = cvrp.dist[path[k]][c] + cvrp.dist[c][path[k + 1]] - cvrp.dist[path[k]][path[k + 1]]
                if best is None or extra < best[0]:
                    best = (extra, ri, k)
        if best is None:
            routes.append([c])
        else:
            _, ri, k = best
            routes[ri].insert(k, c)
    return routes


def update_weights(weights, scores, uses, reaction):
    """Adaptive weights at the end of a segment: w <- (1 - r) w + r * score / uses for operators used at
    least once; unused operators keep their weight."""
    return [(1 - reaction) * w + reaction * s / u if u else w for w, s, u in zip(weights, scores, uses)]


def alns(cvrp, iterations, rng, q=None, segment=50, reaction=0.2, threshold=0.02):
    """ALNS with two destroy operators (0: random_removal, 1: worst_removal) and greedy_insertion as repair.
    Start from greedy_insertion of customers 1..n into no routes. Each iteration: q = q or max(1, n // 10);
    pick a destroy operator with rng.choices(range(2), weights); destroy and repair the current solution.
    Score 33 if the result is a new best, 9 if it beats the current, 13 if it's accepted without improving;
    accept when its cost < current cost, or <= (1 + threshold) * best cost. Every `segment` iterations,
    update_weights and reset scores and uses. Returns (best routes, best cost, list of weights per segment)."""
    n = cvrp.n
    q = q or max(1, n // 10)
    current = greedy_insertion(cvrp, [], list(range(1, n + 1)))
    cur_cost = solution_cost(cvrp, current)
    best, best_cost = current, cur_cost
    weights, scores, uses, history = [1.0, 1.0], [0.0, 0.0], [0, 0], []
    for it in range(1, iterations + 1):
        op = rng.choices(range(2), weights)[0]
        partial, removed = random_removal(current, q, rng) if op == 0 else worst_removal(cvrp, current, q)
        candidate = greedy_insertion(cvrp, partial, removed)
        cost = solution_cost(cvrp, candidate)
        uses[op] += 1
        if cost < best_cost:
            best, best_cost = candidate, cost
            scores[op] += 33
            current, cur_cost = candidate, cost
        elif cost < cur_cost:
            scores[op] += 9
            current, cur_cost = candidate, cost
        elif cost <= (1 + threshold) * best_cost:
            scores[op] += 13
            current, cur_cost = candidate, cost
        if it % segment == 0:
            weights = update_weights(weights, scores, uses, reaction)
            history.append(list(weights))
            scores, uses = [0.0, 0.0], [0, 0]
    return best, best_cost, history


# ---------------------------------------------------------------- step 6 ---

def ttt_points(samples):
    """Time-to-target plot points: the successful run times (not None) sorted, the i-th (from 0) at height
    (i + 0.5) / len(samples). Failures stay in the denominator, so the curve tops out below 1 if any run
    failed. Returns a list of (time, probability)."""
    done = sorted(s for s in samples if s is not None)
    return [(t, (i + 0.5) / len(samples)) for i, t in enumerate(done)]


def mann_whitney(a, b):
    """Two-sided Mann-Whitney U test with the normal approximation, tie correction and continuity correction.
    U is the statistic for sample a: the number of pairs (x in a, y in b) with x > y, plus half the ties.
    Returns (U, p)."""
    n1, n2 = len(a), len(b)
    pooled = sorted([(x, 0) for x in a] + [(y, 1) for y in b])
    ranks = [0.0] * len(pooled)
    tie_term = 0.0
    i = 0
    while i < len(pooled):
        j = i
        while j + 1 < len(pooled) and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        for k in range(i, j + 1):
            ranks[k] = (i + j) / 2 + 1
        t = j - i + 1
        tie_term += t ** 3 - t
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, pooled) if g == 0)
    U = r1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    N = n1 + n2
    sigma = math.sqrt(n1 * n2 / 12 * ((N + 1) - tie_term / (N * (N - 1))))
    if sigma == 0:
        return U, 1.0
    z = (abs(U - mu) - 0.5) / sigma
    p = math.erfc(max(z, 0) / math.sqrt(2))
    return U, min(1.0, p)


def verdict(a, b, alpha=0.05):
    """For run times (lower is better): None if the two-sided test doesn't reject at alpha; otherwise "a" if
    a's values tend to be smaller (U < len(a) * len(b) / 2) and "b" if they tend to be larger. The direction
    comes from U, not from medians: with runs capped at a time limit, both medians can be the cap."""
    U, p = mann_whitney(a, b)
    if p >= alpha:
        return None
    return "a" if U < len(a) * len(b) / 2 else "b"
