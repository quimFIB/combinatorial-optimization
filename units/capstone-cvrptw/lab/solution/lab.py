"""Capstone lab — one problem, four traditions.  REFERENCE SOLUTION, imperative.

The problem is the VRPTW of colib.vrptw: integer data in tenths, unlimited fleet, minimise
total distance. A route is a tuple of customers; the depot is implicit at both ends. A
solution is a list of routes. Every method returns a result dict:

    {"status": "optimal" | "feasible" | "infeasible" | "unknown",
     "value": total distance or None, "bound": a proven lower bound or None,
     "routes": list of routes or None, "nodes": search nodes or None}
"""

from __future__ import annotations

import heapq
import math
import random
import time

import numpy as np

from colib.vrptw import lazy_cut_handler

TOL = 1e-6


def _result(status, value=None, bound=None, routes=None, nodes=None):
    return {"status": status, "value": value, "bound": bound, "routes": routes, "nodes": nodes}


# ---------------------------------------------------------------- step 1 ---

def schedule(inst, route):
    """Service start times along the route, waiting when early: start at the first customer is
    max(ready, ready_0 + dist from the depot), and so on. None if any start is after the customer's
    due time, if the vehicle is back at the depot after due_0, or if the load exceeds capacity."""
    if sum(inst.demand[c] for c in route) > inst.capacity:
        return None
    starts = []
    time_, last = inst.ready[0], 0
    for c in route:
        time_ = max(inst.ready[c], time_ + inst.service[last] + inst.dist[last][c])
        if time_ > inst.due[c]:
            return None
        starts.append(time_)
        last = c
    if time_ + inst.service[last] + inst.dist[last][0] > inst.due[0]:
        return None
    return starts


def latest_starts(inst, route):
    """For each position k, the latest service start at route[k] from which the rest of the route is
    still on time: min(due_k, latest_{k+1} - service_k - dist(k, k+1)), with the depot's due_0 after the
    last customer. It ignores whether the route can *reach* position k in time."""
    out = [0] * len(route)
    nxt, latest = 0, inst.due[0]
    for k in range(len(route) - 1, -1, -1):
        c = route[k]
        latest = min(inst.due[c], latest - inst.service[c] - inst.dist[c][nxt])
        out[k] = latest
        nxt = c
    return out


def violations(inst, routes):
    """Everything wrong with a claimed solution, as a sorted list of (kind, detail) pairs; empty when it's
    feasible. Kinds: "missing" (customer), "repeated" (customer served more than once), "unknown" (a
    vertex that isn't a customer), "capacity" (route index), "late" (route index: some start after its due
    time, or back after the depot closes)."""
    out = set()
    seen = {}
    for k, r in enumerate(routes):
        for c in r:
            if not (isinstance(c, int) and 1 <= c <= inst.n):
                out.add(("unknown", c))
            else:
                seen[c] = seen.get(c, 0) + 1
        good = [c for c in r if isinstance(c, int) and 1 <= c <= inst.n]
        if sum(inst.demand[c] for c in good) > inst.capacity:
            out.add(("capacity", k))
        elif schedule(inst, good) is None:
            out.add(("late", k))
    for c in inst.customers:
        if c not in seen:
            out.add(("missing", c))
        elif seen[c] > 1:
            out.add(("repeated", c))
    return sorted(out, key=lambda v: (v[0], str(v[1])))


def routes_from_arcs(arcs):
    """Routes from a set of used arcs (i, j), following each arc out of the depot until it returns.
    Routes are ordered by their first customer. Raises ValueError if some arc isn't on a depot route (a
    subtour) or a vertex is left twice."""
    succ = {}
    for i, j in arcs:
        if i in succ and i != 0:
            raise ValueError(f"vertex {i} is left twice")
        succ.setdefault(i, []).append(j)
    routes, used = [], 0
    for first in sorted(succ.get(0, [])):
        route, v = [], first
        while v != 0:
            if v in route or v not in succ:
                raise ValueError(f"route from {first} never returns to the depot")
            route.append(v)
            v = succ[v][0]
        routes.append(tuple(route))
        used += len(route) + 1
    if used != len(arcs):
        raise ValueError("some arcs form a subtour away from the depot")
    return routes


# ---------------------------------------------------------------- step 2 ---

