"""Unit 15 lab — matching.

Fill in the functions marked TODO, one step at a time, and run
    uv run co test 15
after each. Read README.md first; HINTS.org has a ladder of hints per step.

Conventions. A bipartite graph has left vertices 0..nl-1, right vertices
0..nr-1, and `edges` is a list of pairs (l, r). A bipartite matching is a dict
{l: r}. Cost matrices are lists of lists, cost[i][j] = cost of row i to column j.
A general graph has vertices 0..n-1 and undirected edges (a, b).

Either style is welcome: loops and arrays, or folds and unfolds over immutable
state (see FUNCTIONAL.md at the project root).
"""

from __future__ import annotations

from collections import deque

INF = float("inf")


# ---------------------------------------------------------------- step 1 ---

def hopcroft_karp(nl, nr, edges):
    """Maximum-cardinality matching in a bipartite graph. Returns {l: r}.

    Repeat phases until no augmenting path exists:
      * BFS from every free left vertex, alternating unmatched edges (left to
        right) and matched edges (right to left), recording each left vertex's
        layer. Stop the phase loop if no free right vertex is reached.
      * DFS from each free left vertex along layer-increasing steps only; each
        success flips one augmenting path. A left vertex whose DFS fails is
        removed from the layered graph (set its layer to infinity) so it is
        never explored again this phase.

    Any correct augmenting-path method passes the tests; the layering is what
    makes it O(E sqrt(V)).
    """
    raise NotImplementedError  # TODO step 1


# ---------------------------------------------------------------- step 2 ---

def konig_cover(nl, nr, edges, matching):
    """A minimum vertex cover built from a maximum `matching`. Returns
    (left_set, right_set) with len(left_set) + len(right_set) == len(matching).

    Let Z be every vertex reachable from a free left vertex by an alternating
    path (unmatched edge left to right, matched edge right to left). The cover is
    (left vertices NOT in Z) together with (right vertices in Z).
    """
    raise NotImplementedError  # TODO step 2


# ---------------------------------------------------------------- step 3 ---

def hungarian(cost):
    """Minimum-cost perfect assignment on an n x n matrix. Returns (assign, total, u, v):
    assign[i] = the column given to row i, total = sum of cost[i][assign[i]], and dual
    potentials u (rows) and v (columns) with u[i] + v[j] <= cost[i][j] everywhere and
    equality on every assigned pair.

    Add rows one at a time. For each new row, grow a shortest-path tree over the
    columns on reduced costs cost[i][j] - u[i] - v[j]: repeatedly take the
    cheapest column not yet in the tree, shift the potentials by that amount
    (u up on tree rows, v down on tree columns), and stop when the column is free.
    Then flip the alternating path back to the new row.

    Costs may be negative or fractional.
    """
    raise NotImplementedError  # TODO step 3


# ---------------------------------------------------------------- step 4 ---

def certify_assignment(cost, assign, u, v, tol=1e-9):
    """True iff `assign` is a permutation, (u, v) is dual feasible
    (u[i] + v[j] <= cost[i][j] + tol for all i, j), and every assigned pair is
    tight (|u[i] + v[assign[i]] - cost[i][assign[i]]| <= tol).

    Those three facts together prove the assignment optimal without re-solving.
    """
    raise NotImplementedError  # TODO step 4


# ---------------------------------------------------------------- step 5 ---

def gale_shapley(proposer_prefs, receiver_prefs):
    """The proposer-optimal stable matching. proposer_prefs[p] lists the
    receivers in p's order, best first, and receiver_prefs[r] likewise.
    Both sides have n members. Returns {proposer: receiver}.

    While someone is free: they propose to the best receiver they haven't tried.
    The receiver keeps whichever of (current holder, proposer) they rank higher;
    the other becomes free.
    """
    raise NotImplementedError  # TODO step 5


def is_stable(proposer_prefs, receiver_prefs, matching):
    """True iff no blocking pair exists: no proposer p and receiver r who each
    prefer the other to their partner in `matching` ({proposer: receiver})."""
    raise NotImplementedError  # TODO step 5


# ---------------------------------------------------------------- step 6 (stretch) ---

def blossom(n, edges):
    """Maximum-cardinality matching in a general (not bipartite) graph, by
    Edmonds' blossom algorithm. Returns a list `mate` with mate[v] = partner of v,
    or -1 if v is unmatched.

    From each free root, BFS an alternating tree. An edge between two
    even-labelled vertices closes an odd cycle (a blossom): find the lowest
    common ancestor of its ends, relabel every vertex on the cycle with that base,
    and put the newly even vertices on the queue. Reaching a free vertex gives an
    augmenting path; flip it along the parent pointers.
    """
    raise NotImplementedError  # TODO step 6
