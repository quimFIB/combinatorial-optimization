"""Tests for unit 17. Run with `uv run co test 17`. You should not need to edit this."""

import itertools
import random

import pytest

from colib.testing import load_lab, time_limit

lab = load_lab(__file__)

EASY = [[5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0], [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3], [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5], [0, 0, 0, 0, 8, 0, 0, 7, 9]]
HARD = [[int(ch) for ch in row] for row in
        ("800000000", "003600000", "070090200", "050007000", "000045700",
         "000100030", "001000068", "008500010", "090000400")]              # Inkala 2012
AUSTRALIA = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
AUS_EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (2, 4), (2, 5), (3, 4), (4, 5)]


# ---------------------------------------------------------------- step 1 ---

def test_step1_store_basics():
    s = lab.Store([range(3), [5], {1, 4}])
    assert [frozenset(d) for d in s.dom] == [frozenset({0, 1, 2}), frozenset({5}), frozenset({1, 4})]
    assert len(s) == 3 and s.is_fixed(1) and not s.is_fixed(0) and s.value(1) == 5
    assert s.remove(0, 1) and s.dom[0] == {0, 2}
    assert s.assign(2, 4) and s.dom[2] == {4}
    assert not s.remove(1, 5) and s.dom[1] == frozenset()


def test_step1_trail_and_undo():
    s = lab.Store([range(4), range(4)])
    m0 = s.mark()
    s.remove(0, 0)
    s.remove(0, 1)
    m1 = s.mark()
    s.assign(1, 2)
    s.remove(0, 3)
    assert s.dom[0] == {2} and s.dom[1] == {2}
    s.undo(m1)
    assert s.dom[0] == {2, 3} and s.dom[1] == {0, 1, 2, 3}
    assert list(s.changed) == [], "undo forgets pending changes"
    s.undo(m0)
    assert s.dom[0] == {0, 1, 2, 3} and s.mark() == m0


def test_step1_no_op_changes_are_not_trailed():
    s = lab.Store([range(3)])
    m = s.mark()
    assert s.set_domain(0, {0, 1, 2}) and s.remove(0, 7)
    assert s.mark() == m and s.changed == []


def test_step1_changed_records_variables():
    s = lab.Store([range(3), range(3)])
    s.remove(1, 0)
    s.assign(0, 2)
    assert list(s.changed) == [1, 0]


@pytest.mark.parametrize("seed", range(10))
def test_step1_random_undo(seed):
    r = random.Random(seed)
    n = 5
    s = lab.Store([range(6)] * n)
    history = [([frozenset(d) for d in s.dom], s.mark())]
    for _ in range(40):
        v = r.randrange(n)
        if r.random() < 0.3 and len(history) > 1:
            snap, m = history.pop()
            s.undo(m)
            assert [frozenset(d) for d in s.dom] == snap
        else:
            history.append(([frozenset(d) for d in s.dom], s.mark()))
            s.remove(v, r.randrange(6))


# ---------------------------------------------------------------- step 2 ---

def naive_arc_consistency(domains, constraints):
    d = {v: frozenset(s) for v, s in domains.items()}
    changed = True
    while changed:
        changed = False
        for (x, y), allowed in constraints.items():
            new = frozenset(a for a in d[x] if any(allowed(a, b) for b in d[y]))
            if new != d[x]:
                d[x], changed = new, True
                if not new:
                    return None
    return d


def test_step2_chain():
    lt = lambda a, b: a < b
    gt = lambda a, b: a > b
    cons = {(0, 1): lt, (1, 0): gt, (1, 2): lt, (2, 1): gt}
    dom, calls = lab.ac3({0: {1, 2, 3}, 1: {1, 2, 3}, 2: {1, 2, 3}}, cons)
    assert dom == {0: {1}, 1: {2}, 2: {3}}
    assert calls >= 4


def test_step2_arc_consistency_is_not_satisfiability():
    ne = lambda a, b: a != b
    cons = {(x, y): ne for x in range(3) for y in range(3) if x != y}       # a triangle, two colours
    dom, _ = lab.ac3({v: {0, 1} for v in range(3)}, cons)
    assert dom == {v: {0, 1} for v in range(3)}, "every value has a support on every arc..."
    assert not any(a != b != c != a for a, b, c in itertools.product((0, 1), repeat=3)), "...yet no solution"


def test_step2_wipeout():
    dom, _ = lab.ac3({0: {1}, 1: {1}}, {(0, 1): lambda a, b: a != b, (1, 0): lambda a, b: a != b})
    assert dom is None