def rounded_capacity_cuts(inst, x, eps=1e-6):
    """Violated rounded capacity inequalities  x(δ⁻(S)) ≥ ⌈q(S)/Q⌉  for customer sets S.
    x is {arc: value}. The candidate sets S are the connected components of the customer support graph:
    customers joined by an arc between them with value > eps, ignoring direction. (Stronger separators
    also try unions of components and shrink the graph; components alone already enforce capacity on
    integer solutions, because there the components are the routes.) Returns a list of
    (sorted tuple S, list of the arcs of x entering S, rhs), ordered by smallest customer, for the
    components whose inflow is below rhs − eps."""
    n = inst.n
    parent = list(range(n + 1))

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for (i, j), v in x.items():
        if i and j and v > eps:
            parent[find(i)] = find(j)
    comps = {}
    for c in inst.customers:
        comps.setdefault(find(c), []).append(c)
    cuts = []
    for S in comps.values():
        members = set(S)
        entering = [a for a in x if a[1] in members and a[0] not in members]
        rhs = math.ceil(sum(inst.demand[c] for c in S) / inst.capacity)
        if sum(x[a] for a in entering) < rhs - eps:
            cuts.append((tuple(sorted(S)), entering, rhs))
    return cuts


def solve_mip(inst, time_limit=60.0, seed=0, cuts=True):
    """Branch-and-cut on SCIP. Binary x_ij over inst.arcs(), continuous service starts t_i in
    [ready_i, due_i]; each customer entered once and left once; time propagation
    t_j ≥ t_i + s_i + d_ij − M_ij (1 − x_ij) between customers, with M_ij = max(0, due_i + s_i + d_ij −
    ready_j); t_j ≥ d_0j for depot arcs out and t_j + s_j + d_j0 ≤ due_0 for depot arcs in (as bounds).
    Capacity isn't in the model: rounded_capacity_cuts, attached with colib.vrptw.lazy_cut_handler,
    enforces it on integer solutions and (when cuts=True) also separates at fractional LP solutions.
    Returns a result dict with SCIP's nodes."""
    from pyscipopt import Model, quicksum
    m = Model()
    m.hideOutput()
    m.setParam("limits/time", float(time_limit))
    m.setParam("randomization/randomseedshift", int(seed))
    arcs = inst.arcs()
    x = {(i, j): m.addVar(vtype="B", obj=inst.dist[i][j]) for i, j in arcs}
    t = {}
    for c in inst.customers:
        lo = max(inst.ready[c], inst.ready[0] + inst.dist[0][c])
        hi = min(inst.due[c], inst.due[0] - inst.service[c] - inst.dist[c][0])
        t[c] = m.addVar(lb=lo, ub=hi)
    for c in inst.customers:
        m.addCons(quicksum(x[a] for a in arcs if a[0] == c) == 1)
        m.addCons(quicksum(x[a] for a in arcs if a[1] == c) == 1)
    for i, j in arcs:
        if i and j:
            M = max(0, inst.due[i] + inst.service[i] + inst.dist[i][j] - inst.ready[j])
            m.addCons(t[j] >= t[i] + inst.service[i] + inst.dist[i][j] - M * (1 - x[i, j]))

    def separate(values):
        found = rounded_capacity_cuts(inst, values)
        if not cuts and any(abs(v - round(v)) > TOL for v in values.values()):
            return []
        return [(entering, rhs) for _, entering, rhs in found]

    handler = lazy_cut_handler(m, x, separate)
    m.setMinimize()
    m.optimize()
    status = m.getStatus()
    routes = None
    if m.getNSols() > 0:
        best = m.getBestSol()
        routes = routes_from_arcs([a for a in arcs if m.getSolVal(best, x[a]) > 0.5])
    value = inst.cost(routes) if routes is not None else None
    st = "optimal" if status == "optimal" else "infeasible" if status == "infeasible" else \
        "feasible" if routes is not None else "unknown"
    bound = m.getDualbound()
    return _result(st, value, math.ceil(bound - TOL) if math.isfinite(bound) else None, routes,
                  int(m.getNTotalNodes())) | {"cuts": handler.added}


# ---------------------------------------------------------------- step 3 ---

