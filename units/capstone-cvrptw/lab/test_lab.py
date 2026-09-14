"""Tests for the capstone. Run with `uv run co test capstone`. You should not need to edit this.

Every exact method is checked against colib.vrptw.brute_force on small random instances; the
tests never need Solomon's files."""

import itertools
import math
import random

import numpy as np
import pytest

from colib.solvers import highs_lp
from colib.testing import load_lab, time_limit
from colib.vrptw import VRPTW, brute_force, feasible_routes

lab = load_lab(__file__)


def line_instance():
    """Depot at 0; customers at 10, 20, 30 on a line (all in tenths). Service 5 everywhere."""
    return VRPTW.build("line", [(0, 0), (10, 0), (20, 0), (30, 0)],
                       demand=[0, 4, 4, 4], ready=[0, 0, 40, 0], due=[200, 100, 60, 30],
                       service=[0, 5, 5, 5], capacity=12)


def small(n, seed, **kw):
    return VRPTW.random(n, seed, **kw)


def arcs_of(routes):
    used = []
    for r in routes:
        path = (0, *r, 0)
        used += list(zip(path, path[1:]))
    return used


def simulate(inst, route, start_pos, start_time):
    """Serve route[start_pos:] starting service at route[start_pos] at start_time; on time?"""
    t = start_time
    if t < inst.ready[route[start_pos]] or t > inst.due[route[start_pos]]:
        return t <= inst.due[route[start_pos]]
    for k in range(start_pos + 1, len(route)):
        a, b = route[k - 1], route[k]
        t = max(inst.ready[b], t + inst.service[a] + inst.dist[a][b])
        if t > inst.due[b]:
            return False
    last = route[-1]
    return t + inst.service[last] + inst.dist[last][0] <= inst.due[0]


def check_result(inst, out, optimum=None):
    assert out["status"] in ("optimal", "feasible", "infeasible", "unknown")
    if out["routes"] is not None:
        assert lab.violations(inst, out["routes"]) == []
        assert inst.cost(out["routes"]) == out["value"]
    if optimum is not None:
        assert out["status"] == "optimal", out
        assert out["value"] == optimum
        if out["bound"] is not None:
            assert out["bound"] <= optimum


# ---------------------------------------------------------------- step 1 ---

def test_step1_schedule_by_hand():
    inst = line_instance()
    # 0 -> 3 (arrive 30) serve 30..35, -> 2 (35+10=45, window opens 40) start 45, -> 1 (45+5+10=60 > due 100 ok)
    assert lab.schedule(inst, (3, 2, 1)) == [30, 45, 60]
    assert lab.schedule(inst, (1, 2)) == [10, 40]                 # waits at customer 2 from 25 to 40
    assert lab.schedule(inst, (1, 2, 3)) is None                  # customer 3 due at 30
    assert lab.schedule(inst, ()) == []
    tight = VRPTW.build("t", [(0, 0), (10, 0)], [0, 4], [0, 0], [25, 100], [0, 10], 10)
    assert lab.schedule(tight, (1,)) is None                      # back at 10 + 10 + 10 = 30 > 25
    heavy = VRPTW.build("h", [(0, 0), (10, 0), (20, 0)], [0, 6, 6], [0, 0, 0], [200, 100, 100], [0, 1, 1], 10)
    assert lab.schedule(heavy, (1, 2)) is None                    # load 12 > 10


@pytest.mark.parametrize("seed", range(6))
def test_step1_schedule_agrees_with_enumeration(seed):
    inst = small(6, seed, capacity=45)
    feasible = set(feasible_routes(inst))
    for k in range(1, 5):
        for route in itertools.permutations(inst.customers, k):
            assert (lab.schedule(inst, route) is not None) == (route in feasible), route


@pytest.mark.parametrize("seed", range(6))
def test_step1_latest_starts(seed):
    inst = small(7, seed, width=500)
    routes = [r for r in feasible_routes(inst) if len(r) >= 2]
    assert routes
    for route in routes[:80]:
        latest = lab.latest_starts(inst, route)
        assert len(latest) == len(route)
        for k in range(len(route)):
            if latest[k] >= inst.ready[route[k]]:
                assert simulate(inst, route, k, latest[k]), (route, k)
            assert not simulate(inst, route, k, latest[k] + 1), (route, k)
    assert lab.latest_starts(line_instance(), (1, 2)) == [min(100, 60 - 5 - 10), 60]


