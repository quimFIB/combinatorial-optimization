"""Tests for unit 20. Run with `uv run co test 20`. You should not need to edit this."""

import itertools
import random

import pytest
from pysat.solvers import Solver as PySat

from colib.drat import check_rup_proof
from colib.testing import load_lab, time_limit

lab = load_lab(__file__)


def rand3(n, m, seed):
    r = random.Random(seed)
    return [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), 3)] for _ in range(m)]


def rand_mixed(n, m, seed):
    r = random.Random(seed)
    return [[v if r.random() < 0.5 else -v for v in r.sample(range(1, n + 1), r.randint(2, min(4, n)))]
            for _ in range(m)]


def reference_sat(clauses):
    with PySat(name="minisat22", bootstrap_with=clauses) as s:
        return s.solve()


def implied(clauses, lits):
    """clauses |= (l1 or l2 or ...), checked by MiniSat."""
    with PySat(name="minisat22", bootstrap_with=clauses) as s:
        return not s.solve(assumptions=[-l for l in lits])


def satisfies(model, clauses):
    return all(any((l > 0) == model[abs(l) - 1] for l in c) for c in clauses)


def naive_propagate(clauses, assignment):
    """Unit propagation to a fixpoint on a dict var -> bool. Returns (assignment, conflict?)."""
    a = dict(assignment)
    while True:
        changed = False
        for c in clauses:
            vals = [None if abs(l) not in a else (a[abs(l)] == (l > 0)) for l in c]
            if any(v is True for v in vals):
                continue
            free = [l for l, v in zip(c, vals) if v is None]
            if not free:
                return a, True
            if len(free) == 1:
                a[abs(free[0])] = free[0] > 0
                changed = True
        if not changed:
            return a, False


def decide(s, lit):
    s.trail_lim.append(len(s.trail))
    s.enqueue(lab.to_internal(lit), None)


def assignment_of(s):
    return {v: s.value[v] for v in range(1, s.n + 1) if s.value[v] is not None}


# ---------------------------------------------------------------- step 1 ---

def test_step1_literals():
    assert lab.to_internal(3) == 6 and lab.to_internal(-3) == 7
    assert lab.to_dimacs(6) == 3 and lab.to_dimacs(7) == -3


def test_step1_add_clause():
    s = lab.Solver(3)
    assert s.add_clause([1, -1, 2])                          # tautology: ignored
    assert len(s.clauses) == 0
    assert s.add_clause([2, 2, 3]) and s.clauses[-1] == [lab.to_internal(2), lab.to_internal(3)]
    assert s.add_clause([-3]) and s.value[3] is False
    assert s.value[2] is True, "the unit propagates through (2 or 3)"
    assert not s.add_clause([-2]) and not s.ok
    assert not lab.Solver(1, [[]]).ok


@pytest.mark.parametrize("seed", range(40))
def test_step1_propagation_matches_naive(seed):
    r = random.Random(seed)
    n = r.randint(4, 14)
    clauses = rand_mixed(n, r.randint(n, 4 * n), seed)
    s = lab.Solver(n, clauses)
    if not s.ok:
        assert naive_propagate(clauses, {})[1], "a level-0 conflict must be real"
        return
    assert assignment_of(s) == naive_propagate(clauses, {})[0]
    for _ in range(n):
        free = [v for v in range(1, n + 1) if s.value[v] is None]
        if not free:
            break
        v = r.choice(free)
        decide(s, v if r.random() < 0.5 else -v)
        confl = s.propagate()
        expected, conflict = naive_propagate(clauses, {**assignment_of(s)})
        if conflict:
            assert confl is not None, "naive propagation finds a conflict"
            break
        assert confl is None and assignment_of(s) == expected


def test_step1_reasons_and_levels():
    s = lab.Solver(4, [[-1, 2], [-2, 3], [-1, -3, 4]])
    decide(s, 1)
    assert s.propagate() is None
    assert [s.value[v] for v in (2, 3, 4)] == [True, True, True]
    assert all(s.level[v] == 1 for v in (1, 2, 3, 4))
    assert s.reason[1] is None and s.reason[4] is not None
    c = s.clauses[s.reason[4]]
    assert c[0] == lab.to_internal(4), "the implied literal sits first in its reason clause"