@pytest.mark.parametrize("seed", range(40))
def test_step2_random_against_naive(seed):
    r = random.Random(seed)
    n = r.randint(2, 6)
    domains = {v: set(r.sample(range(6), r.randint(1, 6))) for v in range(n)}
    cons = {}
    for x in range(n):
        for y in range(n):
            if x != y and r.random() < 0.4:
                rel = frozenset((a, b) for a in range(6) for b in range(6) if r.random() < 0.5)
                cons[(x, y)] = (lambda rel: lambda a, b: (a, b) in rel)(rel)
    dom, calls = lab.ac3(domains, cons)
    assert dom == naive_arc_consistency(domains, cons)


def test_step2_requeues_only_affected_arcs():
    # a long chain x0 < x1 < ... < x9 over 0..9: AC-3 should need far fewer revisions than naive sweeps
    lt, gt = (lambda a, b: a < b), (lambda a, b: a > b)
    cons = {}
    for i in range(9):
        cons[(i, i + 1)] = lt
        cons[(i + 1, i)] = gt
    dom, calls = lab.ac3({v: set(range(10)) for v in range(10)}, cons)
    assert all(dom[v] == {v} for v in range(10))
    assert calls <= 18 * 10


# ---------------------------------------------------------------- step 3 ---

def supported(dom, vars_, holds):
    """Values of each variable that appear in some satisfying tuple over dom."""
    keep = {v: set() for v in vars_}
    for values in itertools.product(*(sorted(dom[v]) for v in vars_)):
        if holds(dict(zip(vars_, values))):
            for v, a in zip(vars_, values):
                keep[v].add(a)
    return keep


def apply(prop, dom):
    out = prop.prune(dom)
    if out is None:
        return None
    new = list(dom)
    for v, d in out.items():
        new[v] = frozenset(d) & new[v]
    return new


@pytest.mark.parametrize("seed", range(30))
def test_step3_not_equal_is_arc_consistent(seed):
    r = random.Random(seed)
    off = r.randint(-2, 2)
    dom = [frozenset(r.sample(range(5), r.randint(1, 3))), frozenset(r.sample(range(5), r.randint(1, 3)))]
    got = apply(lab.NotEqual(0, 1, off), dom)
    keep = supported(dom, (0, 1), lambda t: t[0] != t[1] + off)
    if not keep[0]:
        assert got is None
    else:
        assert got == [frozenset(keep[0]), frozenset(keep[1])]


@pytest.mark.parametrize("seed", range(20))
def test_step3_binary_is_arc_consistent(seed):
    r = random.Random(seed)
    rel = {(a, b) for a in range(5) for b in range(5) if r.random() < 0.35}
    dom = [frozenset(r.sample(range(5), 4)), frozenset(r.sample(range(5), 4))]
    got = apply(lab.Binary(0, 1, lambda a, b: (a, b) in rel), dom)
    keep = supported(dom, (0, 1), lambda t: (t[0], t[1]) in rel)
    assert (got is None) == (not keep[0]) and (got is None or got == [frozenset(keep[0]), frozenset(keep[1])])


@pytest.mark.parametrize("seed", range(40))
def test_step3_linear_le_is_domain_consistent(seed):
    r = random.Random(seed)
    k = r.randint(1, 4)
    coefs = [r.choice([-3, -2, -1, 1, 2, 3]) for _ in range(k)]
    dom = [frozenset(r.sample(range(-3, 5), r.randint(1, 4))) for _ in range(k)]
    rhs = r.randint(-6, 8)
    got = apply(lab.LinearLe(range(k), coefs, rhs), dom)
    keep = supported(dom, tuple(range(k)), lambda t: sum(c * t[i] for i, c in enumerate(coefs)) <= rhs)
    if not keep[0]:
        assert got is None
    else:
        assert got == [frozenset(keep[i]) for i in range(k)], "a single <= is domain consistent after one prune"


@pytest.mark.parametrize("seed", range(40))
def test_step3_linear_eq_and_count_are_sound(seed):
    r = random.Random(seed)
    k = r.randint(2, 4)
    coefs = [r.choice([-2, -1, 1, 2]) for _ in range(k)]
    dom = [frozenset(r.sample(range(0, 4), r.randint(1, 4))) for _ in range(k + 1)]
    rhs = r.randint(-3, 6)
    eq = apply(lab.LinearEq(range(k), coefs, rhs), dom)
    keep = supported(dom, tuple(range(k)), lambda t: sum(c * t[i] for i, c in enumerate(coefs)) == rhs)
    if keep[0]:
        assert eq is not None and all(keep[i] <= eq[i] for i in range(k)), "never remove a supported value"
    value = r.randrange(4)
    cnt = apply(lab.Count(range(k), value, k), dom)
    keep = supported(dom, tuple(range(k + 1)), lambda t: sum(1 for i in range(k) if t[i] == value) == t[k])
    if keep[0]:
        assert cnt is not None and all(keep[i] <= cnt[i] for i in range(k + 1))
    if cnt is None:
        assert not keep[0], "failed on a satisfiable constraint"