def price(inst, duals, allowed, max_columns=30, label_limit=None):
    """Elementary shortest paths with capacity and time windows, by labelling with dominance.

    duals[c] for customers (duals[0] is ignored); allowed is {i: iterable of successors j} (the arcs
    branching hasn't forbidden). A route's reduced cost is its distance minus the duals of its customers.
    A label at vertex v holds (reduced cost, load, service start at v, a bitmask of customers it can no
    longer visit, the route). A customer can no longer be visited if it's on the route, doesn't fit the
    load, or can't be reached before its due time (Feillet et al. 2004). Label L dominates L' at the same
    vertex when cost, load and time are all <= and L's mask is a subset of L''s; drop dominated labels.
    Any order of extension reaches the same non-dominated labels; increasing time is a good one. With
    label_limit=k keep only the k cheapest labels per vertex: a heuristic that can miss columns.
    Returns up to max_columns (reduced cost, route) pairs with reduced cost < -1e-6, most negative
    first, ties by route."""
    n = inst.n
    dist, ready, due, service, demand, Q = inst.dist, inst.ready, inst.due, inst.service, inst.demand, inst.capacity
    succ = {i: [j for j in allowed.get(i, ()) if j != i] for i in range(n + 1)}
    home_ok = {i: 0 in succ[i] for i in inst.customers}

    def unreachable(v, t, load, mask):
        for w in succ_all:
            if not mask >> w & 1:
                if load + demand[w] > Q or max(ready[w], t + service[v] + dist[v][w]) > due[w]:
                    mask |= 1 << w
        return mask

    succ_all = list(inst.customers)
    bucket = {v: [] for v in inst.customers}
    heap, counter = [], 0
    for j in succ[0]:
        if j == 0:
            continue
        t = max(ready[j], ready[0] + dist[0][j])
        if t > due[j] or demand[j] > Q:
            continue
        mask = unreachable(j, t, demand[j], 1 << j)
        lab = [dist[0][j] - duals[j], demand[j], t, mask, (j,), True]
        bucket[j].append(lab)
        heapq.heappush(heap, (t, counter, j, lab))
        counter += 1
    found = []
    while heap:
        _, _, v, lab = heapq.heappop(heap)
        if not lab[5]:
            continue
        rc, load, t, mask, route, _ = lab
        if home_ok[v] and t + service[v] + dist[v][0] <= due[0]:
            total = rc + dist[v][0]
            if total < -1e-6:
                found.append((total, route))
        for w in succ[v]:
            if w == 0 or mask >> w & 1:
                continue
            tw = max(ready[w], t + service[v] + dist[v][w])
            new = [rc + dist[v][w] - duals[w], load + demand[w], tw, 0, route + (w,), True]
            new[3] = unreachable(w, tw, new[1], mask | 1 << w)
            dominated = False
            for o in bucket[w]:
                if o[0] <= new[0] + 1e-9 and o[1] <= new[1] and o[2] <= new[2] and o[3] & new[3] == o[3]:
                    dominated = True
                    break
            if dominated:
                continue
            keep = []
            for o in bucket[w]:
                if new[0] <= o[0] + 1e-9 and new[1] <= o[1] and new[2] <= o[2] and new[3] & o[3] == new[3]:
                    o[5] = False
                else:
                    keep.append(o)
            keep.append(new)
            if label_limit is not None and len(keep) > label_limit:
                keep.sort(key=lambda o: o[0])
                for o in keep[label_limit:]:
                    o[5] = False
                keep = keep[:label_limit]
                if not new[5]:
                    bucket[w] = keep
                    continue
            bucket[w] = keep
            heapq.heappush(heap, (tw, counter, w, new))
            counter += 1
    found.sort()
    out, seen = [], set()
    for rc, r in found:
        if r not in seen:
            seen.add(r)
            out.append((rc, r))
            if len(out) == max_columns:
                break
    return out


def arc_flows(columns, lam):
    """{arc: total λ of the columns using it}, depot arcs included, for columns with λ > 1e-9."""
    flow = {}
    for r, v in zip(columns, lam):
        if v > 1e-9:
            path = (0, *r, 0)
            for a in zip(path, path[1:]):
                flow[a] = flow.get(a, 0.0) + v
    return flow


def _route_allowed(route, forbidden):
    path = (0, *route, 0)
    return not any(a in forbidden for a in zip(path, path[1:]))


