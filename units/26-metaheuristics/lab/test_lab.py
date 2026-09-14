"""Tests for unit 26. Run with `uv run co test 26`. You should not need to edit this."""

import itertools
import math
import random

import pytest
from scipy.stats import mannwhitneyu

from colib.colgen import CVRP
from colib.problems import TSP
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def random_tour(n, seed):
    t = list(range(n))
    random.Random(seed).shuffle(t)
    return t


def improving_2opt_moves(dist, t):
    n = len(t)
    return sum(1 for i in range(n) for j in range(i + 2, n) if not (i == 0 and j == n - 1)
               and dist[t[i]][t[j]] + dist[t[i + 1]][t[(j + 1) % n]] < dist[t[i]][t[i + 1]] + dist[t[j]][t[(j + 1) % n]])


def improving_oropt_moves(dist, t):
    n = len(t)
    count = 0
    for i in range(n):
        for L in (1, 2, 3):
            seg = [t[(i + k) % n] for k in range(L)]
            p, q = t[(i - 1) % n], t[(i + L) % n]
            gain = dist[p][seg[0]] + dist[seg[-1]][q] - dist[p][q]
            rest = [t[(i + L + k) % n] for k in range(n - L)]
            for k in range(len(rest) - 1):          # edges of the reduced tour except (p, q)
                c, e = rest[k], rest[k + 1]
                if (c, e) == (p, q):
                    continue
                for x, y in ((seg[0], seg[-1]), (seg[-1], seg[0])):
                    if dist[c][x] + dist[y][e] - dist[c][e] < gain:
                        count += 1
    return count


def is_perm(t, n):
    return sorted(t) == list(range(n))


class CountingDist:
    """A distance matrix that counts lookups."""
    def __init__(self, dist):
        self.rows = [self.Row(r, self) for r in dist]
        self.count = 0

    class Row:
        def __init__(self, row, owner):
            self.row, self.owner = row, owner

        def __getitem__(self, j):
            self.owner.count += 1
            return self.row[j]

        def __len__(self):
            return len(self.row)

    def __getitem__(self, i):
        return self.rows[i]

    def __len__(self):
        return len(self.rows)


class Script:
    """A stand-in rng replaying fixed samples and uniforms."""
    def __init__(self, pairs, us):
        self.pairs, self.us = list(pairs), list(us)

    def sample(self, population, k):
        return list(self.pairs.pop(0))

    def random(self):
        return self.us.pop(0)


# ---------------------------------------------------------------- step 1 ---

def test_step1_tour_length_and_nearest_neighbour():
    dist = ((0, 1, 5, 2), (1, 0, 3, 4), (5, 3, 0, 1), (2, 4, 1, 0))
    assert lab.tour_length(dist, [0, 1, 2, 3]) == 1 + 3 + 1 + 2
    assert lab.nearest_neighbour_tour(dist, 0) == [0, 1, 2, 3]
    assert lab.nearest_neighbour_tour(dist, 2) == [2, 3, 0, 1]
    tie = ((0, 2, 2, 9), (2, 0, 9, 1), (2, 9, 0, 1), (9, 1, 1, 0))
    assert lab.nearest_neighbour_tour(tie, 0) == [0, 1, 3, 2], "ties go to the lower index"


@pytest.mark.parametrize("seed", range(5))
def test_step1_neighbour_lists(seed):
    dist = TSP.random(25, seed).dist
    nl = lab.neighbour_lists(dist, 6)
    for a in range(25):
        assert len(nl[a]) == 6 and a not in nl[a]
        assert nl[a] == sorted((c for c in range(25) if c != a), key=lambda c: (dist[a][c], c))[:6]


# ---------------------------------------------------------------- step 2 ---

def edges_of(t):
    return {frozenset((t[i - 1], t[i])) for i in range(len(t))}


