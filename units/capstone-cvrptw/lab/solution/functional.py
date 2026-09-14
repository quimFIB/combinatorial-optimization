"""Capstone lab — one problem, four traditions.  REFERENCE SOLUTION, functional.

Schedules are scans, the checker is set algebra over frequencies, and repair and removal are folds whose
state is (routes, customers left). Branch-and-price is an unfold over a search state (open nodes as a
sorted tuple, shared columns, incumbent, node count). The pricer is a label-correcting fixpoint over
immutable per-vertex buckets.

Three places keep mutable state, local to one function, because the tools are built that way: the SCIP
and CP-SAT model builders (their APIs add to a model), and the HiGHS master in column_generation, which
grows by adding columns to a live solver. Random draws happen in the same order as in the imperative
reference, so shaw_removal consumes an rng identically.
"""

from __future__ import annotations

import math
import random
import time
from functools import reduce
from itertools import accumulate, takewhile

import networkx as nx
import numpy as np
import toolz as tz

from colib.vrptw import lazy_cut_handler

TOL = 1e-6


def _result(status, value=None, bound=None, routes=None, nodes=None):
    return {"status": status, "value": value, "bound": bound, "routes": routes, "nodes": nodes}


def _path_arcs(route):
    path = (0, *route, 0)
    return tuple(zip(path, path[1:]))


def _unfold(step, state, done):
    """Iterate step from state until done(state); return that state."""
    return tz.first(s for s in tz.iterate(step, state) if done(s))


# ---------------------------------------------------------------- step 1 ---

def schedule(inst, route):
    if sum(inst.demand[c] for c in route) > inst.capacity:
        return None
    legs = zip((0, *route), route)
    starts = list(accumulate(legs, lambda t, leg: max(inst.ready[leg[1]], t + inst.service[leg[0]] + inst.dist[leg[0]][leg[1]]),
                             initial=inst.ready[0]))[1:]
    if any(s > inst.due[c] for s, c in zip(starts, route)):
        return None
    last, t = (route[-1], starts[-1]) if route else (0, inst.ready[0])
    return starts if t + inst.service[last] + inst.dist[last][0] <= inst.due[0] else None


def latest_starts(inst, route):
    legs = zip(reversed(route), (0, *reversed(route[1:])))            # (customer, the vertex after it)
    backwards = list(accumulate(legs, lambda late, leg: min(inst.due[leg[0]], late - inst.service[leg[0]] - inst.dist[leg[0]][leg[1]]),
                                initial=inst.due[0]))[1:]
    return backwards[::-1]


def violations(inst, routes):
    is_customer = lambda c: isinstance(c, int) and 1 <= c <= inst.n
    counts = tz.frequencies(c for r in routes for c in r if is_customer(c))
    clean = [tuple(filter(is_customer, r)) for r in routes]
    over = {("capacity", k) for k, r in enumerate(clean) if sum(inst.demand[c] for c in r) > inst.capacity}
    late = {("late", k) for k, r in enumerate(clean) if ("capacity", k) not in over and schedule(inst, r) is None}
    found = ({("unknown", c) for r in routes for c in r if not is_customer(c)} | over | late
             | {("missing", c) for c in inst.customers if c not in counts}
             | {("repeated", c) for c, k in counts.items() if k > 1})
    return sorted(found, key=lambda v: (v[0], str(v[1])))


def routes_from_arcs(arcs):
    succ = tz.groupby(0, arcs)
    twice = [i for i, out in succ.items() if i != 0 and len(out) > 1]
    if twice:
        raise ValueError(f"vertex {twice[0]} is left twice")

    def bounded(first):                      # a cycle would make takewhile infinite: cap the walk
        walk = list(tz.take(len(arcs) + 1, takewhile(lambda v: v != 0,
                                                     tz.iterate(lambda v: succ[v][0][1] if v in succ else -1, first))))
        if -1 in walk or len(walk) != len(set(walk)):
            raise ValueError(f"route from {first} never returns to the depot")
        return tuple(walk)

    routes = [bounded(j) for _, j in sorted(succ.get(0, []))]
    if sum(len(r) + 1 for r in routes) != len(arcs):
        raise ValueError("some arcs form a subtour away from the depot")
    return routes