def test_step1_violations():
    inst = line_instance()
    assert lab.violations(inst, [(3, 2, 1)]) == []
    assert lab.violations(inst, [(3, 2)]) == [("missing", 1)]
    assert lab.violations(inst, [(3, 2, 1), (1,)]) == [("repeated", 1)]
    assert lab.violations(inst, [(1, 2, 3)]) == [("late", 0)]
    assert lab.violations(inst, [(3,), (1, 2, 1, 2)]) == [("capacity", 1), ("repeated", 1), ("repeated", 2)]
    assert lab.violations(inst, [(3, 2, 1), (7,)]) == [("unknown", 7)]
    assert lab.violations(inst, [(1,), (2,), (3,)]) == []
    assert lab.violations(inst, []) == [("missing", 1), ("missing", 2), ("missing", 3)]


@pytest.mark.parametrize("seed", range(4))
def test_step1_violations_accepts_the_optimum(seed):
    inst = small(8, seed)
    _, routes = brute_force(inst)
    assert lab.violations(inst, routes) == []
    shuffled = [tuple(reversed(r)) for r in routes if len(r) > 1]
    if any(lab.schedule(inst, r) is None for r in shuffled):
        assert lab.violations(inst, shuffled + [r for r in routes if len(r) == 1])


def test_step1_routes_from_arcs():
    routes = [(2, 5), (3, 1, 4)]
    arcs = arcs_of(routes)
    random.Random(0).shuffle(arcs)
    assert lab.routes_from_arcs(arcs) == [(2, 5), (3, 1, 4)]
    assert lab.routes_from_arcs([]) == []
    with pytest.raises(ValueError):
        lab.routes_from_arcs(arcs_of([(1, 2)]) + [(3, 4), (4, 3)])      # a subtour
    with pytest.raises(ValueError):
        lab.routes_from_arcs([(0, 1), (1, 0), (1, 2), (2, 0)])          # 1 is left twice


# ---------------------------------------------------------------- step 2 ---

def test_step2_rounded_capacity_cuts_by_hand():
    inst = VRPTW.build("q", [(0, 0), (10, 0), (20, 0), (30, 0), (40, 0)], [0, 6, 6, 6, 6],
                       [0] * 5, [1000] * 5, [0] * 5, capacity=10)
    # a fractional point: {1, 2} joined by 0.5 each way, entered from the depot with total 1
    x = {(0, 1): 0.5, (1, 2): 0.5, (2, 1): 0.5, (0, 2): 0.5, (1, 0): 0.5, (2, 0): 0.5,
         (0, 3): 1.0, (3, 0): 1.0, (0, 4): 1.0, (4, 0): 1.0}
    cuts = lab.rounded_capacity_cuts(inst, x)
    assert len(cuts) == 1
    S, entering, rhs = cuts[0]
    assert S == (1, 2) and rhs == 2
    assert sorted(entering) == [(0, 1), (0, 2)]
    # entering lists every arc of x into S from outside, even at value 0
    x2 = dict(x) | {(3, 1): 0.0}
    assert sorted(lab.rounded_capacity_cuts(inst, x2)[0][1]) == [(0, 1), (0, 2), (3, 1)]
    # an integer route carrying 1 and 2 together (load 12 > 10) is cut the same way
    xi = {(0, 1): 1, (1, 2): 1, (2, 0): 1, (0, 3): 1, (3, 0): 1, (0, 4): 1, (4, 0): 1}
    assert [(c[0], c[2]) for c in lab.rounded_capacity_cuts(inst, xi)] == [((1, 2), 2)]
    # feasible routes: no cut
    ok = {(0, 1): 1, (1, 0): 1, (0, 2): 1, (2, 0): 1, (0, 3): 1, (3, 0): 1, (0, 4): 1, (4, 0): 1}
    assert lab.rounded_capacity_cuts(inst, ok) == []


@pytest.mark.parametrize("seed", range(6))
def test_step2_cuts_never_remove_a_feasible_solution(seed):
    inst = small(8, seed)
    rng = random.Random(seed)
    routes = feasible_routes(inst)
    for _ in range(30):                      # random feasible solutions: greedy cover by random routes
        left, sol = set(inst.customers), []
        for r in rng.sample(routes, len(routes)):
            if set(r) <= left:
                sol.append(r)
                left -= set(r)
        sol += [(c,) for c in sorted(left)]
        x = {a: 0.0 for a in inst.arcs()} | {a: 1.0 for a in arcs_of(sol)}
        assert lab.rounded_capacity_cuts(inst, x) == []