def reversed_stretch(t, i, j):
    n = len(t)
    t = list(t)
    for _ in range(((j - i) % n + 1) // 2):
        t[i], t[j] = t[j], t[i]
        i, j = (i + 1) % n, (j - 1) % n
    return t


@pytest.mark.parametrize("seed", range(12))
def test_step2_two_opt_move(seed):
    n, k = 30, 6
    dist = TSP.random(n, seed + 50).dist
    nl = lab.neighbour_lists(dist, k)
    t = random_tour(n, seed)
    pos = [0] * n
    for i, c in enumerate(t):
        pos[c] = i
    for a in range(n):
        move = lab.two_opt_move(dist, t, pos, nl, a)
        candidates = []
        for step in (1, -1):
            b = t[(pos[a] + step) % n]
            for c in nl[a]:
                if dist[a][c] >= dist[a][b]:
                    break
                d = t[(pos[c] + step) % n]
                if c != b and d != a and dist[a][c] + dist[b][d] < dist[a][b] + dist[c][d]:
                    candidates.append((a, b, c, d))
        if not candidates:
            assert move is None, f"city {a} has no improving candidate move"
            continue
        i, j, ends = move
        assert tuple(ends) == candidates[0], "the first candidate, successor direction first"
        a_, b, c, d = ends
        new = reversed_stretch(t, i, j)
        assert edges_of(new) == (edges_of(t) - {frozenset((a_, b)), frozenset((c, d))}) | {frozenset((a_, c)), frozenset((b, d))}
        assert lab.tour_length(dist, new) == lab.tour_length(dist, t) - (dist[a_][b] + dist[c][d] - dist[a_][c] - dist[b][d])


def test_step2_neighbour_lists_are_cut_short():
    n = 200
    dist = TSP.random(n, 11).dist
    nl = lab.neighbour_lists(dist, n - 1)
    t = lab.two_opt(dist, lab.nearest_neighbour_tour(dist), lab.neighbour_lists(dist, 10), dont_look=False)
    t = lab.two_opt(dist, t, nl, dont_look=False)
    pos = [0] * n
    for i, c in enumerate(t):
        pos[c] = i
    counting = CountingDist(dist)
    assert all(lab.two_opt_move(counting, t, pos, nl, a) is None for a in range(n))
    assert counting.count < 40 * n, "stop scanning a's list once dist[a][c] >= dist[a][b]"


@pytest.mark.parametrize("seed", range(15))
def test_step2_sweep_reaches_a_2opt_optimum(seed):
    n = random.Random(seed).randint(5, 40)
    dist = TSP.random(n, seed).dist
    start = random_tour(n, seed)
    with time_limit(20):
        t = lab.two_opt(dist, start, lab.neighbour_lists(dist, n - 1), dont_look=False)
    assert is_perm(t, n) and start == random_tour(n, seed), "input unchanged"
    assert lab.tour_length(dist, t) <= lab.tour_length(dist, start)
    assert improving_2opt_moves(dist, t) == 0


@pytest.mark.parametrize("seed", range(10))
def test_step2_neighbour_lists_limit_the_moves(seed):
    n, k = 40, 5
    dist = TSP.random(n, seed + 100).dist
    nl = lab.neighbour_lists(dist, k)
    t = lab.two_opt(dist, random_tour(n, seed), nl, dont_look=False)
    pos = {c: i for i, c in enumerate(t)}
    for a in range(n):
        for step in (1, -1):
            b = t[(pos[a] + step) % n]
            for c in nl[a]:
                d = t[(pos[c] + step) % n]
                if c != b and d != a and dist[a][c] < dist[a][b]:
                    assert dist[a][c] + dist[b][d] >= dist[a][b] + dist[c][d], "a candidate move still improves"


@pytest.mark.parametrize("seed", range(10))
def test_step2_dont_look_bits(seed):
    n = 60
    dist = TSP.random(n, seed + 200).dist
    nl = lab.neighbour_lists(dist, 8)
    start = random_tour(n, seed)
    t = lab.two_opt(dist, start, nl, dont_look=True)
    assert is_perm(t, n) and lab.tour_length(dist, t) < lab.tour_length(dist, start)
    swept = lab.two_opt(dist, start, nl, dont_look=False)
    assert lab.tour_length(dist, t) <= 1.1 * lab.tour_length(dist, swept)


def test_step2_dont_look_bits_save_work():
    n = 300
    dist = TSP.random(n, 7).dist
    nl = lab.neighbour_lists(dist, 8)
    start = lab.nearest_neighbour_tour(dist)
    fast, slow = CountingDist(dist), CountingDist(dist)
    lab.two_opt(fast, start, nl, dont_look=True)
    lab.two_opt(slow, start, nl, dont_look=False)
    assert fast.count < 0.7 * slow.count


def test_step2_tiny_tours():
    dist = ((0, 1, 2), (1, 0, 1), (2, 1, 0))
    assert is_perm(lab.two_opt(dist, [2, 0, 1], lab.neighbour_lists(dist, 2)), 3)


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(30))
def test_step3_or_opt_optimum(seed):
    n = random.Random(seed).randint(8, 11)
    dist = TSP.random(n, seed + 300).dist
    start = random_tour(n, seed)
    with time_limit(20):
        t = lab.or_opt(dist, start, lab.neighbour_lists(dist, n - 1))
    assert is_perm(t, n) and lab.tour_length(dist, t) <= lab.tour_length(dist, start)
    assert improving_oropt_moves(dist, t) == 0


