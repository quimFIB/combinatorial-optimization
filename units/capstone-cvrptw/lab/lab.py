"""Capstone lab — one problem, four traditions.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test capstone
after each. Read README.md first; HINTS.org has a ladder of hints per step.

The problem is the VRPTW of colib.vrptw: integer data in tenths, unlimited fleet, minimise total distance.
A route is a tuple of customers; the depot is implicit at both ends. A solution is a list of routes. Every
method returns a result dict (build it with _result):

    {"status": "optimal" | "feasible" | "infeasible" | "unknown",
     "value": total distance or None, "bound": a proven lower bound or None,
     "routes": list of routes or None, "nodes": search nodes or None}

Useful from colib.vrptw.VRPTW: inst.n, inst.customers, inst.dist, inst.demand, inst.ready, inst.due,
inst.service, inst.capacity, inst.arcs(), inst.arc_possible(i, j), inst.route_cost(route), inst.cost(routes).
Customer i's time window [a_i, b_i] is [inst.ready[i], inst.due[i]], its service time s_i is inst.service[i],
its demand q_i is inst.demand[i], and d_ij is inst.dist[i][j].
"""

from __future__ import annotations

import heapq
import math
import random
import time

import numpy as np

from colib.vrptw import VRPTW, lazy_cut_handler

TOL = 1e-6

def _result(status, value=None, bound=None, routes=None, nodes=None):
    return {"status": status, "value": value, "bound": bound, "routes": routes, "nodes": nodes}


# ---------------------------------------------------------------- step 1 ---

def schedule(inst: VRPTW, route):
    """Service start times along the route, waiting when early: start at the first customer is
    max(ready, ready_0 + dist from the depot), and so on. None if any start is after the customer's
    due time, if the vehicle is back at the depot after due_0, or if the load exceeds capacity."""
    raise NotImplementedError  # TODO step 1


def latest_starts(inst: VRPTW, route):
    """For each position k, the latest service start at route[k] from which the rest of the route is
    still on time: min(due_k, latest_{k+1} - service_k - dist(k, k+1)), with the depot's due_0 after the
    last customer. It ignores whether the route can *reach* position k in time."""
    raise NotImplementedError  # TODO step 1


def violations(inst: VRPTW, routes):
    """Everything wrong with a claimed solution, as a sorted list of (kind, detail) pairs; empty when it's
    feasible. Kinds: "missing" (customer), "repeated" (customer served more than once), "unknown" (a
    vertex that isn't a customer), "capacity" (route index), "late" (route index: some start after its due
    time, or back after the depot closes)."""
    raise NotImplementedError  # TODO step 1


def routes_from_arcs(arcs):
    """Routes from a set of used arcs (i, j), following each arc out of the depot until it returns.
    Routes are ordered by their first customer. Raises ValueError if some arc isn't on a depot route (a
    subtour) or a vertex is left twice."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def rounded_capacity_cuts(inst: VRPTW, x, eps=1e-6):
    """Violated rounded capacity inequalities  x(δ⁻(S)) ≥ ⌈q(S)/Q⌉  for customer sets S.
    x is {arc: value}. The candidate sets S are the connected components of the customer support graph:
    customers joined by an arc between them with value > eps, ignoring direction. (Stronger separators
    also try unions of components and shrink the graph; components alone already enforce capacity on
    integer solutions, because there the components are the routes.) Returns a list of
    (sorted tuple S, list of the arcs of x entering S, rhs), ordered by smallest customer, for the
    components whose inflow is below rhs − eps."""
    raise NotImplementedError  # TODO step 2


def solve_mip(inst: VRPTW, time_limit=60.0, seed=0, cuts=True):
    """Branch-and-cut on SCIP. Binary x_ij over inst.arcs(), continuous service starts t_i in
    [ready_i, due_i]; each customer entered once and left once; time propagation
    t_j ≥ t_i + s_i + d_ij − M_ij (1 − x_ij) between customers, with M_ij = max(0, due_i + s_i + d_ij −
    ready_j); t_j ≥ d_0j for depot arcs out and t_j + s_j + d_j0 ≤ due_0 for depot arcs in (as bounds).
    Capacity isn't in the model: rounded_capacity_cuts, attached with colib.vrptw.lazy_cut_handler,
    enforces it on integer solutions and (when cuts=True) also separates at fractional LP solutions.
    Returns a result dict with SCIP's nodes."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def price(inst: VRPTW, duals, allowed, max_columns=30, label_limit=None):
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
    raise NotImplementedError  # TODO step 3