# ---------------------------------------------------------------- step 2 ---

def rounded_capacity_cuts(inst, x, eps=1e-6):
    g = nx.Graph()
    g.add_nodes_from(inst.customers)
    g.add_edges_from(a for a, v in x.items() if a[0] and a[1] and v > eps)
    by_first = lambda S: min(S)
    comps = sorted((tuple(sorted(S)) for S in nx.connected_components(g)), key=by_first)

    def cut(S):
        members = set(S)
        entering = [a for a in x if a[1] in members and a[0] not in members]
        rhs = math.ceil(sum(inst.demand[c] for c in S) / inst.capacity)
        return (S, entering, rhs) if sum(x[a] for a in entering) < rhs - eps else None

    return [c for c in map(cut, comps) if c is not None]


def solve_mip(inst, time_limit=60.0, seed=0, cuts=True):
    from pyscipopt import Model, quicksum
    m = Model()
    m.hideOutput()
    m.setParam("limits/time", float(time_limit))
    m.setParam("randomization/randomseedshift", int(seed))
    arcs = inst.arcs()
    x = {a: m.addVar(vtype="B", obj=inst.dist[a[0]][a[1]]) for a in arcs}
    t = {c: m.addVar(lb=max(inst.ready[c], inst.ready[0] + inst.dist[0][c]),
                     ub=min(inst.due[c], inst.due[0] - inst.service[c] - inst.dist[c][0])) for c in inst.customers}
    out_of, into = tz.groupby(0, arcs), tz.groupby(1, arcs)
    for c in inst.customers:
        m.addCons(quicksum(x[a] for a in out_of.get(c, [])) == 1)
        m.addCons(quicksum(x[a] for a in into.get(c, [])) == 1)
    for i, j in (a for a in arcs if a[0] and a[1]):
        M = max(0, inst.due[i] + inst.service[i] + inst.dist[i][j] - inst.ready[j])
        m.addCons(t[j] >= t[i] + inst.service[i] + inst.dist[i][j] - M * (1 - x[i, j]))
    fractional = lambda values: any(abs(v - round(v)) > TOL for v in values.values())
    separate = lambda values: ([] if not cuts and fractional(values)
                               else [(entering, rhs) for _, entering, rhs in rounded_capacity_cuts(inst, values)])
    handler = lazy_cut_handler(m, x, separate)
    m.setMinimize()
    m.optimize()
    routes = (routes_from_arcs([a for a in arcs if m.getSolVal(m.getBestSol(), x[a]) > 0.5])
              if m.getNSols() > 0 else None)
    status = m.getStatus()
    st = ("optimal" if status == "optimal" else "infeasible" if status == "infeasible"
          else "feasible" if routes is not None else "unknown")
    bound = m.getDualbound()
    return _result(st, inst.cost(routes) if routes is not None else None,
                  math.ceil(bound - TOL) if math.isfinite(bound) else None, routes,
                  int(m.getNTotalNodes())) | {"cuts": handler.added}


# ---------------------------------------------------------------- step 3 ---

def _dominates(a, b):
    return a[0] <= b[0] + 1e-9 and a[1] <= b[1] and a[2] <= b[2] and a[3] & b[3] == a[3]