# ---------------------------------------------------------------- step 2 ---

def drive_to_conflict(s, r):
    while True:
        confl = s.propagate()
        if confl is not None:
            return confl
        free = [v for v in range(1, s.n + 1) if s.value[v] is None]
        if not free:
            return None
        v = r.choice(free)
        decide(s, v if r.random() < 0.5 else -v)


@pytest.mark.parametrize("seed", range(60))
def test_step2_first_uip_clause(seed):
    r = random.Random(seed)
    while True:                                               # redraw until a conflict above level 0
        n = r.randint(8, 25)
        clauses = rand3(n, int(4.5 * n), r.randrange(10 ** 6))
        clauses += [[v if r.random() < 0.5 else -v] for v in r.sample(range(1, n + 1), 2)]   # some level-0 facts
        s = lab.Solver(n, clauses)
        if s.ok:
            confl = drive_to_conflict(s, r)
            if confl is not None and s.decision_level() > 0:
                break
    before = list(s.activity)
    learnt, back, lbd = s.analyze(confl)
    lits = [lab.to_dimacs(i) for i in learnt]
    assert len(set(learnt)) == len(learnt)
    assert all(s.lit_value(i) is False for i in learnt), "every learned literal is false now"
    current = s.decision_level()
    assert [s.level[i >> 1] for i in learnt].count(current) == 1 and s.level[learnt[0] >> 1] == current
    others = [s.level[i >> 1] for i in learnt[1:]]
    assert back == (max(others) if others else 0) and all(lv > 0 for lv in others)
    if others:
        assert s.level[learnt[1] >> 1] == back
    assert lbd == len({s.level[i >> 1] for i in learnt})
    assert implied(clauses, lits), "the learned clause follows from the formula"
    assert any(a > b for a, b in zip(s.activity, before)), "variables in the conflict are bumped"
    s.cancel_until(back)
    assert sum(1 for i in learnt if s.lit_value(i) is None) == 1, "asserting after the backjump"


def test_step2_textbook_example():
    # decisions x1 then x2; (-1 or 3), (-2 or -3 or 4), (-2 or -4 or 5), (-4 or -5): conflict at level 2
    clauses = [[-1, 3], [-2, -3, 4], [-2, -4, 5], [-4, -5]]
    s = lab.Solver(5, clauses)
    decide(s, 1)
    assert s.propagate() is None
    decide(s, 2)
    confl = s.propagate()
    assert confl is not None
    learnt, back, lbd = s.analyze(confl)
    # x2 reaches the conflict both through x4 and directly through x5, so x4 is not a UIP: the first UIP
    # is the decision x2 itself, and the learned clause is (not x2 or not x3)
    assert sorted(lab.to_dimacs(i) for i in learnt) == [-3, -2]
    assert lab.to_dimacs(learnt[0]) == -2 and back == 1 and lbd == 2


def test_step2_cancel_until_saves_phase():
    s = lab.Solver(3, [[1, 2, 3]])
    decide(s, -1)
    decide(s, 2)
    s.propagate()
    s.cancel_until(1)
    assert s.value[2] is None and s.value[1] is False and s.phase[2] is True
    s.cancel_until(0)
    assert s.value[1] is None and s.phase[1] is False and s.trail == [] and s.qhead == 0


# ---------------------------------------------------------------- step 3 ---

@pytest.mark.parametrize("seed", range(80))
def test_step3_agrees_with_minisat(seed):
    r = random.Random(seed)
    n = r.randint(5, 50)
    clauses = rand3(n, int(n * 4.26), seed)
    s = lab.Solver(n, clauses)
    with time_limit(30):
        result = s.solve()
    assert result == reference_sat(clauses)
    if result:
        assert satisfies(s.model(), clauses)