def arc_flows(columns, lam):
    """{arc: total λ of the columns using it}, depot arcs included, for columns with λ > 1e-9."""
    raise NotImplementedError  # TODO step 3


def _route_allowed(route, forbidden):
    path = (0, *route, 0)
    return not any(a in forbidden for a in zip(path, path[1:]))


def column_generation(inst: VRPTW, columns, forbidden, deadline=math.inf):
    """The set-partitioning LP  min Σ c_r λ_r, Σ_r [c ∈ r] λ_r = 1 for every customer, λ ≥ 0,  over
    routes avoiding the forbidden arcs, by column generation. Start from the given columns that avoid
    them, plus one artificial column per customer with a prohibitive cost so the LP is always feasible.
    Price heuristically (label_limit=8) first and exactly when that finds nothing. Stops early at the
    deadline (time.perf_counter()). Returns (LP value, columns, λ, converged): value is None if the
    converged LP still uses an artificial column (no feasible routing on this node)."""
    raise NotImplementedError  # TODO step 3


def restricted_master_ip(inst: VRPTW, columns, time_limit):
    """A primal heuristic: the set-partitioning IP over the given columns only, solved with
    colib.mip.highs_mip within time_limit seconds. Returns (cost, routes) of the best solution found, or None if there is none
    (HiGHS can return a vector at its time limit that isn't a solution, so check it with violations)."""
    raise NotImplementedError  # TODO step 3


def branch_and_price(inst: VRPTW, time_limit=60.0, seed=0):
    """Best-first branch-and-price. At each node, column_generation over the node's forbidden arcs;
    prune the node if its bound ⌈LP − 1e-6⌉ can't beat the incumbent (distances are integers). If the
    arc flows are all integral, the columns with λ > 0.5 are a solution. Otherwise branch on the arc
    whose flow is closest to 0.5 (ties: smallest arc): one child forbids it; the other forces it by
    forbidding every other arc out of i (if i is a customer) and into j (if j is a customer). Columns
    are shared by all nodes. After the root's column generation converges, restricted_master_ip over the
    columns so far (with a quarter of the remaining time, at most 10 s) supplies a first incumbent.
    seed is unused (the method is deterministic). Returns a result dict; the bound is the smallest bound
    over open nodes, or the value when the tree is exhausted."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def cpsat_model(inst: VRPTW):
    """The CP-SAT model. One Boolean per arc of inst.arcs(), tied together by add_multiple_circuit
    (vertex 0 is the depot, every customer is on exactly one circuit through it). Integer service starts
    t_c in [max(ready_c, ready_0 + d_0c), min(due_c, due_0 − s_c − d_c0)] and loads u_c in [demand_c, Q].
    For each arc i → j between customers, when its literal is true:
    t_j ≥ t_i + s_i + d_ij and u_j ≥ u_i + demand_j. Objective: minimise the distance of the chosen arcs.
    Returns (model, {arc: literal})."""
    raise NotImplementedError  # TODO step 4


def add_hint(model, lit, routes):
    """Hint a complete solution: every arc literal gets 1 if the arc is used by `routes`, else 0.
    Returns the number of hinted literals set to 1."""
    raise NotImplementedError  # TODO step 4


def add_nearest_strategy(model, inst: VRPTW, lit):
    """A search strategy: branch first on arc literals in increasing order of distance (ties: arc),
    trying value 1 (use the short arc) first. Returns the ordered list of arcs."""
    raise NotImplementedError  # TODO step 4


def solve_cpsat(inst: VRPTW, time_limit=60.0, seed=0, workers=1, hint=None, strategy="default"):
    """Build cpsat_model, optionally add_hint(hint) and, for strategy="nearest", add_nearest_strategy
    with parameters search_branching = FIXED_SEARCH when workers == 1 (with more workers the portfolio
    keeps one worker on it). Solve with the given time limit, random_seed and num_workers. Returns a result
    dict: status "optimal" / "feasible" / "infeasible" / "unknown", value and routes from the best
    solution, bound = ⌈best objective bound⌉, nodes = number of branches."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def insertion_delta(inst: VRPTW, route, starts, latest, pos, c):
    """Extra distance of inserting customer c into route before position pos (0: first, len(route): last),
    or None if that's infeasible. starts = schedule(inst, route), latest = latest_starts(inst, route).
    Constant time apart from the load: c's start is max(ready_c, previous start + service + travel);
    it must be <= due_c, and the pushed start at the next customer must stay <= its latest start (or
    the vehicle must be back by due_0 when c is last)."""
    raise NotImplementedError  # TODO step 5