@pytest.mark.parametrize("n,seed", [(7, 0), (7, 1), (8, 2), (8, 3), (9, 4), (9, 5), (10, 6), (10, 7)])
def test_step2_solve_mip_is_exact(n, seed):
    inst = small(n, seed)
    optimum, _ = brute_force(inst)
    with time_limit(60, "a small instance should take well under a second"):
        out = lab.solve_mip(inst, 30)
    check_result(inst, out, optimum)
    assert out["bound"] == optimum


@pytest.mark.parametrize("seed", range(4))
def test_step2_capacity_comes_only_from_the_cuts(seed):
    # capacity 30 and demands 5-25: many routes the time windows allow are overloaded
    inst = small(9, seed, capacity=30, width=900)
    optimum, _ = brute_force(inst)
    for cuts in (True, False):
        out = lab.solve_mip(inst, 30, cuts=cuts)
        check_result(inst, out, optimum)


# ---------------------------------------------------------------- step 3 ---

def reduced_costs(inst, duals, routes):
    return {r: inst.route_cost(r) - sum(duals[c] for c in r) for r in routes}


def full_allowed(inst, forbidden=()):
    return {i: [j for j in range(inst.n + 1) if inst.arc_possible(i, j) and (i, j) not in forbidden]
            for i in range(inst.n + 1)}


@pytest.mark.parametrize("seed", range(8))
def test_step3_price_finds_the_most_negative_route(seed):
    inst = small(8, seed, width=500)
    rng = random.Random(seed)
    duals = [0.0] + [rng.uniform(0, 1.2) * 2 * inst.dist[0][c] for c in inst.customers]
    rc = reduced_costs(inst, duals, feasible_routes(inst))
    best = min(rc.values())
    got = lab.price(inst, duals, full_allowed(inst), max_columns=5)
    if best >= -1e-6:
        assert got == []
        return
    # dominance guarantees the most negative route; the others returned need only be genuine
    assert got and got[0][0] == pytest.approx(best)
    assert 1 <= len(got) <= 5 and len({r for _, r in got}) == len(got)
    assert [v for v, _ in got] == sorted(v for v, _ in got)
    for v, r in got:
        assert r in rc and v == pytest.approx(rc[r]) and v < -1e-6


def test_step3_price_when_the_depot_deadline_binds():
    # Customers' windows leave room, but the depot closes at 320. Reaching 3 via 1 is cheaper after duals and
    # arrives later, too late to get home; reaching it via 2 is dearer and on time. Dominance must compare
    # times, and closing a route must check the return.
    inst = VRPTW.build("d", [(0, 0), (100, 0), (50, 0), (100, 100)], [0, 1, 1, 1],
                       [0, 0, 0, 0], [320, 100, 50, 5000], [0, 0, 0, 0], capacity=10)
    duals = [0.0, 300.0, 150.0, 420.0]
    rc = reduced_costs(inst, duals, feasible_routes(inst))
    best = min(rc, key=rc.get)
    got = lab.price(inst, duals, full_allowed(inst), max_columns=20)
    assert got[0] == (pytest.approx(rc[best]), best)
    assert all(r in rc for _, r in got)
    # the mirror image: now the cheap, late label reaches customer 3 first and must not delete the on-time one
    mirror = VRPTW.build("m", [(0, 0), (0, -30), (60, 0), (100, 100)], [0, 1, 1, 1],
                         [0, 0, 0, 0], [320, 60, 100, 5000], [0, 0, 0, 0], capacity=10)
    duals = [0.0, 80.0, 40.0, 300.0]
    rc = reduced_costs(mirror, duals, feasible_routes(mirror))
    got = lab.price(mirror, duals, full_allowed(mirror), max_columns=20)
    assert got[0] == (pytest.approx(rc[(2, 3)]), (2, 3)) and rc[(2, 3)] == min(rc.values())