def test_step3_pick_branch():
    s = lab.Solver(3)
    s.activity = [0.0, 1.0, 5.0, 5.0]
    s.phase[2] = True
    assert s.pick_branch() == lab.to_internal(2), "highest activity, lowest index on ties, saved phase"
    s.value[2] = True
    assert s.pick_branch() == lab.to_internal(-3)
    s.value[1] = s.value[3] = False
    assert s.pick_branch() is None


def test_step3_conflict_limit_and_restarts():
    n = 150
    clauses = rand3(n, int(n * 4.26), n)
    s = lab.Solver(n, clauses, restart_base=20)
    assert s.solve(conflict_limit=30) is None and s.decision_level() == 0
    with time_limit(120):
        result = s.solve()
    assert result == reference_sat(clauses) and s.stats["restarts"] > 0
    assert s.var_inc > 1.5, "VSIDS: the bump grows by 1 / decay after every conflict, so recent conflicts weigh more"


def test_step3_harder_instance():
    n = 120
    clauses = rand3(n, int(n * 4.26), 7)
    s = lab.Solver(n, clauses)
    with time_limit(120):
        result = s.solve()
    assert result == reference_sat(clauses)
    assert s.stats["conflicts"] > 50 and s.stats["decisions"] >= s.stats["conflicts"] * 0.5


# ---------------------------------------------------------------- step 4 ---

@pytest.mark.parametrize("seed", range(30))
def test_step4_drat_proofs(seed):
    r = random.Random(seed)
    n = r.randint(10, 40)
    clauses = rand3(n, int(n * 5), seed)                    # above the threshold: mostly unsatisfiable
    proof = []
    s = lab.Solver(n, clauses, proof=proof, restart_base=10, reduce_base=20)
    with time_limit(60):
        result = s.solve()
    assert result == reference_sat(clauses)
    if not result:
        ok, message = check_rup_proof(n, clauses, proof)
        assert ok, message
        assert proof[-1].strip() == "0"


def test_step4_pigeonhole_proof_with_deletions():
    nvars, clauses = lab.pigeonhole(5)
    proof = []
    s = lab.Solver(nvars, clauses, proof=proof, reduce_base=30)
    assert s.solve() is False and s.stats["deleted"] > 0
    assert any(line.startswith("d ") for line in proof)
    ok, message = check_rup_proof(nvars, clauses, proof)
    assert ok, message


def test_step4_reduce_db_keeps_glue_and_reasons():
    n = 60
    clauses = rand3(n, int(n * 4.26), 11)
    s = lab.Solver(n, clauses, reduce_base=10 ** 9)
    s.solve(conflict_limit=200)
    r = random.Random(1)
    drive_to_conflict(s, r)                                  # leave some reasons locked
    learnt_alive = [ci for ci in range(len(s.clauses)) if s.learnt[ci] and not s.deleted[ci]]
    glue = {ci for ci in learnt_alive if s.lbd[ci] <= 2}
    locked = {ci for ci in learnt_alive if s.locked(ci)}
    s.reduce_db()
    assert all(not s.deleted[ci] for ci in glue | locked)
    removable = [ci for ci in learnt_alive if ci not in glue and ci not in locked]
    assert sum(s.deleted[ci] for ci in removable) == len(removable) // 2
    worst_kept = max((s.lbd[ci] for ci in removable if not s.deleted[ci]), default=0)
    best_deleted = min((s.lbd[ci] for ci in removable if s.deleted[ci]), default=99)
    assert worst_kept <= best_deleted, "the deleted half has the largest LBDs"


@pytest.mark.parametrize("seed", range(15))
def test_step4_aggressive_deletion_stays_correct(seed):
    n = 50
    clauses = rand3(n, int(n * 4.26), seed + 100)
    s = lab.Solver(n, clauses, reduce_base=5, restart_base=10)
    with time_limit(60):
        result = s.solve()
    assert result == reference_sat(clauses)
    if result:
        assert satisfies(s.model(), clauses)


# ---------------------------------------------------------------- step 5 ---

def projected_models(clauses, n, extra_vars):
    """The set of assignments to 1..n that extend to a model (extra variables existential)."""
    out = set()
    for t in itertools.product((False, True), repeat=n):
        with PySat(name="minisat22", bootstrap_with=clauses) as s:
            if s.solve(assumptions=[i + 1 if t[i] else -(i + 1) for i in range(n)]):
                out.add(t)
    return out