def price(inst, duals, allowed, max_columns=30, label_limit=None):
    dist, ready, due, service, demand, Q = inst.dist, inst.ready, inst.due, inst.service, inst.demand, inst.capacity
    succ = {i: tuple(j for j in allowed.get(i, ()) if j != i) for i in range(inst.n + 1)}

    def unreachable(v, t, load, mask):
        return mask | sum(1 << w for w in inst.customers
                          if not mask >> w & 1 and (load + demand[w] > Q
                                                    or max(ready[w], t + service[v] + dist[v][w]) > due[w]))

    def label(rc, load, t, mask, route):
        v = route[-1]
        return (rc, load, t, unreachable(v, t, load, mask | 1 << v), route)

    def extend(lab):
        rc, load, t, mask, route = lab
        v = route[-1]
        return [label(rc + dist[v][w] - duals[w], load + demand[w], max(ready[w], t + service[v] + dist[v][w]), mask, route + (w,))
                for w in succ[v] if w != 0 and not mask >> w & 1]

    def merge(buckets, new):
        """Add a label to its vertex's bucket unless dominated; drop the labels it dominates."""
        v = new[4][-1]
        old = buckets.get(v, ())
        if any(_dominates(o, new) for o in old):
            return buckets
        kept = tuple(sorted((*(o for o in old if not _dominates(new, o)), new), key=lambda o: (o[0], o[4])))
        return buckets | {v: kept[:label_limit] if label_limit is not None else kept}

    starts = [label(dist[0][j] - duals[j], demand[j], max(ready[j], ready[0] + dist[0][j]), 0, (j,))
              for j in succ[0] if j != 0 and demand[j] <= Q and max(ready[j], ready[0] + dist[0][j]) <= due[j]]
    first = reduce(merge, starts, {})

    def step(state):
        buckets, frontier = state
        grown = reduce(merge, (e for lab in frontier for e in extend(lab)), buckets)
        alive = {lab for b in grown.values() for lab in b}
        old = {lab for b in buckets.values() for lab in b}
        return grown, tuple(sorted(alive - old, key=lambda o: (o[2], o[0], o[4])))

    initial = (first, tuple(lab for b in first.values() for lab in b))
    final, _ = _unfold(step, initial, lambda s: not s[1])
    closing = sorted({(lab[0] + dist[lab[4][-1]][0], lab[4]) for b in final.values() for lab in b
                      if 0 in succ[lab[4][-1]] and lab[2] + service[lab[4][-1]] + dist[lab[4][-1]][0] <= due[0]})
    return [(rc, r) for rc, r in closing if rc < -1e-6][:max_columns]


def arc_flows(columns, lam):
    return tz.reduceby(0, lambda acc, av: acc + av[1],
                       ((a, v) for r, v in zip(columns, lam) if v > 1e-9 for a in _path_arcs(r)), 0.0)


def _route_allowed(route, forbidden):
    return not any(a in forbidden for a in _path_arcs(route))


def column_generation(inst, columns, forbidden, deadline=math.inf):
    import highspy
    n = inst.n
    big = 2 * sum(max(row) for row in inst.dist) + 1
    allowed = {i: [j for j in range(n + 1) if (i, j) not in forbidden and inst.arc_possible(i, j)] for i in range(n + 1)}
    start = [r for r in dict.fromkeys(columns) if _route_allowed(r, forbidden)]

    # the HiGHS master is a live object: columns are added to it in place, locally
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.addRows(n, np.ones(n), np.ones(n), 0, np.array([0], np.int32), np.array([], np.int32), np.array([]))
    add = lambda route, cost: h.addCol(float(cost), 0.0, highspy.kHighsInf, len(set(route)),
                                       np.array(sorted(c - 1 for c in set(route)), np.int32), np.ones(len(set(route))))
    for c in inst.customers:
        add((c,), big)
    for r in start:
        add(r, inst.route_cost(r))

    def step(state):
        cols, _ = state
        h.run()
        duals = [0.0] + list(h.getSolution().row_dual)
        if time.perf_counter() > deadline:
            return cols, "stopped"
        new = price(inst, duals, allowed, label_limit=8)
        if not new and time.perf_counter() <= deadline:
            new = price(inst, duals, allowed)
        elif not new:
            return cols, "stopped"
        have = set(cols)
        fresh = [r for _, r in new if r not in have]
        for r in fresh:
            add(r, inst.route_cost(r))
        return (cols + tuple(fresh), "running") if fresh else (cols, "converged")

    cols, how = _unfold(step, (tuple(start), "running"), lambda s: s[1] != "running")
    sol = list(h.getSolution().col_value)
    value = h.getInfo().objective_function_value
    feasible = not any(v > 1e-6 for v in sol[:n])
    return (value if feasible else None), list(cols), sol[n:], how == "converged"



