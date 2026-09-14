"""Tests for unit 28. Run with `uv run co test 28`. You should not need to edit this."""

import math
import random
import statistics

import pytest
from scipy.stats import wilcoxon

from colib.testing import load_lab

lab = load_lab(__file__)


def run(solver, instance, seed, status="optimal", seconds=1.0, value=None, nodes=None, experiment="e"):
    return {"experiment": experiment, "solver": solver, "instance": instance, "seed": seed, "status": status,
            "seconds": seconds, "value": value, "nodes": nodes}


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


# ---------------------------------------------------------------- step 1 ---

def test_step1_store_roundtrip(tmp_path):
    path = tmp_path / "bench.sqlite"
    conn = lab.open_store(str(path))
    lab.save_run(conn, run("b", "i2", 1, seconds=2.5, value=10.0, nodes=7))
    lab.save_run(conn, run("a", "i1", 0, status="timeout", seconds=60.0))
    lab.save_run(conn, run("a", "i1", 0, seconds=3.0), )
    lab.save_run(conn, run("a", "i1", 0, experiment="other"))
    conn.close()
    conn = lab.open_store(str(path))
    runs = lab.load_runs(conn, "e")
    assert [(r["solver"], r["instance"], r["seed"]) for r in runs] == [("a", "i1", 0), ("b", "i2", 1)]
    assert runs[0]["status"] == "optimal" and runs[0]["seconds"] == 3.0, "same key replaces"
    assert runs[1] == run("b", "i2", 1, seconds=2.5, value=10.0, nodes=7)
    assert lab.load_runs(conn, "e", solver="b") == [runs[1]]
    assert len(lab.load_runs(conn, "other")) == 1


def test_step1_ordering():
    conn = lab.open_store()
    for s, i, seed in [("b", "x", 2), ("a", "y", 0), ("a", "x", 1), ("a", "x", 0)]:
        lab.save_run(conn, run(s, i, seed))
    assert [(r["solver"], r["instance"], r["seed"]) for r in lab.load_runs(conn, "e")] == \
        [("a", "x", 0), ("a", "x", 1), ("a", "y", 0), ("b", "x", 2)]


# ---------------------------------------------------------------- step 2 ---

def test_step2_run_benchmark_records_and_resumes():
    conn = lab.open_store()
    clock = FakeClock()
    calls = []

    def fast(data, seed, timeout):
        calls.append(("fast", data, seed))
        clock.t += 1.0 + seed
        return {"status": "optimal", "value": data * 2, "nodes": 3}

    def slow(data, seed, timeout):
        calls.append(("slow", data, seed))
        clock.t += 100.0
        return {"status": "optimal"}

    n = lab.run_benchmark(conn, "exp", {"fast": fast, "slow": slow}, {"p": 5, "q": 6}, [0, 1], 10.0, clock)
    assert n == 8
    assert calls[:4] == [("fast", 5, 0), ("fast", 5, 1), ("slow", 5, 0), ("slow", 5, 1)], "instance, solver, seed order"
    runs = lab.load_runs(conn, "exp")
    fast_p1 = next(r for r in runs if (r["solver"], r["instance"], r["seed"]) == ("fast", "p", 1))
    assert fast_p1["seconds"] == 2.0 and fast_p1["value"] == 10 and fast_p1["nodes"] == 3
    slow_q0 = next(r for r in runs if (r["solver"], r["instance"], r["seed"]) == ("slow", "q", 0))
    assert slow_q0["status"] == "timeout" and slow_q0["seconds"] == 10.0 and slow_q0["value"] is None
    calls.clear()
    assert lab.run_benchmark(conn, "exp", {"fast": fast, "slow": slow}, {"p": 5, "q": 6}, [0, 1, 2], 10.0, clock) == 4
    assert all(seed == 2 for _, _, seed in calls), "existing runs are skipped"


def test_step2_just_over_the_timeout():
    conn = lab.open_store()
    clock = FakeClock()

    def slightly_slow(data, seed, timeout):
        clock.t += 10.5
        return {"status": "optimal"}

    lab.run_benchmark(conn, "x", {"s": slightly_slow}, {"i": None}, [0], 10.0, clock)
    assert lab.load_runs(conn, "x")[0]["status"] == "timeout"


