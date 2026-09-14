"""Tests for unit 19. Run with `uv run co test 19`. You should not need to edit this."""

import itertools
import random

import pytest

from colib.csp import quasigroup_completion
from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
cp = unit("17")
gc = unit("18")

HEAVY = quasigroup_completion(12, 0.55, 0)          # a heavy-tailed runtime distribution under random first-fail
LIGHT = quasigroup_completion(12, 0.58, 3)          # a light-tailed one


def luby_reference(i):
    """The textbook recursive definition."""
    k = 1
    while 2 ** k - 1 < i:
        k += 1
    if i == 2 ** k - 1:
        return 2 ** (k - 1)
    return luby_reference(i - 2 ** (k - 1) + 1)


# ---------------------------------------------------------------- step 1 ---

def test_step1_luby():
    assert [lab.luby(i) for i in range(1, 16)] == [1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8]
    assert all(lab.luby(i) == luby_reference(i) for i in range(1, 300))


def test_step1_random_first_fail_breaks_ties_randomly():
    store = cp.Store([{0, 1}, {0, 1, 2}, {5, 6}, {1}, {3, 4}])
    picks = {lab.random_first_fail(random.Random(s))(store) for s in range(60)}
    assert picks == {0, 2, 4}
    assert lab.random_first_fail(random.Random(0))(cp.Store([{1}, {2}])) is None


def test_step1_random_first_fail_is_reproducible():
    store = cp.Store([{0, 1}] * 10)
    a = lab.random_first_fail(random.Random(7))
    b = lab.random_first_fail(random.Random(7))
    assert [a(store) for _ in range(20)] == [b(store) for _ in range(20)]


def test_step1_qcp_model():
    grid = quasigroup_completion(6, 0.5, 2)
    domains, props = lab.qcp_model(grid)
    assert len(domains) == 36 and len(props) == 2 * 6 * 15
    sols, _ = cp.solve(domains, props)
    sq = [sols[0][i * 6: i * 6 + 6] for i in range(6)]
    assert all(sorted(row) == list(range(6)) for row in sq)
    assert all(sorted(sq[i][j] for i in range(6)) == list(range(6)) for j in range(6))
    assert all(sq[i][j] == grid[i][j] for i in range(6) for j in range(6) if grid[i][j] is not None)


# ---------------------------------------------------------------- step 2 ---

def test_step2_weights_and_wdeg():
    p01, p12, p23 = cp.NotEqual(0, 1), cp.NotEqual(1, 2), cp.NotEqual(2, 3)
    h = lab.DomWDeg([p01, p12, p23])
    store = cp.Store([{0, 1}, {0, 1, 2}, {0, 1}, {5}])
    assert h.wdeg(store, 1) == 2 and h.wdeg(store, 2) == 1, "p23 has no other unfixed variable"
    h.on_failure(p12)
    h.on_failure(p12)
    assert h.wdeg(store, 1) == 4 and h.wdeg(store, 2) == 3
    assert h.choose(store) == 2, "|D|/wdeg: 2/3 beats 3/4 and 2/1"
    wider = cp.Store([{0, 1}, {0, 1, 2}, {0, 1, 2}, {5}])
    assert h.choose(wider) == 1, "now 3/4 beats 3/3 and 2/1"


def test_step2_choose_ties_and_none():
    h = lab.DomWDeg([cp.NotEqual(0, 1)])
    assert h.choose(cp.Store([{1, 2}, {1, 2}])) == 0
    assert h.choose(cp.Store([{1}, {2}])) is None
    picks = {lab.DomWDeg([cp.NotEqual(0, 1), cp.NotEqual(1, 2)], random.Random(s)).choose(cp.Store([{1, 2}] * 3))
             for s in range(40)}
    assert picks == {1}, "variable 1 has weighted degree 2, the others 1"
    picks = {lab.DomWDeg([], random.Random(s)).choose(cp.Store([{1, 2}] * 3)) for s in range(40)}
    assert picks == {0, 1, 2}, "no constraints: every score is infinite, and ties are random"


def test_step2_finds_a_hidden_core():
    # an easy chain of 3-valued variables, and 5 variables that must differ over 4 values
    n = 14
    domains = [range(3)] * n + [range(4)] * 5
    props = [cp.NotEqual(i, i + 1) for i in range(n - 1)]
    props += [cp.NotEqual(n + a, n + b) for a in range(5) for b in range(a + 1, 5)]
    with time_limit(60):
        _, ff = cp.solve(domains, props, node_limit=20_000)
        h = lab.DomWDeg(props)
        sols, wd = cp.solve(domains, props, choose=h.choose, on_failure=h.on_failure, node_limit=20_000)
    assert not ff.extra["complete"], "first-fail wanders in the easy chain"
    assert not sols and wd.extra["complete"] and wd.nodes < 500, "dom/wdeg learns where the failures are"


def test_step2_correct_solutions():
    domains, props = cp.queens(8)
    h = lab.DomWDeg(props, random.Random(1))
    sols, _ = cp.solve(domains, props, choose=h.choose, on_failure=h.on_failure, all_solutions=True)
    assert len(sols) == 92


# ---------------------------------------------------------------- step 3 ---

def test_step3_limits_follow_luby(monkeypatch):
    limits = []
    real = lab.cp.solve

    def spy(*args, **kw):
        limits.append(kw.get("node_limit"))
        return real(*args, **kw)
    monkeypatch.setattr(lab.cp, "solve", spy)
    domains, props = cp.queens(3)                             # infeasible; but make each search hit its limit:
    domains = domains + [range(2)] * 12                       # 12 free variables branched first by lowest index
    lowest = lambda store, stats=None: next((v for v in range(3, 15) if len(store.dom[v]) > 1),
                                            next((v for v, d in enumerate(store.dom) if len(d) > 1), None))
    sol, stats = lab.solve_with_restarts(domains, props, lowest, base=3, max_restarts=8)
    assert sol is None
    assert limits == [3 * luby_reference(i) for i in range(1, 9)]
    assert stats.extra["restarts"] == 7


