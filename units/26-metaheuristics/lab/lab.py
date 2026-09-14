"""Unit 26 lab — metaheuristics, benchmarked honestly.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 26
after each. Read README.md first; HINTS.org has a ladder of hints per step.

TSP: dist is a symmetric integer matrix, a tour is a permutation of range(n) (any rotation or direction).
CVRP: colib.colgen.CVRP (vertex 0 the depot); a solution is a list of routes, each a list of customers.
_reverse is an optional helper for two_opt: no test calls it.
"""

from __future__ import annotations

import math
from collections import deque

from colib.colgen import CVRP


# ---------------------------------------------------------------- step 1 ---

def tour_length(dist, tour):
    """Length of the closed tour."""
    raise NotImplementedError  # TODO step 1


def neighbour_lists(dist, k):
    """For each city, its k nearest other cities, nearest first (ties: lower index)."""
    raise NotImplementedError  # TODO step 1


def nearest_neighbour_tour(dist, start=0):
    """Start at `start`, repeatedly go to the nearest unvisited city (ties: lower index)."""
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def two_opt_move(dist, tour, pos, neighbours, a):
    """The first improving 2-opt move from city a (pos[c] is c's position in tour). For each direction
    (successor, then predecessor), let b be a's tour neighbour in that direction; for each c in neighbours[a]
    (in order) while dist[a][c] < dist[a][b], let d be c's neighbour in the same direction; skip c == b and
    d == a. If replacing edges ab and cd by ac and bd shortens the tour, return (i, j, (a, b, c, d)) where
    reversing the cyclic stretch of positions i, i+1, ..., j makes that exchange. Otherwise return None."""
    raise NotImplementedError  # TODO step 2


def _reverse(tour, pos, i, j):
    """Reverse the cyclic stretch of positions i, i+1, ..., j (inclusive), updating pos."""
    raise NotImplementedError  # TODO step 2


def two_opt(dist, tour, neighbours, dont_look=True):
    """2-opt with neighbour lists, applying two_opt_move.
    dont_look=False: sweep all cities in tour order, applying the move found at each city (if any), until a
    sweep makes no change. The result has no improving move of two_opt_move's form.
    dont_look=True: keep a queue of cities (initially the whole tour, in order); pop a city, apply its move
    if it has one and push the four endpoints that aren't already queued; stop when the queue is empty.
    Faster, and very nearly as good, but not guaranteed locally optimal.
    Returns the new tour (the input is not modified)."""
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def or_opt(dist, tour, neighbours):
    """Or-opt: move a segment of 1, 2 or 3 consecutive cities elsewhere, possibly reversed. Sweep start
    positions 0 .. n-1 and lengths 1, 2, 3; for the segment first..last with outside neighbours p and q,
    consider inserting it between each c in neighbours[first] + neighbours[last] (in that order) and c's
    successor e in the tour without the segment (skip c in the segment and c == p), as c,first..last,e
    and then as c,last..first,e. Apply the first strictly improving move and restart the sweep; stop when
    a full sweep finds none. Requires n >= 8. Returns the new tour."""
    raise NotImplementedError  # TODO step 3


def local_search(dist, tour, neighbours):
    """Alternate two_opt (dont_look=False) and or_opt until neither changes the tour length."""
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def accept(delta, temperature, u):
    """Metropolis: accept a non-worsening move always, a worsening one iff u < exp(-delta / temperature).
    A temperature of 0 accepts only non-worsening moves."""
    raise NotImplementedError  # TODO step 4


def temperature(t0, t_end, iterations, i):
    """Geometric cooling from t0 at i = 0 to t_end at i = iterations - 1."""
    raise NotImplementedError  # TODO step 4


def simulated_annealing(dist, tour, rng, iterations, t0, t_end):
    """At iteration it: draw positions i < j with sorted(rng.sample(range(n), 2)), then u = rng.random() (always,
    even if the move is skipped). Propose reversing tour[i..j], a 2-opt move, skipping it if it would reverse
    the whole tour (i = 0 and j = n - 1). Accept with accept(delta, temperature(t0, t_end, iterations, it), u).
    Returns (best tour seen, its length)."""
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def solution_cost(cvrp: CVRP, routes):
    """Total distance of all routes (cvrp.route_cost adds the depot at both ends)."""
    raise NotImplementedError  # TODO step 5


def random_removal(routes, q, rng):
    """Remove rng.sample(sorted customers, q). Returns (routes without them, empty routes dropped; removed list)."""
    raise NotImplementedError  # TODO step 5


def worst_removal(cvrp: CVRP, routes, q):
    """q times: remove the customer whose removal saves the most distance (ties: lower customer number).
    Returns (routes, empty routes dropped; removed customers in removal order)."""
    raise NotImplementedError  # TODO step 5


def greedy_insertion(cvrp: CVRP, routes, removed):
    """Insert customers in the given order, each at its cheapest feasible position over all routes and
    positions (ties: earlier route, then earlier position); if no route has capacity, open a new route at the
    end. Returns the new routes."""
    raise NotImplementedError  # TODO step 5


def update_weights(weights, scores, uses, reaction):
    """Adaptive weights at the end of a segment: w <- (1 - r) w + r * score / uses for operators used at
    least once; unused operators keep their weight."""
    raise NotImplementedError  # TODO step 5


def alns(cvrp: CVRP, iterations, rng, q=None, segment=50, reaction=0.2, threshold=0.02):
    """ALNS with two destroy operators (0: random_removal, 1: worst_removal) and greedy_insertion as repair.
    Start from greedy_insertion of customers 1..n into no routes. Each iteration: q = q or max(1, n // 10);
    pick a destroy operator with rng.choices(range(2), weights); destroy and repair the current solution.
    Score 33 if the result is a new best, 9 if it beats the current, 13 if it's accepted without improving;
    accept when its cost < current cost, or <= (1 + threshold) * best cost. Every `segment` iterations,
    update_weights and reset scores and uses. Returns (best routes, best cost, list of weights per segment)."""
    raise NotImplementedError  # TODO step 5


# ---------------------------------------------------------------- step 6 ---

def ttt_points(samples):
    """Time-to-target plot points: the successful run times (not None) sorted, the i-th (from 0) at height
    (i + 0.5) / len(samples). Failures stay in the denominator, so the curve tops out below 1 if any run
    failed. Returns a list of (time, probability)."""
    raise NotImplementedError  # TODO step 6


def mann_whitney(a, b):
    """Two-sided Mann-Whitney U test with the normal approximation, tie correction and continuity correction.
    U is the statistic for sample a: the number of pairs (x in a, y in b) with x > y, plus half the ties.
    Returns (U, p)."""
    raise NotImplementedError  # TODO step 6


def verdict(a, b, alpha=0.05):
    """For run times (lower is better): None if the two-sided test doesn't reject at alpha; otherwise "a" if
    a's values tend to be smaller (U < len(a) * len(b) / 2) and "b" if they tend to be larger. The direction
    comes from U, not from medians: with runs capped at a time limit, both medians can be the cap."""
    raise NotImplementedError  # TODO step 6