def restricted_master_ip(inst, columns, time_limit):
    """A primal heuristic: the set-partitioning IP over the given columns only, by HiGHS's MIP solver
    within time_limit seconds. Returns (cost, routes) of the best solution found, or None if there is none
    (HiGHS can return a vector at its time limit that isn't a solution, so check it with violations)."""
    from colib.mip import MILP, highs_mip
    cols = list(dict.fromkeys(columns))
    A_eq = tuple(tuple(1 if c in r else 0 for r in cols) for c in inst.customers)
    milp = MILP(c=tuple(inst.route_cost(r) for r in cols), A_eq=A_eq, b_eq=(1,) * inst.n,
                ub=(1,) * len(cols), integer=(True,) * len(cols))
    out = highs_mip(milp, time_limit=max(0.1, time_limit))
    if out.x is None:
        return None
    routes = sorted(r for r, v in zip(cols, out.x) if v > 0.5)
    # a MIP stopped by its time limit can hand back a vector that isn't a solution: check it
    return (inst.cost(routes), routes) if not violations(inst, routes) else None


def branch_and_price(inst, time_limit=60.0, seed=0):
    deadline = time.perf_counter() + time_limit
    everything = range(inst.n + 1)

    def children(bound, forbidden, arc):
        i, j = arc
        force = ({(i, k) for k in everything if k != j} if i else set()) | ({(k, j) for k in everything if k != i} if j else set())
        return [(bound, forbidden | {arc}), (bound, forbidden | frozenset(force))]

    def push(heap, nodes):
        return tuple(sorted((*heap, *nodes), key=lambda nd: (nd[0], sorted(nd[1]))))

    def step(state):
        heap, columns, incumbent, count, _ = state
        (node_bound, forbidden), rest = heap[0], heap[1:]
        if node_bound >= incumbent[0]:
            return rest, columns, incumbent, count, False
        if time.perf_counter() > deadline:
            return heap, columns, incumbent, count, True
        value, cols, lam, converged = column_generation(inst, columns, forbidden, deadline)
        if not converged:
            return heap, cols, incumbent, count + 1, True
        if count == 0 and value is not None:
            found = restricted_master_ip(inst, cols, min(10.0, (deadline - time.perf_counter()) / 4))
            incumbent = min(incumbent, found or (math.inf, None), key=lambda p: p[0])
        if value is None or math.ceil(value - TOL) >= incumbent[0]:
            return rest, cols, incumbent, count + 1, False
        live = [(r, v) for r, v in zip(cols, lam) if v > 1e-9]
        flows = arc_flows([r for r, _ in live], [v for _, v in live])
        fractional = [a for a, f in flows.items() if TOL < f < 1 - TOL]
        if not fractional:
            routes = sorted(r for r, v in live if v > 0.5)
            better = min(incumbent, (inst.cost(routes), routes), key=lambda p: p[0])
            return rest, cols, better, count + 1, False
        arc = min(fractional, key=lambda a: (abs(flows[a] - 0.5), a))
        return push(rest, children(math.ceil(value - TOL), forbidden, arc)), cols, incumbent, count + 1, False

    start = (((0, frozenset()),), [(c,) for c in inst.customers], (math.inf, None), 0, False)
    heap, _, (best_value, best_routes), nodes, _ = _unfold(step, start, lambda s: not s[0] or s[4])
    open_bounds = [b for b, _ in heap if b < best_value]
    if not open_bounds:
        return (_result("infeasible", nodes=nodes) if best_routes is None
                else _result("optimal", best_value, best_value, best_routes, nodes))
    return _result("feasible" if best_routes else "unknown", best_value if best_routes else None,
                  min(open_bounds), best_routes, nodes)


# ---------------------------------------------------------------- step 4 ---