@pytest.mark.parametrize("seed", range(10))
def test_step3_or_opt_with_short_lists(seed):
    n, k = 12, 3
    dist = TSP.random(n, seed + 350).dist
    nl = lab.neighbour_lists(dist, k)
    t = lab.or_opt(dist, random_tour(n, seed), nl)
    for i in range(n):
        for L in (1, 2, 3):
            seg = [t[(i + m) % n] for m in range(L)]
            p, q = t[(i - 1) % n], t[(i + L) % n]
            gain = dist[p][seg[0]] + dist[seg[-1]][q] - dist[p][q]
            rest = [t[(i + L + m) % n] for m in range(n - L)]
            for c in nl[seg[0]] + nl[seg[-1]]:
                if c in seg or c == p:
                    continue
                e = rest[(rest.index(c) + 1) % len(rest)]
                for x, y in ((seg[0], seg[-1]), (seg[-1], seg[0])):
                    assert dist[c][x] + dist[y][e] - dist[c][e] >= gain, "a candidate Or-move still improves"


def test_step3_or_opt_moves_a_reversed_pair():
    # points on a line 0..9 at x = position, tour visits them in order except 5 and 4 swapped and moved
    xs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    dist = tuple(tuple(abs(a - b) * 10 for b in xs) for a in xs)
    start = [0, 1, 2, 3, 6, 7, 5, 4, 8, 9]
    t = lab.or_opt(dist, start, lab.neighbour_lists(dist, 9))
    assert lab.tour_length(dist, t) == 180


@pytest.mark.parametrize("seed", range(25))
def test_step3_local_search(seed):
    n = random.Random(seed).randint(8, 12)
    dist = TSP.random(n, seed + 400).dist
    t = lab.local_search(dist, random_tour(n, seed), lab.neighbour_lists(dist, n - 1))
    assert is_perm(t, n)
    assert improving_2opt_moves(dist, t) == 0 and improving_oropt_moves(dist, t) == 0


def test_step3_local_search_needs_more_than_one_round():
    # on this instance Or-opt, run after 2-opt, opens up a new improving 2-opt move
    n = 40
    dist = TSP.random(n, 128).dist
    t = lab.local_search(dist, random_tour(n, 128), lab.neighbour_lists(dist, n - 1))
    assert improving_2opt_moves(dist, t) == 0 and improving_oropt_moves(dist, t) == 0


# ---------------------------------------------------------------- step 4 ---

def test_step4_accept():
    assert lab.accept(-3, 0, 0.99) and lab.accept(0, 5, 0.99)
    assert not lab.accept(1, 0, 0.0)
    assert lab.accept(2, 4, math.exp(-0.5) - 1e-9) and not lab.accept(2, 4, math.exp(-0.5) + 1e-9)


def test_step4_temperature():
    assert lab.temperature(100, 1, 101, 0) == pytest.approx(100)
    assert lab.temperature(100, 1, 101, 100) == pytest.approx(1)
    assert lab.temperature(100, 1, 101, 50) == pytest.approx(10)
    assert lab.temperature(8, 8, 1, 0) == pytest.approx(8)


