"""Unit 26 lab — metaheuristics, benchmarked honestly.  REFERENCE SOLUTION, functional.

Local search is an unfold: a state, a function that finds the first improving move (or None), and
iteration until None. Tours are tuples, and a 2-opt move rebuilds one by slicing, O(n) per move where the
imperative version reverses in place. The don't-look queue is part of the state. Annealing and ALNS are
folds over iterations whose state carries the current and best solutions. Random draws happen in the
same order as in the imperative reference, so annealing and ALNS consume a seed identically.
"""

from __future__ import annotations

import math
from itertools import accumulate, chain, groupby, takewhile

import toolz as tz


def _until_none(step, state):
    """Apply step while it returns a new state; return the last state."""
    return tz.last(takewhile(lambda s: s is not None, tz.iterate(lambda s: step(s) if s is not None else None, state)))


# ---------------------------------------------------------------- step 1 ---

def tour_length(dist, tour):
    return sum(dist[a][b] for a, b in zip(tour, tour[1:] + tour[:1]))


def neighbour_lists(dist, k):
    n = len(dist)
    return [sorted((c for c in range(n) if c != a), key=lambda c: (dist[a][c], c))[:k] for a in range(n)]


def nearest_neighbour_tour(dist, start=0):
    n = len(dist)

    def step(tour):
        if len(tour) == n:
            return None
        rest = [c for c in range(n) if c not in tour]
        return tour + (min(rest, key=lambda c: (dist[tour[-1]][c], c)),)

    return list(_until_none(step, (start,)))


# ---------------------------------------------------------------- step 2 ---

def _reversed_stretch(tour, i, j):
    """The tour with the cyclic stretch of positions i..j reversed (returned rotated to start at i)."""
    n = len(tour)
    r = tour[i:] + tour[:i]
    length = (j - i) % n + 1
    return r[:length][::-1] + r[length:]


def two_opt_move(dist, tour, pos, neighbours, a):
    n = len(tour)
    ia = pos[a]

    def candidates(succ):
        b = tour[(ia + 1) % n] if succ else tour[(ia - 1) % n]
        for c in takewhile(lambda c: dist[a][c] < dist[a][b], neighbours[a]):
            d = tour[(pos[c] + 1) % n] if succ else tour[(pos[c] - 1) % n]
            if c != b and d != a and dist[a][c] + dist[b][d] < dist[a][b] + dist[c][d]:
                yield ((ia + 1) % n, pos[c], (a, b, c, d)) if succ else (ia, (pos[c] - 1) % n, (a, b, c, d))

    return next(chain(candidates(True), candidates(False)), None)


def _move_from(dist, neighbours, tour, a):
    move = two_opt_move(dist, tour, {c: i for i, c in enumerate(tour)}, neighbours, a)
    return None if move is None else (_reversed_stretch(tour, move[0], move[1]), move[2])


def two_opt(dist, tour, neighbours, dont_look=True):
    tour = tuple(tour)
    if len(tour) < 4:
        return list(tour)
    if not dont_look:
        def sweep(t):
            def visit(state, a):
                cur, changed = state
                found = _move_from(dist, neighbours, cur, a)
                return (found[0], True) if found else (cur, changed)
            new, changed = tz.reduce(visit, t, (t, False))
            return new if changed else None
        return list(_until_none(sweep, tour))

    def step(state):
        t, queue = state
        if not queue:
            return None
        a, rest = queue[0], queue[1:]
        found = _move_from(dist, neighbours, t, a)
        if not found:
            return t, rest
        new, ends = found
        return new, rest + tuple(tz.unique(v for v in ends if v not in rest))

    return list(_until_none(step, (tour, tour))[0])


# ---------------------------------------------------------------- step 3 ---

def _or_move(dist, neighbours, tour):
    n = len(tour)
    for i in range(n):
        for L in (1, 2, 3):
            seg = tuple(tour[(i + k) % n] for k in range(L))
            p, q = tour[(i - 1) % n], tour[(i + L) % n]
            gain = dist[p][seg[0]] + dist[seg[-1]][q] - dist[p][q]
            rest = tuple(tour[(i + L + k) % n] for k in range(n - L))
            where = {c: k for k, c in enumerate(rest)}
            for c in neighbours[seg[0]] + neighbours[seg[-1]]:
                if c in seg or c == p:
                    continue
                k = where[c]
                e = rest[(k + 1) % len(rest)]
                for piece in (seg, seg[::-1]):
                    if dist[c][piece[0]] + dist[piece[-1]][e] - dist[c][e] < gain:
                        return rest[:k + 1] + piece + rest[k + 1:]
    return None


def or_opt(dist, tour, neighbours):
    return list(_until_none(lambda t: _or_move(dist, neighbours, t), tuple(tour)))


def local_search(dist, tour, neighbours):
    def step(t):
        new = or_opt(dist, two_opt(dist, t, neighbours, dont_look=False), neighbours)
        return new if tour_length(dist, new) < tour_length(dist, t) else None
    return list(_until_none(step, list(tour)))


# ---------------------------------------------------------------- step 4 ---

def accept(delta, temperature, u):
    return delta <= 0 or (temperature > 0 and u < math.exp(-delta / temperature))


def temperature(t0, t_end, iterations, i):
    return t0 if iterations <= 1 else t0 * (t_end / t0) ** (i / (iterations - 1))