def column_generation(inst, columns, forbidden, deadline=math.inf):
    """The set-partitioning LP  min Σ c_r λ_r, Σ_r [c ∈ r] λ_r = 1 for every customer, λ ≥ 0,  over
    routes avoiding the forbidden arcs, by column generation. Start from the given columns that avoid
    them, plus one artificial column per customer with a prohibitive cost so the LP is always feasible.
    Price heuristically (label_limit=8) first and exactly when that finds nothing. Stops early at the
    deadline (time.perf_counter()). Returns (LP value, columns, λ, converged): value is None if the
    converged LP still uses an artificial column (no feasible routing on this node)."""
    import highspy
    n = inst.n
    big = 2 * sum(max(row) for row in inst.dist) + 1
    cols = [r for r in dict.fromkeys(columns) if _route_allowed(r, forbidden)]
    allowed = {i: [j for j in range(n + 1) if (i, j) not in forbidden and inst.arc_possible(i, j)]
               for i in range(n + 1)}
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    h.addRows(n, np.ones(n), np.ones(n), 0, np.array([0], np.int32), np.array([], np.int32), np.array([]))

    def add(route, cost):
        rows = sorted(c - 1 for c in set(route))
        h.addCol(float(cost), 0.0, inf, len(rows), np.array(rows, np.int32), np.ones(len(rows)))

    for c in inst.customers:
        add((c,), big)
    for r in cols:
        add(r, inst.route_cost(r))
    converged = False
    while True:
        h.run()
        duals = [0.0] + list(h.getSolution().row_dual)
        if time.perf_counter() > deadline:
            break
        new = price(inst, duals, allowed, label_limit=8)
        if not new:
            if time.perf_counter() > deadline:
                break
            new = price(inst, duals, allowed)
        new = [r for _, r in new if r not in set(cols)]
        if not new:
            converged = True
            break
        for r in new:
            cols.append(r)
            add(r, inst.route_cost(r))
    sol = list(h.getSolution().col_value)
    value = h.getInfo().objective_function_value
    if any(v > 1e-6 for v in sol[:n]):
        return None, cols, sol[n:], converged
    return value, cols, sol[n:], converged