def test_step2_statuses_are_kept():
    conn = lab.open_store()
    clock = FakeClock()
    lab.run_benchmark(conn, "x", {"s": lambda d, seed, t: {"status": "infeasible"}}, {"i": None}, [0], 5.0, clock)
    assert lab.load_runs(conn, "x")[0]["status"] == "infeasible"


# ---------------------------------------------------------------- step 3 ---

def test_step3_shifted_geometric_mean():
    assert lab.shifted_geometric_mean([1, 1, 1], 10) == pytest.approx(1)
    assert lab.shifted_geometric_mean([0, 90], 10) == pytest.approx(math.sqrt(10 * 100) - 10)
    assert lab.shifted_geometric_mean([2, 8], 0) == pytest.approx(4)


@pytest.mark.parametrize("seed", range(10))
def test_step3_sgm_properties(seed):
    r = random.Random(seed)
    v = [r.expovariate(0.1) for _ in range(20)]
    g = lab.shifted_geometric_mean(v, 10)
    assert min(v) <= g <= statistics.mean(v)
    assert lab.shifted_geometric_mean(v, 1e6) == pytest.approx(statistics.mean(v), rel=1e-3), "large shift -> mean"
    assert lab.shifted_geometric_mean([x * 1000 for x in v], 10) > lab.shifted_geometric_mean(v, 10)


def test_step3_penalised_sgm():
    runs = [run("a", "i", 0, seconds=5), run("a", "j", 0, status="timeout", seconds=60),
            run("b", "i", 0, seconds=20), run("b", "j", 0, seconds=30)]
    assert lab.par_seconds(runs[1], 60) == 60 and lab.par_seconds(runs[1], 60, penalty=10) == 600
    assert lab.par_seconds(runs[0], 60, penalty=10) == 5
    table = lab.sgm_by_solver(runs, 60, shift=10)
    assert table["a"] == pytest.approx(math.sqrt(15 * 70) - 10)
    assert table["b"] == pytest.approx(math.sqrt(30 * 40) - 10)
    assert lab.sgm_by_solver(runs, 60, shift=10, penalty=10)["a"] == pytest.approx(math.sqrt(15 * 610) - 10)


# ---------------------------------------------------------------- step 4 ---

def test_step4_performance_profile_by_hand():
    runs = [run("a", "p1", 0, seconds=1), run("b", "p1", 0, seconds=2), run("c", "p1", 0, status="timeout", seconds=9),
            run("a", "p2", 0, seconds=6), run("b", "p2", 0, seconds=3), run("c", "p2", 0, seconds=3),
            run("a", "p3", 0, status="timeout"), run("b", "p3", 0, status="timeout"), run("c", "p3", 0, status="timeout"),
            run("a", "p1", 1, seconds=4), run("b", "p1", 1, seconds=4), run("c", "p1", 1, seconds=40)]
    taus = [1, 2, 10, 1e9]
    prof = lab.performance_profile(runs, taus)
    assert prof["a"] == [0.5, 0.75, 0.75, 0.75]
    assert prof["b"] == [0.5, 0.75, 0.75, 0.75]
    assert prof["c"] == [0.25, 0.25, 0.5, 0.5]


def test_step4_virtual_best():
    runs = [run("b", "p", 0, seconds=2), run("a", "p", 0, seconds=2), run("c", "p", 0, seconds=1, status="timeout"),
            run("a", "q", 0, status="timeout"), run("b", "q", 0, status="error")]
    assert lab.virtual_best(runs) == {("p", 0): ("a", 2), ("q", 0): (None, None)}


