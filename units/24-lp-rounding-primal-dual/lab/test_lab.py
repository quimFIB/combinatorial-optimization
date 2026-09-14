"""Tests for unit 24. Run with `uv run co test 24`. You should not need to edit this."""

import itertools
import math
import random
from fractions import Fraction

import pytest

from colib.approx import FacilityLocation, covering_lp
from colib.mip import MILP, highs_mip, lp_relaxation
from colib.oracle import brute_force
from colib.problems import SetCover, VertexCover
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def random_weighted_graph(seed, n_low=4, n_high=14, p=0.35):
    r = random.Random(seed)
    n = r.randint(n_low, n_high)
    edges = tuple((u, v) for u in range(n) for v in range(u + 1, n) if r.random() < p) or ((0, 1),)
    return n, edges, [r.randint(1, 20) for _ in range(n)]


def weighted_vc_optimum(n, edges, w):
    milp = MILP(c=tuple(w), A_ub=tuple(tuple(-1 if v in e else 0 for v in range(n)) for e in edges),
                b_ub=(-1,) * len(edges), ub=(1,) * n, integer=(True,) * n)
    return round(highs_mip(milp, options={"mip_rel_gap": 0.0}).value)


def set_cover_lp_value(sc):
    return covering_lp([[1 if e in s else 0 for s in sc.sets] for e in range(sc.universe)], sc.costs)[0]