def restricted_master_ip(inst, columns, time_limit):
    """A primal heuristic: the set-partitioning IP over the given columns only, solved with
    colib.mip.highs_mip within time_limit seconds. Returns (cost, routes) of the best solution found, or None if there is none
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
    """Best-first branch-and-price. At each node, column_generation over the node's forbidden arcs;
    prune the node if its bound ⌈LP − 1e-6⌉ can't beat the incumbent (distances are integers). If the
    arc flows are all integral, the columns with λ > 0.5 are a solution. Otherwise branch on the arc
    whose flow is closest to 0.5 (ties: smallest arc): one child forbids it; the other forces it by
    forbidding every other arc out of i (if i is a customer) and into j (if j is a customer). Columns
    are shared by all nodes. After the root's column generation converges, restricted_master_ip over the
    columns so far (with a quarter of the remaining time, at most 10 s) supplies a first incumbent.
    seed is unused (the method is deterministic). Returns a result dict; the bound is the smallest bound
    over open nodes, or the value when the tree is exhausted."""
    deadline = time.perf_counter() + time_limit
    columns = [(c,) for c in inst.customers]
    best_value, best_routes = math.inf, None
    heap = [(0, 0, frozenset())]
    counter, nodes = 1, 0
    open_bound = 0
    while heap:
        node_bound, _, forbidden = heapq.heappop(heap)
        if node_bound >= best_value:
            continue
        if time.perf_counter() > deadline:
            heapq.heappush(heap, (node_bound, 0, forbidden))
            break
        nodes += 1
        value, columns, lam, converged = column_generation(inst, columns, forbidden, deadline)
        if not converged:
            heapq.heappush(heap, (node_bound, 0, forbidden))
            break
        if value is None:
            continue
        if nodes == 1:
            found = restricted_master_ip(inst, columns, min(10.0, (deadline - time.perf_counter()) / 4))
            if found is not None and found[0] < best_value:
                best_value, best_routes = found
        bound = math.ceil(value - TOL)
        if bound >= best_value:
            continue
        live = [(r, v) for r, v in zip(columns, lam) if v > 1e-9]
        flows = arc_flows([r for r, _ in live], [v for _, v in live])
        fractional = [a for a, f in flows.items() if TOL < f < 1 - TOL]
        if not fractional:
            routes = sorted(r for r, v in live if v > 0.5)
            cost = inst.cost(routes)
            if cost < best_value:
                best_value, best_routes = cost, routes
            continue
        i, j = min(fractional, key=lambda a: (abs(flows[a] - 0.5), a))
        heapq.heappush(heap, (bound, counter, forbidden | {(i, j)}))
        force = set()
        if i:
            force |= {(i, k) for k in range(inst.n + 1) if k != j}
        if j:
            force |= {(k, j) for k in range(inst.n + 1) if k != i}
        heapq.heappush(heap, (bound, counter + 1, forbidden | force))
        counter += 2
    open_bounds = [b for b, _, _ in heap if b < best_value]
    if not open_bounds:
        if best_routes is None:
            return _result("infeasible", nodes=nodes)
        return _result("optimal", best_value, best_value, best_routes, nodes)
    bound = min(open_bounds)
    return _result("feasible" if best_routes else "unknown", best_value if best_routes else None, bound,
                  best_routes, nodes)


# ---------------------------------------------------------------- step 4 ---

def cpsat_model(inst):
    """The CP-SAT model. One Boolean per arc of inst.arcs(), tied together by add_multiple_circuit
    (vertex 0 is the depot, every customer is on exactly one circuit through it). Integer service starts
    t_c in [max(ready_c, ready_0 + d_0c), min(due_c, due_0 − s_c − d_c0)] and loads u_c in [demand_c, Q].
    For each arc i → j between customers, when its literal is true:
    t_j ≥ t_i + s_i + d_ij and u_j ≥ u_i + demand_j. Objective: minimise the distance of the chosen arcs.
    Returns (model, {arc: literal})."""
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    arcs = inst.arcs()
    lit = {a: m.new_bool_var(f"x{a[0]}_{a[1]}") for a in arcs}
    m.add_multiple_circuit([(i, j, lit[i, j]) for i, j in arcs])
    t, u = {}, {}
    for c in inst.customers:
        lo = max(inst.ready[c], inst.ready[0] + inst.dist[0][c])
        hi = min(inst.due[c], inst.due[0] - inst.service[c] - inst.dist[c][0])
        t[c] = m.new_int_var(lo, hi, f"t{c}")
        u[c] = m.new_int_var(inst.demand[c], inst.capacity, f"u{c}")
    for (i, j), b in lit.items():
        if i and j:
            m.add(t[j] >= t[i] + inst.service[i] + inst.dist[i][j]).only_enforce_if(b)
            m.add(u[j] >= u[i] + inst.demand[j]).only_enforce_if(b)
    m.minimize(sum(inst.dist[i][j] * b for (i, j), b in lit.items()))
    return m, lit


def add_hint(model, lit, routes):
    """Hint a complete solution: every arc literal gets 1 if the arc is used by `routes`, else 0.
    Returns the number of hinted literals set to 1."""
    used = set()
    for r in routes:
        path = (0, *r, 0)
        used |= set(zip(path, path[1:]))
    for a, b in lit.items():
        model.add_hint(b, a in used)
    return sum(1 for a in lit if a in used)


def add_nearest_strategy(model, inst, lit):
    """A search strategy: branch first on arc literals in increasing order of distance (ties: arc),
    trying value 1 (use the short arc) first. Returns the ordered list of arcs."""
    from ortools.sat.python import cp_model
    order = sorted(lit, key=lambda a: (inst.dist[a[0]][a[1]], a))
    model.add_decision_strategy([lit[a] for a in order], cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE)
    return order


def solve_cpsat(inst, time_limit=60.0, seed=0, workers=1, hint=None, strategy="default"):
    """Build cpsat_model, optionally add_hint(hint) and, for strategy="nearest", add_nearest_strategy
    with parameters search_branching = FIXED_SEARCH when workers == 1 (with more workers the portfolio
    keeps one worker on it). Solve with the given time limit, random_seed and num_workers. Returns a result
    dict: status "optimal" / "feasible" / "infeasible" / "unknown", value and routes from the best
    solution, bound = ⌈best objective bound⌉, nodes = number of branches."""
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
    status = {cp_model.OPTIMAL: "optimal", cp_model.FEASIBLE: "feasible",
              cp_model.INFEASIBLE: "infeasible"}.get(code, "unknown")
    routes = value = None
    if status in ("optimal", "feasible"):
        routes = routes_from_arcs([a for a, b in lit.items() if solver.value(b)])
        value = inst.cost(routes)
    bound = math.ceil(solver.best_objective_bound - TOL) if status in ("optimal", "feasible") else None
    return _result(status, value, bound, routes, int(solver.num_branches))


# ---------------------------------------------------------------- step 5 ---

def insertion_delta(inst, route, starts, latest, pos, c):
    """Extra distance of inserting customer c into route before position pos (0: first, len(route): last),
    or None if that's infeasible. starts = schedule(inst, route), latest = latest_starts(inst, route).
    Constant time apart from the load: c's start is max(ready_c, previous start + service + travel);
    it must be <= due_c, and the pushed start at the next customer must stay <= its latest start (or
    the vehicle must be back by due_0 when c is last)."""
    if sum(inst.demand[v] for v in route) + inst.demand[c] > inst.capacity:
        return None
    p = route[pos - 1] if pos > 0 else 0
    p_start = starts[pos - 1] if pos > 0 else inst.ready[0]
    arrive = max(inst.ready[c], p_start + inst.service[p] + inst.dist[p][c])
    if arrive > inst.due[c]:
        return None
    q = route[pos] if pos < len(route) else 0
    reach = arrive + inst.service[c] + inst.dist[c][q]
    if q == 0:
        if reach > inst.due[0]:
            return None
    elif max(inst.ready[q], reach) > latest[pos]:
        return None
    return inst.dist[p][c] + inst.dist[c][q] - inst.dist[p][q]


def _positions(inst, routes, c):
    """[(extra distance, route index, position)] over every feasible insertion of c, sorted."""
    out = []
    for k, r in enumerate(routes):
        starts, latest = schedule(inst, r), latest_starts(inst, r)
        for pos in range(len(r) + 1):
            d = insertion_delta(inst, r, starts, latest, pos, c)
            if d is not None:
                out.append((d, k, pos))
    out.sort()
    return out


def shaw_removal(inst, routes, q, rng):
    """Remove q related customers (Shaw 1998; Ropke & Pisinger 2006). Relatedness of i and j:
    dist_ij / max distance + |start_i − start_j| / due_0 + |demand_i − demand_j| / capacity, smaller is
    more related, with starts from schedule(). Start from rng.choice(sorted customers); then repeatedly
    pick a removed customer with rng.choice(removed), sort the remaining customers by relatedness to it
    (ties: customer number), and remove the one at index floor(rng.random() ** 6 * len(remaining)).
    Returns (routes without them, empty routes dropped; removed customers in removal order)."""
    start = {}
    for r in routes:
        for c, s in zip(r, schedule(inst, r)):
            start[c] = s
    dmax = max(max(row) for row in inst.dist) or 1
    rel = lambda i, j: (inst.dist[i][j] / dmax + abs(start[i] - start[j]) / inst.due[0]
                        + abs(inst.demand[i] - inst.demand[j]) / inst.capacity)
    remaining = sorted(start)
    removed = [rng.choice(remaining)]
    remaining.remove(removed[0])
    while len(removed) < q and remaining:
        anchor = rng.choice(removed)
        remaining.sort(key=lambda j: (rel(anchor, j), j))
        pick = remaining.pop(int(rng.random() ** 6 * len(remaining)))
        removed.append(pick)
    gone = set(removed)
    kept = [tuple(c for c in r if c not in gone) for r in routes]
    return [r for r in kept if r], removed


def regret_insertion(inst, routes, removed, k=2):
    """Regret-k repair. Repeatedly, over the customers still to insert, list each one's options: its best
    feasible position in each existing route, plus a new route of its own, which costs d_0c + d_c0 and
    counts as one more "route". Its regret is the sum over h = 2..k of (h-th best extra distance − best
    extra distance), with a missing h-th option counting as infinitely bad. Insert the customer with the
    largest regret at its best option (ties: smaller best extra distance, then smaller customer number;
    between options of equal cost, an existing route before a new one, then earlier route and position).
    k=1 is plain greedy: the cheapest insertion first. New routes are appended at the end. Returns the
    new list of routes (tuples)."""
    routes = [tuple(r) for r in routes]
    todo = list(removed)
    while todo:
        best = None
        for c in todo:
            options, seen = [], set()
            for d, ri, p in _positions(inst, routes, c):
                if ri not in seen:
                    seen.add(ri)
                    options.append((d, ri, p))
            options.append((inst.dist[0][c] + inst.dist[c][0], len(routes), 0))
            options.sort()
            regret = sum((options[h][0] if h < len(options) else math.inf) - options[0][0] for h in range(1, k))
            key = (regret, -options[0][0], -c)
            if best is None or key > best[0]:
                best = (key, c, options[0])
        _, c, (_, ri, p) = best
        todo.remove(c)
        if ri == len(routes):
            routes.append((c,))
        else:
            r = routes[ri]
            routes[ri] = r[:p] + (c,) + r[p:]
    return routes


def alns_vrptw(inst, time_limit=60.0, seed=0, iterations=None, q_range=(0.1, 0.3)):
    """ALNS (Ropke & Pisinger 2006) until time_limit seconds or `iterations` iterations, whichever
    comes first. rng = random.Random(seed). Start: regret_insertion(k=2) of all customers into no routes.
    Each iteration: q = rng.randint(max(1, ⌊q_range[0]·n⌋), max(1, ⌊q_range[1]·n⌋)); destroy with
    rng.choices over three operators by weight (random removal of rng.sample(sorted customers, q), worst
    removal of the q customers with the largest saving, shaw_removal), repair with rng.choices over
    regret k = 1, 2, 3 by weight. Accept by simulated annealing: always if not worse, else with probability
    exp(−Δ / T); T starts where a 5% worse solution is accepted with probability 0.5 and falls
    geometrically to 1/1000 of that over the run. Scores 33 / 9 / 13 (new best / improved / accepted),
    unit 26's update_weights with reaction 0.1 every 100 iterations. Returns a result dict with status
    "feasible", no bound, and nodes = iterations performed."""
    from colib.ref import unit
    update_weights = unit("26").update_weights
    rng = random.Random(seed)
    n = inst.n
    deadline = time.perf_counter() + time_limit
    t_start = time.perf_counter()
    current = regret_insertion(inst, [], list(inst.customers), 2)
    cur_cost = inst.cost(current)
    best, best_cost = current, cur_cost
    T0 = 0.05 * cur_cost / math.log(2)
    lo, hi = max(1, int(q_range[0] * n)), max(1, int(q_range[1] * n))
    dw, rw = [1.0] * 3, [1.0] * 3
    ds, rs, du, ru = [0.0] * 3, [0.0] * 3, [0] * 3, [0] * 3
    it = 0
    while (iterations is None or it < iterations) and time.perf_counter() < deadline:
        it += 1
        q = rng.randint(lo, hi)
        d = rng.choices(range(3), dw)[0]
        if d == 0:
            gone = set(rng.sample(sorted(c for r in current for c in r), q))
            partial = [r for r in (tuple(c for c in r if c not in gone) for r in current) if r]
            removed = sorted(gone)
        elif d == 1:
            partial, removed = [tuple(r) for r in current], []
            for _ in range(q):
                cand = []
                for ri, r in enumerate(partial):
                    path = (0, *r, 0)
                    for kk, c in enumerate(r):
                        cand.append((inst.dist[path[kk]][c] + inst.dist[c][path[kk + 2]] - inst.dist[path[kk]][path[kk + 2]], -c, ri, kk))
                _, negc, ri, kk = max(cand)
                removed.append(-negc)
                partial[ri] = partial[ri][:kk] + partial[ri][kk + 1:]
                partial = [r for r in partial if r]
        else:
            partial, removed = shaw_removal(inst, current, q, rng)
        rep = rng.choices(range(3), rw)[0]
        cand = regret_insertion(inst, partial, removed, rep + 1)
        cost = inst.cost(cand)
        du[d] += 1
        ru[rep] += 1
        if iterations is not None:
            frac = it / iterations
        else:
            frac = min(1.0, (time.perf_counter() - t_start) / time_limit)
        T = T0 * 1e-3 ** frac
        score = 0
        if cost < best_cost:
            score = 33
        elif cost < cur_cost:
            score = 9
        elif cost > cur_cost and rng.random() < math.exp(-(cost - cur_cost) / T):
            score = 13
        if cost <= cur_cost or score:
            current, cur_cost = cand, cost
        if cost < best_cost:
            best, best_cost = cand, cost
        ds[d] += score
        rs[rep] += score
        if it % 100 == 0:
            dw, rw = update_weights(dw, ds, du, 0.1), update_weights(rw, rs, ru, 0.1)
            ds, rs, du, ru = [0.0] * 3, [0.0] * 3, [0] * 3, [0] * 3
    return _result("feasible", best_cost, None, sorted(best), it)


# ---------------------------------------------------------------- step 6 ---

def benchmark_solver(method, **options):
    """Adapt a method (inst, time_limit, seed, **options) -> result dict into a solver for unit 28's
    run_benchmark: a function (inst, seed, timeout) -> {"status", "value", "nodes"}. The adapter trusts
    nothing: if the routes fail violations() or their cost isn't the claimed value, the status is
    "invalid" and the value None. A method's "infeasible" is passed through, "unknown" becomes
    "no solution", and "optimal" / "feasible" keep their status."""
    def solve(inst, seed, timeout):
        out = method(inst, timeout, seed, **options)
        status, routes, value = out["status"], out.get("routes"), out.get("value")
        if status in ("optimal", "feasible"):
            if routes is None or violations(inst, routes) or inst.cost(routes) != value:
                return {"status": "invalid", "value": None, "nodes": out.get("nodes")}
            return {"status": status, "value": value, "nodes": out.get("nodes")}
        return {"status": "infeasible" if status == "infeasible" else "no solution", "value": None,
                "nodes": out.get("nodes")}
    return solve


def primal_gap(value, reference):
    """Berthold's primal gap in [0, 1]: 0 if value == reference; 1 if there is no value (None) or the two
    have opposite signs; otherwise |value − reference| / max(|value|, |reference|)."""
    if value is None:
        return 1.0
    if value == reference:
        return 0.0
    if value * reference < 0:
        return 1.0
    return abs(value - reference) / max(abs(value), abs(reference))


def references(runs):
    """{instance: (best value over runs with status "optimal" or "feasible", proven)} where proven is True
    if some run with that best value has status "optimal". Instances with no such run are absent."""
    best = {}
    for r in runs:
        if r["status"] in ("optimal", "feasible") and r["value"] is not None:
            v, proven = best.get(r["instance"], (math.inf, False))
            if r["value"] < v:
                best[r["instance"]] = (r["value"], r["status"] == "optimal")
            elif r["value"] == v and r["status"] == "optimal":
                best[r["instance"]] = (v, True)
    return best


def contradictions(runs):
    """Runs whose claim is refuted by another run: status "optimal" with a value larger than some other
    run's valid ("optimal" or "feasible") value on the same instance. Returns sorted (instance, solver,
    seed) triples."""
    ref = references(runs)
    return sorted((r["instance"], r["solver"], r["seed"]) for r in runs
                  if r["status"] == "optimal" and r["value"] > ref[r["instance"]][0])


def head_to_head(runs, pairs, metric, alpha=0.05):
    """For each (a, b) in pairs: over the instances both solvers ran, the per-instance metric(run) averaged
    over seeds; wins = instances where a's mean is smaller, losses = where b's is, ties the rest; p from unit
    28's wilcoxon_signed_rank on the paired means; p_holm from unit 28's holm over all pairs. The verdict is
    a if p_holm < alpha and wins > losses, b if p_holm < alpha and losses > wins, else "indistinguishable".
    Returns a list of dicts with keys a, b, n, wins, losses, ties, p, p_holm, verdict, in pair order."""
    from colib.ref import unit
    u28 = unit("28")
    means = {}
    for r in runs:
        means.setdefault((r["solver"], r["instance"]), []).append(metric(r))
    rows = []
    for a, b in pairs:
        common = sorted({i for s, i in means if s == a} & {i for s, i in means if s == b})
        xa = [sum(means[a, i]) / len(means[a, i]) for i in common]
        xb = [sum(means[b, i]) / len(means[b, i]) for i in common]
        wins = sum(1 for x, y in zip(xa, xb) if x < y)
        losses = sum(1 for x, y in zip(xa, xb) if x > y)
        rows.append({"a": a, "b": b, "n": len(common), "wins": wins, "losses": losses,
                     "ties": len(common) - wins - losses, "p": u28.wilcoxon_signed_rank(xa, xb)[1]})
    for row, ph in zip(rows, u28.holm([row["p"] for row in rows])):
        row["p_holm"] = ph
        row["verdict"] = (row["a"] if row["wins"] > row["losses"] else row["b"] if row["losses"] > row["wins"]
                          else "indistinguishable") if ph < alpha else "indistinguishable"
    return rows