def test_step4_annealing_follows_the_script():
    dist = TSP.random(6, 3).dist
    tour = [0, 1, 2, 3, 4, 5]
    # iteration 0 proposes reversing positions 1..3; iteration 1 proposes 0..5 (skipped); iteration 2 proposes 2..4
    rng = Script([(3, 1), (0, 5), (4, 2)], [0.0, 0.0, 1.0])
    best, best_len = lab.simulated_annealing(dist, tour, rng, 3, 1e9, 1e9)
    t = [0, 3, 2, 1, 4, 5]                          # u = 0 always accepts
    t2 = t[:2] + t[2:5][::-1] + t[5:]               # u = 1.0 accepts only if not worse
    delta2 = lab.tour_length(dist, t2) - lab.tour_length(dist, t)
    final = t2 if delta2 <= 0 else t
    candidates = [tour, t, final]
    assert best_len == min(lab.tour_length(dist, c) for c in candidates)
    assert lab.tour_length(dist, best) == best_len and is_perm(best, 6)


def test_step4_annealing_keeps_the_best_not_the_last():
    n = 12
    dist = TSP.random(n, 21).dist
    tour = random_tour(n, 21)

    def rev(t, i, j):
        return t[:i] + t[i:j + 1][::-1] + t[j + 1:]

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if not (i == 0 and j == n - 1)]
    i1, j1 = next(p for p in pairs if lab.tour_length(dist, rev(tour, *p)) < lab.tour_length(dist, tour))
    t1 = rev(tour, i1, j1)
    i2, j2 = next(p for p in pairs if lab.tour_length(dist, rev(t1, *p)) > lab.tour_length(dist, t1))
    best, best_len = lab.simulated_annealing(dist, tour, Script([(j1, i1), (i2, j2)], [0.0, 0.0]), 2, 1e9, 1e9)
    assert best_len == lab.tour_length(dist, t1) and lab.tour_length(dist, best) == best_len


@pytest.mark.parametrize("seed", range(6))
def test_step4_annealing(seed):
    n = 40
    dist = TSP.random(n, seed + 500).dist
    start = random_tour(n, seed)
    best, best_len = lab.simulated_annealing(dist, start, random.Random(seed), 20000, 50.0, 0.5)
    assert is_perm(best, n) and lab.tour_length(dist, best) == best_len
    assert best_len < 0.6 * lab.tour_length(dist, start)
    cold, cold_len = lab.simulated_annealing(dist, start, random.Random(seed), 20000, 1e-9, 1e-9)
    assert lab.tour_length(dist, cold) == cold_len <= lab.tour_length(dist, start)


# ---------------------------------------------------------------- step 5 ---

def small_cvrp(seed, n=12):
    return CVRP.random(n, seed=seed, capacity=20, max_demand=8)


def feasible(cvrp, routes):
    served = sorted(c for r in routes for c in r)
    return served == list(range(1, cvrp.n + 1)) and all(cvrp.route_load(r) <= cvrp.capacity for r in routes) \
        and all(r for r in routes)


def test_step5_random_removal():
    routes = [[3, 1], [2], [5, 4]]
    rng = random.Random(9)
    kept, removed = lab.random_removal(routes, 2, rng)
    assert removed == random.Random(9).sample([1, 2, 3, 4, 5], 2)
    assert sorted(c for r in kept for c in r) == sorted(set(range(1, 6)) - set(removed))
    assert all(kept) and routes == [[3, 1], [2], [5, 4]]


def test_step5_worst_removal_by_hand():
    # depot at 0; customer 3 is a far detour on route [1, 3, 2]
    dist = ((0, 1, 1, 10), (1, 0, 1, 10), (1, 1, 0, 10), (10, 10, 10, 0))
    cvrp = CVRP(dist, (0, 1, 1, 1), 10)
    routes, removed = lab.worst_removal(cvrp, [[1, 3, 2]], 1)
    assert removed == [3] and routes == [[1, 2]]
    routes, removed = lab.worst_removal(cvrp, [[3], [1, 2]], 2)
    assert removed == [3, 1] and routes == [[2]]


@pytest.mark.parametrize("seed", range(10))
def test_step5_greedy_insertion_is_cheapest_and_feasible(seed):
    cvrp = small_cvrp(seed)
    r = random.Random(seed)
    routes = lab.greedy_insertion(cvrp, [], list(range(1, cvrp.n + 1)))
    assert feasible(cvrp, routes)
    c = r.randint(1, cvrp.n)
    partial = [[x for x in route if x != c] for route in routes]
    partial = [p for p in partial if p]
    after = lab.greedy_insertion(cvrp, partial, [c])
    options = [lab.solution_cost(cvrp, partial) + cvrp.dist[0][c] + cvrp.dist[c][0]]
    for ri, route in enumerate(partial):
        if cvrp.route_load(route) + cvrp.demand[c] <= cvrp.capacity:
            for k in range(len(route) + 1):
                options.append(lab.solution_cost(cvrp, partial[:ri] + [route[:k] + [c] + route[k:]] + partial[ri + 1:]))
    feasible_insertions = options[1:]
    best = min(feasible_insertions) if feasible_insertions else options[0]
    assert lab.solution_cost(cvrp, after) == best and feasible(cvrp, after)