def test_step3_linear_eq_bounds():
    dom = [frozenset(range(10)), frozenset(range(10)), frozenset({7})]
    got = apply(lab.LinearEq([0, 1, 2], [1, 1, 1], 9), dom)                # x + y = 2
    assert got[0] == set(range(3)) and got[1] == set(range(3))


def test_step3_count_bounds_the_count_variable():
    dom = [frozenset({1}), frozenset({1}), frozenset({1, 2}), frozenset({2}), frozenset(range(6))]
    got = apply(lab.Count([0, 1, 2, 3], 1, 4), dom)                       # two sure, three possible
    assert got[4] == {2, 3}


def test_step3_count_examples():
    dom = [frozenset({1}), frozenset({1, 2}), frozenset({2, 3}), frozenset({1})]
    got = apply(lab.Count([0, 1, 2], 1, 3), dom)                          # exactly one 1, already x0
    assert got[1] == {2} and got[2] == {2, 3}
    dom = [frozenset({1, 2}), frozenset({1, 2}), frozenset({3}), frozenset({2, 3})]
    got = apply(lab.Count([0, 1, 2], 1, 3), dom)                          # at least two 1s: both candidates
    assert got[0] == {1} and got[1] == {1} and got[3] == {2}


def naive_fixpoint(domains, props):
    dom = [frozenset(d) for d in domains]
    runs = 0
    changed = True
    while changed:
        changed = False
        for p in props:
            runs += 1
            new = apply(p, dom)
            if new is None or any(not d for d in new):
                return None, runs
            if new != dom:
                dom, changed = new, True
    return dom, runs


@pytest.mark.parametrize("seed", range(60))
def test_step3_fixpoint(seed):
    r = random.Random(seed)
    n = r.randint(3, 7)
    domains = [r.sample(range(5), r.randint(1, 5)) for _ in range(n)]
    props = []
    for _ in range(r.randint(2, 8)):
        x, y = r.sample(range(n), 2)
        kind = r.random()
        if kind < 0.35:
            props.append(lab.NotEqual(x, y, r.randint(-1, 1)))
        elif kind < 0.5:
            xs = r.sample(range(n), r.randint(2, 3))
            props.append(lab.LinearEq(xs, [r.choice([-1, 1, 2]) for _ in xs], r.randint(0, 6)))
        elif kind < 0.6:
            xs = r.sample(range(n), r.randint(2, 3))
            props.append(lab.Count(xs, r.randrange(3), r.choice([v for v in range(n) if v not in xs] or [xs[0]])))
        elif kind < 0.8:
            xs = r.sample(range(n), r.randint(1, 3))
            props.append(lab.LinearLe(xs, [r.choice([-1, 1, 2]) for _ in xs], r.randint(0, 8)))
        else:
            props.append(lab.Binary(x, y, lambda a, b: (a + b) % 3 != 0))
    store = lab.Store(domains)
    stats = lab.Stats()
    ok = lab.fixpoint(store, props, lab.watches(n, props), stats)
    ref, runs = naive_fixpoint(domains, props)
    if ref is None:
        assert not ok
    else:
        assert ok and [frozenset(d) for d in store.dom] == ref, "same fixpoint as naive sweeps"
        assert stats.propagations <= runs + len(props)


def test_step3_fixpoint_dirty_only_wakes_watchers():
    props = [lab.NotEqual(0, 1), lab.NotEqual(2, 3)]
    store = lab.Store([{0}, {0, 1}, {0}, {0, 1}])
    stats = lab.Stats()
    assert lab.fixpoint(store, props, lab.watches(4, props), stats, dirty=[0])
    assert store.dom[1] == {1} and store.dom[3] == {0, 1}, "only the propagator on variable 0 ran"


def test_step3_fixpoint_reports_the_failing_propagator():
    props = [lab.NotEqual(0, 1)]
    culprits = []
    store = lab.Store([{0}, {0}])
    assert not lab.fixpoint(store, props, lab.watches(2, props), lab.Stats(), on_failure=culprits.append)
    assert culprits == props


# ---------------------------------------------------------------- step 4 ---

def valid_queens(sol):
    n = len(sol)
    return all(sol[i] != sol[j] and abs(sol[i] - sol[j]) != j - i for i in range(n) for j in range(i + 1, n))