@pytest.mark.parametrize("width,horizon", [(150, 2000), (300, 700), (150, 800)])
def test_step3_price_with_tight_windows_and_short_days(width, horizon):
    # windows narrow enough that time decides dominance, and days short enough that returning late matters
    for seed in range(8):
        inst = small(8, seed, width=width, horizon=horizon)
        rng = random.Random(seed)
        duals = [0.0] + [rng.uniform(0.8, 1.6) * 2 * inst.dist[0][c] for c in inst.customers]
        rc = reduced_costs(inst, duals, feasible_routes(inst))
        best = min(rc.values())
        got = lab.price(inst, duals, full_allowed(inst), max_columns=100)
        if best < -1e-6:
            assert got and got[0][0] == pytest.approx(best), (width, horizon, seed)
        for v, r in got:
            assert r in rc and v == pytest.approx(rc[r]), (width, horizon, seed, r)


@pytest.mark.parametrize("seed", range(4))
def test_step3_price_respects_forbidden_arcs_and_limits(seed):
    inst = small(8, seed, width=500)
    duals = [0.0] + [2.5 * inst.dist[0][c] for c in inst.customers]
    rng = random.Random(seed)
    forbidden = set(rng.sample([a for a in inst.arcs() if a[0] and a[1]], 15))
    routes = [r for r in feasible_routes(inst) if not set(arcs_of([r])) & forbidden]
    rc = reduced_costs(inst, duals, routes)
    best = min(rc.values())
    got = lab.price(inst, duals, full_allowed(inst, forbidden), max_columns=50)
    assert got[0][0] == pytest.approx(best)
    assert all(r in rc for _, r in got)
    assert [v for v, _ in got] == sorted(v for v, _ in got)
    limited = lab.price(inst, duals, full_allowed(inst, forbidden), max_columns=50, label_limit=1)
    assert all(r in rc and v == pytest.approx(rc[r]) for v, r in limited)
    assert lab.price(inst, [0.0] * (inst.n + 1), full_allowed(inst)) == []


def test_step3_arc_flows():
    flows = lab.arc_flows([(1, 2), (2,), (1,)], [0.5, 0.5, 0.5])
    assert flows == pytest.approx({(0, 1): 1.0, (1, 2): 0.5, (2, 0): 1.0, (0, 2): 0.5, (1, 0): 0.5})
    assert lab.arc_flows([(1,)], [0.0]) == {}


@pytest.mark.parametrize("seed", range(5))
def test_step3_column_generation_matches_the_full_lp(seed):
    inst = small(8, seed, width=500)
    routes = feasible_routes(inst)
    A = np.array([[1.0 if c in r else 0.0 for r in routes] for c in inst.customers])
    full = highs_lp(A, np.ones(inst.n), [inst.route_cost(r) for r in routes], sense="min",
                    row_lower=np.ones(inst.n))
    value, cols, lam, converged = lab.column_generation(inst, [(c,) for c in inst.customers], frozenset())
    assert converged
    assert value == pytest.approx(full.value, abs=1e-6)
    assert len(cols) == len(lam)
    assert sum(inst.route_cost(r) * v for r, v in zip(cols, lam)) == pytest.approx(value, abs=1e-6)
    for c in inst.customers:
        assert sum(v for r, v in zip(cols, lam) if c in r) == pytest.approx(1.0, abs=1e-6)


def test_step3_column_generation_reports_an_infeasible_node():
    inst = small(6, 0)
    forbidden = frozenset((0, j) for j in inst.customers)      # nobody can leave the depot
    value, *_ = lab.column_generation(inst, [(c,) for c in inst.customers], forbidden)
    assert value is None


@pytest.mark.parametrize("n,seed", [(8, 0), (8, 1), (9, 2), (9, 3), (10, 4), (10, 5), (10, 6), (10, 7)])
def test_step3_branch_and_price_is_exact(n, seed):
    inst = small(n, seed, width=500)
    optimum, _ = brute_force(inst)
    with time_limit(120):
        out = lab.branch_and_price(inst, 60)
    check_result(inst, out, optimum)
    assert out["bound"] == optimum and out["nodes"] >= 1


def test_step3_restricted_master_ip():
    inst = small(9, 3, width=500)
    optimum, routes = brute_force(inst)
    singles = [(c,) for c in inst.customers]
    assert lab.restricted_master_ip(inst, singles + routes + [routes[0][:1]], 10) == (optimum, sorted(routes))
    assert lab.restricted_master_ip(inst, [r for r in routes if r != routes[0]], 10) is None   # can't cover