def cpsat_model(inst):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    lit = {a: m.new_bool_var(f"x{a[0]}_{a[1]}") for a in inst.arcs()}
    m.add_multiple_circuit([(i, j, b) for (i, j), b in lit.items()])
    t = {c: m.new_int_var(max(inst.ready[c], inst.ready[0] + inst.dist[0][c]),
                          min(inst.due[c], inst.due[0] - inst.service[c] - inst.dist[c][0]), f"t{c}") for c in inst.customers}
    u = {c: m.new_int_var(inst.demand[c], inst.capacity, f"u{c}") for c in inst.customers}
    for (i, j), b in ((a, b) for a, b in lit.items() if a[0] and a[1]):
        m.add(t[j] >= t[i] + inst.service[i] + inst.dist[i][j]).only_enforce_if(b)
        m.add(u[j] >= u[i] + inst.demand[j]).only_enforce_if(b)
    m.minimize(sum(inst.dist[i][j] * b for (i, j), b in lit.items()))
    return m, lit


def add_hint(model, lit, routes):
    used = {a for r in routes for a in _path_arcs(r)}
    for a, b in lit.items():
        model.add_hint(b, a in used)
    return len(used & set(lit))


def add_nearest_strategy(model, inst, lit):
    from ortools.sat.python import cp_model
    order = sorted(lit, key=lambda a: (inst.dist[a[0]][a[1]], a))
    model.add_decision_strategy([lit[a] for a in order], cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE)
    return order


def solve_cpsat(inst, time_limit=60.0, seed=0, workers=1, hint=None, strategy="default"):
    from ortools.sat.python import cp_model
    m, lit = cpsat_model(inst)
    if hint is not None:
        add_hint(m, lit, hint)
    solver = cp_model.CpSolver()
    if strategy == "nearest":
        add_nearest_strategy(m, inst, lit)
        if workers == 1:
            solver.parameters.search_branching = cp_model.FIXED_SEARCH
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.random_seed = int(seed)
    solver.parameters.num_workers = int(workers)
    code = solver.solve(m)
    status = {cp_model.OPTIMAL: "optimal", cp_model.FEASIBLE: "feasible", cp_model.INFEASIBLE: "infeasible"}.get(code, "unknown")
    found = status in ("optimal", "feasible")
    routes = routes_from_arcs([a for a, b in lit.items() if solver.value(b)]) if found else None
    return _result(status, inst.cost(routes) if found else None,
                  math.ceil(solver.best_objective_bound - TOL) if found else None, routes, int(solver.num_branches))


# ---------------------------------------------------------------- step 5 ---

def insertion_delta(inst, route, starts, latest, pos, c):
    if sum(inst.demand[v] for v in route) + inst.demand[c] > inst.capacity:
        return None
    p, p_start = (route[pos - 1], starts[pos - 1]) if pos > 0 else (0, inst.ready[0])
    q = route[pos] if pos < len(route) else 0
    arrive = max(inst.ready[c], p_start + inst.service[p] + inst.dist[p][c])
    reach = arrive + inst.service[c] + inst.dist[c][q]
    on_time = arrive <= inst.due[c] and (reach <= inst.due[0] if q == 0 else max(inst.ready[q], reach) <= latest[pos])
    return inst.dist[p][c] + inst.dist[c][q] - inst.dist[p][q] if on_time else None


def _best_per_route(inst, routes, c):
    """[(extra distance, route index, position)]: each route's cheapest feasible position for c."""
    def best(k, r):
        starts, latest = schedule(inst, r), latest_starts(inst, r)
        options = [(d, k, pos) for pos in range(len(r) + 1)
                   if (d := insertion_delta(inst, r, starts, latest, pos, c)) is not None]
        return min(options, default=None)
    return [b for b in (best(k, r) for k, r in enumerate(routes)) if b is not None]