def test_step3_stops_on_proof_and_budget():
    sol, stats = lab.solve_with_restarts(*cp.queens(3), cp.first_fail, base=1000)
    assert sol is None and stats.extra["restarts"] == 0, "a complete search proves infeasibility: no restart"
    sol, stats = lab.solve_with_restarts(*lab.qcp_model(HEAVY), lab.random_first_fail(random.Random(0)),
                                         base=2, node_budget=25)
    assert stats.nodes <= 25


@pytest.mark.parametrize("seed", range(5))
def test_step3_solutions_are_valid(seed):
    domains, props = lab.qcp_model(HEAVY)
    h = lab.DomWDeg(props, random.Random(seed))
    with time_limit(60):
        sol, stats = lab.solve_with_restarts(domains, props, h.choose, h.on_failure, base=30)
    n = 12
    sq = [sol[i * n: i * n + n] for i in range(n)]
    assert all(sorted(r) == list(range(n)) for r in sq)
    assert all(sorted(sq[i][j] for i in range(n)) == list(range(n)) for j in range(n))


# ---------------------------------------------------------------- step 4 ---

def test_step4_summarise():
    samples = [(10, True), (20, True), (30, True), (40, True), (1000, False)]
    s = lab.summarise(samples)
    assert s["n"] == 5 and s["solved"] == 0.8 and s["mean"] == 220 and s["median"] == 30
    assert s["p90"] == 1000 and s["max"] == 1000 and s["tail"] == pytest.approx(1000 / 30)
    s = lab.summarise([(4, True), (8, True)])
    assert s["median"] == 6 and s["p90"] == 8
    s = lab.summarise([(k, True) for k in range(1, 11)])
    assert s["p90"] == 9, "nearest rank: the ceil(0.9 n)-th smallest"


def test_step4_runtime_distribution():
    out = lab.runtime_distribution(lambda s: (s % 2 == 0, 10 - s), range(5))
    assert out == [(6, True), (7, False), (8, True), (9, False), (10, True)]


def distributions(grid, seeds=40, cap=3000):
    domains, props = lab.qcp_model(grid)

    def plain(s):
        sols, st = cp.solve(domains, props, choose=lab.random_first_fail(random.Random(s)), node_limit=cap)
        return bool(sols), st.nodes

    def restarts(s):
        sol, st = lab.solve_with_restarts(domains, props, lab.random_first_fail(random.Random(s)), base=30,
                                          node_budget=cap)
        return sol is not None, st.nodes

    return (lab.summarise(lab.runtime_distribution(plain, range(seeds))),
            lab.summarise(lab.runtime_distribution(restarts, range(seeds))))


def test_step4_restarts_cut_a_heavy_tail():
    with time_limit(120):
        plain, restarts = distributions(HEAVY)
    assert plain["tail"] > 4, "the plain distribution is heavy-tailed"
    assert restarts["mean"] < 0.5 * plain["mean"] and restarts["max"] < plain["max"]


def test_step4_restarts_cost_on_a_light_tail():
    with time_limit(120):
        plain, restarts = distributions(LIGHT)
    assert plain["tail"] < 2
    assert restarts["mean"] > plain["mean"], "without a tail, restarts only throw work away"


# ---------------------------------------------------------------- step 5 ---

def assert_valid(shop, starts):
    for j, job in enumerate(shop.jobs):
        for k in range(len(job) - 1):
            assert starts[(j, k)] + job[k][1] <= starts[(j, k + 1)]
    ops = list(starts)
    for a, b in itertools.combinations(ops, 2):
        (ma, da), (mb, db) = shop.jobs[a[0]][a[1]], shop.jobs[b[0]][b[1]]
        if ma == mb:
            assert starts[a] + da <= starts[b] or starts[b] + db <= starts[a]


@pytest.mark.parametrize("seed", range(4))
def test_step5_greedy_schedule(seed):
    shop = JobShop.random(6, seed=seed, machines=4)
    starts = lab.greedy_schedule(shop)
    assert set(starts) == {(j, k) for j, job in enumerate(shop.jobs) for k in range(len(job))}
    assert_valid(shop, starts)


@pytest.mark.parametrize("seed", range(4))
def test_step5_lns(seed):
    shop = JobShop.random(8, seed=seed, machines=4)
    horizon = sum(d for job in shop.jobs for _, d in job)
    with time_limit(120):
        best, starts, trace = lab.lns_jobshop(shop, horizon, iterations=40, node_limit=150, seed=seed)
    assert_valid(shop, starts)
    assert best == lab.schedule_makespan(shop, starts) == trace[-1][1]
    assert trace[0] == (0, lab.schedule_makespan(shop, lab.greedy_schedule(shop)))
    assert all(a[1] > b[1] and a[0] < b[0] for a, b in zip(trace, trace[1:])), "strictly improving, in order"
    assert best < trace[0][1], "LNS improves on the greedy schedule"


def test_step5_lns_beats_branch_and_bound_on_a_budget():
    lns_total = bb_total = 0
    with time_limit(240):
        for seed in (0, 3, 4):
            shop = JobShop.random(8, seed=seed, machines=4)
            horizon = sum(d for job in shop.jobs for _, d in job)
            lns_total += lab.lns_jobshop(shop, horizon, iterations=60, node_limit=150, seed=0)[0]
            best, _, _, _ = gc.minimise(*gc.jobshop(shop, horizon, True), node_limit=60 * 150)
            bb_total += best if best is not None else horizon
    assert lns_total < bb_total