def _positions(inst: VRPTW, routes, c):
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


def shaw_removal(inst: VRPTW, routes, q, rng):
    """Remove q related customers (Shaw 1998; Ropke & Pisinger 2006). Relatedness of i and j:
    dist_ij / max distance + |start_i − start_j| / due_0 + |demand_i − demand_j| / capacity, smaller is
    more related, with starts from schedule(). Start from rng.choice(sorted customers); then repeatedly
    pick a removed customer with rng.choice(removed), sort the remaining customers by relatedness to it
    (ties: customer number), and remove the one at index floor(rng.random() ** 6 * len(remaining)).
    Returns (routes without them, empty routes dropped; removed customers in removal order)."""
    raise NotImplementedError  # TODO step 5


def regret_insertion(inst: VRPTW, routes, removed, k=2):
    """Regret-k repair. Repeatedly, over the customers still to insert, list each one's options: its best
    feasible position in each existing route, plus a new route of its own, which costs d_0c + d_c0 and
    counts as one more "route". Its regret is the sum over h = 2..k of (h-th best extra distance − best
    extra distance), with a missing h-th option counting as infinitely bad. Insert the customer with the
    largest regret at its best option (ties: smaller best extra distance, then smaller customer number;
    between options of equal cost, an existing route before a new one, then earlier route and position).
    k=1 is plain greedy: the cheapest insertion first. New routes are appended at the end. Returns the
    new list of routes (tuples)."""
    raise NotImplementedError  # TODO step 5


def alns_vrptw(inst: VRPTW, time_limit=60.0, seed=0, iterations=None, q_range=(0.1, 0.3)):
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
    raise NotImplementedError  # TODO step 5


# ---------------------------------------------------------------- step 6 ---

def benchmark_solver(method, **options):
    """Adapt a method (inst, time_limit, seed, **options) -> result dict into a solver for unit 28's
    run_benchmark: a function (inst, seed, timeout) -> {"status", "value", "nodes"}. The adapter trusts
    nothing: if the routes fail violations() or their cost isn't the claimed value, the status is
    "invalid" and the value None. A method's "infeasible" is passed through, "unknown" becomes
    "no solution", and "optimal" / "feasible" keep their status."""
    raise NotImplementedError  # TODO step 6


def primal_gap(value, reference):
    """Berthold's primal gap in [0, 1]: 0 if value == reference; 1 if there is no value (None) or the two
    have opposite signs; otherwise |value − reference| / max(|value|, |reference|)."""
    raise NotImplementedError  # TODO step 6


def references(runs):
    """{instance: (best value over runs with status "optimal" or "feasible", proven)} where proven is True
    if some run with that best value has status "optimal". Instances with no such run are absent."""
    raise NotImplementedError  # TODO step 6


def contradictions(runs):
    """Runs whose claim is refuted by another run: status "optimal" with a value larger than some other
    run's valid ("optimal" or "feasible") value on the same instance. Returns sorted (instance, solver,
    seed) triples."""
    raise NotImplementedError  # TODO step 6


def head_to_head(runs, pairs, metric, alpha=0.05):
    """For each (a, b) in pairs: over the instances both solvers ran, the per-instance metric(run) averaged
    over seeds; wins = instances where a's mean is smaller, losses = where b's is, ties the rest; p from unit
    28's wilcoxon_signed_rank on the paired means; p_holm from unit 28's holm over all pairs. The verdict is
    a if p_holm < alpha and wins > losses, b if p_holm < alpha and losses > wins, else "indistinguishable".
    Returns a list of dicts with keys a, b, n, wins, losses, ties, p, p_holm, verdict, in pair order."""
    raise NotImplementedError  # TODO step 6