def random_set_cover(seed, universe_low=5, universe_high=14):
    r = random.Random(seed)
    u = r.randint(universe_low, universe_high)
    nsets = r.randint(4, 10)
    sets = [set(r.sample(range(u), r.randint(1, max(2, u // 2)))) for _ in range(nsets)]
    for e in range(u):
        if not any(e in s for s in sets):
            sets[r.randrange(nsets)].add(e)
    return SetCover(u, tuple(frozenset(s) for s in sets), tuple(r.randint(1, 9) for _ in range(nsets)))


# ---------------------------------------------------------------- step 1 ---

@pytest.mark.parametrize("seed", range(20))
def test_step1_lp_is_a_relaxation(seed):
    n, edges, w = random_weighted_graph(seed)
    value, x = lab.vertex_cover_lp(n, edges, w)
    assert len(x) == n and all(-1e-9 <= xv <= 1 + 1e-9 for xv in x)
    assert all(x[u] + x[v] >= 1 - 1e-7 for u, v in edges)
    assert abs(value - sum(wi * xi for wi, xi in zip(w, x))) < 1e-6
    assert value <= weighted_vc_optimum(n, edges, w) + 1e-6


def test_step1_threshold_rounding():
    assert lab.threshold_rounding([0.5, 0.4999999999, 0.49, 1.0, 0.0], 0.5) == [1, 1, 0, 1, 0]
    assert lab.threshold_rounding([0.3, 0.34, 0.25], 1 / 3) == [0, 1, 0]


@pytest.mark.parametrize("seed", range(25))
def test_step1_rounding_within_twice_the_lp(seed):
    n, edges, w = random_weighted_graph(seed + 100)
    cover, value = lab.vertex_cover_rounding(n, edges, w)
    assert VertexCover(n, edges).is_feasible(cover)
    cost = sum(wi for wi, c in zip(w, cover) if c)
    assert cost <= 2 * value + 1e-6
    assert value <= weighted_vc_optimum(n, edges, w) + 1e-6


def test_step1_lp_on_an_odd_cycle_is_half_everywhere():
    edges = ((0, 1), (1, 2), (2, 3), (3, 4), (0, 4))
    value, x = lab.vertex_cover_lp(5, edges, [1] * 5)
    assert abs(value - 2.5) < 1e-7
    cover, _ = lab.vertex_cover_rounding(5, edges, [1] * 5)
    assert sum(cover) == 5, "rounding all halves up takes every vertex"


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(10))
def test_step2_set_cover_lp(seed):
    sc = random_set_cover(seed)
    value, x = lab.set_cover_lp(sc)
    assert len(x) == sc.n
    assert all(sum(x[j] for j, s in enumerate(sc.sets) if e in s) >= 1 - 1e-7 for e in range(sc.universe))
    assert abs(value - sum(c * xj for c, xj in zip(sc.costs, x))) < 1e-6
    assert value <= brute_force(sc).value + 1e-6


def test_step2_exact_probabilities_by_hand():
    sc = SetCover(3, (frozenset({0, 1}), frozenset({1, 2}), frozenset({2})), (1, 2, 3))
    x = [0.5, 0.25, 1.0]
    probs = lab.uncovered_probability(sc, x, 2)
    assert probs == pytest.approx([0.25, 0.25 * 0.5625, 0.0])
    assert lab.expected_cost(sc, x, 2) == pytest.approx(1 * 0.75 + 2 * (1 - 0.5625) + 3 * 1.0)
    assert lab.failure_bound(10, 3) == pytest.approx(10 * math.exp(-3))


@pytest.mark.parametrize("seed", range(6))
def test_step2_randomized_rounding_matches_its_probabilities(seed):
    sc = random_set_cover(seed + 20, 8, 14)
    _, x = lab.set_cover_lp(sc)
    rounds = 2
    probs = lab.uncovered_probability(sc, x, rounds)
    rng = random.Random(seed)
    trials = 4000
    missed = [0] * sc.universe
    total_cost = 0
    for _ in range(trials):
        chosen = lab.randomized_rounding(sc, x, rounds, rng)
        assert len(chosen) == sc.n and set(chosen) <= {0, 1}
        total_cost += sc.objective(chosen)
        covered = set().union(*(s for s, c in zip(sc.sets, chosen) if c)) if any(chosen) else set()
        for e in range(sc.universe):
            missed[e] += e not in covered
    for e in range(sc.universe):
        sd = math.sqrt(probs[e] * (1 - probs[e]) / trials)
        assert abs(missed[e] / trials - probs[e]) <= 5 * sd + 2 / trials, f"element {e}"
    mean = lab.expected_cost(sc, x, rounds)
    spread = math.sqrt(sum(c * c for c in sc.costs) / trials)
    assert abs(total_cost / trials - mean) <= 5 * spread
    assert mean <= rounds * lab.set_cover_lp(sc)[0] + 1e-6


def test_step2_rounds_are_independent_repetitions():
    # every pair of 4 elements is a set, all at x = 1/3: each element is in 3 sets, so LP-feasible
    pairs = list(itertools.combinations(range(4), 2))
    sc = SetCover(4, tuple(frozenset(p) for p in pairs), (1,) * 6)
    x = [1 / 3] * 6
    for rounds in (1, 3):
        rng = random.Random(rounds)
        trials = 6000
        miss = sum(0 not in set().union(*(s for s, c in zip(sc.sets, lab.randomized_rounding(sc, x, rounds, rng)) if c),
                                         set()) for _ in range(trials))
        p = (2 / 3) ** (3 * rounds)
        assert abs(miss / trials - p) <= 5 * math.sqrt(p * (1 - p) / trials)
        assert lab.uncovered_probability(sc, x, rounds)[0] == pytest.approx(p)


@pytest.mark.parametrize("seed", range(10))
def test_step2_union_bound_holds(seed):
    sc = random_set_cover(seed + 60, 8, 14)
    _, x = lab.set_cover_lp(sc)
    for rounds in (1, 2, 4, 8):
        assert sum(lab.uncovered_probability(sc, x, rounds)) <= lab.failure_bound(sc.universe, rounds) + 1e-9


# ---------------------------------------------------------------- step 3 ---

def test_step3_frequency():
    sc = SetCover(3, (frozenset({0, 1}), frozenset({1, 2}), frozenset({1})), (1, 1, 1))
    assert lab.frequency(sc) == 3


@pytest.mark.parametrize("seed", range(30))
def test_step3_primal_dual(seed):
    sc = random_set_cover(seed + 200)
    x, y = lab.primal_dual_set_cover(sc)
    y = [Fraction(v) for v in y]
    assert sc.is_feasible(x)
    assert all(v >= 0 for v in y)
    for j, s in enumerate(sc.sets):
        load = sum(y[e] for e in s)
        assert load <= sc.costs[j], "dual feasible"
        if x[j]:
            assert load == sc.costs[j], "only tight sets are bought"
    assert sc.objective(x) <= lab.frequency(sc) * sum(y)
    assert sum(y) <= set_cover_lp_value(sc) + 1e-6


def test_step3_order_and_buying_every_tight_set():
    # element 0: raise y_0 to 2, which makes sets 0 and 1 tight together; both are bought
    sc = SetCover(3, (frozenset({0, 1}), frozenset({0, 2}), frozenset({1, 2})), (2, 2, 5))
    x, y = lab.primal_dual_set_cover(sc)
    assert x == [1, 1, 0] and [Fraction(v) for v in y] == [2, 0, 0]
    sc = SetCover(3, (frozenset({2}), frozenset({0, 1}), frozenset({1, 2})), (4, 3, 1))
    x, y = lab.primal_dual_set_cover(sc)
    assert x == [0, 1, 1] and [Fraction(v) for v in y] == [3, 0, 1]
    sc = SetCover(2, (frozenset({0, 1}), frozenset({0})), (2, 2))
    assert lab.primal_dual_set_cover(sc)[0] == [1, 1], "every set that goes tight is bought, not just the first"


@pytest.mark.parametrize("seed", range(10))
def test_step3_vertex_cover_is_the_f_equals_2_case(seed):
    n, edges, w = random_weighted_graph(seed + 300)
    sc = SetCover(len(edges), tuple(frozenset(k for k, e in enumerate(edges) if v in e) for v in range(n)), tuple(w))
    x, y = lab.primal_dual_set_cover(sc)
    assert lab.frequency(sc) <= 2
    assert sc.objective(x) <= 2 * weighted_vc_optimum(n, edges, w)


# ---------------------------------------------------------------- step 4 ---

def fl_optimum(fl):
    return round(highs_mip(fl.milp(), options={"mip_rel_gap": 0.0}).value)


def test_step4_dual_ascent_by_hand():
    # one facility of cost 6 at distances 1 and 3: receipts (t - 1) + (t - 3) reach 6 at t = 5
    fl = FacilityLocation((6,), ((1, 3),))
    alpha, opened_at = lab.jv_dual_ascent(fl)
    assert [Fraction(a) for a in alpha] == [5, 5] and opened_at == {0: 5}
    # a cheap far facility and a costly near one: the near one is paid first by client 0 alone
    fl = FacilityLocation((2, 30), ((1, 20), (10, 10)))
    alpha, opened_at = lab.jv_dual_ascent(fl)
    assert opened_at[0] == 3 and Fraction(alpha[0]) == 3
    # client 1 keeps growing until it reaches facility 0 at distance 20
    assert Fraction(alpha[1]) == 20


@pytest.mark.parametrize("seed", range(25))
def test_step4_dual_ascent_invariants(seed):
    r = random.Random(seed)
    fl = FacilityLocation.random(r.randint(1, 6), r.randint(1, 12), seed)
    with time_limit(20):
        alpha, opened_at = lab.jv_dual_ascent(fl)
    alpha = [Fraction(a) for a in alpha]
    opened_at = {i: Fraction(t) for i, t in opened_at.items()}
    assert opened_at, "some facility opens"
    for i in range(fl.nf):
        receipts = sum(max(Fraction(0), a - fl.dist[i][j]) for j, a in enumerate(alpha))
        assert receipts <= fl.open_cost[i], "dual feasible: no facility is overpaid"
        if i in opened_at:
            assert receipts == fl.open_cost[i], "a temporarily open facility is exactly paid"
            paid_by_then = sum(max(Fraction(0), min(a, opened_at[i]) - fl.dist[i][j]) for j, a in enumerate(alpha))
            assert paid_by_then == fl.open_cost[i], "and it opened at the moment it was paid"
    for j, a in enumerate(alpha):
        assert a == min(max(t, fl.dist[i][j]) for i, t in opened_at.items()), \
            "each client froze at the first moment it was tight with an open facility"
    assert sum(alpha) <= fl_optimum(fl) + 1e-9


@pytest.mark.parametrize("seed", range(25))
def test_step4_prune_and_guarantee(seed):
    r = random.Random(seed + 40)
    fl = FacilityLocation.random(r.randint(2, 7), r.randint(2, 14), seed + 40)
    with time_limit(20):
        opened, assign, alpha = lab.jain_vazirani(fl)
    alpha = [Fraction(a) for a in alpha]
    _, opened_at = lab.jv_dual_ascent(fl)
    pays = {i: {j for j in range(fl.nc) if alpha[j] > fl.dist[i][j]} for i in opened_at}
    assert opened and set(opened) <= set(opened_at) and opened == sorted(opened)
    for a, b in itertools.combinations(opened, 2):
        assert not (pays[a] & pays[b]), "kept facilities share no paying client"
    for i in opened_at:
        assert i in opened or any(pays[i] & pays[k] for k in opened), "maximal: a dropped facility conflicts"
    assert assign == [min(opened, key=lambda i: (fl.dist[i][j], i)) for j in range(fl.nc)]
    cost = fl.cost(opened, assign)
    assert cost <= 3 * sum(alpha)
    assert cost <= 3 * fl_optimum(fl)


def test_step4_prune_keeps_the_earliest():
    fl = FacilityLocation((4, 4), ((0, 2), (2, 0)))
    alpha = [Fraction(3), Fraction(3)]
    assert lab.jv_prune(fl, alpha, {0: Fraction(2), 1: Fraction(1)}) == [1]
    assert lab.jv_prune(fl, alpha, {0: Fraction(1), 1: Fraction(1)}) == [0]
    assert lab.jv_prune(fl, [Fraction(1), Fraction(1)], {0: Fraction(1), 1: Fraction(1)}) == [0, 1]
    # a client exactly tight with both (alpha = distance) pays neither: no conflict
    fl = FacilityLocation((0, 0), ((1, 3), (1, 3)))
    assert lab.jv_prune(fl, [Fraction(1), Fraction(0)], {0: Fraction(1), 1: Fraction(1)}) == [0, 1]
    # client 0 pays facility 1 (alpha 1 > 0) but is only tight with facility 0 (alpha 1 = 1): no conflict
    fl = FacilityLocation((0, 0), ((1, 3), (0, 3)))
    assert lab.jv_prune(fl, [Fraction(1), Fraction(0)], {1: Fraction(0), 0: Fraction(1)}) == [0, 1]


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("n", [3, 5, 8])
def test_step5_vertex_cover_gap(n):
    vc = lab.vertex_cover_gap_instance(n)
    assert vc.n == n and len(vc.edges) == n * (n - 1) // 2
    value, _ = lab.vertex_cover_lp(n, vc.edges, [1] * n)
    assert abs(value - n / 2) < 1e-7
    assert weighted_vc_optimum(n, vc.edges, [1] * n) == n - 1


@pytest.mark.parametrize("k", [2, 3, 4])
def test_step5_set_cover_gap(k):
    sc = lab.set_cover_gap_instance(k)
    N = 2 ** k - 1
    assert sc.universe == N and sc.n == N and all(c == 1 for c in sc.costs)
    assert all(len(s) == 2 ** (k - 1) for s in sc.sets)
    assert (0 in sc.sets[0]) and (1 not in sc.sets[0]), "set v=1 holds element u=1, not u=2"
    value, x = lab.uniform_fractional(sc)
    assert Fraction(value) == Fraction(N, 2 ** (k - 1))
    assert all(sum(Fraction(x[j]) for j, s in enumerate(sc.sets) if e in s) >= 1 for e in range(N))
    assert set_cover_lp_value(sc) <= float(value) + 1e-7
    assert brute_force(sc).value == k


def test_step5_uniform_fractional_uses_the_rarest_element():
    sc = SetCover(3, (frozenset({0, 1}), frozenset({1, 2}), frozenset({0, 1, 2})), (2, 3, 4))
    value, x = lab.uniform_fractional(sc)
    assert [Fraction(v) for v in x] == [Fraction(1, 2)] * 3 and Fraction(value) == Fraction(9, 2)