@pytest.mark.parametrize("n,count", [(1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (7, 40), (8, 92)])
def test_step4_queens_counts(n, count):
    with time_limit(60):
        sols, stats = lab.solve(*lab.queens(n), all_solutions=True)
    assert len(sols) == count and stats.solutions == count
    assert all(valid_queens(s) for s in sols) and len({tuple(s) for s in sols}) == count
    assert stats.extra["complete"]


def test_step4_first_solution_and_stats():
    sols, stats = lab.solve(*lab.queens(12))
    assert len(sols) == 1 and valid_queens(sols[0])
    assert stats.nodes > 0 and stats.propagations > stats.nodes


def test_step4_node_limit():
    sols, stats = lab.solve(*lab.queens(10), all_solutions=True, node_limit=50)
    assert stats.nodes <= 50 and not stats.extra["complete"] and len(sols) < 724


def test_step4_first_fail():
    s = lab.Store([{1, 2, 3}, {4}, {1, 2}, {0, 5, 6}])
    assert lab.first_fail(s) == 2
    assert lab.first_fail(lab.Store([{1, 2}, {3, 4}, {5, 6}])) == 0, "ties go to the lowest index"
    assert lab.first_fail(lab.Store([{1}, {2}])) is None


@pytest.mark.parametrize("seed", range(15))
def test_step4_colouring_against_brute_force(seed):
    r = random.Random(seed)
    n = r.randint(2, 7)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if r.random() < 0.45]
    k = r.randint(2, 3)
    sols, _ = lab.solve(*lab.map_colouring(n, edges, k), all_solutions=True)
    brute = [list(c) for c in itertools.product(range(k), repeat=n) if all(c[u] != c[v] for u, v in edges)]
    assert sorted(sols) == sorted(brute)


def test_step4_custom_heuristic_is_used():
    order = []

    def lowest_index(store, stats):
        v = next((v for v, d in enumerate(store.dom) if len(d) > 1), None)
        order.append(v)
        return v
    sols, _ = lab.solve(*lab.queens(6), choose=lowest_index)
    assert valid_queens(sols[0]) and order[0] == 0


def test_step4_on_failure_hook():
    failed = []
    lab.solve(*lab.queens(6), on_failure=failed.append)
    assert failed and all(isinstance(p, lab.NotEqual) for p in failed)


# ---------------------------------------------------------------- step 5 ---

def test_step5_sudoku_easy_needs_no_search():
    sols, stats = lab.solve(*lab.sudoku(EASY))
    grid = [sols[0][r * 9: r * 9 + 9] for r in range(9)]
    assert all(sorted(row) == list(range(1, 10)) for row in grid)
    assert all(grid[r][c] == EASY[r][c] for r in range(9) for c in range(9) if EASY[r][c])
    assert stats.nodes == 0, "arc consistency alone solves this puzzle"


def test_step5_sudoku_hard_is_unique():
    with time_limit(120):
        sols, stats = lab.solve(*lab.sudoku(HARD), all_solutions=True)
    assert len(sols) == 1 and stats.nodes > 0
    g = sols[0]
    for i in range(9):
        assert sorted(g[i * 9: i * 9 + 9]) == list(range(1, 10))
        assert sorted(g[r * 9 + i] for r in range(9)) == list(range(1, 10))


def test_step5_sudoku_4x4():
    grid = [[1, 0, 0, 0], [0, 0, 3, 0], [0, 4, 0, 0], [0, 0, 0, 2]]
    domains, props = lab.sudoku(grid)
    assert len(domains) == 16 and len(props) == 56, "each cell has 7 distinct peers: 16 * 7 / 2 pairs"
    sols, _ = lab.solve(domains, props, all_solutions=True)
    assert len(sols) == 1


def test_step5_queens_model_size():
    domains, props = lab.queens(8)
    assert len(domains) == 8 and len(props) == 3 * 28


def test_step5_australia():
    sols, _ = lab.solve(*lab.map_colouring(7, AUS_EDGES, 3), all_solutions=True)
    assert len(sols) == 18


@pytest.mark.parametrize("n,expected", [(4, [[1, 2, 1, 0], [2, 0, 2, 0]]), (5, [[2, 1, 2, 0, 0]]),
                                        (6, []), (7, [[3, 2, 1, 1, 0, 0, 0]]),
                                        (10, [[6, 2, 1, 0, 0, 0, 1, 0, 0, 0]])])
def test_step5_magic_series(n, expected):
    with time_limit(60):
        sols, stats = lab.solve(*lab.magic_series(n), all_solutions=True)
    assert sorted(sols) == expected
    for s in sols:
        assert all(s[i] == s.count(i) for i in range(n))
    assert stats.nodes <= 2 * n, "the redundant constraint sum i * s_i = n keeps the search tiny"