def test_step3_restricted_master_ip_checks_what_the_solver_returns(monkeypatch):
    import colib.mip
    from colib.mip import MIPInfo
    inst = small(9, 3, width=500)
    _, routes = brute_force(inst)
    columns = [(c,) for c in inst.customers] + routes
    stopped = lambda milp, time_limit=60.0, **kw: MIPInfo("time_limit", 0.0, np.zeros(len(milp.c)), 0, time_limit, None)
    monkeypatch.setattr(colib.mip, "highs_mip", stopped)
    if hasattr(lab, "highs_mip"):
        monkeypatch.setattr(lab, "highs_mip", stopped)
    assert lab.restricted_master_ip(inst, columns, 1) is None


def test_step3_branch_and_price_out_of_time_claims_nothing():
    inst = small(60, 2, capacity=300, width=1800)
    out = lab.branch_and_price(inst, 0.5)
    assert out["status"] in ("feasible", "unknown")
    check_result(inst, out)
    if out["value"] is not None and out["bound"] is not None:
        assert out["bound"] <= out["value"]


def test_step3_branch_and_price_branches_correctly():
    # instances whose root LP is fractional, so the tree has to branch to reach the optimum
    branched = 0
    for seed in range(40):
        inst = small(9, seed, width=500)
        optimum, _ = brute_force(inst)
        out = lab.branch_and_price(inst, 60)
        check_result(inst, out, optimum)
        branched += out["nodes"] > 1
        if branched >= 3:
            break
    assert branched >= 3


# ---------------------------------------------------------------- step 4 ---

def cp_solve(model, workers=1, fix_hint=False):
    from ortools.sat.python import cp_model
    s = cp_model.CpSolver()
    s.parameters.num_workers = workers
    s.parameters.max_time_in_seconds = 30
    if fix_hint:
        s.parameters.fix_variables_to_their_hinted_value = True
    return s, s.solve(model)


@pytest.mark.parametrize("n,seed", [(7, 0), (8, 1), (9, 2), (10, 3)])
def test_step4_cpsat_model_is_exact(n, seed):
    from ortools.sat.python import cp_model
    inst = small(n, seed)
    optimum, _ = brute_force(inst)
    model, lit = lab.cpsat_model(inst)
    assert set(lit) == set(inst.arcs())
    s, code = cp_solve(model)
    assert code == cp_model.OPTIMAL and round(s.objective_value) == optimum
    used = [a for a, b in lit.items() if s.value(b)]
    assert inst.cost(lab.routes_from_arcs(used)) == optimum


@pytest.mark.parametrize("seed", range(3))
def test_step4_hint_is_complete_and_consistent(seed):
    from ortools.sat.python import cp_model
    inst = small(9, seed)
    optimum, routes = brute_force(inst)
    worse = [(c,) for c in inst.customers]
    for hint, value in ((routes, optimum), (worse, inst.cost(worse))):
        model, lit = lab.cpsat_model(inst)
        assert lab.add_hint(model, lit, hint) == len(arcs_of(hint))
        s, code = cp_solve(model, fix_hint=True)
        assert code in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        assert round(s.objective_value) == value


def test_step4_nearest_strategy_order():
    inst = small(8, 0)
    model, lit = lab.cpsat_model(inst)
    order = lab.add_nearest_strategy(model, inst, lit)
    assert order == sorted(inst.arcs(), key=lambda a: (inst.dist[a[0]][a[1]], a))
    assert len(model.proto.search_strategy) == 1
    strategy = model.proto.search_strategy[0]
    assert [e.vars[0] for e in strategy.exprs] == [lit[a].index for a in order]


@pytest.mark.parametrize("n,seed", [(8, 4), (9, 5), (10, 6)])
def test_step4_solve_cpsat(n, seed):
    inst = small(n, seed)
    optimum, routes = brute_force(inst)
    for kw in ({}, {"strategy": "nearest"}, {"hint": routes}, {"workers": 4, "strategy": "nearest"}):
        out = lab.solve_cpsat(inst, 30, **kw)
        check_result(inst, out, optimum)
        assert out["bound"] == optimum and out["nodes"] >= 0


def test_step4_solve_cpsat_reports_a_time_out():
    inst = small(60, 1, capacity=200, width=1500)
    out = lab.solve_cpsat(inst, 0.3)
    assert out["status"] in ("feasible", "unknown")
    check_result(inst, out)


# ---------------------------------------------------------------- step 5 ---

