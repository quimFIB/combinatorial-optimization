"""Unit 16's recorded DP runs, for units/16-dynamic-programming/explore.html.

The knapsack table is the textbook 2-D recurrence written out cell by cell (the reference
`knapsack` does the same thing row-vectorised, keeping only one row); its answer and chosen
items are checked against the reference before anything is written. The tree DP follows the
reference `tree_vertex_cover` order (children before parents, then a top-down read-back) and
is checked against its result.
"""

from __future__ import annotations

from colib import ref

L = ref.unit("16")

VALUES, WEIGHTS, CAP = [3, 4, 5, 9], [2, 3, 4, 5], 6


def knapsack_states():
    n = len(VALUES)
    table = [[0] * (CAP + 1) for _ in range(n + 1)]
    filled = [[True] * (CAP + 1)] + [[False] * (CAP + 1) for _ in range(n)]
    states = []

    def snap(note, cell=None, deps=None, explain="", path=None):
        states.append({"table": [row[:] for row in table], "filled": [r[:] for r in filled], "cell": cell,
                       "deps": deps, "note": note, "explain": explain, "path": path})

    snap("row 0: with no items, every capacity is worth 0",
         explain="Row i will hold the best value using items 1..i; column c is the capacity allowed.")
    for i in range(1, n + 1):
        w, v = WEIGHTS[i - 1], VALUES[i - 1]
        for c in range(CAP + 1):
            skip = table[i - 1][c]
            if w <= c:
                take = table[i - 1][c - w] + v
                table[i][c] = max(skip, take)
                deps = [[i - 1, c], [i - 1, c - w]]
                verdict = "take it" if take > skip else "skip it"
                explain = (f"Skip item {i}: {skip} (the cell above). Take it: {table[i - 1][c - w]} (row above, capacity {c} − {w}) "
                           f"+ value {v} = {take}. Keep the larger: {verdict}.")
            else:
                table[i][c] = skip
                deps = [[i - 1, c]]
                explain = f"Item {i} weighs {w}, more than capacity {c}: it can't be taken, so copy the cell above."
            filled[i][c] = True
            snap(f"item {i} (weight {w}, value {v}), capacity {c}: {table[i][c]}", cell=[i, c], deps=deps, explain=explain)
    # read the decisions back from the bottom-right cell
    path, c, items = [], CAP, []
    for i in range(n, 0, -1):
        took = WEIGHTS[i - 1] <= c and table[i][c] != table[i - 1][c]
        path.append([i, c, took])
        if took:
            items.append(i - 1)
            c -= WEIGHTS[i - 1]
    items.sort()
    snap(f"answer {table[n][CAP]}: read back, items {', '.join(str(k + 1) for k in items)}",
         explain="Walk up from the bottom-right cell: where a cell differs from the one above, that item was taken, "
                 "and the walk jumps left by its weight.", path=path)
    value, ref_items = L.knapsack(VALUES, WEIGHTS, CAP)
    assert (table[n][CAP], items) == (value, ref_items), "knapsack table disagrees with the reference"
    return states


TREE_EDGES = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
TREE_W = [3, 2, 4, 1, 1, 2, 2]


def tree_states():
    n = len(TREE_W)
    children = {v: [] for v in range(n)}
    for u, v in TREE_EDGES:
        children[u].append(v)
    inc, exc = [None] * n, [None] * n
    states = []

    def snap(note, focus=None, cover=None, explain=""):
        states.append({"inc": inc[:], "exc": exc[:], "focus": focus, "cover": cover, "note": note, "explain": explain})

    snap("each vertex will get two numbers: in and out",
         explain="in = cheapest cover of its subtree that uses the vertex; out = cheapest that doesn't, which forces every child in.")
    order = [3, 4, 5, 6, 1, 2, 0]                          # children before parents
    for v in order:
        kids = children[v]
        inc[v] = TREE_W[v] + sum(min(inc[k], exc[k]) for k in kids)
        exc[v] = sum(inc[k] for k in kids)
        if kids:
            parts = " + ".join(f"min({inc[k]}, {exc[k]})" for k in kids)
            explain = (f"in: its weight {TREE_W[v]} + {parts} = {inc[v]} (children may do either). "
                       f"out: every child must be in, {' + '.join(str(inc[k]) for k in kids)} = {exc[v]}.")
        else:
            explain = f"A leaf: in costs its own weight {TREE_W[v]}; out costs 0."
        snap(f"vertex {v}: in {inc[v]}, out {exc[v]}", focus=v, explain=explain)
    cover = set()
    for v in [0, 1, 2, 3, 4, 5, 6]:                        # parents before children
        parent = next((u for u, w in TREE_EDGES if w == v), None)
        if parent is None:
            chosen = inc[v] <= exc[v]
            why = f"the root takes the cheaper of in {inc[v]} and out {exc[v]}"
        elif parent not in cover:
            chosen = True
            why = f"its parent {parent} is out, so {v} must be in"
        else:
            chosen = inc[v] <= exc[v]
            why = f"its parent {parent} is in, so {v} takes the cheaper of in {inc[v]} and out {exc[v]}"
        if chosen:
            cover.add(v)
        snap(f"read back: vertex {v} {'in' if chosen else 'out'}", focus=v, cover=sorted(cover), explain=why[0].upper() + why[1:] + ".")
    weight = sum(TREE_W[v] for v in cover)
    snap(f"cover {{{', '.join(map(str, sorted(cover)))}}}, weight {weight}", cover=sorted(cover),
         explain=f"Every edge has an endpoint in the cover, and its weight equals the root's better value, min({inc[0]}, {exc[0]}) = {min(inc[0], exc[0])}: optimal.")
    ref_weight, ref_cover = L.tree_vertex_cover(n, TREE_EDGES, TREE_W)
    assert (weight, cover) == (ref_weight, set(ref_cover)), "tree DP disagrees with the reference"
    return states


def data():
    return {
        "knapsack": {"title": "0/1 knapsack, capacity 6", "values": VALUES, "weights": WEIGHTS, "capacity": CAP,
                     "states": knapsack_states()},
        "tree": {"title": "minimum-weight vertex cover of a tree", "edges": TREE_EDGES, "weights": TREE_W,
                 "states": tree_states()},
    }
