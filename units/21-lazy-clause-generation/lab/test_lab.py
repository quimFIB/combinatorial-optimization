"""Tests for unit 21. Run with `uv run co test 21`. You should not need to edit this."""

import itertools
import random

import pytest
from pysat.solvers import Solver as PySat

from colib.oracle import brute_force
from colib.problems import JobShop
from colib.ref import unit
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)
sat = unit("20")


def literal_truth(lit, ints, var_of):
    """The truth of a DIMACS literal when integer variables take `ints` (dict IntVar -> value)
    and Boolean variables take `ints` entries keyed by their number."""
    v = abs(lit)
    if v in var_of:
        x, value = var_of[v]
        truth = ints[x] <= value
    else:
        truth = ints[v]
    return truth if lit > 0 else not truth


def index_literals(*xs):
    """Map each order-encoding variable number to (IntVar, v) meaning [x <= v]."""
    out = {}
    for x in xs:
        for v in range(x.lb, x.ub):
            out[x.le(v)] = (x, v)
    return out


def solver_with(model, decisions=()):
    s = lab.LCGSolver(model)
    for lit in decisions:
        s.trail_lim.append(len(s.trail))
        s.enqueue(sat.to_internal(lit), None)
    return s


# ---------------------------------------------------------------- step 1 ---

def test_step1_order_encoding_layout():
    m = lab.Model()
    b = m.bool_var()
    x = m.int_var(3, 7, "x")
    assert b == 1 and x.first == 2 and m.nvars == 1 + 4
    assert [x.le(v) for v in range(3, 7)] == [2, 3, 4, 5]
    assert x.ge(5) == -x.le(4)
    assert sorted(map(sorted, m.clauses)) == sorted(map(sorted, [[-2, 3], [-3, 4], [-4, 5]]))


def test_step1_models_are_integers():
    m = lab.Model()
    x = m.int_var(0, 5)
    count = 0
    with PySat(name="minisat22", bootstrap_with=m.clauses) as s:
        for model in s.enum_models():
            count += 1
    assert count == 6, "exactly one Boolean assignment per value 0..5"


def test_step1_bounds():
    m = lab.Model()
    x = m.int_var(2, 9, "x")
    s = sat.Solver(m.nvars, m.clauses)
    assert x.bounds(s) == (2, 9)
    s.trail_lim.append(0)
    s.enqueue(sat.to_internal(x.ge(4)), None)
    s.propagate()
    assert x.bounds(s) == (4, 9)
    s.trail_lim.append(len(s.trail))
    s.enqueue(sat.to_internal(x.le(6)), None)
    s.propagate()
    assert x.bounds(s) == (4, 6)
    s.trail_lim.append(len(s.trail))
    s.enqueue(sat.to_internal(x.le(4)), None)
    s.propagate()
    assert x.bounds(s) == (4, 4) and x.value(s) == 4


# ---------------------------------------------------------------- step 2 ---

@pytest.mark.parametrize("seed", range(40))
def test_step2_precedence_explanations_are_valid(seed):
    r = random.Random(seed)
    m = lab.Model()
    b = m.bool_var() if seed % 2 else None
    x = m.int_var(0, r.randint(3, 7), "x")
    y = m.int_var(r.randint(0, 3), r.randint(6, 10), "y")
    d = r.randint(0, 4)
    p = lab.Precedence(x, d, y, enabled=b)
    decisions = []
    if b is not None:
        decisions.append(b)
    lo = r.randint(x.lb, x.ub)
    if lo > x.lb:
        decisions.append(x.ge(lo))
    hi = r.randint(y.lb, y.ub)
    if hi < y.ub:
        decisions.append(y.le(hi))
    s = solver_with(m, decisions)
    s.propagate()
    var_of = index_literals(x, y)
    for clause in p.propagate(s):
        for xv in range(x.lb, x.ub + 1):
            for yv in range(y.lb, y.ub + 1):
                for bv in ((True, False) if b is not None else (True,)):
                    holds = (not bv) or xv + d <= yv
                    if holds:
                        ints = {x: xv, y: yv, **({b: bv} if b is not None else {})}
                        assert any(literal_truth(l, ints, var_of) for l in clause), \
                            f"clause {clause} is false for x={xv}, y={yv}, b={bv}"


def test_step2_precedence_strength():
    m = lab.Model()
    x = m.int_var(0, 10, "x")
    y = m.int_var(0, 12, "y")
    m.propagators.append(lab.Precedence(x, 3, y))
    s = solver_with(m, [x.ge(4), y.le(9)])
    assert s.propagate() is None
    assert y.bounds(s) == (7, 9) and x.bounds(s) == (4, 6)


def test_step2_disabled_precedence_does_nothing():
    m = lab.Model()
    b = m.bool_var()
    x, y = m.int_var(0, 10), m.int_var(0, 10)
    p = lab.Precedence(x, 5, y, enabled=b)
    s = solver_with(m, [x.ge(4)])
    assert p.propagate(s) == []
    s2 = solver_with(m, [-b, x.ge(4)])
    assert p.propagate(s2) == []