@pytest.mark.parametrize("seed", range(6))
def test_step5_insertion_delta_agrees_with_a_full_check(seed):
    inst = small(9, seed, width=600, capacity=80)
    rng = random.Random(seed)
    routes = [r for r in feasible_routes(inst) if 2 <= len(r) <= 4]
    for route in rng.sample(routes, min(40, len(routes))):
        starts, latest = lab.schedule(inst, route), lab.latest_starts(inst, route)
        for c in inst.customers:
            if c in route:
                continue
            for pos in range(len(route) + 1):
                new = route[:pos] + (c,) + route[pos:]
                got = lab.insertion_delta(inst, route, starts, latest, pos, c)
                if lab.schedule(inst, new) is None:
                    assert got is None, (route, pos, c)
                else:
                    assert got == inst.route_cost(new) - inst.route_cost(route), (route, pos, c)


class Script:
    """A stand-in rng: choice takes the element at a scripted index; random returns scripted floats."""
    def __init__(self, picks, floats):
        self.picks, self.floats = list(picks), list(floats)

    def choice(self, seq):
        return seq[self.picks.pop(0) % len(seq)]

    def random(self):
        return self.floats.pop(0)


def relatedness(inst, routes):
    start = {c: s for r in routes for c, s in zip(r, lab.schedule(inst, r))}
    dmax = max(max(row) for row in inst.dist)
    return lambda i, j: (inst.dist[i][j] / dmax + abs(start[i] - start[j]) / inst.due[0]
                         + abs(inst.demand[i] - inst.demand[j]) / inst.capacity)


@pytest.mark.parametrize("seed", range(4))
def test_step5_shaw_removal_takes_the_most_related(seed):
    inst = small(10, seed)
    _, routes = brute_force(inst)
    rel = relatedness(inst, routes)
    # choice always picks index 0 (the smallest customer, then the first removed); random() = 0: the most related
    kept, removed = lab.shaw_removal(inst, routes, 4, Script([0] * 10, [0.0] * 10))
    expect = [min(inst.customers)]
    while len(expect) < 4:
        rest = [c for c in inst.customers if c not in expect]
        expect.append(min(rest, key=lambda j: (rel(expect[0], j), j)))
    assert removed == expect
    assert sorted(c for r in kept for c in r) == sorted(set(inst.customers) - set(expect))
    assert all(r for r in kept)
    for r in kept:                                   # order inside routes is kept
        whole = next(w for w in routes if set(r) <= set(w))
        assert list(r) == [c for c in whole if c in r]


def test_step5_shaw_removal_randomises_with_the_sixth_power():
    inst = small(10, 3)
    _, routes = brute_force(inst)
    rel = relatedness(inst, routes)
    # second pick: anchor = removed[1 % 1] = first; u = 0.9 -> index floor(0.9**6 * 9) = 4
    _, removed = lab.shaw_removal(inst, routes, 2, Script([2, 1], [0.9]))
    first = sorted(inst.customers)[2]
    rest = sorted((c for c in inst.customers if c != first), key=lambda j: (rel(first, j), j))
    assert removed == [first, rest[int(0.9 ** 6 * 9)]]


def test_step5_regret_insertion_by_hand():
    # depot at 0. Customer 3 fits cheaply only in route (1,); customer 2 fits almost equally well in
    # either route. Greedy inserts the cheapest first; regret-2 inserts 3 first because it has more to lose.
    inst = VRPTW.build("r", [(0, 0), (100, 0), (100, 100), (0, 100), (110, 0)], [0, 5, 5, 5, 5],
                       [0, 0, 0, 0, 0], [5000] * 5, [0] * 5, capacity=10)
    routes = [(1,), (3,)]
    g = lab.regret_insertion(inst, routes, [2, 4], k=1)
    r2 = lab.regret_insertion(inst, routes, [2, 4], k=2)
    for out in (g, r2):
        assert lab.violations(inst, out) == []
    assert inst.cost(r2) <= inst.cost(g)
    assert lab.regret_insertion(inst, [], [1], k=2) == [(1,)]