@pytest.mark.parametrize("encoding", ["amo_pairwise", "amo_sequential", "amo_bitwise"])
@pytest.mark.parametrize("n", [1, 2, 3, 5, 7])
def test_step5_at_most_one(encoding, n):
    fresh = lab.Fresh(n)
    clauses = getattr(lab, encoding)(list(range(1, n + 1)), fresh)
    want = {t for t in itertools.product((False, True), repeat=n) if sum(t) <= 1}
    assert projected_models(clauses, n, fresh.top - n) == want


def test_step5_encoding_sizes():
    lits = list(range(1, 11))
    assert len(lab.amo_pairwise(lits)) == 45
    fresh = lab.Fresh(10)
    assert len(lab.amo_sequential(lits, fresh)) == 3 * 10 - 4 and fresh.top == 10 + 9
    fresh = lab.Fresh(10)
    assert len(lab.amo_bitwise(lits, fresh)) == 10 * 4 and fresh.top == 14


@pytest.mark.parametrize("n,k", [(4, 0), (4, 1), (5, 2), (6, 3), (6, 5), (6, 6)])
def test_step5_at_most_k(n, k):
    fresh = lab.Fresh(n)
    clauses = lab.at_most_k(list(range(1, n + 1)), k, fresh)
    want = {t for t in itertools.product((False, True), repeat=n) if sum(t) <= k}
    assert projected_models(clauses, n, fresh.top - n) == want


def test_step5_pigeonhole_humiliates_cdcl():
    conflicts = {}
    with time_limit(120):
        for n in (4, 5, 6, 7):
            nvars, clauses = lab.pigeonhole(n)
            assert nvars == (n + 1) * n and len(clauses) == (n + 1) + n * (n + 1) * n // 2
            s = lab.Solver(nvars, clauses)
            assert s.solve() is False
            conflicts[n] = s.stats["conflicts"]
    assert conflicts[7] > 3 * conflicts[6] and conflicts[6] > 3 * conflicts[5], conflicts


@pytest.mark.parametrize("amo", ["amo_pairwise", "amo_sequential", "amo_bitwise"])
def test_step5_queens(amo):
    n = 8
    nvars, clauses = lab.queens(n, getattr(lab, amo))
    s = lab.Solver(nvars, clauses)
    assert s.solve()
    m = s.model()
    board = [[m[r * n + c] for c in range(n)] for r in range(n)]
    cols = [row.index(True) for row in board]
    assert all(sum(row) == 1 for row in board)
    assert len(set(cols)) == n and len({r + c for r, c in enumerate(cols)}) == n and len({r - c for r, c in enumerate(cols)}) == n
    nvars6, clauses6 = lab.queens(6, getattr(lab, amo))
    count = 0
    with PySat(name="minisat22", bootstrap_with=clauses6) as ps:
        for model in ps.enum_models():
            count += 1
            ps.add_clause([-l for l in model[:36]])
    assert count >= 4
    assert len(projected_models_queens(clauses6)) == 4


def projected_models_queens(clauses):
    found = set()
    with PySat(name="minisat22", bootstrap_with=clauses) as ps:
        while ps.solve():
            model = ps.get_model()
            key = tuple(l > 0 for l in model[:36])
            found.add(key)
            ps.add_clause([-(i + 1) if key[i] else i + 1 for i in range(36)])
    return found


@pytest.mark.parametrize("seed", range(10))
def test_step5_colouring(seed):
    r = random.Random(seed)
    n = r.randint(3, 8)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if r.random() < 0.5]
    for k in (2, 3):
        nvars, clauses = lab.colouring(n, edges, k)
        s = lab.Solver(nvars, clauses)
        brute = any(all(c[u] != c[v] for u, v in edges) for c in itertools.product(range(k), repeat=n))
        assert s.solve() == brute
        if brute:
            m = s.model()
            colour = [[m[v * k + c] for c in range(k)].index(True) for v in range(n)]
            assert all(colour[u] != colour[v] for u, v in edges)