def shaw_removal(inst, routes, q, rng):
    start = {c: s for r in routes for c, s in zip(r, schedule(inst, r))}
    dmax = max(max(row) for row in inst.dist) or 1
    rel = lambda i, j: (inst.dist[i][j] / dmax + abs(start[i] - start[j]) / inst.due[0]
                        + abs(inst.demand[i] - inst.demand[j]) / inst.capacity)
    everyone = tuple(sorted(start))
    first = rng.choice(everyone)

    def step(state, _):
        removed, remaining = state
        if not remaining:
            return state
        anchor = rng.choice(removed)
        ranked = sorted(remaining, key=lambda j: (rel(anchor, j), j))
        k = int(rng.random() ** 6 * len(ranked))
        return removed + (ranked[k],), tuple(ranked[:k] + ranked[k + 1:])

    removed, _ = reduce(step, range(q - 1), ((first,), tuple(c for c in everyone if c != first)))
    gone = set(removed)
    return [r for r in (tuple(c for c in r if c not in gone) for r in routes) if r], list(removed)


def regret_insertion(inst, routes, removed, k=2):
    def options(routes, c):
        return sorted((*_best_per_route(inst, routes, c), (inst.dist[0][c] + inst.dist[c][0], len(routes), 0)))

    def choose(routes, todo):
        def key(c):
            opts = options(routes, c)
            regret = sum((opts[h][0] if h < len(opts) else math.inf) - opts[0][0] for h in range(1, k))
            return (regret, -opts[0][0], -c), c, opts[0]
        return max(map(key, todo), key=lambda t: t[0])

    def step(state, _):
        routes, todo = state
        _, c, (_, ri, p) = choose(routes, todo)
        rest = tuple(x for x in todo if x != c)
        if ri == len(routes):
            return routes + ((c,),), rest
        return routes[:ri] + (routes[ri][:p] + (c,) + routes[ri][p:],) + routes[ri + 1:], rest

    final, _ = reduce(step, range(len(removed)), (tuple(tuple(r) for r in routes), tuple(removed)))
    return list(final)


def alns_vrptw(inst, time_limit=60.0, seed=0, iterations=None, q_range=(0.1, 0.3)):
    from colib.ref import unit
    update_weights = unit("26").update_weights
    rng = random.Random(seed)
    n = inst.n
    t_start = time.perf_counter()
    lo, hi = max(1, int(q_range[0] * n)), max(1, int(q_range[1] * n))

    def random_removal(routes, q):
        gone = set(rng.sample(sorted(c for r in routes for c in r), q))
        return [r for r in (tuple(c for c in r if c not in gone) for r in routes) if r], sorted(gone)

    def worst_removal(routes, q):
        def step(state, _):
            partial, removed = state
            saving = lambda ri, kk: (inst.dist[_path(partial[ri])[kk]][partial[ri][kk]]
                                     + inst.dist[partial[ri][kk]][_path(partial[ri])[kk + 2]]
                                     - inst.dist[_path(partial[ri])[kk]][_path(partial[ri])[kk + 2]])
            _, negc, ri, kk = max((saving(ri, kk), -c, ri, kk) for ri, r in enumerate(partial) for kk, c in enumerate(r))
            cut = partial[ri][:kk] + partial[ri][kk + 1:]
            return [r for r in (*partial[:ri], cut, *partial[ri + 1:]) if r], removed + [-negc]
        return reduce(step, range(q), ([tuple(r) for r in routes], []))

    start = regret_insertion(inst, [], list(inst.customers), 2)
    c0 = inst.cost(start)
    T0 = 0.05 * c0 / math.log(2)

    def step(state):
        it, cur, cur_cost, best, best_cost, dw, rw, ds, rs, du, ru = state
        it += 1
        q = rng.randint(lo, hi)
        d = rng.choices(range(3), dw)[0]
        partial, removed = (random_removal(cur, q) if d == 0 else worst_removal(cur, q) if d == 1
                            else shaw_removal(inst, cur, q, rng))
        rep = rng.choices(range(3), rw)[0]
        cand = regret_insertion(inst, partial, removed, rep + 1)
        cost = inst.cost(cand)
        frac = it / iterations if iterations is not None else min(1.0, (time.perf_counter() - t_start) / time_limit)
        T = T0 * 1e-3 ** frac
        score = (33 if cost < best_cost else 9 if cost < cur_cost
                 else 13 if cost > cur_cost and rng.random() < math.exp(-(cost - cur_cost) / T) else 0)
        cur, cur_cost = (cand, cost) if cost <= cur_cost or score else (cur, cur_cost)
        best, best_cost = (cand, cost) if cost < best_cost else (best, best_cost)
        bump = lambda xs, i, v: [x + v if j == i else x for j, x in enumerate(xs)]
        ds, rs, du, ru = bump(ds, d, score), bump(rs, rep, score), bump(du, d, 1), bump(ru, rep, 1)
        if it % 100 == 0:
            return (it, cur, cur_cost, best, best_cost, update_weights(dw, ds, du, 0.1), update_weights(rw, rs, ru, 0.1),
                    [0.0] * 3, [0.0] * 3, [0] * 3, [0] * 3)
        return it, cur, cur_cost, best, best_cost, dw, rw, ds, rs, du, ru

    deadline = t_start + time_limit
    done = lambda s: (iterations is not None and s[0] >= iterations) or time.perf_counter() >= deadline
    initial = (0, start, c0, start, c0, [1.0] * 3, [1.0] * 3, [0.0] * 3, [0.0] * 3, [0] * 3, [0] * 3)
    final = _unfold(step, initial, done)
    return _result("feasible", final[4], None, sorted(final[3]), final[0])