def test_step5_regret_counts_a_missing_option_as_infinitely_bad():
    # Two routes with room for one more customer each. Customer 3 can join only route (1,) (its window rules out
    # route (2,)), so with k = 3 it has two options and infinite regret: it must be inserted first, into (1,),
    # even though customer 4 would like that route too.
    inst = VRPTW.build("k", [(0, 0), (100, 0), (-100, 0), (110, 0), (105, 5)], [0, 5, 5, 5, 5],
                       [0, 0, 0, 0, 0], [5000, 5000, 100, 115, 5000], [0] * 5, capacity=10)
    out = lab.regret_insertion(inst, [(1,), (2,)], [4, 3], k=3)
    assert lab.violations(inst, out) == []
    assert (1, 3) in out or (3, 1) in out


@pytest.mark.parametrize("seed", range(6))
def test_step5_greedy_insertion_is_the_cheapest_first(seed):
    inst = small(9, seed, width=800, capacity=80)
    rng = random.Random(seed)
    _, routes = brute_force(inst)
    removed = rng.sample(list(inst.customers), 3)
    partial = [r for r in (tuple(c for c in r if c not in removed) for r in routes) if r]
    out = lab.regret_insertion(inst, partial, removed, k=1)
    assert lab.violations(inst, out) == []
    # replay: the first customer inserted must be one with the globally cheapest option
    best = math.inf
    for c in removed:
        for ri, r in enumerate(partial):
            for pos in range(len(r) + 1):
                new = r[:pos] + (c,) + r[pos:]
                if lab.schedule(inst, new) is not None:
                    best = min(best, inst.route_cost(new) - inst.route_cost(r))
        best = min(best, inst.dist[0][c] + inst.dist[c][0])
    added = inst.cost(out) - inst.cost(partial)
    assert added >= best


def test_step5_regret_new_routes():
    # a tie between inserting and a new route goes to the existing route: 0-2-1-0 and 0-1-0 + 0-2-0 both cost 400
    inst = VRPTW.build("o", [(0, 0), (100, 0), (-100, 0)], [0, 5, 5], [0, 0, 0], [5000] * 3, [0] * 3, 10)
    assert lab.regret_insertion(inst, [(1,)], [2], k=1) == [(2, 1)]
    # no room in the existing route: a new route, appended at the end
    full = VRPTW.build("f", [(0, 0), (100, 0), (110, 0)], [0, 8, 5], [0, 0, 0], [5000] * 3, [0] * 3, 10)
    assert lab.regret_insertion(full, [(1,)], [2], k=2) == [(1,), (2,)]
    near = VRPTW.build("n", [(0, 0), (100, 0), (110, 0)], [0, 5, 5], [0, 0, 0], [5000] * 3, [0] * 3, 10)
    assert lab.regret_insertion(near, [(1,)], [2], k=1) == [(2, 1)]      # both positions add 20: the earlier one


@pytest.mark.parametrize("seed", range(3))
def test_step5_alns_is_valid_and_reproducible(seed):
    inst = small(12, seed)
    a = lab.alns_vrptw(inst, 30, seed=seed, iterations=150)
    b = lab.alns_vrptw(inst, 30, seed=seed, iterations=150)
    check_result(inst, a)
    assert a["status"] == "feasible" and a["bound"] is None and a["nodes"] == 150
    assert a["value"] == b["value"] and a["routes"] == b["routes"]


def test_step5_alns_finds_optima():
    hits = 0
    for seed in range(10):
        inst = small(9, seed)
        optimum, _ = brute_force(inst)
        out = lab.alns_vrptw(inst, 30, seed=0, iterations=300)
        check_result(inst, out)
        assert out["value"] >= optimum
        hits += out["value"] == optimum
    assert hits >= 6


def test_step5_alns_respects_the_time_limit():
    inst = small(40, 0, capacity=100)
    with time_limit(5, "alns_vrptw must stop at its time limit"):
        out = lab.alns_vrptw(inst, 0.5, seed=0)
    check_result(inst, out)


# ---------------------------------------------------------------- step 6 ---

def fake(out):
    return lambda inst, time_limit, seed, **kw: dict(out)