def test_step2_precedence_conflict():
    m = lab.Model()
    x, y = m.int_var(0, 10), m.int_var(0, 10)
    m.propagators.append(lab.Precedence(x, 4, y))
    s = solver_with(m, [x.ge(6), y.le(8)])
    assert s.propagate() is not None


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(40))
def test_step3_unary_explanations_are_valid(seed):
    r = random.Random(seed)
    while True:                                               # redraw until propagation doesn't fail outright
        m = lab.Model()
        n = r.randint(2, 3)
        durs = [r.randint(1, 4) for _ in range(n)]
        xs = [m.int_var(0, 8, f"s{i}") for i in range(n)]
        p = lab.Unary(xs, durs)
        decisions = []
        for x in xs:
            lo, hi = sorted((r.randint(0, 8), r.randint(0, 8)))
            if lo > 0:
                decisions.append(x.ge(lo))
            if hi < 8:
                decisions.append(x.le(hi))
        s = solver_with(m, decisions)
        if s.propagate() is None:
            break
    var_of = index_literals(*xs)
    clauses = p.propagate(s)
    for values in itertools.product(range(9), repeat=n):
        feasible = all(values[i] + durs[i] <= values[j] or values[j] + durs[j] <= values[i]
                       for i in range(n) for j in range(i + 1, n))
        if feasible:
            ints = dict(zip(xs, values))
            for clause in clauses:
                assert any(literal_truth(l, ints, var_of) for l in clause), (clause, values)


def test_step3_unary_pushes_past_a_compulsory_part():
    m = lab.Model()
    a, b = m.int_var(0, 10, "a"), m.int_var(0, 10, "b")
    m.propagators.append(lab.Unary([a, b], [4, 3]))
    s = solver_with(m, [a.ge(2), a.le(3)])                   # a runs during [3, 6) whatever it chooses
    assert s.propagate() is None
    assert b.bounds(s) == (0, 10), "b may still start at 0 and finish at 3: bounds reasoning removes nothing"
    s = solver_with(m, [a.ge(2), a.le(3), b.ge(1)])
    assert s.propagate() is None
    assert b.bounds(s) == (6, 10), "starting at 1 would overlap [3, 6): pushed to 6"


def test_step3_unary_pulls_before():
    m = lab.Model()
    a, b = m.int_var(0, 10, "a"), m.int_var(0, 5, "b")
    m.propagators.append(lab.Unary([a, b], [4, 3]))
    s = solver_with(m, [a.ge(4), a.le(5)])                   # a occupies [5, 8); b <= 5 must end by 5
    assert s.propagate() is None
    assert b.bounds(s) == (0, 2)


def test_step3_unary_overlap_conflict():
    m = lab.Model()
    a, b = m.int_var(0, 10), m.int_var(0, 10)
    m.propagators.append(lab.Unary([a, b], [4, 4]))
    s = solver_with(m, [a.ge(3), a.le(3), b.ge(4), b.le(4)])
    assert s.propagate() is not None


# ---------------------------------------------------------------- step 4 ---

def schedule_ok(shop, starts):
    for j, job in enumerate(shop.jobs):
        for k in range(len(job) - 1):
            assert starts[(j, k)] + job[k][1] <= starts[(j, k + 1)]
    for a, b in itertools.combinations(starts, 2):
        (ma, da), (mb, db) = shop.jobs[a[0]][a[1]], shop.jobs[b[0]][b[1]]
        if ma == mb:
            assert starts[a] + da <= starts[b] or starts[b] + db <= starts[a]


@pytest.mark.parametrize("seed", range(6))
def test_step4_lcg_finds_valid_schedules(seed):
    shop = JobShop.random(4, seed=seed, machines=3)
    horizon = sum(d for job in shop.jobs for _, d in job)
    model, starts, mk = lab.jobshop_model(shop, horizon)
    s = lab.LCGSolver(model)
    with time_limit(60):
        assert s.solve() is True
    values = {op: x.value(s) for op, x in starts.items()}
    schedule_ok(shop, values)
    assert s.stats["explanations"] > 0


def test_step4_learning_happens():
    shop = JobShop.random(5, seed=1, machines=3)
    model, starts, mk = lab.jobshop_model(shop, 30)
    s = lab.LCGSolver(model)
    s.add_clause([mk.le(24)])
    with time_limit(60):
        s.solve()
    assert s.stats["conflicts"] > 0 and s.stats["learned"] > 0
    assert any(s.learnt[ci] for ci in range(len(s.clauses)))


def test_step4_explanation_conflict_is_analysed():
    # a 3-task machine that cannot fit in the horizon: every solution attempt ends in explained conflicts
    shop = JobShop(((( 0, 4),), ((0, 4),), ((0, 4),)))
    model, starts, mk = lab.jobshop_model(shop, 11)
    s = lab.LCGSolver(model)
    with time_limit(30):
        assert s.solve() is False


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(6))
def test_step5_minimise_matches_brute_force(seed):
    shop = JobShop.random(4, seed=seed, machines=3)
    horizon = sum(d for job in shop.jobs for _, d in job)
    with time_limit(120):
        best, proven, stats, trace = lab.minimise_makespan(shop, horizon)
    assert proven and best == brute_force(shop).value
    assert [v for v, _ in trace] == sorted({v for v, _ in trace}, reverse=True)


def test_step5_ft06_proven():
    with time_limit(180):
        best, proven, stats, trace = lab.minimise_makespan(JobShop.ft06(), 60, conflict_limit=5000)
    assert best == 55 and proven, "learning from explanations proves ft06 optimal"


def test_step5_model_structure():
    shop = JobShop.ft06()
    model, starts, mk = lab.jobshop_model(shop, 60)
    kinds = [type(p).__name__ for p in model.propagators]
    assert kinds.count("Unary") == 6, "one explained timetable per machine"
    assert kinds.count("Precedence") == 6 * 5 + 6 + 2 * 6 * 15, "job chains, makespan links, two per disjunction"
    assert len(starts) == 36 and mk.ub == 60


def test_step5_conflict_limit():
    best, proven, stats, trace = lab.minimise_makespan(JobShop.ft06(), 60, conflict_limit=20)
    assert not proven and stats["conflicts"] >= 20