def test_step5_greedy_insertion_ties_and_new_routes():
    dist = ((0, 5, 5, 5), (5, 0, 1, 1), (5, 1, 0, 1), (5, 1, 1, 0))
    cvrp = CVRP(dist, (0, 3, 3, 3), 6)
    assert lab.greedy_insertion(cvrp, [[1]], [2]) == [[2, 1]], "ties: earlier position"
    assert lab.greedy_insertion(cvrp, [[1, 2]], [3]) == [[1, 2], [3]], "no capacity: a new route"


def test_step5_update_weights():
    assert lab.update_weights([1.0, 2.0, 3.0], [66, 0, 10], [2, 0, 5], 0.5) == pytest.approx([17.0, 2.0, 2.5])


class Recording(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.weights_seen = []

    def choices(self, population, weights=None, **kw):
        self.weights_seen.append(None if weights is None else list(weights))
        return super().choices(population, weights, **kw)


def test_step5_alns_roulette_uses_the_adaptive_weights():
    cvrp = small_cvrp(3, 15)
    rng = Recording(0)
    _, _, history = lab.alns(cvrp, 30, rng, segment=10)
    assert len(rng.weights_seen) == 30
    assert rng.weights_seen[0] == [1.0, 1.0]
    assert rng.weights_seen[10] == pytest.approx(history[0]) and rng.weights_seen[25] == pytest.approx(history[1])


@pytest.mark.parametrize("seed", range(5))
def test_step5_alns(seed):
    cvrp = small_cvrp(seed + 20, 25)
    with time_limit(60):
        routes, cost, history = lab.alns(cvrp, 300, random.Random(seed), segment=50)
    assert feasible(cvrp, routes) and lab.solution_cost(cvrp, routes) == cost
    start = lab.solution_cost(cvrp, lab.greedy_insertion(cvrp, [], list(range(1, cvrp.n + 1))))
    assert cost < start
    assert len(history) == 6 and all(len(w) == 2 and min(w) > 0 for w in history)


# ---------------------------------------------------------------- step 6 ---

def test_step6_ttt_points():
    assert lab.ttt_points([3.0, None, 1.0, 2.0]) == [(1.0, 0.125), (2.0, 0.375), (3.0, 0.625)]
    assert lab.ttt_points([None, None]) == []


@pytest.mark.parametrize("seed", range(12))
def test_step6_mann_whitney_matches_scipy(seed):
    r = random.Random(seed)
    a = [r.choice([r.random(), round(r.random(), 1)]) for _ in range(r.randint(5, 30))]
    b = [r.choice([r.random() + 0.2 * (seed % 3), round(r.random(), 1)]) for _ in range(r.randint(5, 30))]
    U, p = lab.mann_whitney(a, b)
    ref = mannwhitneyu(a, b, alternative="two-sided", method="asymptotic", use_continuity=True)
    assert U == pytest.approx(ref.statistic) and p == pytest.approx(ref.pvalue, rel=1e-6, abs=1e-12)


def test_step6_verdict():
    r = random.Random(1)
    fast = [r.expovariate(1.0) for _ in range(30)]
    slow = [r.expovariate(0.2) for _ in range(30)]
    same = [r.expovariate(1.0) for _ in range(30)]
    assert lab.verdict(fast, slow) == "a" and lab.verdict(slow, fast) == "b"
    assert lab.verdict(fast, same) is None
    assert lab.verdict([1, 2, 3], [1, 2, 3]) is None
    capped_a = [4.0] * 16 + [1.0 + 0.01 * i for i in range(14)]
    capped_b = [4.0] * 29 + [1.0]
    assert lab.verdict(capped_a, capped_b) == "a", "both medians are the cap; the ranks still differ"