def test_step6_benchmark_solver_trusts_nothing():
    inst = line_instance()
    good = {"status": "optimal", "value": inst.cost([(3, 2, 1)]), "bound": None, "routes": [(3, 2, 1)], "nodes": 4}
    run = lab.benchmark_solver(fake(good))(inst, 0, 10)
    assert run == {"status": "optimal", "value": good["value"], "nodes": 4}
    lie = dict(good, value=good["value"] - 1)
    assert lab.benchmark_solver(fake(lie))(inst, 0, 10)["status"] == "invalid"
    late = dict(good, routes=[(1, 2, 3)], value=inst.cost([(1, 2, 3)]))
    assert lab.benchmark_solver(fake(late))(inst, 0, 10) == {"status": "invalid", "value": None, "nodes": 4}
    missing = dict(good, status="feasible", routes=[(3, 2)], value=inst.cost([(3, 2)]))
    assert lab.benchmark_solver(fake(missing))(inst, 0, 10)["status"] == "invalid"
    nothing = {"status": "unknown", "value": None, "bound": 3, "routes": None, "nodes": 9}
    assert lab.benchmark_solver(fake(nothing))(inst, 0, 10) == {"status": "no solution", "value": None, "nodes": 9}
    infeasible = dict(nothing, status="infeasible")
    assert lab.benchmark_solver(fake(infeasible))(inst, 0, 10)["status"] == "infeasible"
    seen = {}
    spy = lambda inst, time_limit, seed, **kw: seen.update(t=time_limit, s=seed, kw=kw) or dict(good)
    lab.benchmark_solver(spy, workers=8)(inst, 3, 7.5)
    assert seen == {"t": 7.5, "s": 3, "kw": {"workers": 8}}


def test_step6_primal_gap():
    assert lab.primal_gap(100, 100) == 0.0
    assert lab.primal_gap(110, 100) == pytest.approx(10 / 110)
    assert lab.primal_gap(90, 100) == pytest.approx(0.1)
    assert lab.primal_gap(None, 100) == 1.0
    assert lab.primal_gap(-5, 5) == 1.0
    assert lab.primal_gap(0, 0) == 0.0


def runs_of(rows):
    return [dict(zip(("solver", "instance", "seed", "status", "value"), r), seconds=1.0, nodes=None,
                 experiment="x") for r in rows]


def test_step6_references_and_contradictions():
    runs = runs_of([("a", "i1", 0, "optimal", 100), ("b", "i1", 0, "feasible", 100), ("c", "i1", 0, "feasible", 104),
                    ("a", "i2", 0, "feasible", 50), ("b", "i2", 0, "optimal", 52), ("c", "i2", 0, "invalid", None),
                    ("a", "i3", 0, "no solution", None), ("b", "i3", 1, "feasible", 7), ("b", "i3", 2, "optimal", 7),
                    ("a", "i4", 0, "timeout", None)])
    assert lab.references(runs) == {"i1": (100, True), "i2": (50, False), "i3": (7, True)}
    assert lab.contradictions(runs) == [("i2", "b", 0)]


def test_step6_head_to_head():
    rng = random.Random(0)
    rows = []
    for k in range(30):
        base = rng.uniform(0, 0.1)
        rows += [("fast", f"i{k}", 0, "feasible", base), ("slow", f"i{k}", 0, "feasible", base + 0.05 + rng.uniform(0, 0.01)),
                 ("twin", f"i{k}", 0, "feasible", base + rng.choice([-1, 1]) * rng.uniform(0, 0.01)),
                 ("twin", f"i{k}", 1, "feasible", base)]
    runs = runs_of(rows)
    out = lab.head_to_head(runs, [("fast", "slow"), ("slow", "fast"), ("fast", "twin")], metric=lambda r: r["value"])
    assert [(o["a"], o["b"], o["n"]) for o in out] == [("fast", "slow", 30), ("slow", "fast", 30), ("fast", "twin", 30)]
    assert out[0]["wins"] == 30 and out[0]["verdict"] == "fast"
    assert out[1]["losses"] == 30 and out[1]["verdict"] == "fast"
    assert out[2]["verdict"] == "indistinguishable"
    assert out[0]["p_holm"] >= out[0]["p"]
    assert all(o["wins"] + o["losses"] + o["ties"] == o["n"] for o in out)
    tied = runs_of([(s, f"i{k}", 0, "feasible", float(k % 3 if s == "p" or k < 20 else k % 3 + 1))
                    for k in range(30) for s in ("p", "q")])
    row = lab.head_to_head(tied, [("p", "q")], metric=lambda r: r["value"])[0]
    assert (row["wins"], row["losses"], row["ties"]) == (10, 0, 20)
    only = lab.head_to_head(runs_of([("a", "i", 0, "feasible", 1), ("b", "j", 0, "feasible", 2)]), [("a", "b")],
                            metric=lambda r: r["value"])
    assert only[0]["n"] == 0 and only[0]["verdict"] == "indistinguishable"