def _path(route):
    return (0, *route, 0)


# ---------------------------------------------------------------- step 6 ---

def benchmark_solver(method, **options):
    def solve(inst, seed, timeout):
        out = method(inst, timeout, seed, **options)
        status, routes, value, nodes = out["status"], out.get("routes"), out.get("value"), out.get("nodes")
        if status in ("optimal", "feasible"):
            valid = routes is not None and not violations(inst, routes) and inst.cost(routes) == value
            return {"status": status if valid else "invalid", "value": value if valid else None, "nodes": nodes}
        return {"status": "infeasible" if status == "infeasible" else "no solution", "value": None, "nodes": nodes}
    return solve


def primal_gap(value, reference):
    if value is None or (value != reference and value * reference < 0):
        return 1.0
    return 0.0 if value == reference else abs(value - reference) / max(abs(value), abs(reference))


def references(runs):
    valid = [r for r in runs if r["status"] in ("optimal", "feasible") and r["value"] is not None]
    by_instance = tz.groupby("instance", valid)
    best = lambda rs: min(r["value"] for r in rs)
    return {i: (best(rs), any(r["status"] == "optimal" and r["value"] == best(rs) for r in rs))
            for i, rs in by_instance.items()}


def contradictions(runs):
    ref = references(runs)
    return sorted((r["instance"], r["solver"], r["seed"]) for r in runs
                  if r["status"] == "optimal" and r["value"] > ref[r["instance"]][0])


def head_to_head(runs, pairs, metric, alpha=0.05):
    from colib.ref import unit
    u28 = unit("28")
    means = tz.valmap(lambda rs: sum(map(metric, rs)) / len(rs), tz.groupby(lambda r: (r["solver"], r["instance"]), runs))

    def compare(pair):
        a, b = pair
        common = sorted({i for s, i in means if s == a} & {i for s, i in means if s == b})
        xa, xb = [means[a, i] for i in common], [means[b, i] for i in common]
        wins = sum(x < y for x, y in zip(xa, xb))
        losses = sum(x > y for x, y in zip(xa, xb))
        return {"a": a, "b": b, "n": len(common), "wins": wins, "losses": losses,
                "ties": len(common) - wins - losses, "p": u28.wilcoxon_signed_rank(xa, xb)[1]}

    rows = list(map(compare, pairs))

    def judge(row, ph):
        winner = row["a"] if row["wins"] > row["losses"] else row["b"] if row["losses"] > row["wins"] else None
        return row | {"p_holm": ph, "verdict": winner if ph < alpha and winner else "indistinguishable"}

    return [judge(row, ph) for row, ph in zip(rows, u28.holm([row["p"] for row in rows]))]