def simulated_annealing(dist, tour, rng, iterations, t0, t_end):
    n = len(tour)

    def step(state, it):
        cur, length, best, best_len = state
        i, j = sorted(rng.sample(range(n), 2))
        u = rng.random()
        if i == 0 and j == n - 1:
            return state
        delta = dist[cur[i - 1]][cur[j]] + dist[cur[i]][cur[(j + 1) % n]] - dist[cur[i - 1]][cur[i]] - dist[cur[j]][cur[(j + 1) % n]]
        if not accept(delta, temperature(t0, t_end, iterations, it), u):
            return state
        new = cur[:i] + cur[i:j + 1][::-1] + cur[j + 1:]
        return (new, length + delta) + ((new, length + delta) if length + delta < best_len else (best, best_len))

    start = tuple(tour)
    _, _, best, best_len = tz.reduce(step, range(iterations), (start, tour_length(dist, start), start, tour_length(dist, start)))
    return list(best), best_len


# ---------------------------------------------------------------- step 5 ---

def solution_cost(cvrp, routes):
    return sum(cvrp.route_cost(r) for r in routes)


def random_removal(routes, q, rng):
    removed = rng.sample(sorted(chain.from_iterable(routes)), q)
    kept = [[c for c in r if c not in removed] for r in routes]
    return [r for r in kept if r], removed


def worst_removal(cvrp, routes, q):
    def saving(route, k):
        path = (0, *route, 0)
        return cvrp.dist[path[k]][path[k + 1]] + cvrp.dist[path[k + 1]][path[k + 2]] - cvrp.dist[path[k]][path[k + 2]]

    def remove_one(state, _):
        rs, removed = state
        _, c, ri, k = max((saving(r, k), -c, ri, k) for ri, r in enumerate(rs) for k, c in enumerate(r))
        new = [r[:k] + r[k + 1:] if i == ri else r for i, r in enumerate(rs)]
        return [r for r in new if r], removed + [-c]

    routes, removed = tz.reduce(remove_one, range(q), ([list(r) for r in routes], []))
    return routes, removed


def greedy_insertion(cvrp, routes, removed):
    def insert(rs, c):
        options = [(cvrp.dist[p][c] + cvrp.dist[c][s] - cvrp.dist[p][s], ri, k)
                   for ri, r in enumerate(rs) if cvrp.route_load(r) + cvrp.demand[c] <= cvrp.capacity
                   for k, (p, s) in enumerate(zip((0, *r), (*r, 0)))]
        if not options:
            return rs + [[c]]
        _, ri, k = min(options)
        return [r[:k] + [c] + r[k:] if i == ri else r for i, r in enumerate(rs)]
    return tz.reduce(insert, removed, [list(r) for r in routes])


def update_weights(weights, scores, uses, reaction):
    return [(1 - reaction) * w + reaction * s / u if u else w for w, s, u in zip(weights, scores, uses)]


def alns(cvrp, iterations, rng, q=None, segment=50, reaction=0.2, threshold=0.02):
    n = cvrp.n
    q = q or max(1, n // 10)
    start = greedy_insertion(cvrp, [], list(range(1, n + 1)))

    def step(state, it):
        cur, cur_cost, best, best_cost, weights, scores, uses, history = state
        op = rng.choices(range(2), weights)[0]
        partial, removed = random_removal(cur, q, rng) if op == 0 else worst_removal(cvrp, cur, q)
        cand = greedy_insertion(cvrp, partial, removed)
        cost = solution_cost(cvrp, cand)
        gain = 33 if cost < best_cost else 9 if cost < cur_cost else 13 if cost <= (1 + threshold) * best_cost else 0
        accepted = gain > 0
        scores = [s + gain if i == op else s for i, s in enumerate(scores)]
        uses = [u + 1 if i == op else u for i, u in enumerate(uses)]
        cur, cur_cost = (cand, cost) if accepted else (cur, cur_cost)
        best, best_cost = (cand, cost) if cost < best_cost else (best, best_cost)
        if it % segment == 0:
            weights = update_weights(weights, scores, uses, reaction)
            return cur, cur_cost, best, best_cost, weights, [0.0, 0.0], [0, 0], history + [list(weights)]
        return cur, cur_cost, best, best_cost, weights, scores, uses, history

    c0 = solution_cost(cvrp, start)
    final = tz.reduce(step, range(1, iterations + 1), (start, c0, start, c0, [1.0, 1.0], [0.0, 0.0], [0, 0], []))
    return final[2], final[3], final[7]


# ---------------------------------------------------------------- step 6 ---

def ttt_points(samples):
    return [(t, (i + 0.5) / len(samples)) for i, t in enumerate(sorted(s for s in samples if s is not None))]


def mann_whitney(a, b):
    n1, n2 = len(a), len(b)
    pooled = sorted([(x, 0) for x in a] + [(y, 1) for y in b], key=lambda e: e[0])
    groups = [list(g) for _, g in groupby(pooled, key=lambda e: e[0])]
    starts = list(accumulate((len(g) for g in groups), initial=0))
    r1 = sum((starts[k] + starts[k + 1] + 1) / 2 * sum(1 for _, s in g if s == 0) for k, g in enumerate(groups))
    tie_term = sum(len(g) ** 3 - len(g) for g in groups)
    U = r1 - n1 * (n1 + 1) / 2
    N = n1 + n2
    sigma = math.sqrt(n1 * n2 / 12 * ((N + 1) - tie_term / (N * (N - 1))))
    if sigma == 0:
        return U, 1.0
    z = max(abs(U - n1 * n2 / 2) - 0.5, 0) / sigma
    return U, min(1.0, math.erfc(z / math.sqrt(2)))


def verdict(a, b, alpha=0.05):
    U, p = mann_whitney(a, b)
    return None if p >= alpha else "a" if U < len(a) * len(b) / 2 else "b"