@pytest.mark.parametrize("seed", range(6))
def test_step4_profile_invariants(seed):
    r = random.Random(seed)
    runs = [run(s, f"i{k}", 0, status="optimal" if r.random() < 0.8 else "timeout", seconds=r.uniform(0.1, 50))
            for k in range(15) for s in "xyz"]
    taus = [1, 1.5, 2, 4, 8, 100, 1e12]
    prof = lab.performance_profile(runs, taus)
    for s, fr in prof.items():
        assert fr == sorted(fr) and 0 <= fr[0] and fr[-1] <= 1
        solved = sum(1 for q in runs if q["solver"] == s and q["status"] == "optimal")
        assert fr[-1] == pytest.approx(solved / 15), "for a huge tau: the fraction solved"
    vbs = lab.virtual_best(runs)
    winners = sum(1 for sv, _ in vbs.values() if sv is not None)
    assert sorted(prof) == ["x", "y", "z"]
    assert sum(prof[s][0] for s in prof) >= winners / 15 - 1e-9, "every solved problem has at least one winner at tau = 1"


# ---------------------------------------------------------------- step 5 ---

class Recorder(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        self.calls += 1
        return super().choices(population, weights, cum_weights=cum_weights, k=k)


def test_step5_bootstrap_indices():
    values = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
    rng = Recorder(5)
    lo, hi = lab.bootstrap_ci(values, statistics.mean, rng, level=0.9, resamples=101)
    assert rng.calls == 101
    ref = random.Random(5)
    stats = sorted(statistics.mean(ref.choices(values, k=len(values))) for _ in range(101))
    assert (lo, hi) == (stats[math.floor(0.05 * 100)], stats[math.floor(0.95 * 100)])


def test_step5_bootstrap_width():
    rng = random.Random(0)
    values = [rng.gauss(10, 2) for _ in range(400)]
    lo, hi = lab.bootstrap_ci(values, statistics.mean, random.Random(1))
    assert lo < statistics.mean(values) < hi
    assert (hi - lo) == pytest.approx(2 * 1.96 * 2 / math.sqrt(400), rel=0.2)
    assert lab.bootstrap_ci([7.0] * 10, statistics.median, random.Random(2)) == (7.0, 7.0)


def test_step5_geometric_ratio():
    a = [9, 19, 39]
    b = [0, 10, 30]
    ratio, (lo, hi) = lab.geometric_ratio_ci(a, b, random.Random(3), shift=1, resamples=500)
    assert ratio == pytest.approx(((10 / 1) * (20 / 11) * (40 / 31)) ** (1 / 3))
    assert lo <= ratio <= hi and lo >= min(10, 20 / 11, 40 / 31) - 1e-9 and hi <= 10 + 1e-9
    ratio10, _ = lab.geometric_ratio_ci(a, b, random.Random(3), resamples=50)
    assert ratio10 == pytest.approx(((19 / 10) * (29 / 20) * (49 / 40)) ** (1 / 3)), "the default shift is 10"
    same, (lo, hi) = lab.geometric_ratio_ci(b, b, random.Random(3))
    assert same == 1.0 and lo == hi == 1.0


# ---------------------------------------------------------------- step 6 ---

def test_step6_holm():
    assert lab.holm([0.01, 0.04, 0.03, 0.005]) == pytest.approx([0.03, 0.06, 0.06, 0.02])
    assert lab.holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])
    assert lab.holm([]) == []


@pytest.mark.parametrize("seed", range(10))
def test_step6_wilcoxon_matches_scipy(seed):
    r = random.Random(seed)
    a = [r.randint(0, 40) for _ in range(r.randint(8, 40))]
    b = [x + r.randint(-6, 6 + seed % 3) for x in a]
    if all(x == y for x, y in zip(a, b)):
        b[0] += 1
    T, p = lab.wilcoxon_signed_rank(a, b)
    ref = wilcoxon(a, b, zero_method="wilcox", correction=True, method="approx")
    assert T == pytest.approx(ref.statistic) and p == pytest.approx(ref.pvalue, rel=1e-9, abs=1e-12)


def test_step6_wilcoxon_edge_cases():
    assert lab.wilcoxon_signed_rank([1, 2, 3], [1, 2, 3]) == (0.0, 1.0)
    T, p = lab.wilcoxon_signed_rank([1] * 20, [2] * 20)
    assert T == 0 and p < 1e-4
